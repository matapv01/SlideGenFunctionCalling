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
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
os.environ.setdefault("PYTORCH_ALLOC_CONF", "expandable_segments:True")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, PeftConfig, PeftModel, TaskType, get_peft_model
from trl import GRPOTrainer, GRPOConfig
from datasets import Dataset
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from rl.rewards import slide_aesthetics_reward, content_preservation_reward, visual_consistency_reward
from rl.rewards.conciseness_reward import conciseness_reward
from rl.rewards.text_embedding_reward import text_embedding_reward
from scripts.generate_challenge_dataset import generate_docs
from backend.config import EXECUTOR_MAX_RETRIES
from backend.workflows.slidegen_workflow.tools.ddgs_tool import SEARCH_DDGS_TOOL
from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT, execute_tool, execute_tool_plan
from backend.workflows.slidegen_workflow.executors.tool_plan_executor import ToolPlanError
from backend.workflows.slidegen_workflow.nodes.tool_call_executor import validate_tool_call
from backend.workflows.slidegen_workflow.utils.helper import (
    format_tool_for_qwen,
    parse_tool_call_json,
    parse_tool_calls_json,
    QWEN_CHAT_TEMPLATE,
    render_html_to_png,
    sanitize_to_placeholders,
    get_slide_style_context,
)
from backend.workflows.slidegen_workflow.utils.prompts import (
    QWEN_GENERATOR_SYSTEM_PROMPT,
    QWEN_COT_GENERATOR_SYSTEM_PROMPT,
    QWEN_GENERATOR_HUMAN_TEMPLATE,
    SLIDE_PLANNER_SYSTEM_PROMPT,
    SLIDE_PLANNER_HUMAN_PROMPT,
    SLIDE_PREPARER_SYSTEM_PROMPT,
    SLIDE_PREPARER_HUMAN_TEMPLATE,
    IMAGE_SEARCH_EXECUTION_PLAN_RULES,
    CONTENT_PROMPT,
    TRANSITION_PROMPT,
    SLIDE_TYPE_PROMPTS,
    INTRO_PROMPT,
    MATH_EQUATION_RULES,
)
from backend.workflows.slidegen_workflow.nodes.slide_generator import _build_tool_description_text
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
data_dir = os.path.join(os.path.dirname(__file__), "data")
resume_grpo = os.getenv("GRPO_RESUME", "true").lower() in ("1", "true", "yes", "on")
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
sdft_adapter_path = os.getenv("SDFT_ADAPTER_PATH", "./qwen_slidegen_sft/final_adapter")
model_dtype = torch.bfloat16 if device == "cuda" and torch.cuda.is_bf16_supported() else (torch.float16 if device == "cuda" else torch.float32)


def _build_grpo_lora_config() -> LoraConfig:
    return LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=LORA_TARGET_MODULES,
        bias="none",
    )


def _latest_grpo_adapter():
    """Find the latest completely-written GRPO step adapter."""
    candidates = []
    for path in glob.glob(os.path.join(data_dir, "step_*_adapter")):
        if not os.path.isfile(os.path.join(path, "adapter_model.safetensors")):
            continue
        try:
            step = int(os.path.basename(path).split("_")[1])
        except (IndexError, ValueError):
            continue
        candidates.append((step, path))
    return max(candidates, default=(0, None))


resumed_grpo_step, grpo_adapter_path = _latest_grpo_adapter() if resume_grpo else (0, None)
initial_adapter_path = grpo_adapter_path or sdft_adapter_path

if USE_LORA and os.path.exists(initial_adapter_path):
    adapter_kind = f"GRPO step {resumed_grpo_step}" if grpo_adapter_path else "SDFT"
    print(f"Loading {adapter_kind} adapter from {initial_adapter_path}")
    adapter_config = PeftConfig.from_pretrained(initial_adapter_path)
    base_model_id = adapter_config.base_model_name_or_path or model_id
    print(f"Loading adapter base model: {base_model_id}")
    model = AutoModelForCausalLM.from_pretrained(
        base_model_id,
        torch_dtype=model_dtype,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(base_model_id, trust_remote_code=True)
    model = PeftModel.from_pretrained(model, initial_adapter_path, is_trainable=True)
    sdft_loaded = not bool(grpo_adapter_path)
else:
    print(f"Loading model: {model_id}")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=model_dtype,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if USE_LORA:
        model = get_peft_model(model, _build_grpo_lora_config())
    sdft_loaded = False

if USE_GRAD_CHECKPOINT and hasattr(model, "gradient_checkpointing_enable"):
    model.gradient_checkpointing_enable()
if hasattr(model, "config"):
    model.config.use_cache = False
if device == "cuda":
    model = model.to(device)

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


# parse_tool_call_json imported from helper.py replaces _extract_last_json


def process_doc(doc_slides: list, step_num: int, doc_idx: int) -> list:
    """
    Mỗi slide đã có đầy đủ các trường pre-computed từ dataset_with_candidate_tools.json:
      - slide_content       : nội dung slide
      - style_context       : context phong cách từ slide trước
      - design_instruction  : hướng dẫn thiết kế
      - action              : loại slide (CONTENT_TOOLS, INTRO_TOOLS...)
      - candidate_tools     : danh sách tên tool đã pre-retrieved
    """
    prompts_data = []
    prev_embedding = [0.0] * 768
    rendered_paths = []
    render_dir = os.path.join(data_dir, f"step_{step_num:04d}", "renders", f"doc_{doc_idx}")
    os.makedirs(render_dir, exist_ok=True)

    for si, slide in enumerate(doc_slides):
        # Đọc trực tiếp từ các trường đã pre-computed trong dataset
        action          = slide.get("action") or slide.get("category") or "CONTENT_TOOLS"
        style_context   = slide.get("style_context", "")
        design          = slide.get("design_instruction", "")
        slide_content   = slide.get("slide_content", "")
        candidate_names = slide.get("candidate_tools", [])

        # Lấy tool objects từ danh sách tên đã pre-retrieved và ĐẢM BẢO THÊM SEARCH_DDGS_TOOL ở đầu (giống slide_generator.py)
        category_tools = {t.name: t for t in TOOLS_DICT.get(action, [])}
        retrieved_tools = [category_tools[n] for n in candidate_names if n in category_tools]
        if not retrieved_tools:
            retrieved_tools = [t for t in TOOLS_DICT.get(action, []) if t.name in flat_tools]
        if len(retrieved_tools) > 5:
            retrieved_tools = retrieved_tools[:5]

        # Đưa SEARCH_DDGS_TOOL lên đầu danh sách tool
        all_slide_tools = [SEARCH_DDGS_TOOL] + retrieved_tools
        filtered_tools = [format_tool_for_qwen(t) for t in all_slide_tools]
        available_tool_names = [t.name for t in all_slide_tools]

        # Build per-slide-type system prompt matching slide_generator.py
        if action == 'CONTENT_TOOLS':
            highlight_instruction = "- This is a content slide - choose ONE color from the list and use it consistently"
            generator_system_prompt = CONTENT_PROMPT.format(highlight_instruction=highlight_instruction)
        elif action == 'TRANSITION_TOOLS':
            transition_context = "* Transition slide - establish a strong, consistent style"
            generator_system_prompt = TRANSITION_PROMPT.format(previous_transition_context=transition_context)
        else:
            generator_system_prompt = SLIDE_TYPE_PROMPTS.get(action, INTRO_PROMPT)

        generator_system_prompt = MATH_EQUATION_RULES + "\n\n" + generator_system_prompt

        # Build full system prompt matching production slide_generator.py format
        tool_desc_text = _build_tool_description_text(filtered_tools)
        full_system_prompt = (
            generator_system_prompt
            + "\n\n"
            + IMAGE_SEARCH_EXECUTION_PLAN_RULES
            + "\n\n"
            + QWEN_COT_GENERATOR_SYSTEM_PROMPT
            + "\n\n"
            + tool_desc_text
        )
        user_prompt = QWEN_GENERATOR_HUMAN_TEMPLATE.format(
            style_context=style_context,
            design_instruction=design[:600] if design else "",
            slide_content=slide_content[:1200],
        )
        messages = [
            {"role": "system", "content": full_system_prompt},
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
        real_html = None

        for attempt in range(EXECUTOR_MAX_RETRIES):
            with _gen_lock:
                with torch.no_grad():
                    out = model.generate(**inputs, max_new_tokens=max_completion_length,
                                         temperature=0.0, do_sample=False,
                                         pad_token_id=tokenizer.eos_token_id)
            completion = tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

            tool_plan = parse_tool_calls_json(completion)
            executor_feedback = ""

            if not tool_plan:
                executor_feedback = "CRITICAL: No tool call was generated. You must output a valid function call using <tool_call> JSON format."
            else:
                first_tool = tool_plan[0]
                is_valid, errors = validate_tool_call(first_tool, available_tool_names)
                if not is_valid:
                    executor_feedback = f"EXECUTOR VALIDATION FAILED ({len(errors)} errors):\n" + "\n".join(f"- {e}" for e in errors)
                else:
                    try:
                        real_html, tool_call, search_history = execute_tool_plan(tool_plan)
                        if real_html:
                            log_node(step_num, doc_idx, si, "Qwen", f"attempt {attempt+1}/{EXECUTOR_MAX_RETRIES} OK → {tool_call.get('name')}")
                            break
                        else:
                            executor_feedback = "EXECUTOR TOOL PLAN FAILED: HTML output is empty."
                    except ToolPlanError as tpe:
                        executor_feedback = str(tpe)
                    except Exception as e:
                        executor_feedback = f"EXECUTOR TOOL PLAN FAILED:\n- {e}"

            log_node(step_num, doc_idx, si, "Qwen", f"attempt {attempt+1}/{EXECUTOR_MAX_RETRIES} FAIL — {executor_feedback[:100].strip()}")
            prompt += f"\n\n[EXECUTOR VALIDATION FEEDBACK]\n{executor_feedback.strip()}"
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=8192).to(model.device)

        # Append prompt and embedding of the PREVIOUS slide
        prompts_data.append({
            "prompt": prompt,
            "previous_slide_embedding": prev_embedding,
        })

        if real_html:
            real_path = os.path.join(render_dir, f"slide_{si:03d}_real.png")
            try:
                render_html_to_png(real_html, real_path)
                rendered_paths.append(real_path)
                log_node(step_num, doc_idx, si, "Render", "OK")
            except Exception as e:
                log_node(step_num, doc_idx, si, "Render", f"FAILED ({e})")

            if tool_call:
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
        "resume_enabled": resume_grpo,
        "resumed_grpo_step": resumed_grpo_step,
        "initial_adapter_path": initial_adapter_path if os.path.exists(initial_adapter_path) else None,
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

os.makedirs(data_dir, exist_ok=True)

for step in range(1, total_steps + 1):
    print(f"\n--- Step {step}/{total_steps} ---")

    step_ckpt = os.path.join(data_dir, f"step_{step:04d}_adapter")
    if os.path.exists(os.path.join(step_ckpt, "adapter_model.safetensors")):
        print(f"  Step {step} skipped (checkpoint found at {step_ckpt})")
        continue

    # Đường dẫn đến file dataset đã pre-computed
    precomputed_dataset_path = os.path.join(os.path.dirname(__file__), "data", "dataset_with_candidate_tools.json")
    if not os.path.exists(precomputed_dataset_path):
        print(f"  ❌ Không tìm thấy file dataset: {precomputed_dataset_path}")
        print(f"  → Hãy chạy: python scripts/pre_retrieve_candidate_tools.py")
        continue

    with open(precomputed_dataset_path, "r", encoding="utf-8") as f:
        all_slides_flat = json.load(f)

    # Nhóm các slide theo doc_id
    by_doc = {}
    for s in all_slides_flat:
        by_doc.setdefault(s["doc_id"], []).append(s)

    all_doc_ids = sorted(by_doc.keys())
    # Chọn batch_docs doc theo vòng tròn dựa vào step
    step_offset = ((step - 1) * batch_docs) % len(all_doc_ids)
    selected_ids = [all_doc_ids[(step_offset + i) % len(all_doc_ids)] for i in range(min(batch_docs, len(all_doc_ids)))]
    docs = [by_doc[did] for did in selected_ids]

    all_slides_flat_selected = [s for doc in docs for s in doc]
    print(f"  Loaded {len(all_slides_flat_selected)} slides across {len(docs)} docs (doc_ids={selected_ids}) from pre-computed dataset")


    all_prompts = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=batch_docs) as ex:
        futures = [ex.submit(process_doc, doc, step, i) for i, doc in enumerate(docs)]
        for f in concurrent.futures.as_completed(futures):
            all_prompts.extend(f.result())


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
