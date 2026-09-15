# File: backend/workflows/slidegen_workflow/nodes/slide_generator.py
import json
import re
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
from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
    get_image_targets_in_order,
)
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


def _build_fallback_image_query(slide_content: str, target: dict) -> str:
    """Build a deterministic image query when the model omits a search call."""
    description = str(target.get("description") or "")
    raw = f"{slide_content} {description}"
    raw = re.sub(r"https?://\S+", " ", raw)
    raw = re.sub(r"[\[\]{}<>\"']", " ", raw)

    generic_terms = {
        "url", "image", "images", "photo", "portrait", "landscape", "wide",
        "tall", "square", "displayed", "display", "sized", "approximately",
        "aspect", "ratio", "powerpoint", "slide", "px", "color", "background",
    }
    words = [
        word.strip(".,:;()")
        for word in raw.split()
        if word.strip(".,:;()")
        and word.strip(".,:;()").lower() not in generic_terms
    ]
    query = " ".join(words[:16]).strip()
    return query[:240] or "professional presentation visual"


def _complete_native_tool_plan(
    tool_plan: list[dict],
    candidate_tools: list,
    slide_content: str,
) -> list[dict]:
    """Complete omitted image searches without issuing another LLM request.

    Qwen can return a valid XML function call while silently omitting the
    companion image-search calls.  Image targets are deterministic from the
    selected tool schema, so fill only the missing searches here and preserve
    any searches the model did return.
    """
    if not isinstance(tool_plan, list):
        return tool_plan

    search_name = SEARCH_DDGS_TOOL.name
    slide_calls = [call for call in tool_plan if call.get("name") != search_name]
    if len(slide_calls) != 1:
        return tool_plan

    allowed_names = [tool.name for tool in candidate_tools]
    slide_call = constrain_tool_call_to_candidates(slide_calls[0], allowed_names)
    selected_tool = next(
        (tool for tool in candidate_tools if tool.name == slide_call.get("name")),
        None,
    )
    if selected_tool is None:
        return [slide_call, *[call for call in tool_plan if call.get("name") == search_name]]

    image_targets = get_image_targets_in_order(
        selected_tool,
        slide_call.get("arguments", {}),
    )
    search_calls = [
        call for call in tool_plan if call.get("name") == search_name
    ]
    missing_targets = image_targets[len(search_calls):]
    for target in missing_targets:
        search_calls.append(
            {
                "name": search_name,
                "arguments": {
                    "query": _build_fallback_image_query(slide_content, target),
                    "layout": None,
                    "size": "Large",
                },
            }
        )
        print(
            "  -> Added omitted image search for "
            f"{target['path_string']} (deterministic fallback query)"
        )

    return [slide_call, *search_calls]


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
    # This is the previous attempt for the same slide, used only on retry.
    # Slides in parallel workers never inherit another slide's tool call.
    previous_function_call = state.get('current_tool_call', {})
    deck_style_plan = state.get('deck_style_plan', {})
    length_slide_chunks = state.get('length_slide_chunks', 0)
    
    if isinstance(current_text, (dict, list)):
        current_text = _format_content_as_str(current_text)
    if not current_text:
        current_text = "Default slide content"
        
    tool_category = current_plan.get('action', 'CONTENT_TOOLS')
    creative_thought = current_plan.get('thought', '')
    slide_topic = str(current_plan.get('slide_topic') or creative_thought)
    
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
        generator_system_prompt += """

TRANSITION SLIDE CONTRACT:
- Generate this transition independently from every other slide.
- Use the assigned transition layout and the immutable deck style contract.
- Keep the transition title aligned with the slide topic and section context.
- Do not copy or infer parameters from a previous tool call.
"""
        
    generator_system_prompt = MATH_EQUATION_RULES + "\n\n" + generator_system_prompt
    
    # 5. The deck contract and layout assignment are immutable inputs. Do not
    # read mutable tool history from another slide worker.
    recent_tools_str = "- Layout assigned globally before parallel generation"
    style_context_str = json.dumps(deck_style_plan, ensure_ascii=False, indent=2)

    # 6. Reuse the planner's creative brief. Planning and deck-style planning
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
        deck_style_contract=style_context_str,
        slide_topic=slide_topic,
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
            parallel_tool_calls=True,
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
        tool_plan = _complete_native_tool_plan(
            tool_plan,
            my_tools,
            f"{slide_topic}\n{current_text}",
        )
        tool_call_dict = tool_plan[0]
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

    print(f"Time taken: {time.time() - start_time:.2f} seconds.")
    return state
