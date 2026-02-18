# File: backend/workflows/idea_workflow/main.py

import logging
import uuid
from typing import Dict, Any

from backend.workflows.idea_workflow.graph.builder import build_idea_workflow
from backend.workflows.idea_workflow.tools.search_tools import get_all_search_tools # File search_tools của bạn

logger = logging.getLogger(__name__)

def calculate_constraints(content_length: str, enable_transition: bool, enable_thank_you: bool) -> Dict[str, Any]:
    """Tính toán số lượng slide và section dựa trên độ dài yêu cầu."""
    
    length_map = {
        'brief': {'min': 5, 'max': 8, 'desc': 'Brief Overview'},
        'standard': {'min': 8, 'max': 12, 'desc': 'Standard Presentation'},
        'detailed': {'min': 12, 'max': 18, 'desc': 'Detailed Analysis'},
        'extensive': {'min': 18, 'max': 25, 'desc': 'Extensive Report'}
    }
    
    info = length_map.get(content_length, length_map['standard'])
    
    # Ước lượng số phần (sections)
    sections_map = {'brief': 2, 'standard': 3, 'detailed': 4, 'extensive': 5}
    estimated_sections = sections_map.get(content_length, 3)
    
    # Tính "Overhead" (Intro + Transition + Thank You)
    overhead = 1 # Intro luôn có
    if enable_transition: 
        overhead += max(0, estimated_sections - 1)
    if enable_thank_you: 
        overhead += 1
    
    # Tính số slide nội dung chính (trừ overhead ra)
    content_min = max(1, info['min'] - overhead)
    content_max = max(content_min + 1, info['max'] - overhead)

    return {
        'min_content': content_min,
        'max_content': content_max,
        'min_total': info['min'],
        'max_total': info['max'],
        'estimated_sections': estimated_sections,
        'content_length_desc': info['desc'],
        'enable_transition': enable_transition,
        'enable_thank_you': enable_thank_you
    }

async def run_idea_generation(
    title: str,
    prompt: str,
    content_length: str,
    enable_transition: bool,
    enable_thank_you: bool,
    infra_providers: Dict[str, Any] # Nhận LLM từ bên ngoài
) -> Dict[str, Any]:
    """
    Hàm chính để chạy Idea Workflow.
    Trả về JSON chứa session_id và danh sách chunks.
    """
    logger.info(f"🚀 Starting Idea Generation for: {title}")

    try:
        # 1. Chuẩn bị Infrastructure
        llm_provider = infra_providers['llm_provider']
        langchain_llm = llm_provider.llm_client # Lấy instance langchain
        
        # Lấy tools (Search)
        tools = get_all_search_tools() 

        # 2. Tính toán ràng buộc (Constraints)
        constraints = calculate_constraints(content_length, enable_transition, enable_thank_you)

        # 3. Build & Compile Graph
        workflow = build_idea_workflow()
        app = workflow.compile()

        # 4. Config cho Graph
        config = {
            "configurable": {
                "llm": langchain_llm,
                "tools": tools,
            }
        }

        # 5. Khởi tạo State input
        initial_state = {
            "title": title,
            "user_prompt": prompt,
            "constraints": constraints,
            "slide_chunks": []
        }

        # 6. Chạy Graph
        result = await app.ainvoke(initial_state, config=config)
        
        slide_chunks = result.get("slide_chunks", [])
        
        if not slide_chunks:
            raise ValueError("Workflow finished but no slides were generated.")

        # 7. Lưu kết quả tạm để debug hoặc dùng cho bước sau
        session_id = str(uuid.uuid4())[:8]
        output_data = {
            "session_id": session_id,
            "title": title,
            "prompt": prompt,
            "options": {
                "enable_transition": enable_transition,
                "enable_thank_you": enable_thank_you
            },
            "slide_chunks": slide_chunks
        }

        return output_data

    except Exception as e:
        logger.error(f"❌ Idea Generation Failed: {e}")
        import traceback; traceback.print_exc()
        return {"error": str(e)}