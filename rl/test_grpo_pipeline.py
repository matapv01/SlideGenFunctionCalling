import json
from types import SimpleNamespace

import numpy as np
import pytest
import torch
from PIL import Image
from pydantic import BaseModel
from trl import GRPOTrainer

from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
    tool_matches_image_mode,
)
from backend.workflows.slidegen_workflow.nodes.section_batch_orchestrator import (
    assign_layouts,
)
from backend.workflows.slidegen_workflow.tools.tool_des_xml import TOOLS_DICT
import rl.rewards.aesthetic_reward as aesthetic_reward
import rl.slidegen_adapter as slidegen_adapter
import rl.rewards.composite_reward as composite_reward
import rl.rewards.content_reward as content_reward
from rl.grpo_trainer import DapoAccumulationGRPOTrainer
from rl.rewards.composite_reward import slidegen_composite_reward
from rl.train import _checkpoint_complete
from rl.train_data import deck_style_for_document, normalize_jobs, split_documents
from scripts.generate_challenge_dataset import load_offline_documents


def test_offline_split_is_document_grouped():
    documents = load_offline_documents()
    train_documents, eval_documents = split_documents(documents, eval_docs=2, seed=42)
    train_ids = {doc[0]["source_doc_id"] for doc in train_documents}
    eval_ids = {doc[0]["source_doc_id"] for doc in eval_documents}
    assert train_ids.isdisjoint(eval_ids)
    assert len(train_documents) + len(eval_documents) == len(documents)


def test_training_refuses_to_invent_missing_production_deck_style():
    with pytest.raises(ValueError, match="requires style_context"):
        deck_style_for_document([{"source_doc_id": "legacy"}])


def test_layout_assignment_uses_only_no_image_tools():
    document = load_offline_documents()[0]
    jobs = normalize_jobs(document)
    assigned = assign_layouts(
        {"slide_jobs": jobs},
        {"configurable": {"tools_dict": TOOLS_DICT, "tool_retriever": None}},
    )["slide_jobs"]
    by_name = {
        tool.name: tool
        for tools in TOOLS_DICT.values()
        for tool in tools
    }
    assert all(job.get("preferred_tool_name") for job in assigned)
    assert all(
        tool_matches_image_mode(by_name[job["preferred_tool_name"]], "none", 0)
        for job in assigned
    )


def test_strict_layout_retrieval_fails_on_errors_and_empty_results():
    document = load_offline_documents()[0]
    jobs = normalize_jobs(document)

    class BrokenRetriever:
        def get_relevant_tools(self, **kwargs):
            raise OSError("index unavailable")

    class EmptyRetriever:
        def get_relevant_tools(self, **kwargs):
            return []

    for retriever, message in (
        (BrokenRetriever(), "retrieval failed"),
        (EmptyRetriever(), "no candidates"),
    ):
        with pytest.raises(RuntimeError, match=message):
            assign_layouts(
                {"slide_jobs": jobs},
                {
                    "configurable": {
                        "tools_dict": TOOLS_DICT,
                        "tool_retriever": retriever,
                        "strict_tool_retrieval": True,
                    }
                },
            )


def test_wrong_assigned_tool_is_rejected_before_rendering():
    completion = (
        '<tool_call>{"name":"invented_tool","arguments":{"title":"x"}}'
        "</tool_call>"
    )
    assert slidegen_composite_reward(
        [""],
        [completion],
        assigned_tool_name=["expected_tool"],
        source_content=["x"],
        deck_style=[{}],
    ) == [-2.0]


@pytest.mark.parametrize(
    "completion",
    [
        'prose <tool_call>{"name":"ok","arguments":{}}</tool_call>',
        '<tool_call>{"name":"ok","name":"ok","arguments":{}}</tool_call>',
        '<tool_call>{"name":"ok","arguments":{},}</tool_call>',
        '<tool_call>{"name":"ok","arguments":{},"extra":1}</tool_call>',
        '<tool_call>{"name":"ok","arguments":{}}</tool_call></tool_call>',
    ],
)
def test_noncanonical_tool_calls_are_rejected(completion):
    try:
        parsed = composite_reward._parse_canonical_completion(completion)
    except ValueError:
        parsed = None
    assert parsed is None


def test_reward_missing_metadata_fails_instead_of_scoring_invalid():
    with pytest.raises(ValueError, match="metadata does not match"):
        slidegen_composite_reward(["prompt"], ["not a tool call"])


def test_tool_schema_rejects_unassigned_extra_arguments():
    class Args(BaseModel):
        text: str

    tool = SimpleNamespace(args_schema=Args)
    assert composite_reward._validate_tool_arguments(
        tool, {"text": "visible", "hidden": "unrendered payload"}
    ) is None


def test_content_reward_uses_frontend_rendered_text_not_tool_arguments(monkeypatch):
    class Args(BaseModel):
        text: str

    tool = SimpleNamespace(name="assigned_layout", args_schema=Args)
    monkeypatch.setattr(composite_reward, "_TOOL_BY_NAME", {tool.name: tool})
    monkeypatch.setattr(
        composite_reward,
        "apply_deck_style_to_tool_call",
        lambda call, tools, style: call,
    )
    monkeypatch.setattr(composite_reward, "execute_tool", lambda call: "<slide />")
    monkeypatch.setattr(
        composite_reward,
        "render_xml_batch_to_png",
        lambda xml, paths, max_concurrency=4: [
            {"visible_text": "frontend output has no matching words", "issues": []}
        ],
    )
    monkeypatch.setattr(composite_reward, "_get_model", lambda: object())
    monkeypatch.setattr(
        composite_reward, "_evaluate_batch", lambda model, paths: [0.5]
    )

    class Embedder:
        def encode(self, texts, **kwargs):
            return np.tile(np.array([[1.0, 0.0]], dtype=np.float32), (len(texts), 1))

    monkeypatch.setattr(composite_reward, "_get_text_embedder", lambda: Embedder())
    for name in ("VALID", "SEMANTIC", "FORMAT", "DOM", "AESTHETIC"):
        monkeypatch.setenv(f"RL_REWARD_{name}_WEIGHT", "0")
    monkeypatch.setenv("RL_REWARD_LEXICAL_WEIGHT", "1")
    monkeypatch.setenv("RL_REWARD_NUMERIC_FACT_WEIGHT", "0")
    monkeypatch.setenv("RL_REWARD_IMAGE_LOADED_WEIGHT", "0")
    monkeypatch.setenv("RL_REWARD_LANGUAGE_WEIGHT", "0")

    source = "quantum quasar neutron"
    completion = (
        '<tool_call>{"name":"assigned_layout","arguments":{"text":"'
        + source
        + '"}}</tool_call>'
    )
    reward = slidegen_composite_reward(
        ["prompt"],
        [completion],
        assigned_tool_name=[tool.name],
        source_content=[source],
        deck_style=[{}],
    )
    assert reward == [0.0]
    assert composite_reward._lexical_score(source, "frontend output has no matching words") == 0.0
    assert composite_reward._lexical_score(source, source) == 1.0


@pytest.mark.parametrize(
    ("loss_type", "training", "accumulated_steps", "expected"),
    [
        ("dapo", True, 16, 2.0),
        ("dapo", True, 4, 8.0),
        ("dapo", False, 16, 8.0),
        ("grpo", True, 16, 8.0),
    ],
)
def test_dapo_accumulation_scaling_uses_actual_optimizer_window(
    monkeypatch, loss_type, training, accumulated_steps, expected
):
    monkeypatch.setattr(
        GRPOTrainer,
        "_compute_loss",
        lambda self, model, inputs: torch.tensor(8.0),
    )
    trainer = object.__new__(DapoAccumulationGRPOTrainer)
    trainer.loss_type = loss_type
    trainer.args = SimpleNamespace(steps_per_generation=4)
    trainer.current_gradient_accumulation_steps = accumulated_steps
    actual = trainer._compute_loss(SimpleNamespace(training=training), {})
    assert actual.item() == expected


def test_dapo_scaling_rejects_partial_generation_window(monkeypatch):
    monkeypatch.setattr(
        GRPOTrainer,
        "_compute_loss",
        lambda self, model, inputs: torch.tensor(8.0),
    )
    trainer = object.__new__(DapoAccumulationGRPOTrainer)
    trainer.loss_type = "dapo"
    trainer.args = SimpleNamespace(steps_per_generation=4)
    trainer.current_gradient_accumulation_steps = 2
    with pytest.raises(RuntimeError, match="whole generation windows"):
        trainer._compute_loss(SimpleNamespace(training=True), {})


def test_semantic_reward_scores_content_after_embedding_context_limit():
    class TinyTokenizer:
        def encode(self, text, add_special_tokens=False):
            return text.split()

        def decode(self, tokens, skip_special_tokens=True):
            return " ".join(tokens)

        def num_special_tokens_to_add(self, pair=False):
            return 2

    class TinyEmbedder:
        tokenizer = TinyTokenizer()
        max_seq_length = 10

        def encode(self, texts, **kwargs):
            vocabulary = {"context": 0, "profit": 1, "increase": 2, "decline": 3}
            vectors = []
            for text in texts:
                vector = np.zeros(len(vocabulary), dtype=np.float32)
                for token in text.split():
                    if token in vocabulary:
                        vector[vocabulary[token]] += 1.0
                if not vector.any():
                    vector[0] = 1.0
                vector /= np.linalg.norm(vector)
                vectors.append(vector)
            return np.stack(vectors)

    source = " ".join(["context"] * 16 + ["profit", "increase"])
    faithful = source
    contradictory_tail = " ".join(["context"] * 16 + ["profit", "decline"])
    faithful_score, contradictory_score = content_reward._semantic_reward_scores(
        [source, source], [faithful, contradictory_tail], TinyEmbedder()
    )
    assert faithful_score == pytest.approx(1.0)
    assert contradictory_score < faithful_score


def test_checkpoint_resume_requires_matching_model_loss_and_accumulation(tmp_path):
    checkpoint = tmp_path / "checkpoint-10"
    checkpoint.mkdir()
    for filename in (
        "adapter_model.safetensors",
        "optimizer.pt",
        "scheduler.pt",
        "trainer_state.json",
    ):
        (checkpoint / filename).touch()
    (checkpoint / "rl_checkpoint_metadata.json").write_text(
        json.dumps(
            {
                "model_id": "Qwen/Qwen3-8B",
                "loss_type": "dapo",
                "dapo_accumulation_factor": 4,
            }
        ),
        encoding="utf-8",
    )

    assert _checkpoint_complete(checkpoint, "Qwen/Qwen3-8B", "dapo", 4)
    assert not _checkpoint_complete(checkpoint, "Qwen/Qwen3-4B", "dapo", 4)
    assert not _checkpoint_complete(checkpoint, "Qwen/Qwen3-8B", "grpo", 4)
    assert not _checkpoint_complete(checkpoint, "Qwen/Qwen3-8B", "dapo", 2)
    (checkpoint / "rl_checkpoint_metadata.json").write_text("[]", encoding="utf-8")
    assert not _checkpoint_complete(checkpoint, "Qwen/Qwen3-8B", "dapo", 4)


def test_reward_preflight_runs_vit_on_frontend_render(monkeypatch):
    model = object()
    calls = []
    monkeypatch.setattr(composite_reward, "_get_model", lambda: model)

    def fake_render(xml, output_path):
        calls.append(xml)
        with open(output_path, "wb") as output:
            output.write(b"rendered image")

    monkeypatch.setattr(slidegen_adapter, "render_xml_to_png", fake_render)
    monkeypatch.setattr(
        composite_reward,
        "_evaluate_batch",
        lambda actual_model, paths: [0.75] if actual_model is model and paths else [],
    )
    composite_reward.preflight_reward_runtime()
    assert len(calls) == 1


def test_vit_pairwise_reward_is_higher_for_preferred_logits(tmp_path):
    class FixedClassifier(torch.nn.Module):
        def __init__(self, logits):
            super().__init__()
            self.register_buffer("fixed_logits", logits)

        def forward(self, pixel_values):
            return SimpleNamespace(
                logits=self.fixed_logits.expand(pixel_values.shape[0], -1)
            )

    image_path = tmp_path / "slide.png"
    Image.new("RGB", (16, 16), "white").save(image_path)

    def evaluate(value):
        provider = aesthetic_reward.PairwiseRewardModel(
            model=FixedClassifier(torch.full((1, 1), value)),
            transform=lambda image: torch.zeros((3, 224, 224)),
            device=torch.device("cpu"),
        )
        return aesthetic_reward._evaluate_batch(provider, [image_path])[0]

    assert evaluate(4.0) > evaluate(-4.0)
    assert evaluate(0.0) == pytest.approx(0.5)


def _stub_reward_runtime(monkeypatch, execute):
    class Args(BaseModel):
        text: str

    tool = SimpleNamespace(name="assigned_layout", args_schema=Args)
    monkeypatch.setattr(composite_reward, "_TOOL_BY_NAME", {tool.name: tool})
    monkeypatch.setattr(composite_reward, "apply_deck_style_to_tool_call", lambda call, tools, style: call)
    monkeypatch.setattr(composite_reward, "execute_tool", execute)

    def render(xml, paths, max_concurrency=4):
        for path in paths:
            Image.new("RGB", (8, 8)).save(path)
        return [{"visible_text": "Doanh thu tăng", "issues": []} for _ in paths]

    monkeypatch.setattr(composite_reward, "render_xml_batch_to_png", render)
    monkeypatch.setattr(composite_reward, "_get_model", lambda: object())
    monkeypatch.setattr(composite_reward, "_evaluate_batch", lambda model, paths: [0.5] * len(paths))

    class Embedder:
        def encode(self, texts, **kwargs):
            return np.tile(np.array([[1.0, 0.0]], dtype=np.float32), (len(texts), 1))

    monkeypatch.setattr(composite_reward, "_get_text_embedder", lambda: Embedder())
    return '<tool_call>{"name":"assigned_layout","arguments":{"text":"Doanh thu tăng"}}</tool_call>'


def test_layout_code_exceptions_from_policy_text_are_invalid_not_fatal(monkeypatch):
    from xml.parsers.expat import ExpatError

    def broken(call):
        raise ExpatError("not well-formed (invalid token)")

    completion = _stub_reward_runtime(monkeypatch, broken)
    reward = slidegen_composite_reward(
        ["p"], [completion], assigned_tool_name=["assigned_layout"],
        source_content=["Doanh thu tăng"], deck_style=[{}],
    )
    assert reward == [-2.0]


def test_watched_eval_slides_are_saved_once_per_step(monkeypatch, tmp_path):
    completion = _stub_reward_runtime(monkeypatch, lambda call: "<slide />")
    composite_reward.configure_sample_dump(tmp_path, [("doc-a", 3)])
    try:
        slidegen_composite_reward(
            ["p"] * 3, [completion, completion, "not a tool call"],
            assigned_tool_name=["assigned_layout"] * 3, source_content=["Doanh thu tăng"] * 3,
            deck_style=[{}] * 3, source_doc_id=["doc-a", "doc-a", "doc-b"], slide_index=[3, 3, 1],
            trainer_state=SimpleNamespace(global_step=25),
        )
    finally:
        composite_reward.configure_sample_dump(None, [])
    saved = sorted(path.name for path in (tmp_path / "step_0025").iterdir())
    assert saved == ["doc-a_slide03.json", "doc-a_slide03.png"]
    record = json.loads((tmp_path / "step_0025" / "doc-a_slide03.json").read_text(encoding="utf-8"))
    assert record["valid"] and record["visible_text"] == "Doanh thu tăng" and record["components"]


def _score_one(monkeypatch, visible_text, source):
    completion = _stub_reward_runtime(monkeypatch, lambda call: "<slide />")
    monkeypatch.setattr(
        composite_reward, "render_xml_batch_to_png",
        lambda xml, paths, max_concurrency=4: [{"visible_text": visible_text, "issues": []} for _ in paths],
    )
    return slidegen_composite_reward(
        ["p"], [completion], assigned_tool_name=["assigned_layout"],
        source_content=[source], deck_style=[{}],
    )[0]


def test_wrong_language_zeroes_an_otherwise_valid_slide(monkeypatch):
    source = "Doanh thu tăng trưởng mạnh nhờ chuyển đổi số toàn diện"
    assert _score_one(monkeypatch, "Revenue grew strongly thanks to digital transformation", source) == 0.0
    assert _score_one(monkeypatch, "Doanh thu tăng trưởng mạnh nhờ chuyển đổi số", source) > 0.0


def test_leaked_highlight_markup_costs_layout_score(monkeypatch):
    source = "Chuyển từ đánh nhanh thắng nhanh sang đánh chắc tiến chắc"
    clean = _score_one(monkeypatch, "Chuyển từ đánh nhanh thắng nhanh sang đánh chắc tiến chắc", source)
    leaked = _score_one(monkeypatch, "Chuyển từ <đánh nhanh thắng nhanh[/hl]]> sang đánh chắc tiến chắc", source)
    assert leaked < clean


def test_unsupported_figures_are_logged_for_diagnosis(monkeypatch, tmp_path):
    composite_reward.configure_sample_dump(tmp_path, [])
    try:
        _score_one(monkeypatch, "Doanh thu tăng 48% và lợi nhuận đạt 1.200 tỷ", "Doanh thu tăng 48%")
    finally:
        composite_reward.configure_sample_dump(None, [])
    records = [json.loads(line) for line in (tmp_path / "unsupported_numbers.jsonl").read_text().splitlines()]
    assert [item["value"] for item in records[0]["flagged"]] == ["1.200"]
    assert records[0]["source_numbers"] == ["48%"]
