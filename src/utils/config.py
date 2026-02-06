import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import logging
logger = logging.getLogger(__name__)
import re
from PIL import Image
import io

# ============================================================================
# HYPERPARAMETERS - Tùy chỉnh để điều chỉnh hành vi của hệ thống
# ============================================================================

# --- LLM Configuration ---
# Model name sử dụng cho tất cả các LLM calls (slide generation)
# LLM_MODEL = "gemini-2.5-flash"
LLM_MODEL = "gemini-3-flash-preview"
# Base URL cho API endpoint
LLM_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# Temperature: 0.0 = deterministic, 1.0 = creative (khuyến nghị: 0.5-0.7 cho slides)
LLM_TEMPERATURE = 0.5
# Max tokens trong response (Gemini Flash hỗ trợ lên đến 8k output tokens)
LLM_MAX_TOKENS = 20000
# Top-p sampling (nucleus sampling) - khuyến nghị giữ 1.0 cho tool calling
LLM_TOP_P = 1.0

# --- Idea Structure LLM Configuration ---
# Model cho việc tạo cấu trúc slide từ idea (create with idea feature)
# IDEA_STRUCTURE_LLM_MODEL = "gemini-2.0-flash-exp"
IDEA_STRUCTURE_LLM_MODEL = "gemini-2.5-flash"
# Temperature cao hơn để sáng tạo structure (0.7 = khá creative nhưng vẫn có logic)
IDEA_STRUCTURE_LLM_TEMPERATURE = 0.7
# Max tokens cho structure generation (cần ít hơn vì chỉ gen JSON structure)
IDEA_STRUCTURE_LLM_MAX_TOKENS = 4096

# --- Content Splitting ---
# Giới hạn ký tự cho mỗi slide (vượt quá sẽ không split nữa)
SLIDE_CHAR_LIMIT = 600
# Giới hạn ký tự để quyết định có cần split content hay không
# Nếu content > giá trị này, LLM sẽ chia nhỏ thành sub-sections
CONTENT_CHAR_LIMIT_FOR_SPLIT = 800

# --- Slide Planning ---
# Số lượng slides được plan cùng lúc trong 1 batch (tăng = nhanh hơn nhưng tốn RAM)
PLANNING_BATCH_SIZE = 5

# --- Slide Generation ---
# Số lần thử lại tối đa khi generate slide bị lỗi (ví dụ: invalid function call)
SLIDE_GENERATION_MAX_RETRIES = 2

# --- Tool Retrieval ---
# Số lượng tools relevant được retrieve từ FAISS index cho mỗi slide
# Tăng số này nếu muốn LLM có nhiều lựa chọn tool hơn (nhưng làm chậm)
TOOL_RETRIEVER_TOP_K = 5

# --- Tool Retrieval Diversity Configuration ---
# MMR (Maximal Marginal Relevance) lambda parameter
# Higher = more focus on relevance, Lower = more focus on diversity
# Range: 0.0 to 1.0, Recommended: 0.6-0.8
TOOL_RETRIEVER_MMR_LAMBDA = 0.7

# Number of candidates to retrieve before applying MMR
# Should be 2-3x larger than TOOL_RETRIEVER_TOP_K
TOOL_RETRIEVER_CANDIDATE_MULTIPLIER = 3

# Temporal decay penalty weight
# Higher = stronger penalty for recently used tools
# Range: 0.0 to 1.0, Recommended: 0.15-0.3
TOOL_RETRIEVER_TEMPORAL_DECAY_WEIGHT = 0.2

# Maximum history window for temporal decay (in number of slides)
# Tools used beyond this window won't receive penalty
TOOL_RETRIEVER_TEMPORAL_WINDOW = 10

# Enable/disable temporal decay feature
TOOL_RETRIEVER_ENABLE_TEMPORAL_DECAY = True

# Enable/disable MMR diversity re-ranking
TOOL_RETRIEVER_ENABLE_MMR = True

# --- VLM Evaluation (Visual Language Model) ---
# Số lần retry tối đa khi VLM đánh giá slide (vòng lặp: generate → evaluate → regenerate)
# Đặt = 3 nghĩa là tối đa 3 lần thử (lần đầu + 2 lần retry)
VLM_MAX_RETRIES = 3

# --- Playwright Browser Configuration ---
# Viewport size cho rendering slides (1920x1080 là standard HD)
BROWSER_VIEWPORT_WIDTH = 1600
BROWSER_VIEWPORT_HEIGHT = 900
# Device scale factor (1 = normal, 2 = retina display)
BROWSER_DEVICE_SCALE_FACTOR = 1

# ============================================================================
# END OF HYPERPARAMETERS
# ============================================================================

def setup_environment():
    """Load environment variables and set API keys and return a dictionary of them."""
    load_dotenv()
    api_keys = {
        "GEMINI_API_KEY": os.getenv('GEMINI_API_KEY'),
        # "AQUANG2": os.getenv('AQUANG2'),
        # "MATA01": os.getenv('MATA01'),
        # "AQUANG1": os.getenv('AQUANG1')
    }
    if "GEMINI_API_KEY" not in os.environ:
        os.environ["GEMINI_API_KEY"] = os.getenv('GEMINI_API_KEY')
    # if "AQUANG1" not in os.environ:
    #     os.environ["AQUANG1"] = os.getenv('AQUANG1')
    # if "AQUANG2" not in os.environ:
    #     os.environ["AQUANG2"] = os.getenv('AQUANG2')
    # if "MATA01" not in os.environ:
    #     os.environ["MATA01"] = os.getenv('MATA01')
    
    return api_keys
async def initialize_playwright():
    try:
        playwright = await async_playwright().__aenter__()
        browser = await playwright.chromium.launch(headless=True, args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-web-security",
            "--allow-running-insecure-content",
            "--disable-extensions",
            "--disable-plugins",
        ])
        context = await browser.new_context(
            viewport={"width": BROWSER_VIEWPORT_WIDTH, "height": BROWSER_VIEWPORT_HEIGHT},
            device_scale_factor=BROWSER_DEVICE_SCALE_FACTOR
        )
        print("✅ Playwright initialized successfully")
        return {"playwright": playwright, "browser": browser, "context": context}
    except Exception as e:
        print(f"❌ Error initializing Playwright: {e}")
        import traceback; traceback.print_exc()
        return None