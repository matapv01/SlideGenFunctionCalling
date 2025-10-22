from __future__ import annotations

from base import BaseService
import json

from logger import get_logger
from .html import create_default_html
from .prompts import SLIDEGEN_SYSTEM_PROMPT, HUMAN_PROMPT_TEMPLATE

from agent import AgentService 
from tool_registry import ToolRegistryService

from graph.shared.agent import SlidegenState
from graph.shared.tools import get_relevant_tool

from langchain_core.prompts import ChatPromptTemplate

logger = get_logger(__name__)


class GenerateSlideService(BaseService):
    
    agent: AgentService
    registry: ToolRegistryService

    def process(self, inputs: SlidegenState) -> dict:
        
        idx = inputs['current_slide_index']
        slide_plans = inputs['slide_plans']
        current_plan = slide_plans[idx]
        
        tool_category = current_plan.get('action', 'content')
        creative_thought = current_plan.get('though', '')

        retrieved_tool = get_relevant_tool(
            category=tool_category,
            though=creative_thought
        )
        
        if not retrieved_tool:
            logger.warning('Could not retrieve any tools. Falling back to all tools in category.', extra={
                'tool_category': tool_category
            })
            my_tools = self.registry.get_tools_by_category(tool_category)
        else:
            my_tools = retrieved_tool
            logger.info('Retrieved {len(my_tools)} relevant tools', extra={
                'len_my_tools': len(my_tools),
                'tool_names': [tool.name for tool in my_tools]
            })
            
        llm_with_tools = self.agent.bind_tools(my_tools)
        
        slidegen_prompt = ChatPromptTemplate.from_messages([
            ("system", SLIDEGEN_SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT_TEMPLATE)
        ])
        
        slide_generator_runnable = slidegen_prompt | llm_with_tools
        
        response = slide_generator_runnable.invoke({
            "slide_context_map": inputs['slide_context_maps'][idx],
            "previous_slide_function_call": json.dumps(inputs['previous_slide_function_call'], indent=2),
            "slide_plan": json.dumps(current_plan, indent=2),
            "slide_content": inputs['slide_texts'][idx],
            "previous_function_call": json.dumps(inputs['previous_function_call'], indent=2),
            "previous_evaluation": inputs['previous_evaluation'],
            "slide_index": idx + 1,
            "length_slide_chunks": inputs['length_slide_chunks']
        })
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_call = response.tool_calls[0]
            tool_call_dict = {"name": tool_call["name"], "arguments": tool_call["args"]}
            
            html_content = self.agent.client().invoke(tool_call_dict)
            
            logger.info('Generated slide tool call successfully', extra={
                'tool_call': tool_call
            })
        
            return {
                'current_tool_call': tool_call_dict,
                'current_html_content': html_content,
            }
            
        return {
            'current_tool_call': {
                "name": "default_html", 
                "arguments": {
                    "content": inputs.get("current_slide_text", "Default slide content")}
            },
            'current_html_content': create_default_html(inputs.get("current_slide_text", "Default slide content"))
        }