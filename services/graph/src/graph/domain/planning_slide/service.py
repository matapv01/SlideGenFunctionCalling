from __future__ import annotations

from base import BaseService

from litellm import LiteLLMService
from litellm import LiteLLMToolInput
from litellm import MessageRole

from logger import get_logger
from graph.shared.agent import SlidegenState
from graph.shared.settings import PlanningSlideSettings
from graph.shared.tools import (
    planning_slide_tool,
    PLANNING_SLIDE_TOOL_ID,
    PLANNING_SLIDE_TOOL_NAME,
    PLANNING_SLIDE_TOOL_DESC,
)
from typing import Optional, Dict, Any
import json

from .prompts import SLIDE_PLANNER_SYSTEM_PROMPT
from .prompts import SLIDE_PLANNER_HUMAN_PROMPT

logger = get_logger(__name__)

class PlanningSlideService(BaseService):
    
    litellm: LiteLLMService
    planning_slide_settings: PlanningSlideSettings
    
    def process(self, inputs: SlidegenState) -> dict:
        
        slide_chunks = inputs.get('slide_chunks', [])
        slide_context_maps = inputs.get('slide_context_maps', [])

        if not slide_chunks or not slide_context_maps:
            logger.warning("No slide chunks or context maps found in input state.")
            return {'slide_plans': []}

        all_slide_plans = []

        for i, content in enumerate(slide_chunks):
            context_map = slide_context_maps[i] if i < len(slide_context_maps) else ""
            
            messages = self.build_conversation(
                slide_context_map=context_map,
                slide_content=content
            )
            
            # Build tool metadata to send to the LLM (JSON-serializable)
            planning_tools_for_llm = [
                {
                    'id': PLANNING_SLIDE_TOOL_ID,
                    'name': PLANNING_SLIDE_TOOL_NAME,
                    'description': PLANNING_SLIDE_TOOL_DESC,
                    # don't include 'func' here — only metadata goes to the model
                }
            ]

            # Local map of tool id -> callable used to execute the tool when LLM
            # returns a tool call. This map is NOT sent over the wire.
            planning_local_funcs = {
                PLANNING_SLIDE_TOOL_ID: planning_slide_tool,
            }

            try:
                with self.litellm.client as client:
                    response = self.litellm.use_tools(
                        client=client, inputs=LiteLLMToolInput(
                            message=messages,
                            model=self.planning_slide_settings.model,
                            tools=planning_tools_for_llm,
                        ))

                logger.info('Done planning slide: %s', i)

                # If the model returned tool calls, attempt to execute them
                resp = response.response
                executed: Optional[Dict[str, Any]] = None
                if isinstance(resp, list):
                    # Expect list of ToolCall-like objects with id and function.arguments
                    for tc in resp:
                        tool_id = getattr(tc, 'id', None) or tc.get('id') if isinstance(tc, dict) else None
                        func_call = None
                        # extract arguments - could be string JSON
                        args_str = None
                        if isinstance(tc, dict):
                            func_call = tc.get('function') or tc.get('tool')
                        else:
                            func_call = getattr(tc, 'function', None)

                        if func_call:
                            args_str = getattr(func_call, 'arguments', None) or func_call.get('arguments') if isinstance(func_call, dict) else None

                        # Lookup local function by id and execute if available
                        if tool_id and tool_id in planning_local_funcs:
                            try:
                                parsed_args = json.loads(args_str) if isinstance(args_str, str) and args_str.strip() else {}
                            except Exception:
                                parsed_args = {}

                            try:
                                executed = planning_local_funcs[tool_id](parsed_args)
                                # use first successful execution
                                break
                            except Exception:
                                logger.exception('Tool execution failed for %s', tool_id)
                        else:
                            logger.warning('Received tool call for unknown tool id: %s', tool_id)

                else:
                    # If response is plain text, keep it
                    executed = resp

                all_slide_plans.append(executed)
                
            except Exception as e:
                logger.exception("Failed to call tools via LiteLLMService: %s", e)
                raise e

        return {'slide_plans': all_slide_plans}

    def build_conversation(self, slide_context_map: str, slide_content: str) -> list[dict]:

        return [
            {
                'role': MessageRole.SYSTEM,
                'content': SLIDE_PLANNER_SYSTEM_PROMPT,
            },
            {
                'role': MessageRole.USER,
                'content': SLIDE_PLANNER_HUMAN_PROMPT.format(
                    slide_context_map=slide_context_map,
                    slide_content=slide_content
                ),
            },
        ]