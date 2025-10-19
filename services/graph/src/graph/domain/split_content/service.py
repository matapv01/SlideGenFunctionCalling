from __future__ import annotations

from base import BaseService

from litellm import LiteLLMChatInput
from litellm import LiteLLMService
from litellm import MessageRole

import json
from typing import Any
from typing import Dict

from .prompts import SYSTEM_PROMPT
from .prompts import HUMAN_PROMPT_TEMPLATE
from graph.shared.settings import ContentSplitterSettings

from graph.shared.agent import SlidegenState

from logger import get_logger

logger = get_logger(__name__)

class SplitContentService(BaseService):
    
    litellm: LiteLLMService
    content_splitter_settings: ContentSplitterSettings
    
    
    def process(self, inputs: SlidegenState) -> dict:

        def _process_node(node: Dict[str, Any], parent_headings: list[str]):
            """Recursively checks and splits content for a node and its children."""

            current_heading = node.get('numbered_title', node.get('title', ''))

            if node.get('content') and len(node['content']) > self.content_splitter_settings.content_char_limit_for_split:
                logger.info('Found oversized content, lets split:', extra={'current_heading': current_heading})
                
                messages = self.build_conversation(
                    document_title=inputs.get('document_title'),
                    parent_headings=' -> '.join(parent_headings),
                    current_heading=current_heading,
                    content_to_split=node['content'],
                )
                
                response = self.litellm.process(
                    inputs=LiteLLMChatInput(
                        message=messages
                    )
                )

                try:
                    # 1. Clean and find the JSON substring
                    # This is more robust against markdown code blocks or other text
                    start_index = response.response.find('[')
                    if start_index == -1: 
                        start_index = response.response.find('{')

                    end_index = response.response.rfind(']')
                    if end_index == -1: 
                        end_index = response.response.rfind('}')

                    if start_index == -1 or end_index == -1:
                        raise ValueError("Could not find a JSON-like object in the response.")

                    substring = response.response[start_index : end_index + 1]

                    # 2. Parse using strict=False. This can help with some formatting issues.
                    split_data = json.loads(substring, strict=False)

                    # If the LLM returns a single dict instead of a list
                    if isinstance(split_data, dict):
                        split_data = [split_data]

                    if not isinstance(split_data, list):
                        logger.exception('LLM response is not a JSON list', extra={'current_heading': current_heading, 'response': response.response})
                        raise ValueError("LLM response is not a JSON list or object.")

                    # Convert the LLM's nested tree into our standard node format
                    new_children = self.___convert_llm_tree_to_nodes(split_data, node['level'])

                    if not new_children:
                        raise ValueError("Failed to convert LLM response into valid nodes.")

                    # Replace the old content with the new hierarchical child nodes
                    node['content'] = "" # Clear the original long content
                    node['children'] = new_children + node.get('children', []) # Prepend new structure

                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning('Failed to process LLM response; keeping original content', extra={'current_heading': current_heading, 'error': str(e)})

            # Recurse into all children (including any that were just added)
            new_parent_headings = parent_headings + [current_heading]
            for child_node in node.get('children', []):
                _process_node(child_node, new_parent_headings)

        # Start the recursive process from the root nodes
        for root_node in inputs.get('document_structure', []):
            _process_node(root_node, [])
            
        return {'document_structure': inputs.get('document_structure')}
            
    def __convert_llm_tree_to_nodes(self, llm_json_list: list[Dict], parent_level: int) -> list[Dict]:
        """
        Recursively converts the LLM's nested JSON output into the standard
        node format used by the document_structure.
        """
        new_nodes = []
        for item in llm_json_list:
            if "sub_headline" not in item or "sub_content" not in item:
                continue # Skip malformed items

            new_node = {
                "level": parent_level + 1,
                "title": item["sub_headline"],
                "content": "\n".join(item.get("sub_content", [])),
                "children": [] # Default to empty
            }

            # If there are nested sections, recurse!
            if item.get("sub_sections") and isinstance(item["sub_sections"], list):
                new_node["children"] = self.__convert_llm_tree_to_nodes(item["sub_sections"], parent_level + 1)

            new_nodes.append(new_node)
        return new_nodes
        
    def build_conversation(self, document_title: str, document_structure: list[dict]) -> list[dict]:

        return [
            {
                'role': MessageRole.SYSTEM,
                'content': SYSTEM_PROMPT,
            },
            {
                'role': MessageRole.USER,
                'content': HUMAN_PROMPT_TEMPLATE.format(
                    document_title=document_title,
                    document_structure=document_structure
                ),
            },
        ]