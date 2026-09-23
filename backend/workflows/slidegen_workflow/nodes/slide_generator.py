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
from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
    tool_matches_image_mode,
)
from backend.workflows.slidegen_workflow.utils.prompts import (
    HUMAN_PROMPT_TEMPLATE,
    XML_CONTENT_PROMPT,
    MATH_EQUATION_RULES,
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


def _resolve_image_mode(plan: dict) -> str:
    """Resolve the explicit planner mode with a conservative default."""
    explicit_mode = str((plan or {}).get("image_mode") or "").lower()
    if explicit_mode in {"none", "semantic"}:
        return explicit_mode
    return "none"


def _filter_tools_by_image_mode(
    tools: list,
    image_mode: str,
    approved_image_count: int | None = None,
) -> list:
    """Keep retriever candidates compatible with the planner's image mode."""
    if image_mode not in {"none", "semantic"}:
        return list(tools)
    return [
        tool
        for tool in tools
        if tool_matches_image_mode(tool, image_mode, approved_image_count)
    ]


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
        state["force_no_image_layout"] = False
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
    previous_evaluation = (
        "\n\n".join(eval_parts)
        if eval_parts
        else "None — this is the first attempt for this slide."
    )
    # This is the previous attempt for the same slide, used only on retry.
    # Slides in parallel workers never inherit another slide's tool call.
    previous_function_call = state.get('current_tool_call') or {}
    deck_style_plan = state.get('deck_style_plan', {})
    length_slide_chunks = state.get('length_slide_chunks', 0)
    presentation_instruction = str(
        (state.get("slide_options") or {}).get("presentation_instruction") or ""
    ).strip()
    approved_images = [
        image for image in state.get("current_approved_images") or []
        if isinstance(image, dict)
    ]
    
    if isinstance(current_text, (dict, list)):
        current_text = _format_content_as_str(current_text)
    if not current_text:
        current_text = "Default slide content"

    if approved_images:
        verified_image_context = "\n".join(
            json.dumps(
                {
                    "source_id": image.get("source_id") or image.get("image_id"),
                    "source_type": image.get("source_type"),
                    "source_url": image.get("source_url") or image.get("source_path"),
                    "role": image.get("role", "illustration"),
                    "visual_notes": image.get("visual_notes", ""),
                    "caption_hint": image.get("caption_hint", ""),
                    "placement_hint": image.get("placement_hint", ""),
                },
                ensure_ascii=False,
            )
            for image in approved_images
        )
        current_context_map = (
            f"{current_context_map or ''}\n{verified_image_context}"
        ).strip()
        
    tool_category = current_plan.get('action', 'CONTENT_TOOLS')
    creative_thought = current_plan.get('thought', '')
    slide_topic = str(current_plan.get('slide_topic') or creative_thought)
    image_mode = (
        "none"
        if state.get("force_no_image_layout")
        else _resolve_image_mode(current_plan)
    )

    # An approved image is a concrete asset, not a suggestion. Prefer an
    # image-capable layout so the executor can inject it deterministically.
    if approved_images and not state.get("force_no_image_layout"):
        image_mode = "semantic"

    approved_image_count = len(approved_images)
    if image_mode == "semantic":
        has_compatible_image_layout = any(
            tool_matches_image_mode(tool, "semantic", approved_image_count)
            for tools in all_tools_dict.values()
            for tool in tools
        )
        if not has_compatible_image_layout:
            # Do not select a gallery layout that needs more assets than the
            # verifier approved. A clean no-image layout is deterministic and
            # avoids a late executor retry with a blank image area.
            print(
                "  -> No compatible image layout for approved asset count; "
                "switching to no-image composition"
            )
            state["force_no_image_layout"] = True
            image_mode = "none"

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
        category_tools = _filter_tools_by_image_mode(
            all_tools_dict.get(tool_category, []),
            image_mode,
            approved_image_count,
        )
        category_lookup = {
            tool.name: tool for tool in category_tools
        }
        selected_name = next(
            (name for name in assigned_names if name not in excluded_tools and name in category_lookup),
            None,
        )
        if selected_name:
            my_tools = [category_lookup[selected_name]]
            print(f"  -> Using deck-assigned layout: {selected_name}")

    if not my_tools and state.get("candidate_tools"):
        cached = [
            tool
            for tool in state["candidate_tools"]
            if getattr(tool, "name", "") not in excluded_tools
        ]
        cached = _filter_tools_by_image_mode(
            cached,
            image_mode,
            approved_image_count,
        )
        if cached:
            my_tools = cached
            print(f"  -> Reusing {len(my_tools)} cached tools from state (retry attempt)")

    if not my_tools:
        if tool_retriever:
            try:
                retrieved_tools = tool_retriever.get_relevant_tools(
                    category=tool_category,
                    query=slide_topic or creative_thought,
                    top_k=max(
                        TOOL_RETRIEVER_TOP_K,
                        len(all_tools_dict.get(tool_category, [])),
                    ),
                    current_slide_index=idx
                )
                retrieved_tools = _filter_tools_by_image_mode(
                    retrieved_tools or [],
                    image_mode,
                    approved_image_count,
                )[:TOOL_RETRIEVER_TOP_K]
                if retrieved_tools:
                    my_tools = retrieved_tools
                else:
                    # FAISS returned 0 results for this category (e.g. CHART_TOOLS, TEAM_TOOLS
                    # when no dedicated tools are registered). Fall back to category list first,
                    # then CONTENT_TOOLS — but cap at TOOL_RETRIEVER_TOP_K to avoid overflowing
                    # remote models with tight context windows (e.g. 10 000 tokens).
                    my_tools = _filter_tools_by_image_mode(
                        all_tools_dict.get(tool_category, []),
                        image_mode,
                        approved_image_count,
                    )[:TOOL_RETRIEVER_TOP_K]
                print(
                    f"  -> FAISS selected {len(retrieved_tools)} tools for '{tool_category}': "
                    f"{[tool.name for tool in retrieved_tools]}"
                )
            except Exception as e:
                print(f"⚠️ tool_retriever error ({e}), falling back to category tools for '{tool_category}'")
                my_tools = _filter_tools_by_image_mode(
                    all_tools_dict.get(tool_category, []),
                    image_mode,
                    approved_image_count,
                )[:TOOL_RETRIEVER_TOP_K]
        else:
            my_tools = _filter_tools_by_image_mode(
                all_tools_dict.get(tool_category, []),
                image_mode,
                approved_image_count,
            )[:TOOL_RETRIEVER_TOP_K]

    if not my_tools:
        # Last-resort fallback: cap to avoid context overflow on remote models
        my_tools = _filter_tools_by_image_mode(
            all_tools_dict.get('CONTENT_TOOLS', []),
            image_mode,
            approved_image_count,
        )[:TOOL_RETRIEVER_TOP_K]

    # A duplicate-layout retry excludes the rejected layout tool. This is a
    # retry constraint, not a permanent per-tool quota.
    if excluded_tools:
        filtered_tools = [tool for tool in my_tools if tool.name not in excluded_tools]
        if not filtered_tools:
            filtered_tools = [
                tool for tool in all_tools_dict.get(tool_category, [])
                if tool.name not in excluded_tools
                and tool_matches_image_mode(
                    tool,
                    image_mode,
                    approved_image_count,
                )
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
    assigned_tool_name = str(state.get("preferred_tool_name") or "").strip()
    recent_tools_str = (
        "The previous image layout was rejected by the image verifier. Choose "
        "only a supplied XML layout with no image parameters."
        if state.get("force_no_image_layout")
        else (
            f"Use only the assigned XML layout tool: {assigned_tool_name}"
            if assigned_tool_name
            else "No layout was pre-assigned; choose one supplied XML layout tool."
        )
    )
    style_context_str = json.dumps(deck_style_plan, ensure_ascii=False, indent=2)

    # 6. Reuse the planner's creative brief. Planning and deck-style planning
    # already own their LLM calls; slide generation should make exactly one
    # generation call and should not invoke a second hidden preparer model.
    design_instruction = str(current_plan.get("visual_layout_request") or "").strip()
    if not design_instruction:
        design_instruction = state.get("design_instruction")
    if not design_instruction:
        design_instruction = creative_thought
            
    output_format_rules = """

OUTPUT FORMAT: TOOL CALLS ONLY
- Invoke exactly one XML slide tool from the native tools supplied for this request; do not write the XML document yourself.
- Return native tool calls only. Do not return raw arguments, CSS, markdown, or a prose explanation.
- Keep text values as plain editable text accepted by the XML tool schema.
- The only allowed inline control syntax is [[hl color="#RRGGBB"]]phrase[[/hl]] for text-color emphasis; it is removed before final XML generation.
"""

    system_prompt = (
        generator_system_prompt
        + output_format_rules
    )
    native_system_prompt = system_prompt + "\n\n" + NATIVE_TOOL_CALLING_SYSTEM_PROMPT
    generator_tools = list(my_tools)

    # The configured LangChain chat model owns tool schemas and transport.
    human_prompt = HUMAN_PROMPT_TEMPLATE.format(
        slide_context_map=current_context_map,
        deck_style_contract=style_context_str,
        slide_topic=slide_topic,
        presentation_instruction=presentation_instruction,
        image_mode=image_mode,
        visual_layout_request=str(current_plan.get("visual_layout_request") or ""),
        approved_images=(
            json.dumps(
                [
                    {
                        "source_id": image.get("source_id") or image.get("image_id"),
                        "source_url": image.get("source_url") or image.get("source_path"),
                        "role": image.get("role", "illustration"),
                        "visual_notes": image.get("visual_notes", ""),
                        "caption_hint": image.get("caption_hint", ""),
                        "placement_hint": image.get("placement_hint", ""),
                    }
                    for image in approved_images
                ],
                ensure_ascii=False,
                indent=2,
            )
            if approved_images
            else "None — use a layout with no image fields."
        ),
        recent_tools=recent_tools_str,
        slide_plan=json.dumps(current_plan, indent=2),
        slide_content=current_text,
        previous_function_call=(
            json.dumps(previous_function_call, indent=2)
            if previous_function_call
            else "None — this is the first attempt for this slide."
        ),
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
        request_limiter = configurable.get("llm_request_limiter")
        bound_llm = llm.bind_tools(
            generator_tools,
            tool_choice="required",
            parallel_tool_calls=True,
        )
        if request_limiter is None:
            response = bound_llm.invoke(messages)
        else:
            with request_limiter.slot():
                response = bound_llm.invoke(messages)
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

    if tool_plan:
        tool_call_dict = tool_plan[0]

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
        tool_plan = [constrain_tool_call_to_candidates(tool_call_dict, allowed_slide_tool_names)]
        tool_call_dict = tool_plan[0]
        tool_call_dict = apply_deck_style_to_tool_call(
            tool_call_dict,
            my_tools,
            deck_style_plan,
        )
        tool_plan = [
            apply_deck_style_to_tool_call(call, my_tools, deck_style_plan)
            for call in tool_plan
        ]
        tool_call_dict = tool_plan[0]
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
