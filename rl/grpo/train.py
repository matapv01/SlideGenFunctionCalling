from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT
from backend.workflows.slidegen_workflow.utils.helper import QWEN_CHAT_TEMPLATE
from backend.workflows.slidegen_workflow.utils.prompts import SLIDE_PREPARER_SYSTEM_PROMPT
from backend.workflows.slidegen_workflow.utils.prompts import SLIDE_PREPARER_HUMAN_TEMPLATE
from backend.workflows.slidegen_workflow.utils.prompts import SLIDE_PLANNER_SYSTEM_PROMPT
from backend.workflows.slidegen_workflow.utils.prompts import SLIDE_PLANNER_HUMAN_PROMPT
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
from datasets import Dataset
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from scripts.generate_challenge_dataset import generate_docs
from backend.config import EXECUTOR_MAX_RETRIES
from rl.grpo.rollout_processor import process_doc
from backend.infrastructure.llm_providers.base import LocalPyTorchLLMProvider
from backend.workflows.slidegen_workflow.nodes.slide_generator import generate_slide
from backend.workflows.slidegen_workflow.nodes.tool_call_executor import tool_call_executor
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
# 1b. LOCAL PYTORCH LLM PROVIDER (dùng cho generate_slide node trong GRPO rollout)
# ==============================================================================
local_provider = LocalPyTorchLLMProvider(
    model=model,
    tokenizer=tokenizer,
    model_name=model_id,
    max_completion_length=max_completion_length,
    gen_lock=_gen_lock,
)

# grpo_config truyền vào các node, chứa LLM provider và tool retriever
grpo_config = {
    "configurable": {
        "llm": local_provider,
        "tool_retriever": None,  # sẽ được cập nhật sau khi embedding_provider init
    }
}

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
    grpo_config["configurable"]["tool_retriever"] = tool_retriever
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


# ==============================================================================
# 5. TRAINING LOOP
# ==============================================================================
from trl import GRPOTrainer, GRPOConfig
from rl.rewards import slide_aesthetics_reward, content_preservation_reward, visual_consistency_reward
from rl.rewards.conciseness_reward import conciseness_reward
from rl.rewards.text_embedding_reward import text_embedding_reward
from rl.rewards.dom_overflow_reward import dom_overflow_reward

# ==============================================================================
# 5a. EMA BASELINE — Chống triệt tiêu gradient khi σ_R → 0
# ==============================================================================
# Khi tất cả phương án trong cùng nhóm G có reward giống hệt nhau,
# Advantage A_i = (R_i - μ_R) / (σ_R + ε) → 0, gradient bị triệt tiêu hoàn toàn.
# Giải pháp: Duy trì một đường cơ sở EMA (Exponential Moving Average) từ các
# bước trước đó. Khi σ_R quá nhỏ, ta dùng V_EMA làm baseline thay vì μ_R.
# ==============================================================================
class EMABaseline:
    """Exponential Moving Average baseline để chống Gradient Vanishing trong GRPO."""
    def __init__(self, decay: float = 0.99, sigma_floor: float = 0.05):
        self.decay = decay
        self.sigma_floor = sigma_floor  # σ tối thiểu để giữ gradient
        self.v_ema = None  # V_EMA — baseline trung bình lịch sử
        self.sigma_global = None  # σ toàn cục lịch sử

    def update_and_adjust(self, rewards: list) -> list:
        """
        Cập nhật EMA và điều chỉnh rewards nếu cần.
        
        Công thức Advantage cải tiến:
            A_i = (R_i - max(μ_R, V_EMA)) / max(σ_R, σ_global, σ_floor)
        
        Args:
            rewards: List of reward values cho nhóm G phương án
        Returns:
            List of adjusted rewards (để TRL tự tính advantage từ đó)
        """
        import numpy as np
        rewards_np = np.array(rewards, dtype=np.float64)
        mu = rewards_np.mean()
        sigma = rewards_np.std()
        
        # Cập nhật EMA
        if self.v_ema is None:
            self.v_ema = mu
            self.sigma_global = max(sigma, self.sigma_floor)
        else:
            self.v_ema = self.decay * self.v_ema + (1 - self.decay) * mu
            self.sigma_global = self.decay * self.sigma_global + (1 - self.decay) * max(sigma, self.sigma_floor)
        
        # Phát hiện trường hợp triệt tiêu gradient
        if sigma < self.sigma_floor:
            # σ_R quá nhỏ → dùng V_EMA làm baseline và σ_global làm mẫu
            baseline = max(mu, self.v_ema)
            effective_sigma = max(self.sigma_global, self.sigma_floor)
            # Tính advantage thủ công và encode lại vào rewards
            # (TRL sẽ tính lại, nhưng ta shift rewards để advantage không bằng 0)
            adjusted = ((rewards_np - baseline) / effective_sigma).tolist()
            print(f"  [EMA Baseline] σ_R={sigma:.4f} < floor={self.sigma_floor}. "
                  f"Using V_EMA={self.v_ema:.4f}, σ_global={self.sigma_global:.4f}")
            return adjusted
        
        return rewards  # Trả về nguyên bản nếu σ_R đủ lớn

ema_baseline = EMABaseline(decay=0.99, sigma_floor=0.05)

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

# ==============================================================================
# 5b. OPTIMIZER + SCHEDULER — TẠO MỘT LẦN DUY NHẤT, DÙNG XUYÊN SUỐT MỌI STEP
# ------------------------------------------------------------------------------
# Trước đây mỗi step tạo GRPOTrainer mới -> optimizer Adam bị khởi tạo lại
# (mất hết m/v đã tích luỹ) và LR scheduler cũng reset theo max_steps=1.
# Ở đây ta tự tạo optimizer + scheduler bên ngoài vòng lặp rồi truyền vào
# GRPOTrainer qua `optimizers=(...)`. Vì Trainer chỉ tự tạo optimizer/scheduler
# khi self.optimizer / self.lr_scheduler còn None, việc truyền sẵn khiến nó
# tái sử dụng đúng object cũ mỗi lần train() được gọi -> momentum và lịch LR
# được bảo toàn qua các step, dù mỗi lần vẫn dựng GRPOTrainer mới.
# LƯU Ý: hãy test nhanh với total_steps nhỏ (vd 2) để xác nhận hành vi này
# đúng với bản TRL/transformers đang cài, vì API nội bộ có thể đổi giữa các version.
# ==============================================================================
from transformers import get_linear_schedule_with_warmup

_trainable_params = [p for p in model.parameters() if p.requires_grad]
optimizer = torch.optim.AdamW(_trainable_params, lr=learning_rate)
lr_scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=0,
    num_training_steps=total_steps,  # mỗi vòng lặp ngoài ứng với đúng 1 optimizer step (max_steps=1)
)

_effective_gen_batch = per_device_train_batch_size  # x số GPU nếu chạy multi-GPU
if _effective_gen_batch % num_generations != 0:
    print(
        f"  [WARN] per_device_train_batch_size ({_effective_gen_batch}) không chia hết cho "
        f"num_generations ({num_generations}). TRL có thể raise lỗi khi train() — "
        f"nên chỉnh per_device_train_batch_size hoặc num_generations cho khớp."
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
step_ckpt = None  # tránh NameError phía dưới nếu total_steps=0 hoặc mọi step đều bị skip

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
    if not all_doc_ids:
        print("  ❌ Dataset rỗng (không có doc nào), skip step.")
        continue

    # Chọn batch_docs doc theo vòng tròn dựa vào step
    step_offset = ((step - 1) * batch_docs) % len(all_doc_ids)
    selected_ids = [all_doc_ids[(step_offset + i) % len(all_doc_ids)] for i in range(min(batch_docs, len(all_doc_ids)))]
    docs = [by_doc[did] for did in selected_ids]

    all_slides_flat_selected = [s for doc in docs for s in doc]
    print(f"  Loaded {len(all_slides_flat_selected)} slides across {len(docs)} docs (doc_ids={selected_ids}) from pre-computed dataset")


    all_prompts = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=batch_docs) as ex:
        futures = [
            ex.submit(process_doc, doc, step, i, grpo_config, data_dir, embedding_provider)
            for i, doc in enumerate(docs)
        ]  # truyền embedding_provider dùng chung, tránh mỗi thread tự load lại DINOv2
        for f in concurrent.futures.as_completed(futures):
            all_prompts.extend(f.result())


    if not all_prompts:
        print("  No valid prompts generated, skipping step.")
        continue

    print(f"  Collected {len(all_prompts)} prompts. Running GRPO update...")

    dataset = Dataset.from_list(all_prompts)
    # Reward functions bao gồm cả DOM Overflow Reward mới
    reward_funcs_list = [
        slide_aesthetics_reward,
        content_preservation_reward,
        visual_consistency_reward,
        conciseness_reward,
        text_embedding_reward,
        dom_overflow_reward,  # DOM Guardrail — phạt tràn chữ, đè chữ, ảnh chết
    ]

    trainer = GRPOTrainer(
        model=model,
        processing_class=tokenizer,
        reward_funcs=reward_funcs_list,
        args=training_args,
        train_dataset=dataset,
        peft_config=peft_config_for_trainer,
        optimizers=(optimizer, lr_scheduler),
    )

    # Áp dụng EMA Baseline: Hook vào reward computation để chống triệt tiêu gradient
    _orig_compute_rewards = trainer.compute_rewards if hasattr(trainer, 'compute_rewards') else None
    if _orig_compute_rewards is not None:
        def _patched_compute_rewards(*args, **kwargs):
            rewards = _orig_compute_rewards(*args, **kwargs)
            # Nếu rewards là tensor, chuyển sang list để xử lý
            import torch as _torch
            if isinstance(rewards, _torch.Tensor):
                adjusted = ema_baseline.update_and_adjust(rewards.detach().cpu().tolist())
                return _torch.tensor(adjusted, dtype=rewards.dtype, device=rewards.device)
            elif isinstance(rewards, list):
                return ema_baseline.update_and_adjust(rewards)
            return rewards
        trainer.compute_rewards = _patched_compute_rewards

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
if step_ckpt and os.path.exists(step_ckpt):
    shutil.copytree(step_ckpt, final_adapter)
    print(f"Final adapter: {final_adapter} (from step {step})")
else:
    print("[WARN] Không có step nào tạo checkpoint — bỏ qua bước copy final_adapter.")

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