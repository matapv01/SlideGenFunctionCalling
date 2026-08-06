# File: backend/application/services/idea_service.py

from fastapi import HTTPException
from backend.config import TEMP_DIR
from backend.application.services.idea_workflow_service import IdeaWorkflowService
import json
import uuid
import logging

logger = logging.getLogger(__name__)

class IdeaService:
    def __init__(self, idea_workflow_service: IdeaWorkflowService):
        # Inject Service chuyên trách thay vì LLMProvider trực tiếp
        self.workflow_service = idea_workflow_service

    async def generate_structure(
        self, 
        title: str, 
        prompt: str, 
        content_length: str, 
        enable_transition: bool, 
        enable_thank_you: bool,
        output_format: str = "xml",
    ) -> dict:
        
        logger.info(f"💡 IdeaService: Requesting structure for '{title}'")

        try:
            # Gọi Workflow Service để lấy cấu trúc
            # Workflow này đã bao gồm logic tính toán constraints và gọi Agent
            result = await self.workflow_service.generate_structure_from_idea(
                title=title,
                prompt=prompt,
                content_length=content_length,
                enable_transition=enable_transition,
                enable_thank_you=enable_thank_you
            )
        except Exception as e:
            logger.error(f"❌ Idea Workflow Error: {e}")
            raise HTTPException(status_code=500, detail=f"Idea generation failed: {str(e)}")

        # Check if the result contains an error from the workflow
        if isinstance(result, dict) and 'error' in result:
            raise HTTPException(status_code=500, detail=f"Idea workflow failed: {result['error']}")

        slide_chunks = result.get('slide_chunks', [])
        
        if not slide_chunks:
            raise HTTPException(status_code=500, detail="Workflow completed but returned no slides.")

        # --- LOGIC NGHIỆP VỤ ---
        # Lưu kết quả vào file tạm để Frontend có thể fetch hoặc dùng cho bước tiếp theo
        session_id = str(uuid.uuid4())[:8]
        temp_filename = f"idea_{session_id}.json"
        
        save_data = {
            'title': title,
            'slide_chunks': slide_chunks,
            'enable_transition_slides': enable_transition,
            'enable_thank_you_slide': enable_thank_you,
            'output_format': 'xml',
            'prompt': prompt,
            'is_from_idea': True, # Cờ đánh dấu nguồn gốc
            'metadata': {
                'content_length': content_length,
                'generated_by': 'IdeaWorkflowAgent'
            }
        }
        
        try:
            with open(TEMP_DIR / temp_filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Structure saved to {temp_filename} (Session: {session_id})")
            
            return {
                'session_id': session_id,
                'filename': temp_filename,
                'slide_count': len(slide_chunks),
                'is_from_idea': True,
                'output_format': save_data['output_format'],
            }
        except Exception as e:
            logger.error(f"Failed to save temp file: {e}")
            raise HTTPException(status_code=500, detail="Failed to save generation results.")
