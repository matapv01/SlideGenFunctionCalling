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

# Upload and output directories
UPLOAD_DIR = STATIC_DIR / "uploads"
OUTPUT_DIR = STATIC_DIR / "output"
TEMP_DIR = STATIC_DIR / "temp"
CAPTURES_DIR = STATIC_DIR / "captures"

# Create directories
for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR, CAPTURES_DIR]:
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
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 12008

# ============================================================================
# HYPERPARAMETERS - Tùy chỉnh để điều chỉnh hành vi của hệ thống
# ============================================================================

# --- LLM Configuration ---
# Model name sử dụng cho tất cả các LLM calls (slide generation)
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3-flash-preview")
# Base URL cho API endpoint
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
# Temperature: 0.0 = deterministic, 1.0 = creative (khuyến nghị: 0.5-0.7 cho slides)
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.5"))
# Max tokens trong response (Gemini Flash hỗ trợ lên đến 8k output tokens)
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "20000"))
# Top-p sampling (nucleus sampling) - khuyến nghị giữ 1.0 cho tool calling
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "1.0"))
# Số lần retry tối đa khi gọi LLM thất bại (network error, timeout, v.v.)
MAX_REMAKE = int(os.getenv("MAX_REMAKE", "3"))

# --- Idea Structure LLM Configuration ---
# Model cho việc tạo cấu trúc slide từ idea (create with idea feature)
IDEA_STRUCTURE_LLM_MODEL = os.getenv("IDEA_STRUCTURE_LLM_MODEL", "gemini-2.5-flash")
# Temperature cao hơn để sáng tạo structure (0.7 = khá creative nhưng vẫn có logic)
IDEA_STRUCTURE_LLM_TEMPERATURE = float(os.getenv("IDEA_STRUCTURE_LLM_TEMPERATURE", "0.7"))
# Max tokens cho structure generation (cần ít hơn vì chỉ gen JSON structure)
IDEA_STRUCTURE_LLM_MAX_TOKENS = int(os.getenv("IDEA_STRUCTURE_LLM_MAX_TOKENS", "4096"))

# --- Content Splitting ---
# Giới hạn ký tự cho mỗi slide (vượt quá sẽ không split nữa)
SLIDE_CHAR_LIMIT = 600
# Giới hạn ký tự để quyết định có cần split content hay không
CONTENT_CHAR_LIMIT_FOR_SPLIT = 800
# Giới hạn ký tự cho 1 chunk content (nếu vượt quá sẽ split)
THRESHOLD_CHAR_LIMIT = 800

# --- Slide Planning ---
# Số lượng slides được plan cùng lúc trong 1 batch (tăng = nhanh hơn nhưng tốn RAM)
PLANNING_BATCH_SIZE = 5

# --- Slide Generation ---
# Số lần thử lại tối đa khi generate slide bị lỗi (ví dụ: invalid function call)
SLIDE_GENERATION_MAX_RETRIES = 2

# Generate top-level document sections concurrently while preserving sequential
# slide generation inside each section. Disable this flag to use the legacy
# whole-deck sequential graph.
ENABLE_SECTION_PARALLELISM = os.getenv(
    "ENABLE_SECTION_PARALLELISM",
    "true",
).lower() in ("1", "true", "yes")
SECTION_MAX_CONCURRENCY = max(
    1,
    int(os.getenv("SECTION_MAX_CONCURRENCY", "3")),
)
SECTION_FALLBACK_BATCH_SIZE = max(
    1,
    int(os.getenv("SECTION_FALLBACK_BATCH_SIZE", "3")),
)

# Rendered-layout deduplication runs inside each sequential section batch.
# Cross-section diversity is handled before fan-out by layout assignment, so
# there is no final whole-deck regeneration pass. Transitions remain exempt.
ENABLE_LAYOUT_DUPLICATE_CHECK = os.getenv(
    "ENABLE_LAYOUT_DUPLICATE_CHECK",
    "true",
).lower() in ("1", "true", "yes")
ADJACENT_LAYOUT_SIMILARITY = float(
    os.getenv("ADJACENT_LAYOUT_SIMILARITY", "0.85")
)
GLOBAL_LAYOUT_SIMILARITY = float(
    os.getenv("GLOBAL_LAYOUT_SIMILARITY", "0.92")
)
DUPLICATE_REGEN_MAX_ROUNDS = max(
    0,
    int(os.getenv("DUPLICATE_REGEN_MAX_ROUNDS", "2")),
)

# Create one immutable visual direction before per-slide planning so parallel
# workers do not need to wait for the previous slide to establish a style.
ENABLE_DECK_STYLE_PLAN = os.getenv(
    "ENABLE_DECK_STYLE_PLAN",
    "true",
).lower() in ("1", "true", "yes")

# --- Tool Retrieval ---
# Số lượng tools relevant được retrieve từ FAISS index cho mỗi slide
TOOL_RETRIEVER_TOP_K = 5

# --- Embedding Model Configuration ---
# Model để tạo embeddings cho tool descriptions
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Device cho embedding model: 'cpu', 'cuda', 'mps' (Apple Silicon)
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cuda")

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
FAISS_INDEX_PATH = "faiss_tool_retriever_index"

# Force rebuild FAISS index on startup (set True after changing EMBEDDING_MODEL_NAME)
FAISS_FORCE_REBUILD = False  # Changed to False - only rebuild when tools change

# --- VLM Evaluation (Visual Language Model) ---
VLM_MAX_RETRIES = 3
# Keep the ViT evaluator available in code, but disable the graph call by
# default until its score calibration is verified. Set this to true to enable.
ENABLE_VIT_EVALUATION = os.getenv("ENABLE_VIT_EVALUATION", "false").lower() in (
    "1",
    "true",
    "yes",
    "on",
)
# Rule-based XML overflow handling. The LLM is called only for textboxes that
# fail the geometry check, and each textbox is re-measured after rewriting.
# Keep the bounded repair loop short; an alternate layout-tool retry is used
# when the same tool still cannot fit the complete slide.
TEXT_OVERFLOW_MAX_ROUNDS = int(os.getenv("TEXT_OVERFLOW_MAX_ROUNDS", "2"))
TEXT_OVERFLOW_MAX_BOXES_PER_ROUND = int(
    os.getenv("TEXT_OVERFLOW_MAX_BOXES_PER_ROUND", "12")
)

# --- Executor Validator Configuration ---
# Max retries when executor detects logic errors (None, missing params, type mismatch)
# and when the overflow fallback asks the main generator for another layout tool.
EXECUTOR_MAX_RETRIES = int(os.getenv("EXECUTOR_MAX_RETRIES", "2"))
# Enable CoT (Chain-of-Thought) thinking mode for Qwen generator
ENABLE_COT_THINKING = os.getenv("ENABLE_COT_THINKING", "true").lower() in ("1", "true", "yes")
# Max tokens for CoT generation (should be higher than non-CoT to account for thinking block)
COT_MAX_TOKENS = int(os.getenv("COT_MAX_TOKENS", "4096"))

# --- Playwright Browser Configuration ---
BROWSER_VIEWPORT_WIDTH = 1920
BROWSER_VIEWPORT_HEIGHT = 1080
BROWSER_DEVICE_SCALE_FACTOR = float(os.getenv("BROWSER_DEVICE_SCALE_FACTOR", "2"))
# URL of the frontend route used by Playwright for XML slide previews.
# Development overrides this to the Vite server in docker-compose.dev.yml.
BROWSER_PREVIEW_URL = os.getenv(
    "BROWSER_PREVIEW_URL",
    "http://127.0.0.1:12008/render/xml-preview",
)

# ============================================================================
# END OF HYPERPARAMETERS
# ============================================================================

def setup_environment():
    """Load environment variables and set API keys."""
    load_dotenv()
    api_keys = {
        "GEMINI_API_KEY": os.getenv('GEMINI_API_KEY'),
    }
    if "GEMINI_API_KEY" not in os.environ:
        os.environ["GEMINI_API_KEY"] = os.getenv('GEMINI_API_KEY')
    return api_keys
