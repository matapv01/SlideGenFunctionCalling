# File: backend/workflows/slidegen_workflow/nodes/slide_generator.py
import json
import time
from langchain_core.runnables import RunnableConfig

from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.tools.tool_des_xml import (
    TOOLS_DICT as XML_TOOLS_DICT,
    constrain_tool_call_to_candidates,
)
from backend.config import (
    TOOL_RETRIEVER_TOP_K,
)
from backend.workflows.slidegen_workflow.tools.ddgs_tool import SEARCH_DDGS_TOOL
from backend.workflows.slidegen_workflow.utils.prompts import (
    HUMAN_PROMPT_TEMPLATE,
    XML_CONTENT_PROMPT,
    MATH_EQUATION_RULES,
    IMAGE_SEARCH_EXECUTION_PLAN_RULES,
    NATIVE_TOOL_CALLING_SYSTEM_PROMPT,
)

from backend.workflows.slidegen_workflow.utils.deck_style import (
    apply_deck_style_to_tool_call,
)

# Keys that carry slide *content* — these must NOT leak into the next slide's prompt
_CONTENT_KEYS = frozenset({
    # text / titles
    "main_title", "subtitle", "subtitle1", "subtitle2", "content_text",
    "description_text", "header_text", "headline", "top_text", "title",
    "author_line", "top_left_text", "bottom_text", "year",
    "section_title", "section_subtitle",
    # body content
    "main_content", "content1", "content2", "content3", "content4",
    "left_title", "right_title", "left_text", "right_text",
    "left_content", "right_content", "description",
    # list / structured content
    "items", "agenda_items", "mission_items", "list_items", "steps",
    # image alt text (content-specific)
    "image_alt_text",
})


def _extract_style_params(tool_call: dict) -> dict:
    """
    Return a copy of *tool_call* that keeps only style-related parameters
    (colors, fonts, opacity, layout, image URLs) and removes content fields
    so the LLM won't copy text from the previous slide.
    """
    if not tool_call:
        return {}
    
    result = {"name": tool_call.get("name", "")}
    args = tool_call.get("arguments", {})
    
    style_args = {k: v for k, v in args.items() if k not in _CONTENT_KEYS}
    result["arguments"] = style_args
    return result





def _format_content_as_str(content) -> str:
    """Safely convert slide content (str, dict, list) to a plain string."""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        parts = []
        for k, v in content.items():
            if isinstance(v, list):
                parts.extend([str(item) for item in v])
            elif isinstance(v, (str, int, float)):
                parts.append(str(v))
            elif isinstance(v, dict):
                parts.append(_format_content_as_str(v))
        return "\n".join(parts) if parts else json.dumps(content, ensure_ascii=False)
    if isinstance(content, list):
        return "\n".join([_format_content_as_str(item) for item in content])
    return str(content) if content is not None else ""


def _normalize_native_tool_calls(response) -> list[dict]:
    """Convert a LangChain AIMessage's native calls to the workflow format."""
    normalized = []
    for tool_call in getattr(response, "tool_calls", None) or []:
        if not isinstance(tool_call, dict):
            continue
        function = tool_call.get("function", tool_call)
        if not isinstance(function, dict):
            continue
        name = tool_call.get("name") or function.get("name")
        arguments = tool_call.get("args")
        if arguments is None:
            arguments = tool_call.get("arguments", function.get("arguments", {}))
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {}
        if not isinstance(arguments, dict) or not name:
            continue
        normalized.append({"name": name, "arguments": arguments})
    return normalized

def generate_slide(state: State, config: RunnableConfig) -> State:
    """
    Node for slide generation: Prepares tools/instructions, then invokes the LLM.
    Uses the injected LangChain chat model with native tool binding.
    """
    print("\n---------------- Executing Node: slide_generator (Merged) ----------------")
    start_time = time.time()
    
    # 1. Get resources from config
    configurable = config["configurable"]
    llm = configurable.get('llm')
    if not llm:
        raise ValueError("LLM instance not found in config.")

    tool_retriever = configurable.get('tool_retriever')
    all_tools_dict = configurable.get('tools_dict', XML_TOOLS_DICT)
    requested_output_format = str(
        configurable.get('output_format')
        or state.get('output_format')
        or 'xml'
    ).lower()
    if requested_output_format != 'xml':
        raise ValueError("This workflow is XML-only; output_format must be 'xml'.")
    # The XML FAISS retriever is injected through the workflow config. Keep it
    # enabled so the LLM receives only the most relevant tools for this slide.
    
    # 2. Get dynamic data from state
    idx = state['current_slide_index']
    
    # If moving to a new slide index, clear cached candidate_tools and design_instruction from previous slide
    if state.get("last_processed_slide_index") != idx:
        state["candidate_tools"] = None
        state["design_instruction"] = None
        state["last_processed_slide_index"] = idx
    current_text = state.get("current_slide_text", "")
    current_plan = state.get('current_slide_plan')
    current_context_map = state.get('current_slide_context_map')
    vlm_fb = state.get('vlm_feedback', '')
    executor_fb = state.get('executor_feedback', '')
    eval_parts = []
    if executor_fb:
        eval_parts.append(f"[EXECUTOR VALIDATION FEEDBACK]\n{executor_fb}")
    if vlm_fb and vlm_fb != "No feedback provided.":
        eval_parts.append(f"[VLM VISUAL FEEDBACK]\n{vlm_fb}")
    previous_evaluation = "\n\n".join(eval_parts) if eval_parts else "No evaluation yet."
    previous_function_call = state.get('current_tool_call', {})
    previous_slide_function_call = state.get('previous_accepted_tool_call', {})
    deck_style_plan = state.get('deck_style_plan', {})
    length_slide_chunks = state.get('length_slide_chunks', 0)
    
    if isinstance(current_text, (dict, list)):
        current_text = _format_content_as_str(current_text)
    if not current_text:
        current_text = "Default slide content"
        
    tool_category = current_plan.get('action', 'CONTENT_TOOLS')
    creative_thought = current_plan.get('thought', '')
    
    print(f"--- Preparing & Generating slide {idx + 1}/{length_slide_chunks} ---")
    print(f"  -> Category: '{tool_category}'")
    
    # 3. Retrieve relevant tools (Reuse candidate_tools if available in state for retries)
    my_tools = []
    assigned_names = list(state.get("assigned_tool_candidates") or [])
    excluded_tools = {
        *list(state.get("duplicate_excluded_tools") or []),
        *list(state.get("overflow_excluded_tools") or []),
    }
    if assigned_names:
        category_lookup = {
            tool.name: tool for tool in all_tools_dict.get(tool_category, [])
        }
        selected_name = next(
            (name for name in assigned_names if name not in excluded_tools and name in category_lookup),
            None,
        )
        if selected_name:
            my_tools = [category_lookup[selected_name]]
            print(f"  -> Using deck-assigned layout: {selected_name}")

    if not my_tools and state.get("candidate_tools"):
        # Remove search tool if present in candidate_tools cache to get original my_tools.
        cached = [
            tool
            for tool in state["candidate_tools"]
            if getattr(tool, "name", "") != SEARCH_DDGS_TOOL.name
            and getattr(tool, "name", "") not in excluded_tools
        ]
        if cached:
            my_tools = cached
            print(f"  -> Reusing {len(my_tools)} cached tools from state (retry attempt)")

    if not my_tools and tool_category == 'TRANSITION_TOOLS' and 'previous_transition_tool_call' in state:
        prev_transition_tool_name = state['previous_transition_tool_call'].get('name')
        if prev_transition_tool_name:
            all_transition_tools = all_tools_dict.get('TRANSITION_TOOLS', [])
            matching_tool = next((t for t in all_transition_tools if t.name == prev_transition_tool_name), None)
            if matching_tool:
                my_tools = [matching_tool]
                print(f"  -> Reusing transition tool for consistency: {prev_transition_tool_name}")
                
    if not my_tools:
        if tool_retriever:
            try:
                retrieved_tools = tool_retriever.get_relevant_tools(
                    category=tool_category,
                    query=creative_thought,
                    top_k=TOOL_RETRIEVER_TOP_K,
                    current_slide_index=idx
                )
                if retrieved_tools:
                    my_tools = retrieved_tools
                else:
                    # FAISS returned 0 results for this category (e.g. CHART_TOOLS, TEAM_TOOLS
                    # when no dedicated tools are registered). Fall back to category list first,
                    # then CONTENT_TOOLS — but cap at TOOL_RETRIEVER_TOP_K to avoid overflowing
                    # remote models with tight context windows (e.g. 10 000 tokens).
                    my_tools = all_tools_dict.get(tool_category, [])[:TOOL_RETRIEVER_TOP_K]
                print(
                    f"  -> FAISS selected {len(retrieved_tools)} tools for '{tool_category}': "
                    f"{[tool.name for tool in retrieved_tools]}"
                )
            except Exception as e:
                print(f"⚠️ tool_retriever error ({e}), falling back to category tools for '{tool_category}'")
                my_tools = all_tools_dict.get(tool_category, [])[:TOOL_RETRIEVER_TOP_K]
        else:
            my_tools = all_tools_dict.get(tool_category, [])[:TOOL_RETRIEVER_TOP_K]
        
    if not my_tools:
        # Last-resort fallback: cap to avoid context overflow on remote models
        my_tools = all_tools_dict.get('CONTENT_TOOLS', [])[:TOOL_RETRIEVER_TOP_K]

    # A duplicate-layout retry excludes the rejected layout tool. This is a
    # retry constraint, not a permanent per-tool quota.
    if excluded_tools:
        filtered_tools = [tool for tool in my_tools if tool.name not in excluded_tools]
        if not filtered_tools:
            filtered_tools = [
                tool for tool in all_tools_dict.get(tool_category, [])
                if tool.name not in excluded_tools
            ]
        if filtered_tools:
            my_tools = filtered_tools
            print(f"  -> Excluding duplicate layouts: {sorted(excluded_tools)}")
        
    print(f"  -> Prepared {len(my_tools)} tools: {[t.name for t in my_tools]}")
    
    # 4. XML is the only active generation prompt.
    slide_type = current_plan.get('action', 'CONTENT_TOOLS')
    generator_system_prompt = XML_CONTENT_PROMPT
    if slide_type == 'TRANSITION_TOOLS':
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
        generator_system_prompt += f"\n\n{transition_context}"
        
    generator_system_prompt = MATH_EQUATION_RULES + "\n\n" + generator_system_prompt
    
    # 5. Extract history for recent tools
    recent_tools_list = []
    local_history = [
        item for item in state.get("batch_tool_usage_history", [])
        if item.get("category") == tool_category
    ]
    if local_history:
        seen = set()
        for item in reversed(local_history):
            tool_name = item.get("tool_name")
            if tool_name and tool_name not in seen:
                recent_tools_list.append(f"- {tool_name}")
                seen.add(tool_name)
                if len(recent_tools_list) >= 3:
                    break
    elif hasattr(tool_retriever, 'tool_usage_history') and tool_category in tool_retriever.tool_usage_history:
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
    style_context = deck_style_plan or _extract_style_params(previous_slide_function_call)
    style_context_str = json.dumps(style_context, ensure_ascii=False, indent=2)
    
    # 7. Reuse the planner's creative brief.  Planning and deck-style planning
    # already own their LLM calls; slide generation should make exactly one
    # generation call and should not invoke a second hidden preparer model.
    design_instruction = state.get("design_instruction")
    if not design_instruction:
        design_instruction = creative_thought
            
    # Assign prepared values. The image-search plan is produced by this same
    # generator invocation; no later LLM call is allowed to create search specs.
    image_search_rules = IMAGE_SEARCH_EXECUTION_PLAN_RULES
    output_format_rules = """

OUTPUT FORMAT: TOOL CALLS ONLY
- Invoke exactly one XML slide tool from the native tools supplied for this request; do not write the XML document yourself.
- Return native tool calls only. Do not return raw arguments, CSS, markdown, or a prose explanation.
- Keep text values as plain editable text accepted by the XML tool schema.
- The only allowed inline control syntax is [[hl color="#RRGGBB"]]phrase[[/hl]] for text-color emphasis; it is removed before final XML generation.
"""

    system_prompt = (
        generator_system_prompt
        + "\n\n"
        + image_search_rules
        + output_format_rules
    )
    native_system_prompt = system_prompt + "\n\n" + NATIVE_TOOL_CALLING_SYSTEM_PROMPT
    generator_tools = [SEARCH_DDGS_TOOL, *my_tools]

    # The configured LangChain chat model owns tool schemas and transport.
    human_prompt = HUMAN_PROMPT_TEMPLATE.format(
        slide_context_map=current_context_map,
        previous_slide_function_call=style_context_str,
        recent_tools=recent_tools_str,
        slide_plan=json.dumps(current_plan, indent=2),
        slide_content=current_text,
        previous_function_call=json.dumps(previous_function_call, indent=2),
        previous_evaluation=previous_evaluation,
        slide_index=idx + 1,
        length_slide_chunks=length_slide_chunks,
        design_instruction=design_instruction,
    )
    messages = [
        {"role": "system", "content": native_system_prompt},
        {"role": "user", "content": human_prompt},
    ]
    raw_llm_prompt = json.dumps(messages, ensure_ascii=False)
    content = ""
    response = None
    native_tool_calls = []
    raw_llm_response = ""

    try:
        response = llm.bind_tools(
            generator_tools,
            tool_choice="required",
        ).invoke(messages)
        native_tool_calls = _normalize_native_tool_calls(response)
        content = getattr(response, "content", "") or ""
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)
        content = content.strip()
        raw_llm_response = json.dumps(
            {
                "content": content,
                "tool_calls": native_tool_calls,
            },
            ensure_ascii=False,
            default=str,
        )
    except Exception as invoke_err:
        print(f"❌ LLM tool invocation failed: {invoke_err}")
        raw_llm_response = ""

    # 3. Parse JSON / Extract tool call
    tool_call_dict = None
    tool_plan = native_tool_calls

    for call in tool_plan:
        if call.get("name") != SEARCH_DDGS_TOOL.name:
            tool_call_dict = call
            break

    if not tool_call_dict:
        raw_text = (content or "").strip()
        if not raw_text:
            failure_reason = "NO_OUTPUT_GENERATED: The model returned an empty response. You MUST generate a slide tool call."
        else:
            failure_reason = (
                "MISSING_NATIVE_TOOL_CALL: The model returned text instead of invoking "
                "one of the supplied slide tools. Return a native function/tool call only."
            )

        print(f"❌ Tool extraction failed: {failure_reason}")
        print(f"  -> Raw model response preview: {raw_text[:1000]!r}")
        tool_call_dict = {
            "name": "PARSE_ERROR",
            "_parse_error": failure_reason,
            "arguments": {}
        }
        tool_plan = [tool_call_dict]
    else:
        allowed_slide_tool_names = [tool.name for tool in my_tools]
        generated_name = tool_call_dict.get("name")
        tool_call_dict = constrain_tool_call_to_candidates(
            tool_call_dict,
            allowed_slide_tool_names,
        )
        if tool_call_dict.get("name") != generated_name:
            print(
                "  -> Corrected generated tool name "
                f"'{generated_name}' to assigned layout '{tool_call_dict.get('name')}'"
            )
        tool_plan = [
            constrain_tool_call_to_candidates(call, allowed_slide_tool_names)
            if call.get("name") != SEARCH_DDGS_TOOL.name else call
            for call in tool_plan
        ]
        tool_call_dict = apply_deck_style_to_tool_call(
            tool_call_dict,
            my_tools,
            deck_style_plan,
        )
        tool_plan = [
            apply_deck_style_to_tool_call(call, my_tools, deck_style_plan)
            if call.get("name") != SEARCH_DDGS_TOOL.name else call
            for call in tool_plan
        ]
        # Save valid parsed tool call for retry memory
        state["last_valid_tool_call"] = tool_call_dict
        
    print(f"✅ Generated Tool Call: {tool_call_dict.get('name')}")
    state["current_tool_call"] = tool_call_dict
    state["current_tool_plan"] = tool_plan
    state["raw_llm_response"] = raw_llm_response or content
    state["raw_llm_prompt"] = raw_llm_prompt
    
    # Save helper state variables for downstream nodes
    state["candidate_tools"] = generator_tools
    state["style_context_str"] = style_context_str
    state["design_instruction"] = design_instruction

    if slide_type == "TRANSITION_TOOLS":
        state["previous_transition_tool_call"] = tool_call_dict
    
    print(f"Time taken: {time.time() - start_time:.2f} seconds.")
    return state
