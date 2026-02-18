# File: backend/infrastructure/llm/gemini_provider.py

import json
import re
import logging
from typing import List, Dict, Any
from backend.domain.ports.llm_provider import LLMProvider
from backend.infrastructure.llm.client import LLMClient
from backend.infrastructure.llm.prompts import SLIDE_STRUCTURE_PROMPT
# from backend.workflows.slidegen_workflow.utils.config import (
#     IDEA_STRUCTURE_LLM_MODEL, LLM_BASE_URL,
#     IDEA_STRUCTURE_LLM_TEMPERATURE, IDEA_STRUCTURE_LLM_MAX_TOKENS
# )

logger = logging.getLogger(__name__)

class GeminiLLMProvider(LLMProvider):
    def __init__(self, api_keys: str = None, base_url: str = None, model: str = None, temperature: float = None, max_tokens: int = None, top_p: float = None, add_stop_token: List[str] = None):
        # Khởi tạo LLM Client 1 lần
        self.llm_client = LLMClient(
            api_keys=api_keys,
            base_url=base_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            add_stop_token=add_stop_token
        ).llm


    async def generate_slide_structure(
        self, 
        title: str, 
        user_prompt: str, 
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        
        transition_txt = "~" + str(constraints.get('estimated_sections', 3) - 1) + " transition slides (position -1)" if constraints['enable_transition'] else "No transition slides"
        thank_you_txt = "1 thank you slide (position -2)" if constraints['enable_thank_you'] else "No thank you slide"
        
        final_prompt = SLIDE_STRUCTURE_PROMPT.format(
            title=title,
            prompt=user_prompt,
            content_length_upper=constraints.get('content_length_desc', 'Standard').upper(),
            min_content=constraints['min_content'],
            max_content=constraints['max_content'],
            min_total=constraints['min_total'],
            max_total=constraints['max_total'],
            estimated_sections=constraints.get('estimated_sections', 3),
        )

        if constraints['enable_transition']:
            final_prompt += f"\n- {transition_txt}"
        
        if constraints['enable_thank_you']:
            final_prompt += f"\n- {thank_you_txt}"
        
        logger.info("📤 Calling LLM Provider...")
        response = await self.llm_client.ainvoke(final_prompt)
        response_text = response.content.strip()
        logger.info(f"📥 LLM Response: {len(response_text)} chars")

        try:
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            json_str = json_match.group(0) if json_match else response_text
            data = json.loads(json_str)
            return data.get('slide_chunks', [])
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise e