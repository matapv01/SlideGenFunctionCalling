# File: backend/workflows/slidegen_workflow/nodes/slide_preparer.py

import json
from langchain_core.runnables import RunnableConfig

from backend.workflows.slidegen_workflow.graph.stage import State
from backend.config import TOOL_RETRIEVER_TOP_K
from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT
from backend.workflows.slidegen_workflow.utils.prompts import (
    CONTENT_PROMPT,
    TRANSITION_PROMPT,
    SLIDE_TYPE_PROMPTS,
    HUMAN_PROMPT_TEMPLATE,
    INTRO_PROMPT,
    MATH_EQUATION_RULES,
    SLIDE_PREPARER_SYSTEM_PROMPT,
    SLIDE_PREPARER_HUMAN_TEMPLATE
)
from backend.workflows.slidegen_workflow.utils.helper import get_slide_style_context

def prepare_slide(state: State, config: RunnableConfig) -> State:
    """
    Node to prepare tools, style context, and call Gemini (Preparer)
    to generate detailed slide design instructions for the generator model.
    """
    print("\n---------------- Executing Node: slide_preparer ----------------")
    
    # 1. Get resources from config
    configurable = config["configurable"]
    tool_retriever = configurable.get('tool_retriever')
    all_tools_dict = configurable.get('tools_dict', TOOLS_DICT)
    planner_llm = configurable.get('planner_llm') or configurable.get('llm')
    
    # 2. Get dynamic data from state
    idx = state['current_slide_index']
    current_text = state.get("current_slide_text", "")
    previous_slide_function_call = state.get('previous_accepted_tool_call', {})
    current_plan = state.get('current_slide_plan')
    length_slide_chunks = state.get('length_slide_chunks', 0)
    current_context_map = state.get('current_slide_context_map')
    
    if not current_text:
        current_text = "Default slide content"
        
    tool_category = current_plan.get('action', 'CONTENT_TOOLS')
    creative_thought = current_plan.get('thought', '')
    
    print(f"--- Preparing slide {idx + 1}/{length_slide_chunks} ---")
    print(f"  -> Category: '{tool_category}'")
    
    # 3. Retrieve relevant tools
    my_tools = []
    if tool_category == 'TRANSITION_TOOLS' and 'previous_transition_tool_call' in state:
        prev_transition_tool_name = state['previous_transition_tool_call'].get('name')
        if prev_transition_tool_name:
            all_transition_tools = all_tools_dict.get('TRANSITION_TOOLS', [])
            matching_tool = next((t for t in all_transition_tools if t.name == prev_transition_tool_name), None)
            if matching_tool:
                my_tools = [matching_tool]
                print(f"  -> Reusing transition tool for consistency: {prev_transition_tool_name}")
                
    if not my_tools:
        retrieved_tools = tool_retriever.get_relevant_tools(
            category=tool_category,
            query=creative_thought,
            top_k=TOOL_RETRIEVER_TOP_K,
            current_slide_index=idx
        )
        my_tools = retrieved_tools if retrieved_tools else all_tools_dict.get(tool_category, [])
        
    if not my_tools:
        my_tools = all_tools_dict.get('CONTENT_TOOLS', [])
        
    print(f"  -> Prepared {len(my_tools)} tools: {[t.name for t in my_tools]}")
    
    # 4. Resolve system prompt (legacy fallback for API models)
    slide_type = current_plan.get('action', 'CONTENT_TOOLS')
    if slide_type == 'CONTENT_TOOLS':
        if 'highlight_color' in state:
            highlight_instruction = f"- MUST use this color: {state['highlight_color']} (maintain consistency!)"
        else:
            highlight_instruction = "- This is the FIRST content slide - choose ONE color from the list and use it consistently"
        system_prompt = CONTENT_PROMPT.format(highlight_instruction=highlight_instruction)
        
    elif slide_type == 'TRANSITION_TOOLS':
        previous_transition = state.get('previous_transition_tool_call', {})
        if previous_transition:
            prev_tool_name = previous_transition.get('name', 'unknown')
            prev_args = previous_transition.get('arguments', {})
            args_text = "\n".join([f"    - {key}: {value}" for key, value in prev_args.items()])
            
            transition_context = f"""* PREVIOUS TRANSITION details:
  - Tool used: {prev_tool_name}
  - Parameters used:
{args_text}

* YOU MUST match these parameters EXACTLY:
  - Same font sizes, colors, background
  - Same text formatting style (numbered/unnumbered)
  - Same visual elements and layout
  - If previous had "1." then use "2.", "3." etc. in sequence
  - If previous had no numbers, don't add numbers
* ONLY change the text content to match the new section heading"""
        else:
            transition_context = "* This is the FIRST transition slide - establish a strong, consistent style that will be reused for ALL future transitions"
        system_prompt = TRANSITION_PROMPT.format(previous_transition_context=transition_context)
        
    else:
        system_prompt = SLIDE_TYPE_PROMPTS.get(slide_type, INTRO_PROMPT)
        
    system_prompt = MATH_EQUATION_RULES + "\n\n" + system_prompt
    
    # 5. Extract history for recent tools
    recent_tools_list = []
    if hasattr(tool_retriever, 'tool_usage_history') and tool_category in tool_retriever.tool_usage_history:
        history = list(tool_retriever.tool_usage_history[tool_category])
        history.reverse()
        seen = set()
        for t_name, _ in history:
            if t_name not in seen:
                recent_tools_list.append(f"- {t_name}")
                seen.add(t_name)
                if len(recent_tools_list) >= 3:
                    break
    recent_tools_str = "\n".join(recent_tools_list) if recent_tools_list else "- (None used recently)"
    
    # 6. Format Style Context
    style_context_str = get_slide_style_context(previous_slide_function_call)
    
    # 7. Invoke Gemini (Planner LLM) to get design instruction for the next slide
    print("  -> Calling Gemini to prepare design instructions...")
    design_instruction = creative_thought
    if planner_llm:
        try:
            human_msg = SLIDE_PREPARER_HUMAN_TEMPLATE.format(
                previous_style_context=style_context_str,
                slide_plan=json.dumps(current_plan, indent=2),
                slide_content=current_text
            )
            messages = [
                {"role": "system", "content": SLIDE_PREPARER_SYSTEM_PROMPT},
                {"role": "user", "content": human_msg}
            ]
            response = planner_llm.invoke(messages)
            if hasattr(response, "content") and response.content:
                design_instruction = response.content.strip()
                print("  -> Prepared Instruction:")
                print(f"     {design_instruction.replace('\n', '\n     ')}")
        except Exception as e:
            print(f"⚠️ Gemini preparer failed, falling back to planner plan: {e}")
            
    # 8. Store prepared inputs into state for slide generator
    state["slide_prompt_system"] = system_prompt
    state["slide_prompt_human"] = HUMAN_PROMPT_TEMPLATE
    state["candidate_tools"] = my_tools
    state["recent_tools_str"] = recent_tools_str
    state["style_context_str"] = style_context_str
    state["design_instruction"] = design_instruction
    
    return state
