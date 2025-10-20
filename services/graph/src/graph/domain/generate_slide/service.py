from __future__ import annotations

from base import BaseService
from litellm import LiteLLMService
from litellm import LiteLLMToolInput
from litellm import MessageRole

import json

from logger import get_logger
from src.tools.tool_des import execute_tool, TOOLS_DICT
from .html import create_default_html
from .prompts import SLIDEGEN_SYSTEM_PROMPT, HUMAN_PROMPT_TEMPLATE

from graph.shared.agent import SlidegenState

logger = get_logger(__name__)


class GenerateSlideService(BaseService):
    
    litellm: LiteLLMService

    def process(self, inputs: SlidegenState) -> dict:
        logger.info(
            'GenerateSlideService.process starting',
            extra={'index': inputs.get('current_slide_index', 0)}
        )

        # --- start process ---
        idx = inputs.get('current_slide_index', 0)
        current_text = inputs.get('current_slide_text', '')
        previous_function_call = inputs.get('current_tool_call', {})
        previous_evaluation = inputs.get('vlm_feedback', 'No evaluation yet.')
        length_slide_chunks = inputs.get('length_slide_chunks', 0)
        previous_slide_function_call = inputs.get('previous_accepted_tool_call', {})
        slide_plans = inputs.get('slide_plans', [])
        slide_context_maps = inputs.get('slide_context_maps', [])

        logger.info('Generating slide', extra={'index': idx + 1, 'length': length_slide_chunks})

        if not current_text:
            logger.warning('No slide text provided. Using default.')
            current_text = 'Default slide content'

        if not slide_plans or idx >= len(slide_plans):
            raise ValueError(f'Missing slide plan for slide index {idx}.')

        if not slide_context_maps or idx >= len(slide_context_maps):
            raise ValueError(f'Missing slide context map for slide index {idx}.')

        current_plan = slide_plans[idx]
        current_context_map = slide_context_maps[idx]
        tool_category = current_plan.get('action', 'CONTENT_TOOLS')
        creative_thought = current_plan.get('thought', '')

        logger.info('Using plan', extra={'action': tool_category, 'thought': (creative_thought[:120] + '...') if len(creative_thought) > 120 else creative_thought})

        # Retrieve candidate tools from inputs (tool_retriever) or fall back to TOOLS_DICT
        tool_retriever = inputs.get('tool_retriever')

        if tool_retriever:
            try:
                my_tools = tool_retriever.get_relevant_tools(category=tool_category, query=creative_thought, top_k=3)
            except Exception:
                my_tools = []
        else:
            my_tools = TOOLS_DICT.get(tool_category, [])

        if not my_tools:
            logger.warning('No tools retrieved for category, falling back to CONTENT_TOOLS', extra={'category': tool_category})
            my_tools = TOOLS_DICT.get('CONTENT_TOOLS', [])

        # Build metadata for LLM (JSON-serializable list of tools)
        llm_tools_for_payload = []
        for t in my_tools:
            # StructuredTool objects expose .name and .description
            name = getattr(t, 'name', None) or getattr(t, 'id', None) or str(t)
            desc = getattr(t, 'description', '')
            llm_tools_for_payload.append({'id': name, 'name': name, 'description': desc})

        messages = [
            {'role': MessageRole.SYSTEM, 'content': SLIDEGEN_SYSTEM_PROMPT},
            {'role': MessageRole.USER, 'content': HUMAN_PROMPT_TEMPLATE.format(
                slide_context_map=current_context_map,
                previous_slide_function_call=json.dumps(previous_slide_function_call, indent=2),
                slide_plan=json.dumps(current_plan, indent=2),
                slide_content=current_text,
                previous_function_call=json.dumps(previous_function_call, indent=2),
                previous_evaluation=previous_evaluation,
                slide_index=idx + 1,
                length_slide_chunks=length_slide_chunks,
            )}
        ]

        # Try LLM tool-calling a couple times
        for attempt in (1, 2):
            logger.info('Attempt to generate tool call', extra={'attempt': attempt})
            try:
                with self.litellm.client as client:
                    response = self.litellm.use_tools(
                        client=client,
                        inputs=LiteLLMToolInput(
                            message=messages,
                            model=getattr(self, 'model', None) or getattr(self.litellm, 'model', None),
                            tools=llm_tools_for_payload,
                        )
                    )

                resp = response.response

                if isinstance(resp, list):
                    # iterate tool calls
                    for tc in resp:
                        # tc may be dataclass-like or dict
                        func = getattr(tc, 'function', None) or tc.get('function') if isinstance(tc, dict) else None
                        if not func:
                            continue
                        func_name = getattr(func, 'name', None) or func.get('name') if isinstance(func, dict) else None
                        args_str = getattr(func, 'arguments', None) or func.get('arguments') if isinstance(func, dict) else None

                        try:
                            parsed_args = json.loads(args_str) if isinstance(args_str, str) and args_str.strip() else (args_str or {})
                        except Exception:
                            parsed_args = {}

                        tool_call_dict = {'name': func_name, 'arguments': parsed_args}
                        html_content = execute_tool(tool_call_dict)
                        if html_content:
                            logger.info('Successfully generated HTML with tool', extra={'tool': func_name})
                            return {
                                'current_tool_call': tool_call_dict,
                                'current_html_content': html_content,
                            }

                else:
                    # If plain text returned, store as plan content
                    logger.info('LLM returned plain text response; storing as current_html_content')
                    return {'current_html_content': str(resp)}

            except Exception as e:
                logger.exception('LLM tool call attempt failed', extra={'error': str(e)})

        # All attempts failed -> fallback to default HTML
        logger.error('All attempts to generate slide failed. Creating default HTML slide.')
        default_call = {'name': 'default_html', 'arguments': {'content': current_text}}
        return {
            'current_tool_call': default_call,
            'current_html_content': create_default_html(current_text),
        }

    def build_conversation(self, *, slide_context_map, previous_slide_function_call, slide_plan, slide_content, previous_function_call, previous_evaluation, slide_index, length_slide_chunks) -> list[dict]:
        """Construct system+user messages for the slide generator LLM call."""
        return [
            {'role': MessageRole.SYSTEM, 'content': SLIDEGEN_SYSTEM_PROMPT},
            {'role': MessageRole.USER, 'content': HUMAN_PROMPT_TEMPLATE.format(
                slide_context_map=slide_context_map,
                previous_slide_function_call=json.dumps(previous_slide_function_call, indent=2),
                slide_plan=json.dumps(slide_plan, indent=2),
                slide_content=slide_content,
                previous_function_call=json.dumps(previous_function_call, indent=2),
                previous_evaluation=previous_evaluation,
                slide_index=slide_index,
                length_slide_chunks=length_slide_chunks,
            )}
        ]
