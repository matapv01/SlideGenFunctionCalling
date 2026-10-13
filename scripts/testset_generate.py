"""Generate and score SlideGen test-set slides for each compared system.

Every system gets the exact training-time inputs: the same planned corpus, layout assignment,
generator prompt, single assigned tool schema, deck style, approved images, tool executor,
renderer and composite reward. Only the policy that writes the tool call differs.

Steps (run in order; each one resumes from what is already on disk):
  prepare  build prompts + chat messages from the planned test corpus
  qwen     sample completions from the base model and the DAPO adapter (GPU)
  gemini   sample completions from Gemini through native function calling (API)
  score    render, score every completion, save PNG + component scores per sample

Usage (training venv, same env as rl/train.py):
  python scripts/testset_generate.py prepare
  python scripts/testset_generate.py qwen --adapter <ckpt> --base-samples 8 --rl-samples 4
  python scripts/testset_generate.py gemini --samples 1
  python scripts/testset_generate.py score
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

TESTSET = ROOT / "slidegen_data" / "testset"
ROWS = TESTSET / os.getenv("TESTSET_ROWS", "eval_rows.json")
OUTPUTS = TESTSET / "outputs"
SCORED = TESTSET / os.getenv("TESTSET_SCORED_DIR", "scored")
MODEL_ID = "Qwen/Qwen3.5-35B-A3B"
MODEL_REVISION = "59d61f3ce65a6d9863b86d2e96597125219dc754"
RETRIEVER_INDEX = ROOT / "qwen3_5_35b_dapo_content_final_v3_20261005" / "tool_retriever_index"
SAMPLING = {"temperature": 1.0, "top_p": 0.95, "top_k": 0, "min_p": None, "repetition_penalty": 1.0}
MAX_NEW_TOKENS = 1024


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _append_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


class _CapturingTokenizer:
    """Records the chat messages and tool schema behind each templated prompt."""

    def __init__(self, tokenizer):
        self._tokenizer = tokenizer
        self.calls = []

    def apply_chat_template(self, messages, tools=None, **kwargs):
        self.calls.append({"messages": messages, "tools": tools})
        return self._tokenizer.apply_chat_template(messages, tools=tools, **kwargs)

    def __getattr__(self, name):
        return getattr(self._tokenizer, name)


def prepare(args) -> None:
    from transformers import AutoTokenizer

    from backend.infrastructure.rag.gemini_provider import LocalEmbeddingToolRetrieveProvider
    from rl.slidegen_adapter import TOOLS_DICT
    from rl.train_data import prepare_document
    from scripts.generate_challenge_dataset import load_offline_documents

    tokenizer = _CapturingTokenizer(AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION))
    retriever = LocalEmbeddingToolRetrieveProvider(TOOLS_DICT, str(RETRIEVER_INDEX))
    documents = load_offline_documents(str(args.corpus))
    rows = []
    for document in documents:
        start = len(tokenizer.calls)
        samples = prepare_document(document, tokenizer, retriever, strict_tool_retrieval=True)
        for sample, call in zip(samples, tokenizer.calls[start:], strict=True):
            sample["messages"] = call["messages"]
            sample["tools"] = call["tools"]
            sample["key"] = f"{sample['source_doc_id']}_{sample['slide_index']:02d}"
            rows.append(sample)
    extracted = json.loads((TESTSET / "wiki_testset_rows.json").read_text(encoding="utf-8"))
    sources = {(str(row["doc_id"]), int(row["slide_index"])): row.get("source") for row in extracted}
    for row in rows:
        row["source_meta"] = sources.get((row["source_doc_id"], row["slide_index"]))
    ROWS.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(rows)} prompts from {len(documents)} decks -> {ROWS}")


def _generate_qwen(model, tokenizer, prompts: list[str], seed: int) -> list[tuple[str, int]]:
    import torch
    from transformers import GenerationConfig

    torch.manual_seed(seed)
    encoded = tokenizer(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
    config = GenerationConfig(
        max_new_tokens=MAX_NEW_TOKENS, do_sample=True, pad_token_id=tokenizer.pad_token_id,
        bos_token_id=tokenizer.bos_token_id, eos_token_id=tokenizer.eos_token_id,
        use_cache=True, disable_compile=True, **SAMPLING,
    )
    with torch.no_grad():
        output = model.generate(**encoded, generation_config=config)
    completion_ids = output[:, encoded["input_ids"].shape[1]:]
    texts = tokenizer.batch_decode(completion_ids, skip_special_tokens=True)
    lengths = [int((ids != tokenizer.pad_token_id).sum()) for ids in completion_ids]
    return list(zip(texts, lengths))


def qwen(args) -> None:
    # Load exactly as training does: NF4 base, BF16 experts, LoRA copied by name.
    os.environ.update({
        "TRAINING_MODEL_ID": MODEL_ID, "GRPO_LOAD_IN_4BIT": "true", "USE_GRAD_CHECKPOINT": "false",
        "GRPO_INIT_ADAPTER": str(args.adapter), "GRPO_FLA_ROLLOUT_ONLY": "false",
    })
    from rl import train

    rows = json.loads(ROWS.read_text(encoding="utf-8"))
    model, tokenizer, _, _ = train._load_model(revision=MODEL_REVISION)
    tokenizer.padding_side = "left"
    model.eval()
    plans = [("dapo", args.rl_samples, False), ("base", args.base_samples, True)]
    for system, samples, disable_adapter in plans:
        path = OUTPUTS / f"{system}.jsonl"
        done = {(record["key"], record["sample"]) for record in _read_jsonl(path)}
        jobs = [(row, k) for k in range(samples) for row in rows if (row["key"], k) not in done]
        print(f"{system}: {len(jobs)} completions to generate ({len(done)} on disk)")
        batch = args.batch_size
        index = 0
        while index < len(jobs):
            chunk = jobs[index:index + batch]
            started = time.perf_counter()
            try:
                if disable_adapter:
                    with model.disable_adapter():
                        results = _generate_qwen(model, tokenizer, [row["prompt"] for row, _ in chunk], seed=index)
                else:
                    results = _generate_qwen(model, tokenizer, [row["prompt"] for row, _ in chunk], seed=index)
            except Exception as error:  # noqa: BLE001
                import torch

                if "out of memory" not in str(error).lower() or batch == 1:
                    raise
                torch.cuda.empty_cache()
                batch = max(1, batch // 2)
                print(f"OOM, batch -> {batch}")
                continue
            seconds = (time.perf_counter() - started) / len(chunk)
            _append_jsonl(path, [
                {"system": system, "key": row["key"], "sample": k, "completion": text,
                 "completion_tokens": length, "seconds": round(seconds, 2)}
                for (row, k), (text, length) in zip(chunk, results, strict=True)
            ])
            index += len(chunk)
            print(f"{system}: {index}/{len(jobs)} ({seconds:.2f}s/completion, batch {batch})", flush=True)


def _gemini_schema(schema):
    """Gemini's OpenAPI subset: inline $defs, collapse nullable anyOf, drop keys it rejects."""
    defs = schema.get("$defs", {})
    allowed = {"type", "description", "enum", "items", "properties", "required", "nullable",
               "minItems", "maxItems", "minimum", "maximum", "format"}

    def convert(node):
        if "$ref" in node:
            node = {**defs[node["$ref"].split("/")[-1]], **{k: v for k, v in node.items() if k != "$ref"}}
        if "anyOf" in node:
            options = [option for option in node["anyOf"] if option.get("type") != "null"]
            node = {**options[0], **{k: v for k, v in node.items() if k != "anyOf"},
                    **({"nullable": True} if len(options) < len(node["anyOf"]) else {})}
            return convert(node)
        result = {key: value for key, value in node.items() if key in allowed}
        if "items" in result:
            result["items"] = convert(result["items"])
        if "properties" in result:
            result["properties"] = {name: convert(value) for name, value in result["properties"].items()}
        return result

    return convert(schema)


def _gemini_call(row: dict, model: str, api_key: str, schema_mode: str = "json") -> tuple[str, dict]:
    import requests

    function = row["tools"][0]["function"]
    system = next(message["content"] for message in row["messages"] if message["role"] == "system")
    user = next(message["content"] for message in row["messages"] if message["role"] == "user")
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "tools": [{"functionDeclarations": [{
            "name": function["name"], "description": function.get("description", ""),
            # Full JSON Schema when the API accepts it; the OpenAPI subset otherwise.
            **({"parametersJsonSchema": function["parameters"]} if schema_mode == "json"
               else {"parameters": _gemini_schema(function["parameters"])}),
        }]}],
        "toolConfig": {"functionCallingConfig": {"mode": "ANY", "allowedFunctionNames": [function["name"]]}},
        "generationConfig": {"temperature": 1.0, "topP": 0.95, "maxOutputTokens": 8192},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent"
    for attempt in range(6):
        # The key travels in a header so it can never end up in an error message or a log line.
        response = requests.post(url, headers={"x-goog-api-key": api_key}, json=body, timeout=180)
        if response.status_code == 400 and schema_mode == "json" and "chema" in response.text:
            return _gemini_call(row, model, api_key, schema_mode="openapi")
        if response.status_code in {429, 500, 502, 503, 504}:
            time.sleep(min(60, 5 * 2 ** attempt))
            continue
        if not response.ok:
            raise RuntimeError(f"Gemini HTTP {response.status_code}: {response.text[:200]}")
        data = response.json()
        parts = (data.get("candidates") or [{}])[0].get("content", {}).get("parts", [])
        call = next((part["functionCall"] for part in parts if "functionCall" in part), None)
        if call is None:
            text = "".join(part.get("text", "") for part in parts)
            return text, data.get("usageMetadata", {})
        payload = {"name": call["name"], "arguments": call.get("args", {})}
        return f"<tool_call>{json.dumps(payload, ensure_ascii=False)}</tool_call>", data.get("usageMetadata", {})
    raise RuntimeError(f"Gemini kept failing for {row['key']}")


from rl.slidegen_adapter import add_capacity_hints  # noqa: E402


def gemini(args) -> None:
    from concurrent.futures import ThreadPoolExecutor

    rows = json.loads(ROWS.read_text(encoding="utf-8"))
    if args.capacity_hints:
        capacity = json.loads((ROOT / "rl/data/tool_text_capacity.json").read_text(encoding="utf-8"))
        for row in rows:
            row["tools"] = [add_capacity_hints(tool, capacity) for tool in row["tools"]]
    api_key = os.environ["GEMINI_API_KEY"].strip()
    path = OUTPUTS / args.output
    done = {(record["key"], record["sample"]) for record in _read_jsonl(path)}
    jobs = [(row, k) for k in range(args.samples) for row in rows if (row["key"], k) not in done]
    print(f"gemini: {len(jobs)} completions to generate ({len(done)} on disk)")

    def run(job):
        row, k = job
        started = time.perf_counter()
        try:
            text, usage = _gemini_call(row, args.model, api_key)
        except Exception as error:  # noqa: BLE001
            text, usage = "", {"error": str(error)[:300]}
        return {"system": Path(args.output).stem, "model": args.model, "key": row["key"], "sample": k, "completion": text,
                "usage": usage, "seconds": round(time.perf_counter() - started, 2)}

    with ThreadPoolExecutor(args.workers) as pool:
        for count, record in enumerate(pool.map(run, jobs), 1):
            _append_jsonl(path, [record])
            if count % 20 == 0 or count == len(jobs):
                print(f"gemini: {count}/{len(jobs)}", flush=True)


def _with_retries(function, attempts: int = 5, **kwargs):
    """The renderer is shared with training; a screenshot timeout should not end a long scoring run."""
    for attempt in range(attempts):
        try:
            return function(**kwargs)
        except Exception as error:  # noqa: BLE001
            if attempt == attempts - 1:
                raise
            print(f"scoring batch failed ({type(error).__name__}); retry {attempt + 1}", flush=True)
            time.sleep(20)


def llm(args) -> None:
    """Sample completions from the project's OpenAI-compatible LLM server (backend.config.LLM_BASE_URL)."""
    from concurrent.futures import ThreadPoolExecutor

    import requests

    from backend import config

    rows = json.loads(ROWS.read_text(encoding="utf-8"))
    if args.capacity_hints:
        capacity = json.loads((ROOT / "rl/data/tool_text_capacity.json").read_text(encoding="utf-8"))
        for row in rows:
            row["tools"] = [add_capacity_hints(tool, capacity) for tool in row["tools"]]
    if args.extra_system:
        for row in rows:
            row["messages"] = [
                {**message, "content": message["content"].rstrip() + "\n" + args.extra_system + "\n"}
                if message["role"] == "system" else message for message in row["messages"]
            ]
    if args.extra_user:
        for row in rows:
            row["messages"] = [
                {**message, "content": message["content"].rstrip() + "\n" + args.extra_user + "\n"}
                if message["role"] == "user" else message for message in row["messages"]
            ]
    path = OUTPUTS / args.output
    done = {(record["key"], record["sample"]) for record in _read_jsonl(path)}
    jobs = [(row, k) for k in range(args.samples) for row in rows if (row["key"], k) not in done]
    headers = {"Authorization": f"Bearer {os.environ.get('LLM_API_KEY', '').strip()}"}
    print(f"{path.stem}: {len(jobs)} completions to generate ({len(done)} on disk)")

    def run(job):
        row, k = job
        body = {"model": config.LLM_MODEL, "messages": row["messages"], "tools": row["tools"], "tool_choice": "required",
                "temperature": SAMPLING["temperature"], "top_p": SAMPLING["top_p"], "max_tokens": MAX_NEW_TOKENS}
        text = ""
        for attempt in range(4):
            try:
                response = requests.post(f"{config.LLM_BASE_URL}/chat/completions", headers=headers, json=body, timeout=240)
                if response.ok:
                    calls = response.json()["choices"][0]["message"].get("tool_calls") or []
                    if calls:
                        payload = {"name": calls[0]["function"]["name"], "arguments": json.loads(calls[0]["function"]["arguments"])}
                        text = f"<tool_call>{json.dumps(payload, ensure_ascii=False)}</tool_call>"
                    break
            except Exception:  # noqa: BLE001
                pass
            time.sleep(5 * (attempt + 1))
        return {"system": path.stem, "key": row["key"], "sample": k, "completion": text}

    with ThreadPoolExecutor(args.workers) as pool:
        for count, record in enumerate(pool.map(run, jobs), 1):
            _append_jsonl(path, [record])
            if count % 40 == 0 or count == len(jobs):
                print(f"{path.stem}: {count}/{len(jobs)}", flush=True)


def score(args) -> None:
    from rl.rewards import composite_reward
    from rl.rewards.content_reward import set_text_embedder
    from backend.infrastructure.rag.gemini_provider import LocalEmbeddingToolRetrieveProvider
    from rl.slidegen_adapter import TOOLS_DICT

    rows = {row["key"]: row for row in json.loads(ROWS.read_text(encoding="utf-8"))}
    retriever = LocalEmbeddingToolRetrieveProvider(TOOLS_DICT, str(RETRIEVER_INDEX))
    set_text_embedder(retriever.embeddings.model)
    composite_reward.preflight_reward_runtime()
    for path in sorted(OUTPUTS.glob("*.jsonl")):
        system = path.stem
        if args.systems and system not in args.systems.split(","):
            continue
        target = SCORED / f"{system}.jsonl"
        done = {(record["key"], record["sample"]) for record in _read_jsonl(target)}
        records = [record for record in _read_jsonl(path) if (record["key"], record["sample"]) not in done]
        if args.only_annotated:
            shown = {(("base" if side["system"] == "best8" else side["system"]), side["key"], side["sample"])
                     for pair in json.loads((ROOT / "slidegen_data/annotation/secret_mapping.json").read_text())["pairs"].values()
                     for side in (pair["a"], pair["b"])}
            records = [record for record in records if (system, record["key"], record["sample"]) in shown]
        dump = SCORED / "png" / system
        for start in range(0, len(records), args.batch_size):
            chunk = records[start:start + args.batch_size]
            # One unique dump key per completion: "<doc>_<slide>-s<sample>" with slide index 0.
            keys = [f"{record['key']}-s{record['sample']}" for record in chunk]
            composite_reward.configure_sample_dump(dump, [(key, 0) for key in keys])
            meta = [rows[record["key"]] for record in chunk]
            rewards = _with_retries(
                composite_reward.slidegen_composite_reward,
                prompts=[row["prompt"] for row in meta],
                completions=[record["completion"] for record in chunk],
                assigned_tool_name=[row["assigned_tool_name"] for row in meta],
                source_content=[row["source_content"] for row in meta],
                deck_style=[row["deck_style"] for row in meta],
                approved_images=[row["approved_images"] for row in meta],
                image_mode=[row["image_mode"] for row in meta],
                numeric_facts=[row["numeric_facts"] for row in meta],
                source_doc_id=keys, slide_index=[0] * len(chunk),
            )
            scored = []
            for record, key, reward in zip(chunk, keys, rewards, strict=True):
                detail = json.loads((dump / "step_0000" / f"{key}_slide00.json").read_text(encoding="utf-8"))
                png = dump / "step_0000" / f"{key}_slide00.png"
                scored.append({
                    "system": system, "key": record["key"], "sample": record["sample"], "reward": reward,
                    "valid": detail["valid"], "components": detail.get("components"),
                    "dom_issues": detail.get("dom_issues"), "visible_text": detail.get("visible_text"),
                    "min_contrast": detail.get("min_contrast"), "min_font_px": detail.get("min_font_px"),
                    "png": str(png.relative_to(ROOT)) if png.exists() and not args.discard_png else None,
                })
                if args.discard_png:
                    png.unlink(missing_ok=True)
            _append_jsonl(target, scored)
            print(f"score {system}: {start + len(chunk)}/{len(records)}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare")
    p.add_argument("--corpus", type=Path, default=TESTSET / "wiki_testset_planned.json")
    p = commands.add_parser("qwen")
    p.add_argument("--adapter", type=Path, required=True)
    p.add_argument("--rl-samples", type=int, default=4)
    p.add_argument("--base-samples", type=int, default=8)
    p.add_argument("--batch-size", type=int, default=32)
    p = commands.add_parser("gemini")
    p.add_argument("--model", default="models/gemini-3.5-flash")
    p.add_argument("--samples", type=int, default=1)
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--capacity-hints", action="store_true", help="add measured per-field text capacity to the schema")
    p.add_argument("--output", default="gemini.jsonl")
    p = commands.add_parser("llm")
    p.add_argument("--samples", type=int, default=1)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--capacity-hints", action="store_true")
    p.add_argument("--output", required=True)
    p.add_argument("--extra-user", default="", help="extra line appended to the user prompt (prompt experiments)")
    p.add_argument("--extra-system", default="", help="extra rule appended to the system prompt (prompt experiments)")
    p = commands.add_parser("score")
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--discard-png", action="store_true", help="keep scores only (re-scoring with a new reward)")
    p.add_argument("--only-annotated", action="store_true", help="score only slides shown to human annotators")
    p.add_argument("--systems", default="", help="comma-separated subset of outputs/*.jsonl stems")
    args = parser.parse_args()
    {"prepare": prepare, "qwen": qwen, "gemini": gemini, "llm": llm, "score": score}[args.command](args)


if __name__ == "__main__":
    main()
