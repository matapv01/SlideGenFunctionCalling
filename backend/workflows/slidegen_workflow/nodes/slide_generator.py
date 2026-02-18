# File: backend/workflows/slidegen_workflow/nodes/slide_generator.py

import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.tools.tool_des import execute_tool
from backend.config import TOOL_RETRIEVER_TOP_K, MAX_REMAKE
from backend.workflows.slidegen_workflow.utils.prompts import (
    CONTENT_PROMPT,
    TRANSITION_PROMPT,
    SLIDE_TYPE_PROMPTS,
    HUMAN_PROMPT_TEMPLATE
)

from backend.domain.ports.tool_retrieve_provider import ToolRetrieveProvider

def generate_slide(state: State, config: RunnableConfig) -> State:
    """
    Node: Slide Generator
    Responsibility: 
    1. Retrieve best tools using ToolRetrieveProvider.
    2. Use LLM to generate function call.
    3. Execute the tool to generate HTML.
    """
    print("\n---------------- Executing Node: slide_generator ----------------")

    # 1. Get Dependencies from Config (Dependency Injection)
    configurable = config["configurable"]
    
    # 'llm' ở đây là LangChain Runnable object (được lấy từ GeminiLLMProvider.llm_client trong main.py)
    llm = configurable.get('llm') 
    
    # 'tool_retriever' ở đây là GeminiToolRetrieveProvider instance
    tool_retriever: ToolRetrieveProvider = configurable.get('tool_retriever')
    
    all_tools_dict = configurable.get('tools_dict', {})

    if not llm:
        raise ValueError("LLM instance not found in config.")
    if not tool_retriever:
        raise ValueError("Tool Retrieve Provider not found in config.")

    # 2. Get Dynamic Data from State
    idx = state['current_slide_index']
    current_text = state.get("current_slide_text", "Default slide content")
    previous_function_call = state.get('current_tool_call', {})
    previous_evaluation = state.get('vlm_feedback', "No evaluation yet.")
    length_slide_chunks = state.get('length_slide_chunks', 0)
    previous_slide_function_call = state.get('previous_accepted_tool_call', {})
    slide_plans = state.get('slide_plans', [])
    slide_context_maps = state.get('slide_context_maps', [])

    print(f"--- Generating slide {idx + 1}/{length_slide_chunks} ---")

    # Validation
    if not slide_plans or idx >= len(slide_plans):
        raise ValueError(f"Missing slide plan for slide index {idx}.")

    current_plan = slide_plans[idx]
    current_context_map = slide_context_maps[idx] if idx < len(slide_context_maps) else ""
    tool_category = current_plan.get('action', 'CONTENT_TOOLS')
    creative_thought = current_plan.get('thought', '')

    print(f"  -> Plan Action: '{tool_category}'")
    print(f"  -> Thought: '{creative_thought[:100]}...'")

    # 3. Tool Retrieval Strategy
    my_tools = []
    
    # A. Special Handling for Transition Slides (Consistency Check)
    if tool_category == 'TRANSITION_TOOLS' and 'previous_transition_tool_call' in state:
        prev_tool_name = state['previous_transition_tool_call'].get('name')
        # Tìm tool cũ trong danh sách tất cả tool
        all_transition_tools = all_tools_dict.get('TRANSITION_TOOLS', [])
        matching_tool = next((t for t in all_transition_tools if t.name == prev_tool_name), None)

        if matching_tool:
            my_tools = [matching_tool]
            print(f"  -> 🔄 REUSING previous transition tool: {prev_tool_name}")
        else:
            print(f"  -> ⚠️ Previous tool '{prev_tool_name}' not found. Fallback to retrieval.")

    # B. Standard Retrieval (If tools not yet selected)
    if not my_tools:
        # 🟢 GỌI INFRASTRUCTURE: Retrieve tools
        retrieved_tools = tool_retriever.get_relevant_tools(
            category=tool_category,
            query=creative_thought,
            top_k=TOOL_RETRIEVER_TOP_K
        )
        
        if retrieved_tools:
            my_tools = retrieved_tools
            print(f"  -> Retrieved {len(my_tools)} tools: {[t.name for t in my_tools]}")
        else:
            print(f"  -> WARNING: No relevant tools found. Fallback to ALL tools in category '{tool_category}'.")
            my_tools = all_tools_dict.get(tool_category, [])

    # C. Critical Fallback
    if not my_tools:
        print(f"  -> CRITICAL: Category '{tool_category}' is empty. Using CONTENT_TOOLS default.")
        my_tools = all_tools_dict.get('CONTENT_TOOLS', [])

    # 4. Bind Tools to LLM
    llm_with_tools = llm.bind_tools(my_tools)

    # 5. Prepare Prompt
    system_prompt = _get_system_prompt(tool_category, state)
    
    slidegen_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", HUMAN_PROMPT_TEMPLATE)
    ])

    slide_generator_runnable = slidegen_prompt | llm_with_tools

    # 6. Generation Loop (Retry Logic)
    retry_feedback = ""
    for attempt in range(1, MAX_REMAKE + 1):
        print(f"🔁 Attempt {attempt}/{MAX_REMAKE}")

        try:
            response = slide_generator_runnable.invoke({
                "slide_context_map": current_context_map,
                "previous_slide_function_call": json.dumps(previous_slide_function_call, indent=2),
                "slide_plan": json.dumps(current_plan, indent=2),
                "slide_content": current_text,
                "previous_function_call": json.dumps(previous_function_call, indent=2),
                "previous_evaluation": previous_evaluation + retry_feedback,
                "slide_index": idx + 1,
                "length_slide_chunks": length_slide_chunks,
            })
        except Exception as e:
            print(f"❌ LLM Invocation Failed: {e}")
            retry_feedback += f"\n❌ LLM Error: {e}"
            continue

        # Check Output
        if not hasattr(response, "tool_calls") or not response.tool_calls:
            print("❌ No function call generated.")
            retry_feedback += "\n❌ Error: You must call a tool to generate the slide."
            continue

        tool_call = response.tool_calls[0]
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})
        
        # Validate Tool Existence
        available_tool_names = {t.name for t in my_tools}
        if tool_name not in available_tool_names:
             # Fallback check in all tools dict just in case hallucination picked a valid tool but not in retrieved list
            all_known_tools = {t.name for cat in all_tools_dict.values() for t in cat}
            if tool_name in all_known_tools:
                 print(f"⚠️ LLM picked '{tool_name}' which wasn't in retrieved list but exists. Allowing it.")
            else:
                print(f"❌ Invalid Tool: '{tool_name}'")
                retry_feedback += f"\n❌ Error: Tool '{tool_name}' does not exist. Please use one of: {list(available_tool_names)}"
                continue

        # Execute Tool
        tool_call_dict = {"name": tool_name, "arguments": tool_args}
        try:
            # Note: execute_tool is currently an application utility, not strict infra, so direct call is acceptable
            html_content = execute_tool(tool_call_dict)
            
            if not html_content:
                raise ValueError("Tool returned empty output")

            print(f"✅ Tool '{tool_name}' executed successfully")
            
            # Update State
            state["current_tool_call"] = tool_call_dict
            state["current_html_content"] = html_content
            
            if tool_category == "TRANSITION_TOOLS":
                state["previous_transition_tool_call"] = tool_call_dict

            return state

        except Exception as e:
            print(f"❌ Tool Execution Failed: {e}")
            retry_feedback += f"\n❌ Tool Error: {e}"
            continue

    # If all retries fail
    print("❌ All generation attempts failed.")
    return state


def _get_system_prompt(slide_type: str, state: State) -> str:
    """Helper to select and format the correct system prompt."""
    
    if slide_type == 'CONTENT_TOOLS':
        color = state.get('highlight_color')
        instruction = f"- MUST use this color: {color}" if color else "- This is the FIRST content slide - choose ONE color and use it consistently."
        return CONTENT_PROMPT.format(highlight_instruction=instruction)

    elif slide_type == 'TRANSITION_TOOLS':
        prev = state.get('previous_transition_tool_call', {})
        if prev:
            args_text = "\n".join([f"    - {k}: {v}" for k, v in prev.get('arguments', {}).items()])
            context = f"""* PREVIOUS TRANSITION details:
  - Tool used: {prev.get('name')}
  - Parameters:
{args_text}
* YOU MUST match these parameters EXACTLY (fonts, colors, layout). ONLY change text."""
        else:
            context = "* This is the FIRST transition slide - establish a strong style."
        return TRANSITION_PROMPT.format(previous_transition_context=context)

    else:
        return SLIDE_TYPE_PROMPTS.get(slide_type, CONTENT_PROMPT)
