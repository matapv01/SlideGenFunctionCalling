"""CPU-only regression tests; no model downloads or external endpoints."""
import json
from types import SimpleNamespace
from pathlib import Path

import numpy as np
import pytest
from PIL import Image
from pydantic import BaseModel

import rl.rewards.composite_reward as reward
import rl.rewards.content_reward as content_reward
import rl.slidegen_adapter as adapter
import rl.train as train
from rl.render_runtime import RenderRuntime
from rl.training_contract import contract_digest
from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
    NoApprovedImageError, inject_approved_images, tool_matches_image_mode,
)
from backend.workflows.slidegen_workflow.nodes.section_batch_orchestrator import assign_layouts


def test_preflight_only_stops_before_policy_and_forces_reward_check(monkeypatch, tmp_path):
    import torch

    monkeypatch.setattr(train, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(train, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(train, "RUN_PREFLIGHT", False)
    monkeypatch.setattr(train, "_model_runtime", lambda: ("cpu", torch.float32))
    monkeypatch.setattr(train, "load_offline_documents", lambda path: [[{"approved_images": [{}]}]] * 2)
    monkeypatch.setattr(train, "split_documents", lambda *args: ([[]], [[]]))
    tokenizer = SimpleNamespace(pad_token=None, eos_token="<eos>", encode=lambda *a, **k: [1, 2])
    monkeypatch.setattr(train.AutoConfig, "from_pretrained", lambda *a, **k: SimpleNamespace(max_position_embeddings=8192))
    monkeypatch.setattr(train.AutoTokenizer, "from_pretrained", lambda *a, **k: tokenizer)
    retriever = SimpleNamespace(embeddings=SimpleNamespace(model=object()))
    monkeypatch.setattr(train, "LocalEmbeddingToolRetrieveProvider", lambda *a: retriever)
    monkeypatch.setattr(train, "set_text_embedder", lambda *a: None)
    asset = {"source_id": "test"}
    row = {"prompt": "test", "image_mode": "semantic", "approved_images": [asset]}
    monkeypatch.setattr(train, "prepare_document", lambda *a, **k: [row])
    monkeypatch.setattr(train, "GRPOConfig", lambda **k: SimpleNamespace(**k, steps_per_generation=1))
    monkeypatch.setattr(train, "build_training_contract", lambda *a, **k: {"test": True})
    monkeypatch.setattr(train, "_latest_checkpoint", lambda *a: None)
    monkeypatch.setattr(train, "start_run_logging", lambda *a: None)
    checked = []
    monkeypatch.setattr(train, "preflight_reward_runtime", lambda assets: checked.extend(assets))

    def forbidden(*args, **kwargs):
        pytest.fail("Preflight must not load a policy or construct a trainer")

    monkeypatch.setattr(train, "_load_model", forbidden)
    monkeypatch.setattr(train, "DapoAccumulationGRPOTrainer", forbidden)
    train._train_main(preflight_only=True)
    assert checked == [asset, asset]
    reports = list(tmp_path.glob("rl/log/grpo/run_*/preflight.json"))
    assert len(reports) == 1
    report = json.loads(reports[0].read_text())
    assert report["status"] == "passed"
    assert report["policy_loaded"] is False
    assert report["optimizer_step_tested"] is False
    assert not (train.OUTPUT_DIR / "dataset_snapshots").exists()


def test_preflight_cli_closes_renderer_on_failure(monkeypatch):
    closed = []
    def fail(**kwargs):
        assert kwargs == {"preflight_only": True}
        raise RuntimeError("preflight failed")
    monkeypatch.setattr(train, "_train_main", fail)
    monkeypatch.setattr(train, "close_render_runtime", lambda: closed.append(True))
    with pytest.raises(RuntimeError, match="preflight failed"):
        train.main(["--preflight-only"])
    assert closed == [True]


def test_vit_loader_freezes_reward_parameters(monkeypatch, tmp_path):
    import torch
    import rl.rewards.aesthetic_reward as aesthetic

    checkpoint = tmp_path / "best.pt"
    checkpoint.touch()
    model = torch.nn.Linear(2, 1)
    monkeypatch.setattr(aesthetic, "_MODEL", None)
    monkeypatch.setattr(aesthetic, "_model_path", lambda: checkpoint)
    monkeypatch.setenv("REWARD_MODEL_DEVICE", "cpu")
    monkeypatch.setattr(aesthetic, "ViTForImageClassification", lambda config: model)
    monkeypatch.setattr(aesthetic.torch, "load", lambda *a, **k: model.state_dict())
    provider = aesthetic._get_model()
    assert provider.model is model
    assert not model.training
    assert all(not p.requires_grad for p in model.parameters())
    assert aesthetic._get_model() is provider


@pytest.mark.parametrize("source,output,expected", [
    ("Doanh thu tăng 5 phần trăm", "Doanh thu tăng 9 phần trăm", 0.0),
    ("Giảm -5%", "Giảm 5%", 0.0),
    ("Giảm −5,2%", "Giảm -5,2 %", 1.0),
    ("Tăng 5%", "Tăng 5", 0.0),
    ("Năm 2024 đạt 5", "Năm 2024 đạt 9", 0.5),
    ("Tiêu đề", "Tiêu đề", 1.0),
])
def test_numeric_fact_score_tracks_missing_or_changed_values(source, output, expected):
    assert content_reward._numeric_fact_coverage(source, output) == pytest.approx(expected)


@pytest.mark.parametrize("source,output,expected", [
    ("Doanh thu đạt 15.501 tỷ", "Doanh thu: 15501", 0.0),
    ("Tăng 48%", "Tăng 48% và 3 trụ cột", 0.0),
    ("Tăng 48%", "Tăng 48%, lợi nhuận 1.200 tỷ", 0.5),
    ("Không có số liệu", "Lợi nhuận tăng 35,8%", 1.0),
])
def test_unsupported_numbers_ignore_formatting_and_enumerations(source, output, expected):
    assert content_reward._unsupported_number_fraction(source, output) == pytest.approx(expected)


def test_fabricated_figures_reduce_numeric_fact_score():
    assert content_reward._numeric_fact_coverage("Tiêu đề", "Tăng 35,8%") == 0.0
    assert content_reward._numeric_fact_coverage("Tăng 48%", "Tăng 48%, đạt 900 dự án") == pytest.approx(0.5)


class Embedder:
    def __init__(self):
        self.calls = []

    def encode(self, texts, **kwargs):
        self.calls.append(list(texts))
        return np.tile([1., 0.], (len(texts), 1))


def test_source_cache_deduplicates_reuses_and_resets(monkeypatch):
    monkeypatch.setenv("RL_SOURCE_EMBEDDING_CACHE_SIZE", "1")
    model = Embedder()
    result = content_reward._encode_reward_chunks(["a", "b", "a"], {"a"}, model)
    assert result.shape == (3, 2)
    assert model.calls == [["a", "b"]]
    content_reward._encode_reward_chunks(["a", "b"], {"a"}, model)
    assert model.calls[-1] == ["b"]  # Output vectors are not retained.
    content_reward._encode_reward_chunks(["c"], {"c"}, model)
    assert list(content_reward._SOURCE_EMBEDDINGS) == ["c"]
    replacement = Embedder()
    content_reward._encode_reward_chunks(["c"], {"c"}, replacement)
    assert replacement.calls == [["c"]]
    monkeypatch.setenv("RL_SOURCE_EMBEDDING_CACHE_SIZE", "0")
    content_reward._encode_reward_chunks(["c"], {"c"}, replacement)
    assert not content_reward._SOURCE_EMBEDDINGS


def test_semantic_and_numeric_signals_are_independent():
    source, generated = "Tăng 5%", "Tăng 9%"
    assert content_reward._semantic_reward_scores([source], [generated], Embedder()) == [1.0]
    assert content_reward._numeric_fact_coverage(source, generated) == 0.0


def test_numeric_literals_are_scored_only_by_the_numeric_fact_component():
    assert content_reward.clean_words("Revenue grew 10% in 2024") == ["revenue", "grew", "in"]
    assert content_reward.clean_words("Qwen3 won 3rd place in 2024") == [
        "qwen3", "won", "3rd", "place", "in"
    ]
    assert content_reward._without_numeric_values("Revenue grew 10% in 2024").split() == [
        "Revenue", "grew", "in"
    ]
    assert [number for number, _ in content_reward._numeric_occurrences("3rd quarter grew 5%.")] == ["5%"]
    assert content_reward._without_numeric_values("3rd quarter grew 5%.").split() == [
        "3rd", "quarter", "grew", "."
    ]
    assert content_reward._numeric_occurrences("The 5G network is in its 3rd phase.") == []


def test_loaded_image_must_match_each_expected_asset():
    statuses = [{"src": "http://backend/static/output/a.png", "loaded": True},
                {"src": "/static/output/unrelated.png", "loaded": True}]
    assert reward._image_loading_score(["/static/output/a.png"], statuses) == 1
    assert reward._image_loading_score(["/static/output/a.png", "/static/output/b.png"], statuses) == .5
    assert reward._image_loading_score(["/static/output/a.png"] * 2, statuses) == .5
    assert reward._image_loading_score([], statuses) == 1


class TwoImages(BaseModel):
    image_url_1: str = ""
    image_url_2: str = ""


class TextOnly(BaseModel):
    title: str = ""


def test_exact_image_count_and_strict_layout_failure():
    tool = SimpleNamespace(name="two", args_schema=TwoImages)
    text_tool = SimpleNamespace(name="text", args_schema=TextOnly)
    assert tool_matches_image_mode(tool, "semantic", 2)
    assert not tool_matches_image_mode(tool, "semantic", 3)
    with pytest.raises(NoApprovedImageError):
        inject_approved_images({"name": "two", "arguments": {}}, tool=tool,
                               approved_images=[{}] * 3, asset_dir=None)
    job = {"index": 0, "batch_id": "one", "plan": {"action": "CONTENT_TOOLS", "image_mode": "semantic"},
           "approved_images": [{"source_id": "a"}] * 3}
    config = {"configurable": {"tools_dict": {"CONTENT_TOOLS": [tool, text_tool]},
                                "strict_image_layouts": True}}
    with pytest.raises(RuntimeError, match="exactly"):
        assign_layouts({"slide_jobs": [job]}, config)
    config["configurable"]["strict_image_layouts"] = False
    output = assign_layouts({"slide_jobs": [job]}, config)["slide_jobs"][0]
    assert output["approved_images"] == []
    assert output["plan"]["image_mode"] == "none"
    assert output["preferred_tool_name"] == "text"


def test_preflight_checks_actual_asset_url(monkeypatch, tmp_path):
    image = tmp_path / "asset.png"
    Image.new("RGB", (4, 4)).save(image)
    monkeypatch.setattr(reward, "_get_model", lambda: object())
    monkeypatch.setattr(reward, "_evaluate_batch", lambda *args: [.5])
    monkeypatch.setattr(adapter, "render_xml_to_png", lambda xml, path: Image.new("RGB", (4, 4)).save(path))
    urls = []
    def render(xmls, paths, **kwargs):
        urls.extend(xmls)
        return [{"image_status": [{"src": "/static/output/wrong.png", "loaded": True}]}]
    monkeypatch.setattr(reward, "render_xml_batch_to_png", render)
    with pytest.raises(RuntimeError, match="cannot be loaded"):
        reward.preflight_reward_runtime([{"source_path": "/static/output/asset.png", "local_path": str(image)}])
    assert "/static/output/asset.png" in urls[0]


def test_contract_sets_are_canonical_and_changes_detected():
    first = {"lora": {"q_proj", "v_proj"}, "rows": [1, 2]}
    second = {"rows": [1, 2], "lora": set(["v_proj", "q_proj"])}
    assert contract_digest(first) == contract_digest(second)
    second["rows"] = [2, 1]
    assert contract_digest(first) != contract_digest(second)


def test_resume_rejects_latest_incompatible_checkpoint(monkeypatch, tmp_path):
    monkeypatch.setattr(train, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(train, "RESUME", True)
    for step, fingerprint in [(1, "matching"), (2, "changed")]:
        checkpoint = tmp_path / f"checkpoint-{step}"
        checkpoint.mkdir()
        for filename in ("adapter_model.safetensors", "optimizer.pt", "scheduler.pt", "trainer_state.json"):
            (checkpoint / filename).touch()
        (checkpoint / "rl_checkpoint_metadata.json").write_text(json.dumps({
            "model_id": "qwen", "loss_type": "dapo", "dapo_accumulation_factor": 4,
            "training_contract": fingerprint,
        }))
    with pytest.raises(ValueError, match="incompatible"):
        train._latest_checkpoint("qwen", "dapo", 4, "matching")
    assert train._latest_checkpoint("qwen", "dapo", 4, "changed").name == "checkpoint-2"


def test_browser_reuse_and_failed_batch_cleanup(monkeypatch, tmp_path):
    import playwright.async_api
    pages, launches, stops = [], [], []
    class Page:
        closed = False
        async def evaluate(self, script):
            return {"visible_text": self.xml}
        async def screenshot(self, **kwargs):
            pass
        async def close(self):
            self.closed = True
    class Browser:
        connected = True
        def is_connected(self):
            return self.connected
        async def new_page(self, **kwargs):
            page = Page()
            pages.append(page)
            return page
        async def close(self):
            self.connected = False
    browser = Browser()
    class Playwright:
        @property
        def chromium(self):
            return self
        async def launch(self, **kwargs):
            launches.append(kwargs)
            return browser
        async def stop(self):
            stops.append(True)
    class Manager:
        async def start(self):
            return Playwright()
    monkeypatch.delenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE", raising=False)
    monkeypatch.setattr(playwright.async_api, "async_playwright", Manager)
    monkeypatch.setenv("RL_RENDER_TIMEOUT_SECONDS", "1")
    monkeypatch.setenv("RL_RENDER_TIMEOUT_RETRIES", "0")
    runtime = RenderRuntime()
    async def prepare(page, xml, index, **kwargs):
        page.xml = xml
        if xml == "slow":
            import asyncio
            await asyncio.sleep(5)
        if xml == "bad":
            raise ValueError("bad sample")
    runtime._capture._prepare_xml_preview_page = prepare
    try:
        assert runtime.submit(["first"], [tmp_path / "1.png"], "", 2).result(5)[0]["visible_text"] == "first"
        with pytest.raises(ValueError, match="bad sample"):
            runtime.submit(["bad", "good"], [tmp_path / "2.png", tmp_path / "3.png"], "", 2).result(5)
        assert all(page.closed for page in pages)
        with pytest.raises(TimeoutError):
            runtime.submit(["slow"], [tmp_path / "slow.png"], "", 1).result(3)
        assert all(page.closed for page in pages)
        assert runtime.submit(["last"], [tmp_path / "4.png"], "", 2).result(5)[0]["visible_text"] == "last"
        assert len(launches) == 1
        assert len(pages) == 5
    finally:
        runtime.close()
    assert all(page.closed for page in pages)
    assert stops == [True]
    assert not runtime._thread.is_alive()


def test_training_contract_builds_and_detects_asset_changes(monkeypatch, tmp_path):
    from rl.training_contract import build_training_contract
    import rl.rewards.aesthetic_reward as aesthetic
    corpus = tmp_path / "corpus.json"
    corpus.write_text("[]")
    vit = tmp_path / "vit.bin"
    vit.write_bytes(b"vit")
    asset = tmp_path / "asset.png"
    asset.write_bytes(b"first")
    monkeypatch.setattr(aesthetic, "_model_path", lambda: vit)
    rows = [{"prompt": "qwen prompt", "source_content": "source",
             "approved_images": [{"source_path": "/static/output/asset.png", "local_path": str(asset)}]}]
    def build():
        return build_training_contract(rows, [], SimpleNamespace(), "qwen", train._lora_config(), corpus)
    first = build()
    assert isinstance(first["lora"]["target_modules"], list)
    assert contract_digest(first) == contract_digest(build())
    monkeypatch.setenv("RL_PAIRWISE_TEMPERATURE", "2")
    assert contract_digest(first) != contract_digest(build())
    monkeypatch.delenv("RL_PAIRWISE_TEMPERATURE")
    asset.write_bytes(b"changed")
    assert contract_digest(first) != contract_digest(build())


def test_training_contract_fingerprints_local_base_model_weights(monkeypatch, tmp_path):
    from rl.training_contract import build_training_contract
    import rl.rewards.aesthetic_reward as aesthetic

    monkeypatch.setattr(aesthetic, "_model_path", lambda: tmp_path / "vit.bin")
    (tmp_path / "vit.bin").write_bytes(b"vit")
    model_dir = tmp_path / "qwen3-8b"
    model_dir.mkdir()
    (model_dir / "config.json").write_text("{}")
    (model_dir / "model.safetensors").write_bytes(b"weights-v1")
    corpus = tmp_path / "corpus.json"
    corpus.write_text("[]")

    def build():
        return build_training_contract(
            [], [], SimpleNamespace(), str(model_dir), train._lora_config(), corpus
        )

    first = build()
    (model_dir / "model.safetensors").write_bytes(b"weights-v2")
    assert contract_digest(first) != contract_digest(build())


def test_no_image_executor_retry_does_not_reinject_old_assets(monkeypatch):
    from importlib import import_module
    executor = import_module("backend.workflows.slidegen_workflow.nodes.tool_call_executor")
    monkeypatch.setattr(executor, "validate_tool_call", lambda *args, **kwargs: (True, []))
    monkeypatch.setattr(executor, "_normalize_plan_for_execution", lambda plan, lookup: plan)
    received = []
    def execute(plan, **kwargs):
        received.append(kwargs["approved_images"])
        return "<slide />", plan[0], []
    monkeypatch.setattr(executor, "execute_xml_tool_plan", execute)
    state = {"current_slide_index": 0, "force_no_image_layout": True,
             "current_tool_call": {"name": "no_image", "arguments": {}},
             "current_approved_images": [{"source_id": "old"}],
             "slide_options": {"approved_image_assignments": [{"slide_index": 0, "source_id": "old"}]}}
    assert executor.tool_call_executor(state, {})["executor_decision"] == "pass"
    assert received == [[]]


@pytest.mark.parametrize("source,generated,minimum", [
    ("Năm 2024, doanh thu 150 tỷ đồng, lợi nhuận 30 tỷ đồng.",
     "Năm 2024, doanh thu 150 tỷ đồng, lợi nhuận 30 tỷ đồng.", .99),
    ("Năm 2024, doanh thu 150 tỷ đồng, lợi nhuận 30 tỷ đồng.",
     "Năm 2024, lợi nhuận 150 tỷ đồng, doanh thu 30 tỷ đồng.", 0.0),
    ("Doanh thu 150 tỷ đồng, lợi nhuận 30 tỷ đồng.",
     "Doanh thu 150 tỷ đồng.", .5),
])
def test_numeric_fact_context_detects_swapped_and_missing_values(source, generated, minimum):
    assert content_reward._numeric_fact_coverage(source, generated) >= minimum


def test_structural_list_numbers_are_not_scored_as_factual_values():
    source = "1. Alice has 15 years of experience.\n• 2. Bob has 20 years of experience."
    generated = "Alice has 15 years of experience.\nBob has 20 years of experience."
    assert [number for number, _ in content_reward._numeric_occurrences(source)] == ["15", "20"]
    assert content_reward._numeric_fact_coverage(source, generated) == 1.0


def test_unanchored_coordinated_values_preserve_fact_attribution():
    source = "Japan and APAC, respectively, grew 43.4% and 37.7%."
    generated = "Japan and APAC, respectively, grew 43.4% and 37.7%."
    scores = content_reward._numeric_fact_scores(source, generated)
    assert scores == [1.0, 1.0]
    assert content_reward._numeric_fact_coverage(source, generated) == 1.0


def test_swapped_metric_values_are_detected_across_conjunctions():
    source = "Năm 2024, doanh thu 150 tỷ đồng và lợi nhuận 30 tỷ đồng."
    swapped = "Năm 2024, lợi nhuận 150 tỷ đồng và doanh thu 30 tỷ đồng."
    scores = content_reward._numeric_fact_scores(source, swapped)
    assert scores == [1.0, 0.0, 0.0]
    assert content_reward._numeric_fact_coverage(source, swapped) == pytest.approx(1 / 3)


def test_weighted_reward_applies_each_component_once():
    weights = reward.reward_weights()
    perfect = {name: 1.0 for name in weights}
    baseline = reward._weighted_reward(perfect, weights)

    changed_number = dict(perfect, numeric_fact=0.0)
    assert baseline - reward._weighted_reward(changed_number, weights) == pytest.approx(
        weights["numeric_fact"]
    )

    missing_image = dict(perfect, image_loaded=0.0)
    assert baseline - reward._weighted_reward(missing_image, weights) == pytest.approx(
        weights["image_loaded"]
    )

    layout_failure = dict(perfect, dom=0.0)
    assert baseline - reward._weighted_reward(layout_failure, weights) == pytest.approx(
        weights["dom"]
    )

    omitted_content = dict(perfect, lexical=0.0, semantic=0.0)
    assert baseline - reward._weighted_reward(omitted_content, weights) == pytest.approx(
        weights["lexical"] + weights["semantic"]
    )


def test_reward_components_are_bounded_and_have_matching_weights():
    with pytest.raises(ValueError, match="identical keys"):
        reward._weighted_reward({"lexical": 1.0}, {"semantic": 1.0})
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        reward._weighted_reward({"lexical": 1.1}, {"lexical": 1.0})


def test_dom_score_is_normalized_and_does_not_recount_image_failures():
    assert reward._dom_score([]) == 1.0
    assert reward._dom_score([{"type": "image_load"}]) == 1.0
    one_issue = reward._dom_score([{"type": "text_cutoff", "textbox": "body"}])
    many_issues = reward._dom_score([
        {"type": "text_cutoff", "textbox": f"body-{index}"}
        for index in range(20)
    ])
    assert one_issue == 0.0
    assert many_issues == 0.0


def test_bbox_collision_ignores_overlap_of_expanded_textbox_bounds():
    metrics = {
        "issues": [],
        "collision_boxes": [
            {
                "id": "bullet-marker",
                "bounds": {"x": 71.7, "y": 276.6, "width": 58.1, "height": 160.6},
                "rects": [{"x": 71.7, "y": 282.6, "width": 31.2, "height": 62.4}],
            },
            {
                "id": "bullet-content",
                "bounds": {"x": 116.6, "y": 276.6, "width": 919.0, "height": 160.6},
                "rects": [{"x": 116.6, "y": 282.6, "width": 737.6, "height": 62.4}],
            },
        ],
    }
    marker, content = metrics["collision_boxes"]
    assert (
        marker["bounds"]["x"] + marker["bounds"]["width"]
        > content["bounds"]["x"]
    )

    result = adapter._attach_bbox_collision_issues(metrics)

    assert result["issues"] == []
    assert "collision_boxes" not in result


def test_bbox_collision_detects_meaningful_visible_text_overlap():
    metrics = {
        "issues": [],
        "collision_boxes": [
            {"id": "title", "rects": [{"x": 10, "y": 20, "width": 100, "height": 30}]},
            {"id": "body", "rects": [{"x": 90, "y": 25, "width": 100, "height": 30}]},
        ],
    }

    result = adapter._attach_bbox_collision_issues(metrics)

    assert result["issues"] == [
        {"type": "bbox_collision", "textbox": "title", "other": "body"}
    ]


def test_fact_context_allows_real_corpus_identity_and_common_rephrasing():
    import json
    rows = json.loads((Path(__file__).parent / "data" / "sft_function_call_dataset.json").read_text())
    numeric_rows = [str(row.get("slide_content") or "") for row in rows
                    if content_reward._numeric_occurrences(str(row.get("slide_content") or ""))]
    # Exclude list ordinals and embedded labels such as 2G/5G from numeric facts.
    assert len(numeric_rows) == 130
    assert all(content_reward._numeric_fact_coverage(text, text) == 1.0 for text in numeric_rows)
    variants = (
        ("doanh thu", "nguồn thu"),
        ("tăng", "gia tăng"),
        ("giảm", "suy giảm"),
    )
    for source_phrase, replacement in variants:
        candidates = [text for text in numeric_rows if source_phrase in text.casefold()]
        for text in candidates:
            rewritten = text.casefold().replace(source_phrase, replacement)
            scores = content_reward._numeric_fact_scores(text, rewritten)
            assert content_reward._numeric_fact_coverage(text, rewritten) == 1.0
            assert all(score == 1.0 for score in scores)


def test_numeric_context_is_sentence_local_and_scores_one_bad_fact():
    source = "Revenue rose 10%. Profit fell 5%."
    wrong_direction = "Revenue fell 10%. Profit fell 5%."
    facts = content_reward._numeric_fact_scores(source, wrong_direction)
    assert facts == [0.0, 1.0]
    assert content_reward._numeric_fact_coverage(source, wrong_direction) == pytest.approx(0.5)


def test_sentence_local_context_keeps_neighboring_opposite_facts_separate():
    text = "Revenue rose 10%. Profit fell 5%."
    assert content_reward._numeric_fact_scores(text, text) == [1.0, 1.0]


def test_precomputed_numeric_facts_match_runtime_extraction():
    source = "Năm 2025, doanh thu tăng 20% và lợi nhuận đạt 30 tỷ đồng."
    records = content_reward._numeric_fact_records(source)
    assert records
    assert content_reward._numeric_fact_scores(source, source, records) == [1.0] * len(records)
    changed = source.replace("doanh thu", "lợi nhuận", 1)
    assert content_reward._numeric_fact_scores(
        source, changed, records
    ) == content_reward._numeric_fact_scores(source, changed)


def test_language_consistency_penalizes_english_slides_for_vietnamese_sources():
    source = "Đã đến lúc chuyển từ bán cái mình có sang chế biến sâu và bán câu chuyện thị trường cần."
    assert content_reward._language_consistency(source, "Strategic shift to value creation") == 0.0
    assert content_reward._language_consistency(source, "Bước ngoặt: chế biến sâu cà phê Việt") == 1.0
    assert content_reward._language_consistency("Revenue grew strongly", "Doanh thu tăng") == 1.0


def test_timeline_milestones_survive_structured_tool_invocation():
    from backend.workflows.slidegen_workflow.tools import tool_des_xml

    xml = tool_des_xml.TOOL_MAP["generate_implementation_timeline_slide_xml"].invoke({
        "title": "Lộ trình", "subtitle": "Ba giai đoạn",
        "timeline_items": [{"label": "Hiện tại", "content": "Bán thô"}, {"label": "Mục tiêu", "content": "Chế biến sâu"}],
    })
    assert "Hiện tại" in xml and "Chế biến sâu" in xml


def test_warm_start_lora_copies_adapter_weights(tmp_path):
    import torch
    from peft import LoraConfig, get_peft_model, get_peft_model_state_dict
    from safetensors.torch import save_file
    from rl import train

    def tiny():
        torch.manual_seed(0)
        base = torch.nn.Sequential()
        base.add_module("q_proj", torch.nn.Linear(8, 8))
        return get_peft_model(base, LoraConfig(r=2, lora_alpha=4, target_modules=["q_proj"]))

    trained = tiny()
    for name, parameter in trained.named_parameters():
        if "lora_B" in name:
            torch.nn.init.normal_(parameter)
    save_file(get_peft_model_state_dict(trained), str(tmp_path / "adapter_model.safetensors"))
    fresh = tiny()
    train._warm_start_lora(fresh, str(tmp_path))
    expected = dict(trained.named_parameters())
    for name, parameter in fresh.named_parameters():
        if "lora_" in name:
            assert torch.equal(parameter, expected[name])


def test_fabricated_contact_details_count_as_unsupported():
    assert content_reward._unsupported_number_fraction("Cảm ơn quý vị", "Cảm ơn info@vinfast.com vinfast.com") == 1.0
    assert content_reward._unsupported_number_fraction(
        "Website: https://fpt.com.vn, email support@fpt.com", "support@fpt.com www.fpt.com.vn"
    ) == 0.0


def test_contrast_issue_uses_rendered_pixels(tmp_path):
    from PIL import Image

    from rl.slidegen_adapter import _attach_contrast_issues

    png = tmp_path / "slide.png"
    image = Image.new("RGB", (320, 180), "#0F172A")
    image.paste("#FFFFFF", (0, 90, 320, 180))
    image.save(png)
    run = {"x": 20, "width": 200, "height": 20}
    metrics = {
        "issues": [],
        "canvas": {"width": 160, "height": 90},
        "color_boxes": [
            {"id": "dark_on_dark", "runs": [{**run, "x": 10, "width": 100, "y": 10, "color": "rgb(15, 23, 42)"}]},
            {"id": "dark_on_light", "runs": [{**run, "x": 10, "width": 100, "y": 60, "color": "rgb(15, 23, 42)"}]},
            {"id": "translucent", "runs": [{**run, "x": 10, "width": 100, "y": 60, "color": "rgba(15, 23, 42, 0.1)"}]},
        ],
    }
    result = _attach_contrast_issues(metrics, str(png))
    flagged = {issue["textbox"] for issue in result["issues"] if issue["type"] == "low_contrast"}
    assert flagged == {"dark_on_dark", "translucent"}
    assert result["min_contrast"] < 1.1
    assert "color_boxes" not in result and "canvas" not in result


def test_dom_score_penalizes_unreadable_and_cut_off_text():
    from rl.rewards.composite_reward import _dom_score

    assert _dom_score([]) == 1.0
    assert _dom_score([{"type": "low_contrast", "textbox": "title"}]) == 0.0
    assert _dom_score([{"type": "text_cutoff", "textbox": "body"}]) == 0.0
    assert _dom_score([{"type": "text_height", "textbox": "body"}]) == pytest.approx(0.75)
    # Width overflow that people never flagged as a display error costs nothing on its own.
    assert _dom_score([{"type": "text_width", "textbox": "body"}]) == 1.0


def test_lenient_json_repairs_inner_quotes_only_when_enabled(monkeypatch):
    raw = '["Ô nhiễm", "Giải pháp "nói không với rác thải"", "Tăng [[hl color="#0D9488"]]495%[[/hl]]"]'
    monkeypatch.delenv("RL_LENIENT_JSON", raising=False)
    with pytest.raises(json.JSONDecodeError):
        reward._loads_structured(raw)
    monkeypatch.setenv("RL_LENIENT_JSON", "true")
    assert reward._loads_structured(raw) == [
        "Ô nhiễm", 'Giải pháp "nói không với rác thải"', "Tăng [[hl color=#0D9488]]495%[[/hl]]",
    ]
    # Structurally broken arrays stay invalid.
    with pytest.raises(json.JSONDecodeError):
        reward._loads_structured('[{"label": "a", "content": "b" [[/hl]], "label": "c"}')
