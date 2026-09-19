import os
from dotenv import load_dotenv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Base directories
PROJECT_DIR = Path(__file__).parent.parent
STATIC_DIR = PROJECT_DIR / "static"
FRONTEND_DIR = PROJECT_DIR / "frontend"
FRONTEND_DIST_DIR = PROJECT_DIR / "frontend" / "dist"
RUNNING_IN_DOCKER = Path("/.dockerenv").exists()

# `.env` contains credentials and deployment secrets. Load it once before
# reading them; application behavior stays centralized in this config module.
load_dotenv(PROJECT_DIR / ".env")

# Upload and output directories
UPLOAD_DIR = STATIC_DIR / "uploads"
OUTPUT_DIR = STATIC_DIR / "output"
TEMP_DIR = STATIC_DIR / "temp"
CAPTURES_DIR = STATIC_DIR / "captures"
CHATBOT_DOCUMENTS_DIR = STATIC_DIR / "chatbot_documents"

# Create directories
for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR, CAPTURES_DIR, CHATBOT_DOCUMENTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# CORS settings
CORS_ORIGINS = [
    "http://localhost",            # nginx port 80 (production)
    "http://localhost:5173",       # Vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:12008",
    "http://127.0.0.1:12008",
]

# Logging
LOG_LEVEL = "INFO"

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 12008

# --- Credentials / secrets (the only values read from .env) ---
LLM_API_KEY = os.getenv("LLM_API_KEY")
TAVILY_API_KEYS = tuple(
    key
    for key in (
        os.getenv("TAVILY_API_KEY1"),
        os.getenv("TAVILY_API_KEY2"),
        os.getenv("TAVILY_API_KEY3"),
    )
    if key
)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "").strip()
GOOGLE_FRONTEND_URL = os.getenv("GOOGLE_FRONTEND_URL", "").strip().rstrip("/")

# Email verification. SMTP is intentionally explicit so password and Google
# sign-ins both use the same second step before an access token is issued.
SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USERNAME).strip()
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").strip().lower() in {"1", "true", "yes", "on"}
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").strip().lower() in {"1", "true", "yes", "on"}
AUTH_OTP_EXPIRE_MINUTES = int(os.getenv("AUTH_OTP_EXPIRE_MINUTES", "10"))
AUTH_OTP_RESEND_COOLDOWN_SECONDS = int(os.getenv("AUTH_OTP_RESEND_COOLDOWN_SECONDS", "45"))
AUTH_OTP_MAX_ATTEMPTS = int(os.getenv("AUTH_OTP_MAX_ATTEMPTS", "5"))

# ============================================================================
# HYPERPARAMETERS - Tùy chỉnh để điều chỉnh hành vi của hệ thống
# ============================================================================

# --- LLM Configuration ---
# Model name sử dụng cho tất cả các LLM calls (slide generation)
LLM_MODEL = "qwen"
# Qwen chạy trên host: dùng localhost khi backend chạy trực tiếp,
# và host.docker.internal khi backend chạy trong Docker. Cho phép từng môi
# trường ghi đè rõ ràng, vì Qwen cũng có thể chạy ở container/service riêng.
_DEFAULT_LLM_BASE_URL = (
    "http://host.docker.internal:8080/v1"
    if RUNNING_IN_DOCKER
    else "http://127.0.0.1:8080/v1"
)
LLM_BASE_URL = (os.getenv("LLM_BASE_URL") or _DEFAULT_LLM_BASE_URL).strip().rstrip("/")
# Temperature: 0.0 = deterministic, 1.0 = creative (khuyến nghị: 0.5-0.7 cho slides)
LLM_TEMPERATURE = 0.5
# Max tokens trong response của provider OpenAI-compatible.
LLM_MAX_TOKENS = 20000
# Top-p sampling (nucleus sampling) - khuyến nghị giữ 1.0 cho tool calling
LLM_TOP_P = 1.0

# --- VLM Configuration ---
# Image relevance verification currently uses the same multimodal Qwen
# endpoint as the rest of the application. Keep this as a config constant so
# changing the model later is a deliberate code/config change, not a hidden
# .env override that can make Docker and local behave differently.
VLM_MODEL = LLM_MODEL
# Short-term conversation memory configuration.
CHATBOT_MAX_HISTORY_TURNS = 5
CHATBOT_DEFAULT_MODEL = "genius-3"
CHATBOT_DEFAULT_EFFORT = "medium"

# The UI exposes stable product names. Each profile maps to the provider model
# currently available in this deployment and owns its generation defaults.
# Keep these aliases independent from the provider's internal model name so a
# future model rollout does not require changing the API contract.
CHATBOT_MODEL_CONFIGS = {
    "genius-1": {
        "provider_model": LLM_MODEL,
        "temperature": 0.25,
        "top_p": 0.90,
    },
    "genius-2": {
        "provider_model": LLM_MODEL,
        "temperature": 0.45,
        "top_p": 0.95,
    },
    "genius-3": {
        "provider_model": LLM_MODEL,
        "temperature": 0.60,
        "top_p": 1.00,
    },
}

# Effort controls response budget and a small creativity adjustment. It is
# deliberately separate from model profiles so every model supports the same
# product-level effort choices.
CHATBOT_EFFORT_CONFIGS = {
    "low": {"max_tokens": 2048, "temperature_delta": -0.05},
    "medium": {"max_tokens": 4096, "temperature_delta": 0.00},
    "high": {"max_tokens": 8192, "temperature_delta": 0.05},
}

# Document RAG configuration. The index is intentionally stored as SQLite
# rows plus JSON embeddings so Docker dev/prod use the same persisted format;
# no second database or vector service is required.
CHATBOT_RAG_TOP_K = 6
CHATBOT_RAG_MAX_CONTEXT_CHARS = 14_000
CHATBOT_RAG_MIN_SIMILARITY = 0.28
CHATBOT_RAG_CHUNK_CHARS = 2_400
# Tree-aware retrieval budgets. Summary nodes provide coverage first; detail
# nodes are expanded only for the facets that need evidence.
CHATBOT_RAG_MAX_ANCESTOR_DEPTH = 4
CHATBOT_RAG_MAX_SIBLINGS = 3
CHATBOT_RAG_OVERVIEW_SECTION_LIMIT = 24
CHATBOT_RAG_DETAIL_NODE_LIMIT = 8


def resolve_chatbot_generation_config(
    model: str | None = None,
    effort: str | None = None,
) -> dict[str, str | float | int]:
    """Resolve public chatbot choices into one validated LLM configuration."""
    model_key = (model or CHATBOT_DEFAULT_MODEL).strip().lower()
    effort_key = (effort or CHATBOT_DEFAULT_EFFORT).strip().lower()
    model_config = CHATBOT_MODEL_CONFIGS.get(model_key)
    effort_config = CHATBOT_EFFORT_CONFIGS.get(effort_key)
    if model_config is None:
        raise ValueError(f"Unsupported chatbot model: {model_key}")
    if effort_config is None:
        raise ValueError(f"Unsupported chatbot effort: {effort_key}")

    temperature = max(
        0.0,
        min(1.0, model_config["temperature"] + effort_config["temperature_delta"]),
    )
    return {
        "model": model_key,
        "provider_model": model_config["provider_model"],
        "effort": effort_key,
        "temperature": temperature,
        "max_tokens": effort_config["max_tokens"],
        "top_p": model_config["top_p"],
        # Usage cost is loaded from the administrator-managed SQLite policy by
        # SubscriptionService. Keep a neutral compatibility value here for
        # callers that only need generation parameters.
        "usage_cost": 1.0,
    }

# Số lần retry tối đa khi gọi LLM thất bại (network error, timeout, v.v.)
MAX_REMAKE = 3

# --- Content Splitting ---
# Giới hạn ký tự cho mỗi slide (vượt quá sẽ được split)
SLIDE_CHAR_LIMIT = 600
# Giới hạn ký tự để quyết định có cần split content hay không
CONTENT_CHAR_LIMIT_FOR_SPLIT = 800
# Giới hạn ký tự cho 1 chunk content (cũng dùng để ước lượng số slide)
THRESHOLD_CHAR_LIMIT = 800
# LangGraph steps needed by long-document preprocessing and slide batches.
WORKFLOW_RECURSION_LIMIT = 2000

# --- Slide Planning ---
# Số lượng slides được plan cùng lúc trong 1 batch (tăng = nhanh hơn nhưng tốn RAM)
PLANNING_BATCH_SIZE = 5
# Maximum characters used for the compact whole-deck outline sent to each
# planner request. Raw slide content is intentionally not repeated here.
PLANNER_OUTLINE_MAX_CHARS = 6000

# --- Slide Generation ---
# Số lần thử lại tối đa khi generate slide bị lỗi (ví dụ: invalid function call)
SLIDE_GENERATION_MAX_RETRIES = 2

# Generate independent slide jobs concurrently after deck-wide style and
# layout assignment. Disable this flag to use the legacy whole-deck graph.
ENABLE_SLIDE_PARALLELISM = True
# Backward-compatible alias for older callers/config imports.
ENABLE_SECTION_PARALLELISM = ENABLE_SLIDE_PARALLELISM
# Allow up to five independent slide workers while keeping an explicit cap
# around the local Qwen endpoint.
SLIDE_MAX_CONCURRENCY = 5
# The planner, slide generators, and Qwen-VL share one endpoint. Keep the
# endpoint-wide request cap at five while allowing the workflow itself to fan
# out five slide workers.
LLM_REQUEST_MAX_CONCURRENCY = 5
# Match the configured planner batch concurrency.
PLANNER_MAX_CONCURRENCY = 5
IMAGE_SEARCH_MAX_RESULTS = 10
IMAGE_SEARCH_MAX_CONCURRENCY = 5
# Backward-compatible alias for integrations that still import the old name.
SECTION_MAX_CONCURRENCY = SLIDE_MAX_CONCURRENCY
SECTION_FALLBACK_BATCH_SIZE = 3

# Layout diversity is assigned globally before slide fan-out. Generation
# workers do not inspect previous slide tool calls.
ENABLE_LAYOUT_DUPLICATE_CHECK = True
ADJACENT_LAYOUT_SIMILARITY = 0.85
GLOBAL_LAYOUT_SIMILARITY = 0.92
DUPLICATE_REGEN_MAX_ROUNDS = 2

# Create one immutable visual direction before per-slide planning so parallel
# workers do not need to wait for the previous slide to establish a style.
ENABLE_DECK_STYLE_PLAN = True

# --- Tool Retrieval ---
# Số lượng tools relevant được retrieve từ FAISS index cho mỗi slide
TOOL_RETRIEVER_TOP_K = 5

# --- Embedding Model Configuration ---
# Model để tạo embeddings cho tool descriptions.
# Chạy local trên CPU để không tranh VRAM với Qwen và hỗ trợ tiếng Việt.
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Device cho embedding model: 'cpu', 'cuda', 'mps' (Apple Silicon).
# GPU hiện đang dành cho Qwen nên embedding phải chạy trên CPU.
EMBEDDING_DEVICE = "cpu"

# Normalize embeddings để cosine similarity hoạt động tốt hơn
EMBEDDING_NORMALIZE = True

# Batch size khi encoding embeddings (giảm nếu bị out of memory)
EMBEDDING_BATCH_SIZE = 32

# Cache directory cho HuggingFace models (None = default ~/.cache/huggingface)
EMBEDDING_CACHE_DIR = None

# --- Tool Retrieval Diversity Configuration ---
# MMR (Maximal Marginal Relevance) lambda parameter
# Higher = more focus on relevance, Lower = more focus on diversity
TOOL_RETRIEVER_MMR_LAMBDA = 0.5

# Number of candidates to retrieve before applying MMR (should be 2-3x TOOL_RETRIEVER_TOP_K)
TOOL_RETRIEVER_CANDIDATE_MULTIPLIER = 3

# Temporal decay penalty weight
TOOL_RETRIEVER_TEMPORAL_DECAY_WEIGHT = 0.5

# Maximum history window for temporal decay (in number of slides)
TOOL_RETRIEVER_TEMPORAL_WINDOW = 5

# Enable/disable temporal decay feature
TOOL_RETRIEVER_ENABLE_TEMPORAL_DECAY = True

# Enable/disable MMR diversity re-ranking
TOOL_RETRIEVER_ENABLE_MMR = True

# --- FAISS Index Configuration ---
# Index riêng cho model local 384 chiều. Không dùng lại index Gemini cũ
# vì hai model có số chiều vector khác nhau.
FAISS_INDEX_PATH = (
    PROJECT_DIR
    / "backend"
    / "infrastructure"
    / "faiss_tool_retriever_index_multilingual_minilm"
)

# Force rebuild FAISS index on startup (set True after changing EMBEDDING_MODEL_NAME)
FAISS_FORCE_REBUILD = False  # Changed to False - only rebuild when tools change

# --- VLM Evaluation (Visual Language Model) ---
VLM_MAX_RETRIES = 3
# Keep the ViT evaluator available in code, but disable the graph call by
# default until its score calibration is verified. Set this to true to enable.
ENABLE_VIT_EVALUATION = False
# Rule-based XML overflow handling. The LLM is called only for textboxes that
# fail the geometry check, and each textbox is re-measured after rewriting.
# Keep the bounded repair loop short; an alternate layout-tool retry is used
# when the same tool still cannot fit the complete slide.
TEXT_OVERFLOW_MAX_ROUNDS = 2
TEXT_OVERFLOW_MAX_BOXES_PER_ROUND = 12

# --- Executor Validator Configuration ---
# Max retries when executor detects logic errors (None, missing params, type mismatch)
# and when the overflow fallback asks the main generator for another layout tool.
EXECUTOR_MAX_RETRIES = 2

# --- Playwright Browser Configuration ---
BROWSER_VIEWPORT_WIDTH = 1920
BROWSER_VIEWPORT_HEIGHT = 1080
BROWSER_DEVICE_SCALE_FACTOR = 2.0
# URL of the frontend route used by Playwright for XML slide previews.
# Use Vite when the production bundle is absent; otherwise use the backend SPA.
BROWSER_PREVIEW_URL = (
    "http://127.0.0.1:12008/render/xml-preview"
    if (FRONTEND_DIST_DIR / "index.html").exists()
    else "http://127.0.0.1:5173/render/xml-preview"
)

# --- Local asset/provider configuration ---
VIT_MODEL_DIR = PROJECT_DIR / "models" / "vit"
VIT_MODEL_FILENAME = "best_model_multilabel_DX_10_0.77.pt"
HF_ENDPOINT = "https://hf-mirror.com"
PUPPETEER_EXECUTABLE_PATH = None
MATHLIVE_PACKAGE_DIR = None

# ============================================================================
# END OF HYPERPARAMETERS
# ============================================================================
