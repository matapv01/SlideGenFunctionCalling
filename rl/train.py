import os, sys, json, random, threading, concurrent.futures, glob
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rl.run_artifacts import (
    append_jsonl,
    get_runtime_metadata,
    save_contact_sheet,
    save_metric_trend_image,
    save_text_summary_image,
    start_run_logging,
    write_json,
)
from dotenv import load_dotenv
load_dotenv()

os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "300")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "300")

from rl.common import auto_select_gpu, build_flat_tools, setup_tokenizer
from rl.common import LORA_R, LORA_ALPHA, LORA_DROPOUT, LORA_TARGET_MODULES
auto_select_gpu()
os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"

import torch

from unsloth import FastLanguageModel
from trl import GRPOTrainer, GRPOConfig
from datasets import Dataset
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from rl.rewards import slide_aesthetics_reward, content_preservation_reward, visual_consistency_reward
from rl.rewards.conciseness_reward import conciseness_reward
from rl.rewards.text_embedding_reward import text_embedding_reward
from scripts.generate_challenge_dataset import generate_docs
from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT, execute_tool
from backend.workflows.slidegen_workflow.utils.helper import (
    format_tool_for_qwen,
    QWEN_CHAT_TEMPLATE,
    render_html_to_png,
    sanitize_to_placeholders,
    get_slide_style_context,
)
from backend.workflows.slidegen_workflow.utils.prompts import (
    QWEN_GENERATOR_SYSTEM_PROMPT,
    QWEN_GENERATOR_HUMAN_TEMPLATE,
    SLIDE_PLANNER_SYSTEM_PROMPT,
    SLIDE_PLANNER_HUMAN_PROMPT,
    SLIDE_PREPARER_SYSTEM_PROMPT,
    SLIDE_PREPARER_HUMAN_TEMPLATE,
)
from backend.workflows.slidegen_workflow.graph.stage import SlidePlan
from backend.infrastructure.embedding.dinov2_provider import DINOv2EmbeddingProvider
from backend.infrastructure.rag.gemini_provider import GeminiToolRetrieveProvider
from backend.config import TOOL_RETRIEVER_TOP_K

# ==============================================================================
# CONFIG
# ==============================================================================
model_id = os.getenv("TRAINING_MODEL_ID", "Qwen/Qwen3-4B-Instruct-2507")
total_steps = int(os.getenv("TOTAL_STEPS", "500"))
batch_docs = int(os.getenv("BATCH_DOCS", "5"))
USE_CPU = os.getenv("USE_CPU", "False").lower() == "true"
USE_LORA = os.getenv("USE_LORA", "True").lower() == "true"
USE_GRAD_CHECKPOINT = os.getenv("USE_GRAD_CHECKPOINT", "True").lower() == "true"
learning_rate = float(os.getenv("LEARNING_RATE", "1e-6"))
per_device_train_batch_size = int(os.getenv("PER_DEVICE_TRAIN_BATCH_SIZE", "1"))
gradient_accumulation_steps = int(os.getenv("GRADIENT_ACCUMULATION_STEPS", "16"))
num_generations = int(os.getenv("NUM_GENERATIONS", "2"))
max_completion_length = int(os.getenv("MAX_COMPLETION_LENGTH", "2048"))
output_dir = os.getenv("GRPO_OUTPUT_DIR", "./qwen_slidegen_grpo")
run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
run_log_dir = os.path.join(os.path.dirname(__file__), "log", "grpo", f"run_{run_id}")
os.makedirs(run_log_dir, exist_ok=True)
run_log_path = start_run_logging(run_log_dir)

api_key = os.getenv("GEMINI_API_KEY")
base_url = os.getenv("GEMINI_API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
gemini_model = os.getenv("GEMINI_GENERATION_MODEL", "gemini-2.5-pro")

flat_tools = build_flat_tools(TOOLS_DICT)
device = "cuda" if torch.cuda.is_available() and not USE_CPU else "cpu"
_gen_lock = threading.Lock()

# ==============================================================================
# 1. LOAD MODEL
# ==============================================================================
max_seq_length = 8192
sdft_adapter_path = os.getenv("SDFT_ADAPTER_PATH", "./qwen_slidegen_sdft/final_adapter")

if USE_LORA and os.path.exists(sdft_adapter_path):
    print(f"Loading SDFT adapter from {sdft_adapter_path}")
    model, tokenizer = FastLanguageModel.from_pretrained(
        sdft_adapter_path, max_seq_length=max_seq_length, dtype=torch.bfloat16, load_in_4bit=False)
    sdft_loaded = True
else:
    print(f"Loading model: {model_id}")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_id, max_seq_length=max_seq_length, dtype=torch.bfloat16, load_in_4bit=False)
    if USE_LORA:
        model = FastLanguageModel.get_peft_model(
            model, r=LORA_R, target_modules=LORA_TARGET_MODULES,
            lora_alpha=LORA_ALPHA, lora_dropout=LORA_DROPOUT,
            bias="none", use_gradient_checkpointing="unsloth", random_state=42)
    sdft_loaded = False

setup_tokenizer(tokenizer, QWEN_CHAT_TEMPLATE)
peft_config_for_trainer = None

# ==============================================================================
# 2. GEMINI CLIENTS (Planner + Preparer)
# ==============================================================================
planner_llm = ChatOpenAI(api_key=api_key, base_url=base_url, model=gemini_model, temperature=0.3)
preparer_llm = ChatOpenAI(api_key=api_key, base_url=base_url, model=gemini_model, temperature=0.3)

planner_chain = ChatPromptTemplate.from_messages([
    ("system", SLIDE_PLANNER_SYSTEM_PROMPT),
    ("human", SLIDE_PLANNER_HUMAN_PROMPT),
]) | planner_llm.with_structured_output(SlidePlan)

# ==============================================================================
# 3. EMBEDDING PROVIDER
# ==============================================================================
embedding_provider = DINOv2EmbeddingProvider(device=device)

# ==============================================================================
# 3b. TOOL RETRIEVER (RAG — reuse BE's GeminiToolRetrieveProvider)
# ==============================================================================
faiss_index_path = os.path.join(os.path.dirname(__file__), "faiss_index")
try:
    tool_retriever = GeminiToolRetrieveProvider(TOOLS_DICT, faiss_index_path, api_key=api_key)
    print(f"  Tool retriever initialized at {faiss_index_path}")
except Exception as e:
    print(f"  [WARN] Tool retriever init failed: {e}. GRPO will fall back to random tool selection.")
    tool_retriever = None

# ==============================================================================
# 4. SEQUENTIAL ROLLOUT (per doc)
# ==============================================================================
def log_node(step_num, doc_idx, si, node, msg):
    print(f"  [Step {step_num} Doc {doc_idx} Slide {si}] {node} → {msg}")


def run_planner_one(slide_id: int, slide: dict, step_num: int, doc_idx: int, cache: dict) -> dict:
    ck = f"{doc_idx}_{slide_id}"
    if ck in cache.get("plans", {}):
        log_node(step_num, doc_idx, slide_id, "Planner", f"cached → {cache['plans'][ck]['action']}")
        return cache["plans"][ck]

    inp = {
        "slide_number": slide_id + 1,
        "slide_context_map": "[Slide 1] Content Slide",
        "slide_content": json.dumps({"heading": slide.get("heading", "Slide"), "content": slide["user_prompt"][:500]}, ensure_ascii=False),
    }
    try:
        plan = planner_chain.invoke(inp).model_dump()
        if slide_id == 0:
            plan["action"] = "INTRO_TOOLS"
        log_node(step_num, doc_idx, slide_id, "Planner", plan["action"])
    except Exception as e:
        log_node(step_num, doc_idx, slide_id, "Planner", f"FAILED ({e})")
        plan = {"action": "CONTENT_TOOLS", "thought": slide["user_prompt"][:100]}

    cache.setdefault("plans", {})[ck] = plan
    return plan


def run_preparer_one(slide: dict, plan: dict, prev_style_context: str, step_num: int, doc_idx: int, si: int) -> str:
    try:
        msg = SLIDE_PREPARER_HUMAN_TEMPLATE.format(
            previous_style_context=prev_style_context,
            slide_plan=json.dumps(plan, indent=2),
            slide_content=slide["user_prompt"],
        )
        resp = preparer_llm.invoke([{"role": "system", "content": SLIDE_PREPARER_SYSTEM_PROMPT},
                                     {"role": "user", "content": msg}])
        design = resp.content.strip() if hasattr(resp, "content") and resp.content else plan.get("thought", "")
        log_node(step_num, doc_idx, si, "Preparer", f"OK ({len(design)} chars)")
    except Exception as e:
        log_node(step_num, doc_idx, si, "Preparer", f"FAILED ({e})")
        design = plan.get("thought", "")
    return design


def _extract_last_json(text: str) -> dict | None:
    if not text:
        return None
    cleaned = text.strip()
    if "<tool_call>" in cleaned:
        for part in reversed(cleaned.split("<tool_call>")):
            if "</tool_call>" in part:
                return _extract_last_json(part.split("</tool_call>")[0].strip())
    for delim in ["```json", "```"]:
        if delim in cleaned:
            cleaned = cleaned.split(delim)[1].split("```")[0].strip()
            break
    try:
        obj = json.loads(cleaned)
        if isinstance(obj, dict) and "name" in obj:
            return obj
        if isinstance(obj, list) and obj and isinstance(obj[0], dict) and "name" in obj[0]:
            return obj[0]
    except Exception:
        pass
    pos = cleaned.rfind("}")
    while pos >= 0:
        depth = 0
        for i in range(pos, -1, -1):
            if cleaned[i] == "}":
                depth += 1
            elif cleaned[i] == "{":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(cleaned[i:pos+1])
                        if isinstance(obj, dict) and "name" in obj:
                            return obj
                    except Exception:
                        pass
                    pos = i - 1
                    break
        else:
            break
    return None


def process_doc(doc_slides: list, step_num: int, doc_idx: int, cache: dict) -> list:
    prompts_data = []
    prev_embedding = [0.0] * 768
    prev_tool_call = None
    rendered_paths = []
    render_dir = os.path.join(data_dir, f"step_{step_num:04d}", "renders", f"doc_{doc_idx}")
    os.makedirs(render_dir, exist_ok=True)

    for si, slide in enumerate(doc_slides):
        plan = run_planner_one(si, slide, step_num, doc_idx, cache)
        action = plan["action"]
        style_context = get_slide_style_context(prev_tool_call) if prev_tool_call else ""
        design = run_preparer_one(slide, plan, style_context, step_num, doc_idx, si)

        filtered_tools = []
        if tool_retriever is not None:
            retrieved = tool_retriever.get_relevant_tools(
                category=action, query=plan.get("thought", ""),
                top_k=TOOL_RETRIEVER_TOP_K, current_slide_index=si)
            filtered_tools = [format_tool_for_qwen(t) for t in retrieved] if retrieved else []
        if not filtered_tools:
            filtered_tools = [format_tool_for_qwen(t) for t in TOOLS_DICT.get(action, []) if t.name in flat_tools]
        if len(filtered_tools) > 6:
            random.shuffle(filtered_tools)
            filtered_tools = filtered_tools[:6]

        user_prompt = QWEN_GENERATOR_HUMAN_TEMPLATE.format(
            style_context=style_context,
            design_instruction=design[:600] if design else "",
            slide_content=slide["user_prompt"][:1200],
        )
        messages = [
            {"role": "system", "content": QWEN_GENERATOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        prompt = tokenizer.apply_chat_template(messages, tools=filtered_tools, tokenize=False, add_generation_prompt=True)

        if step_num == 1 and doc_idx == 0 and si == 0:
            print(f"  [DEBUG] === PROMPT PREVIEW (last 500 chars) ===")
            print(f"  [DEBUG] {prompt[-500:]}")
            print(f"  [DEBUG] =========================================")

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=8192).to(model.device)
        completion = ""
        tool_call = None

        for attempt in range(3):
            with _gen_lock:
                with torch.no_grad():
                    out = model.generate(**inputs, max_new_tokens=max_completion_length,
                                         temperature=0.0, do_sample=False,
                                         pad_token_id=tokenizer.eos_token_id)
            completion = tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

            reason = None
            try:
                tool_call = _extract_last_json(completion)
            except Exception:
                tool_call = None
                reason = "NOT_JSON"

            if tool_call and "name" in tool_call:
                real_html = execute_tool(tool_call)
                if real_html:
                    log_node(step_num, doc_idx, si, "Qwen", f"attempt {attempt+1}/3 OK → {tool_call['name']}")
                    break
                reason = "EXEC_FAIL"

            if reason is None:
                if not tool_call:
                    reason = "NOT_JSON"
                elif "name" not in tool_call:
                    reason = "NO_NAME"
                else:
                    reason = "EXEC_FAIL"

            if reason == "NOT_JSON":
                log_node(step_num, doc_idx, si, "Qwen", f"attempt {attempt+1}/3 NOT_JSON — full output:")
                print(f"    === FULL OUTPUT (attempt {attempt+1}) ===")
                print(f"    {completion.strip()}")
                print(f"    ====================================")
            else:
                log_node(step_num, doc_idx, si, "Qwen", f"attempt {attempt+1}/3 {reason} — {completion[:120].strip()}")
            prompt += f"\n\n[FAILED: {reason} — {completion[:100]}]"
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=8192).to(model.device)

        if tool_call and "name" in tool_call:
            real_html = execute_tool(tool_call)
            if real_html:
                real_path = os.path.join(render_dir, f"slide_{si:03d}_real.png")
                try:
                    render_html_to_png(real_html, real_path)
                    rendered_paths.append(real_path)
                    log_node(step_num, doc_idx, si, "Render", "OK")
                except Exception as e:
                    log_node(step_num, doc_idx, si, "Render", f"FAILED ({e})")

                sanitized = sanitize_to_placeholders(tool_call)
                sanitized_html = execute_tool(sanitized)
                if sanitized_html:
                    sanitized_path = os.path.join(render_dir, f"slide_{si:03d}_sanitized.png")
                    try:
                        render_html_to_png(sanitized_html, sanitized_path)
                        rendered_paths.append(sanitized_path)
                        prev_embedding = embedding_provider.get_embedding(sanitized_path)
                        log_node(step_num, doc_idx, si, "Embed", "OK")
                    except Exception as e:
                        log_node(step_num, doc_idx, si, "Embed", f"FAILED ({e})")
            prev_tool_call = tool_call

        prompts_data.append({
            "prompt": prompt,
            "previous_slide_embedding": prev_embedding,
        })

    overview_path = os.path.join(render_dir, "overview.png")
    save_contact_sheet(
        rendered_paths,
        overview_path,
        title=f"GRPO Step {step_num:04d} / Doc {doc_idx} Render Overview",
        subtitle=f"{len(doc_slides)} slides, {len(rendered_paths)} rendered images",
        columns=4,
        thumb_size=(420, 236),
    )
    write_json(
        os.path.join(render_dir, "summary.json"),
        {
            "step": step_num,
            "doc_idx": doc_idx,
            "slide_count": len(doc_slides),
            "prompt_count": len(prompts_data),
            "rendered_images": rendered_paths,
            "overview_path": overview_path,
        },
    )
    log_node(step_num, doc_idx, "-", "Done", f"{len(doc_slides)} slides, {len(rendered_paths)} renders")
    return prompts_data


# ==============================================================================
# 5. TRAINING LOOP
# ==============================================================================
training_args = GRPOConfig(
    output_dir=output_dir,
    learning_rate=learning_rate,
    per_device_train_batch_size=per_device_train_batch_size,
    gradient_accumulation_steps=gradient_accumulation_steps,
    max_steps=1,
    save_steps=0,
    logging_steps=1,
    report_to="none",
    num_generations=num_generations,
    max_completion_length=max_completion_length,
    use_cpu=USE_CPU,
    bf16=torch.cuda.is_bf16_supported() if not USE_CPU else False,
    fp16=not torch.cuda.is_bf16_supported() if not USE_CPU else False,
    gradient_checkpointing=USE_GRAD_CHECKPOINT if not USE_CPU else False,
)

run_manifest = get_runtime_metadata(
    {
        "run_name": "grpo",
        "run_id": run_id,
        "log_dir": run_log_dir,
        "run_log": str(run_log_path),
        "output_dir": output_dir,
        "model_id": model_id,
        "sdft_adapter_path": sdft_adapter_path if os.path.exists(sdft_adapter_path) else None,
        "total_steps": total_steps,
        "batch_docs": batch_docs,
        "learning_rate": learning_rate,
        "per_device_train_batch_size": per_device_train_batch_size,
        "gradient_accumulation_steps": gradient_accumulation_steps,
        "num_generations": num_generations,
        "max_completion_length": max_completion_length,
        "use_cpu": USE_CPU,
        "use_lora": USE_LORA,
        "use_grad_checkpoint": USE_GRAD_CHECKPOINT,
        "device": device,
        "sdft_loaded": sdft_loaded,
        "tool_retriever": tool_retriever is not None,
        "embedding_provider": type(embedding_provider).__name__,
    }
)
write_json(os.path.join(run_log_dir, "manifest.json"), run_manifest)
step_summaries = []

print(f"\n{'='*60}")
print(f"Starting Sequential GRPO Training")
print(f"  Model: {model_id}, Steps: {total_steps}, Docs/step: {batch_docs}")
print(f"  Generations (GRPO): {num_generations}")
print(f"{'='*60}\n")

data_dir = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(data_dir, exist_ok=True)

for step in range(1, total_steps + 1):
    print(f"\n--- Step {step}/{total_steps} ---")

    step_ckpt = os.path.join(data_dir, f"step_{step:04d}_adapter")
    if os.path.exists(os.path.join(step_ckpt, "adapter_model.safetensors")):
        print(f"  Step {step} skipped (checkpoint found at {step_ckpt})")
        continue

    doc_path = os.path.join(data_dir, f"step_{step:04d}_docs.json")
    cache_path = os.path.join(data_dir, f"step_{step:04d}_cache.json")

    if os.path.exists(doc_path):
        with open(doc_path, "r", encoding="utf-8") as f:
            all_slides_flat = json.load(f)
        docs = []
        by_doc = {}
        for s in all_slides_flat:
            by_doc.setdefault(s["doc_id"], []).append(s)
        for did in sorted(by_doc):
            docs.append(by_doc[did])
        print(f"  Loaded {len(all_slides_flat)} slides from {doc_path}")
    else:
        docs = generate_docs(num_docs=batch_docs)
        all_slides_flat = [s for doc in docs for s in doc]
        with open(doc_path, "w", encoding="utf-8") as f:
            json.dump(all_slides_flat, f, indent=2, ensure_ascii=False)
        print(f"  Saved {len(all_slides_flat)} slides to {doc_path}")

    cache = {"plans": {}}
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            cache = json.load(f)
        print(f"  Loaded {len(cache.get('plans', {}))} cached plans from {cache_path}")

    all_prompts = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=batch_docs) as ex:
        futures = [ex.submit(process_doc, doc, step, i, cache) for i, doc in enumerate(docs)]
        for f in concurrent.futures.as_completed(futures):
            all_prompts.extend(f.result())

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump({"plans": cache.get("plans", {})}, f, indent=2, ensure_ascii=False)
    print(f"  Saved {len(cache.get('plans', {}))} plans to {cache_path}")

    if not all_prompts:
        print("  No valid prompts generated, skipping step.")
        continue

    print(f"  Collected {len(all_prompts)} prompts. Running GRPO update...")

    dataset = Dataset.from_list(all_prompts)
    trainer = GRPOTrainer(
        model=model,
        processing_class=tokenizer,
        reward_funcs=[slide_aesthetics_reward, content_preservation_reward,
                       visual_consistency_reward, conciseness_reward, text_embedding_reward],
        args=training_args,
        train_dataset=dataset,
        peft_config=peft_config_for_trainer,
    )
    trainer.train()

    history = list(trainer.state.log_history or [])
    metric_rows = [row for row in history if any(isinstance(v, (int, float)) and not isinstance(v, bool) for v in row.values())]
    last = metric_rows[-1] if metric_rows else {}
    if last:
        loss = last.get("loss", "?")
        mean_reward = last.get("reward", "?")
        print(f"  GRPO: loss={loss}, mean_reward={mean_reward}")

    doc_overviews = sorted(
        glob.glob(os.path.join(data_dir, f"step_{step:04d}", "renders", "doc_*", "overview.png"))
    )
    step_overview_path = os.path.join(run_log_dir, f"step_{step:04d}_overview.png")
    save_contact_sheet(
        doc_overviews,
        step_overview_path,
        title=f"GRPO Step {step:04d} Overview",
        subtitle=f"Docs: {len(docs)} | Prompts: {len(all_prompts)} | Render overviews: {len(doc_overviews)}",
        columns=3,
        thumb_size=(420, 236),
    )

    step_summary = {
        "step": step,
        "docs": len(docs),
        "slides": len(all_slides_flat),
        "prompts": len(all_prompts),
        "doc_overviews": len(doc_overviews),
        "overview_path": step_overview_path,
        "dataset_path": os.path.join(data_dir, f"step_{step:04d}_dataset.json"),
        "checkpoint_path": os.path.join(data_dir, f"step_{step:04d}_adapter"),
    }
    for key, value in last.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            step_summary[key] = value
    step_summaries.append(step_summary)
    append_jsonl(os.path.join(run_log_dir, "metrics.jsonl"), [step_summary])
    write_json(os.path.join(run_log_dir, "step_summaries.json"), step_summaries)
    write_json(os.path.join(run_log_dir, f"step_{step:04d}_summary.json"), step_summary)
    save_metric_trend_image(
        step_summaries,
        os.path.join(run_log_dir, "metrics_trend.png"),
        title="GRPO Step Metrics",
        preferred_keys=["loss", "reward", "learning_rate", "grad_norm", "kl", "entropy"],
    )
    summary_lines = [
        f"Step: {step}",
        f"Docs: {len(docs)}",
        f"Slides: {len(all_slides_flat)}",
        f"Prompts: {len(all_prompts)}",
        f"Render overviews: {len(doc_overviews)}",
        f"Checkpoint: {step_summary['checkpoint_path']}",
        f"Overview: {step_overview_path}",
    ]
    if last:
        summary_lines.append(f"Last metrics: {json.dumps(last, ensure_ascii=False, default=str)}")
    save_text_summary_image(
        os.path.join(run_log_dir, f"step_{step:04d}_summary.png"),
        f"GRPO Step {step:04d} Summary",
        [
            {
                "title": "Step",
                "body": "\n".join(summary_lines),
            }
        ],
        subtitle=f"Run {run_id}",
        footer=f"Log: {run_log_path.name}",
    )

    step_ckpt = os.path.join(data_dir, f"step_{step:04d}_adapter")
    model.save_pretrained(step_ckpt)
    tokenizer.save_pretrained(step_ckpt)
    print(f"  Saved checkpoint to {step_ckpt}")

    ds_path = os.path.join(data_dir, f"step_{step:04d}_dataset.json")
    with open(ds_path, "w", encoding="utf-8") as f:
        json.dump({"prompts": [p["prompt"] for p in all_prompts]}, f, indent=2, ensure_ascii=False)
    print(f"  Saved training dataset to {ds_path}")

# Copy final step to well-known location
import shutil
final_adapter = os.path.join(output_dir, "final_adapter")
if os.path.exists(final_adapter):
    shutil.rmtree(final_adapter)
if os.path.exists(step_ckpt):
    shutil.copytree(step_ckpt, final_adapter)
    print(f"Final adapter: {final_adapter} (from step {step})")

selected_overviews = []
if step_summaries:
    raw_candidates = [s.get("overview_path") for s in step_summaries if s.get("overview_path")]
    if len(raw_candidates) <= 6:
        selected_overviews = raw_candidates
    else:
        selected_overviews = raw_candidates[:3] + raw_candidates[-3:]
    selected_overviews = list(dict.fromkeys(selected_overviews))
    save_contact_sheet(
        selected_overviews,
        os.path.join(run_log_dir, "training_overview.png"),
        title="GRPO Training Overview",
        subtitle=f"Selected {len(selected_overviews)} step overviews from {len(step_summaries)} steps",
        columns=3,
        thumb_size=(420, 236),
    )
    final_metrics = {k: v for k, v in step_summaries[-1].items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
else:
    final_metrics = {}

run_manifest["final_adapter"] = final_adapter
run_manifest["final_step"] = step_summaries[-1]["step"] if step_summaries else None
run_manifest["completed_steps"] = len(step_summaries)
run_manifest["final_metrics"] = final_metrics
run_manifest["artifacts"] = {
    "metrics_jsonl": os.path.join(run_log_dir, "metrics.jsonl"),
    "metrics_trend_png": os.path.join(run_log_dir, "metrics_trend.png"),
    "training_overview_png": os.path.join(run_log_dir, "training_overview.png"),
    "run_summary_png": os.path.join(run_log_dir, "run_summary.png"),
    "run_log": str(run_log_path),
}
write_json(os.path.join(run_log_dir, "manifest.json"), run_manifest)
summary_lines = [
    f"Model: {model_id}",
    f"Steps completed: {len(step_summaries)} / {total_steps}",
    f"Final adapter: {final_adapter}",
    f"Output dir: {output_dir}",
]
if final_metrics:
    summary_lines.append(f"Final metrics: {json.dumps(final_metrics, ensure_ascii=False, default=str)}")
save_text_summary_image(
    os.path.join(run_log_dir, "run_summary.png"),
    "GRPO Run Summary",
    [
        {
            "title": "Run",
            "body": "\n".join(summary_lines),
        }
    ],
    subtitle=f"Run {run_id}",
    footer=f"Log: {run_log_path.name}",
)

print(f"\n{'='*60}")
print(f"Training complete! Checkpoints: qwen_slidegen_grpo/")
print(f"{'='*60}")
