"""
Auto-Structure Generator Node
Generates hierarchical structure from plain text documents without headings
"""
import json
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.workflows.slidegen_workflow.graph.stage import State
from langchain_core.runnables import RunnableConfig
import time
from backend.workflows.slidegen_workflow.utils.prompts import (
    AUTO_STRUCTURE_SYSTEM_PROMPT,
    HUMAN_PROMPT_TEMPLATE_AUTO as HUMAN_PROMPT_TEMPLATE
)


def generate_structure_from_plaintext(state: State, config: RunnableConfig) -> State:
    """
    Generate hierarchical document structure from plain text using LLM
    
    This node is used when the document has no existing heading structure.
    It calls LLM to analyze the content and create logical sections.
    
    Args:
        state: Current workflow state containing plain_text
        config: Runtime configuration with LLM instance
        
    Returns:
        Updated state with document_structure populated
    """
    print("\n---------------- Executing Node: generate_structure_from_plaintext ----------------")
    
    # DEBUG: Print full state keys to see what's available
    print(f"🔍 DEBUG auto_structure - State keys: {list(state.keys())}")
    print(f"   - document_structure exists: {'document_structure' in state}")
    print(f"   - plain_text exists: {'plain_text' in state}")
    print(f"   - docx_file exists: {'docx_file' in state}")
    
    if 'document_structure' in state:
        print(f"   - document_structure length: {len(state.get('document_structure', []))}")
    if 'plain_text' in state:
        print(f"   - plain_text length: {len(state.get('plain_text', ''))} chars")
    
    # Skip if document_structure already exists
    if state.get('document_structure'):
        print("⏭️  Skipping auto-structure: document_structure already exists")
        return state
    
    start_time = time.time()
    
    # Get resources from config
    configurable = config["configurable"]
    llm = configurable.get('llm')
    
    # Emit streaming event
    stream_callback = configurable.get('stream_callback')
    if stream_callback:
        stream_callback('status', {
            'step': 1,
            'title': 'Auto-Generating Structure',
            'description': 'AI analysis in progress',
            'message': 'Generating document structure from content...'
        })
        time.sleep(2) # Delay for UX
    
    if not llm:
        raise ValueError("LLM is not found in config. Cannot generate structure.")
    
    # Get data from state
    document_title = state.get('document_title', 'Untitled Document')
    plain_text = state.get('plain_text', '')
    
    if not plain_text:
        raise ValueError("No plain_text found in state. Cannot generate structure.")
    
    print(f"📄 Generating structure for: {document_title}")
    print(f"📊 Text length: {len(plain_text)} characters")
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", AUTO_STRUCTURE_SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT_TEMPLATE)
    ])
    
    # Create chain
    chain = prompt | llm | StrOutputParser()
    
    # Invoke LLM
    print("🤖 Calling LLM to generate structure...")
    llm_response_str = chain.invoke({
        "document_title": document_title,
        "full_text": plain_text
    })
    
    try:
        # Parse JSON response
        start_index = llm_response_str.find('[')
        if start_index == -1:
            start_index = llm_response_str.find('{')
        
        end_index = llm_response_str.rfind(']')
        if end_index == -1:
            end_index = llm_response_str.rfind('}')
        
        if start_index == -1 or end_index == -1:
            raise ValueError("Could not find JSON in LLM response")
        
        json_substring = llm_response_str[start_index:end_index + 1]
        document_structure = json.loads(json_substring, strict=False)
        
        # Ensure it's a list
        if isinstance(document_structure, dict):
            document_structure = [document_structure]
        
        if not isinstance(document_structure, list):
            raise ValueError("LLM response is not a valid JSON array")
        
        # Validate structure
        def validate_node(node: Dict, expected_level: int = 1) -> bool:
            """Validate node has required fields and correct structure"""
            if not isinstance(node, dict):
                return False
            
            if 'level' not in node or 'title' not in node:
                return False
            
            # Set content to empty string if not present
            if 'content' not in node:
                node['content'] = ''
            
            # Ensure children is a list
            if 'children' not in node:
                node['children'] = []
            elif not isinstance(node['children'], list):
                node['children'] = []
            
            # Recursively validate children
            for child in node['children']:
                if not validate_node(child, node['level'] + 1):
                    return False
            
            return True
        
        # Validate all root nodes
        valid_nodes = []
        for node in document_structure:
            if validate_node(node):
                valid_nodes.append(node)
            else:
                print(f"⚠️  Skipping invalid node: {node.get('title', 'Unknown')}")
        
        if not valid_nodes:
            raise ValueError("No valid nodes generated by LLM")
        
        document_structure = valid_nodes
        
        print(f"✅ Successfully generated structure with {len(document_structure)} top-level sections")
        
        # Count total nodes
        def count_nodes(nodes: List[Dict]) -> int:
            count = len(nodes)
            for node in nodes:
                count += count_nodes(node.get('children', []))
            return count
        
        total_nodes = count_nodes(document_structure)
        print(f"📊 Total sections created: {total_nodes}")
        
        # Update state
        state['document_structure'] = document_structure
        
        # Log structure summary
        print("\n📋 Generated Structure:")
        print(json.dumps(document_structure, indent=2, ensure_ascii=False))
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"❌ Failed to parse LLM response: {e}")
        print(f"🔍 Raw LLM response:\n{llm_response_str}")
        raise ValueError(f"Failed to generate valid structure: {e}")
    
    end_time = time.time()
    print(f"⏱️  Structure generation took {end_time - start_time:.2f} seconds")
    print("✅ Auto-structure generation complete")
    
    return state
