# File: backend/workflows/slidegen_workflow/nodes/slide_generator.py
import os
import json
import time
from openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from transformers import AutoTokenizer

from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.tools.tool_des import execute_tool, TOOLS_DICT, execute_tool_plan
from backend.workflows.slidegen_workflow.nodes.tool_call_executor import validate_tool_call
from backend.config import MAX_REMAKE, TOOL_RETRIEVER_TOP_K, COT_MAX_TOKENS
from backend.workflows.slidegen_workflow.tools.ddgs_tool import SEARCH_DDGS_TOOL
from backend.workflows.slidegen_workflow.utils.prompts import (
    QWEN_GENERATOR_SYSTEM_PROMPT,
    QWEN_COT_GENERATOR_SYSTEM_PROMPT,
    QWEN_GENERATOR_HUMAN_TEMPLATE,
    HUMAN_PROMPT_TEMPLATE,
    CONTENT_PROMPT,
    TRANSITION_PROMPT,
    SLIDE_TYPE_PROMPTS,
    INTRO_PROMPT,
    MATH_EQUATION_RULES,
    SLIDE_PREPARER_SYSTEM_PROMPT,
    SLIDE_PREPARER_HUMAN_TEMPLATE,
    IMAGE_SEARCH_EXECUTION_PLAN_RULES,
)

from backend.workflows.slidegen_workflow.utils.helper import (
    format_tool_for_qwen,
    parse_tool_calls_json,
    QWEN_CHAT_TEMPLATE,
)
from backend.infrastructure.llm_providers.base import BaseLLMProvider

_tokenizer_cache = {}

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


def create_default_html(content_data) -> str:
    """Create default HTML when unable to get from LLM"""
    # Handle both dict and string formats
    if isinstance(content_data, dict):
        title = content_data.get('heading', 'Slide')
        content_text = content_data.get('text_content', 'Default slide content')
    else:
        content_text = content_data if content_data else "Default slide content"
        title = "Slide"
    
    lines = content_text.split('\n')
    if not title:
        title = lines[0] if lines else "Slide"
    content_html = '<br>'.join(lines[1:]) if len(lines) > 1 else content_text
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .slide {{ width: 800px; height: 600px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); padding: 40px; position: relative; }}
        .title {{ font-size: 32px; color: #2c3e50; margin-bottom: 30px; text-align: center; }}
        .content {{ font-size: 24px; line-height: 1.5; color: #34495e; }}
    </style>
</head>
<body>
    <div class="slide">
        <div class="title">{title}</div>
        <div class="content">{content_html}</div>
    </div>
</body>
</html>"""
    return html




def _build_tool_description_text(tool_schemas: list) -> str:
    """Build a structured section listing available layout tools and parameter constraints for the LLM."""
    lines = [
        "AVAILABLE LAYOUT TOOLS (YOU MUST SELECT EXACTLY ONE TOOL FROM THIS LIST):",
        "Below are the allowed layout tools for this slide. You MUST pick the single best matching tool from this list and strictly supply all required parameters:"
    ]
    for schema in tool_schemas:
        func = schema.get("function", {})
        name = func.get("name", "?")
        desc = func.get("description", "")
        params = func.get("parameters", {})
        properties = params.get("properties", {})
        required = params.get("required", [])
        
        lines.append(f"\n• Tool Name: `{name}`")
        lines.append(f"  Description: {desc}")
        
        param_desc_list = []
        image_param_names = []
        for prop_name, prop_spec in properties.items():
            prop_type = prop_spec.get("type", "any")
            is_req = " (REQUIRED)" if prop_name in required else ""
            
            # Detect image params using same logic as executor
            is_image = (
                "image_url" in prop_name.lower()
                or "image_path" in prop_name.lower()
                or prop_name.lower() in {"bg_image", "background_image"}
            )

            if prop_type == "array":
                item_spec = prop_spec.get("items", {})
                if item_spec.get("type") == "object":
                    item_props = list(item_spec.get("properties", {}).keys())
                    param_desc_list.append(f"`{prop_name}`: List[dict with keys: {item_props}]{is_req}")
                else:
                    item_type = item_spec.get("type", "string")
                    param_desc_list.append(f"`{prop_name}`: List[{item_type}]{is_req}")
            else:
                if is_image:
                    param_desc_list.append(f"`{prop_name}`: {prop_type}{is_req} ⚠️ IMAGE PARAM — requires a search_ddgs_images call")
                    image_param_names.append(prop_name)
                else:
                    param_desc_list.append(f"`{prop_name}`: {prop_type}{is_req}")
                
        if param_desc_list:
            lines.append(f"  Parameters: {', '.join(param_desc_list)}")

        # Add image search notice if this tool has image params
        if image_param_names:
            lines.append(
                f"  ⚠️ IMAGE SEARCH REQUIRED: This tool has {len(image_param_names)} image param(s): {image_param_names}. "
                f"Your tool plan MUST output the slide tool FIRST, then {len(image_param_names)} search_ddgs_images call(s) AFTER it."
            )
            
    return "\n".join(lines)


def _get_qwen_tokenizer(model_name: str):
    if model_name not in _tokenizer_cache:
        tok = AutoTokenizer.from_pretrained(model_name)
        tok.chat_template = QWEN_CHAT_TEMPLATE
        tok.pad_token = tok.eos_token
        _tokenizer_cache[model_name] = tok
    return _tokenizer_cache[model_name]


def _get_qwen_config(llm):
    """Extract (model_name, base_url, api_key) from any LLM wrapper or environment."""
    model_name = (
        getattr(llm, 'model_name', None) or 
        getattr(llm, 'model', None) or 
        os.environ.get("OPENAI_MODEL", "Qwen/Qwen3-8B")
    )
    base_url = (
        getattr(llm, 'openai_api_base', None) or 
        getattr(llm, 'base_url', None) or 
        os.environ.get("OPENAI_BASE_URL", None)
    )
    api_key = (
        getattr(llm, 'openai_api_key', None) or 
        getattr(llm, 'api_key', None) or 
        os.environ.get("NVIDIA_API_KEY") or 
        os.environ.get("OPENAI_API_KEY") or 
        'not-needed'
    )
    return model_name, base_url, api_key


def _check_is_qwen(llm) -> bool:
    """Helper to detect if the loaded LLM is a Qwen variant or NVIDIA API Qwen or a LocalPyTorchLLMProvider."""
    # BaseLLMProvider with model_type=qwen is always treated as Qwen path
    if isinstance(llm, BaseLLMProvider):
        return llm.model_type == "qwen"
    model_name = ""
    for attr in ["model", "model_name", "model_id"]:
        if hasattr(llm, attr):
            model_name = str(getattr(llm, attr)).lower()
            break
    if not model_name:
        model_name = os.environ.get("OPENAI_MODEL", "").lower()
    
    base_url = str(getattr(llm, 'base_url', '') or getattr(llm, 'openai_api_base', '') or os.environ.get("OPENAI_BASE_URL", "")).lower()
    return "qwen" in model_name or "nvidia" in base_url or "nvidia" in model_name

def generate_slide(state: State, config: RunnableConfig) -> State:
    """
    Node for slide generation: Prepares tools/instructions, then invokes the LLM.
    Supports separate execution paths for Gemini (structured tool binding) and Qwen (native JSON generation).
    """
    print("\n---------------- Executing Node: slide_generator (Merged) ----------------")
    start_time = time.time()
    
    # 1. Get resources from config
    configurable = config["configurable"]
    llm = configurable.get('llm')
    if not llm:
        raise ValueError("LLM instance not found in config.")
        
    tool_retriever = configurable.get('tool_retriever')
    all_tools_dict = configurable.get('tools_dict', TOOLS_DICT)
    planner_llm = configurable.get('planner_llm') or llm
    
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
    if state.get("candidate_tools"):
        # Remove search tool if present in candidate_tools cache to get original my_tools
        cached = [t for t in state["candidate_tools"] if getattr(t, 'name', '') != SEARCH_DDGS_TOOL.name]
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
                my_tools = retrieved_tools if retrieved_tools else all_tools_dict.get(tool_category, [])
            except Exception as e:
                print(f"⚠️ tool_retriever error ({e}), falling back to category tools for '{tool_category}'")
                my_tools = all_tools_dict.get(tool_category, [])
        else:
            my_tools = all_tools_dict.get(tool_category, [])
        
    if not my_tools:
        my_tools = all_tools_dict.get('CONTENT_TOOLS', [])
        
    print(f"  -> Prepared {len(my_tools)} tools: {[t.name for t in my_tools]}")
    
    # 4. Build per-slide-type system prompt for the API generator
    slide_type = current_plan.get('action', 'CONTENT_TOOLS')
    if slide_type == 'CONTENT_TOOLS':
        if 'highlight_color' in state:
            highlight_instruction = f"- MUST use this color: {state['highlight_color']} (maintain consistency!)"
        else:
            highlight_instruction = "- This is the FIRST content slide - choose ONE color from the list and use it consistently"
        generator_system_prompt = CONTENT_PROMPT.format(highlight_instruction=highlight_instruction)
        
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
        generator_system_prompt = TRANSITION_PROMPT.format(previous_transition_context=transition_context)
        
    else:
        generator_system_prompt = SLIDE_TYPE_PROMPTS.get(slide_type, INTRO_PROMPT)
        
    generator_system_prompt = MATH_EQUATION_RULES + "\n\n" + generator_system_prompt
    
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
    style_context_str = json.dumps(_extract_style_params(previous_slide_function_call), indent=2)
    
    # 7. Invoke Gemini (Planner LLM) to get design instruction for the next slide (Reuse cached instruction if available for retries)
    design_instruction = state.get("design_instruction")
    if design_instruction:
        print("  -> Reusing cached design instructions from state (retry attempt)")
    else:
        design_instruction = creative_thought
        if planner_llm:
            try:
                print("  -> Calling Gemini to prepare design instructions...")
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
                    print("     " + design_instruction.replace("\n", "\n     "))
            except Exception as e:
                print(f"⚠️ Gemini preparer failed, falling back to planner plan: {e}")
            
    # Assign prepared values. The image-search plan is produced by this same
    # generator invocation; no later LLM call is allowed to create search specs.
    system_prompt = (
        generator_system_prompt
        + "\n\n"
        + IMAGE_SEARCH_EXECUTION_PLAN_RULES
    )
    human_template = HUMAN_PROMPT_TEMPLATE
    generator_tools = [SEARCH_DDGS_TOOL, *my_tools]
            
    is_qwen = _check_is_qwen(llm)
    model_name, base_url, api_key = _get_qwen_config(llm)
    print(f"  -> Model Mode: {'QWEN / OPENAI API (' + str(model_name) + ' @ ' + str(base_url or 'Local') + ')' if is_qwen else 'GEMINI / API'}")
    content = ""
    
    # Format human prompt variables
    human_vars = {
        "slide_context_map": current_context_map,
        "previous_slide_function_call": style_context_str,
        "recent_tools": recent_tools_str,
        "slide_plan": json.dumps(current_plan, indent=2),
        "slide_content": current_text,
        "previous_function_call": json.dumps(previous_function_call, indent=2),
        "previous_evaluation": previous_evaluation,
        "slide_index": idx + 1,
        "length_slide_chunks": length_slide_chunks,
    }
    
    # A. QWEN LOCAL EXECUTION PATH (Native JSON tool call)
    if is_qwen:
        tool_schemas = [format_tool_for_qwen(t) for t in generator_tools]

        qwen_user_prompt = QWEN_GENERATOR_HUMAN_TEMPLATE.format(
            style_context=style_context_str,
            design_instruction=design_instruction,
            slide_content=current_text
        )

        prev_tool_to_show = previous_function_call
        if prev_tool_to_show.get("name") == "default_fallback" and state.get("last_valid_tool_call"):
            prev_tool_to_show = state["last_valid_tool_call"]

        if prev_tool_to_show and prev_tool_to_show != {} and prev_tool_to_show.get("name") != "default_fallback":
            qwen_user_prompt += f"\n\n[YOUR PREVIOUS TOOL CALL ATTEMPT]\n{json.dumps(prev_tool_to_show, indent=2)}"

        full_feedback = (previous_evaluation if previous_evaluation != "No evaluation yet." else "")
        if full_feedback.strip():
            qwen_user_prompt += f"\n\n[PREVIOUS EVALUATION / ERRORS TO CORRECT]\n{full_feedback.strip()}"

        # Format with apply_chat_template using QWEN_CHAT_TEMPLATE (matches training format)
        use_cot = state.get("use_cot", True)
        qwen_base_sys = QWEN_COT_GENERATOR_SYSTEM_PROMPT if use_cot else QWEN_GENERATOR_SYSTEM_PROMPT
        tool_desc_text = _build_tool_description_text(tool_schemas)
        full_qwen_system_prompt = (
            generator_system_prompt
            + "\n\n"
            + IMAGE_SEARCH_EXECUTION_PLAN_RULES
            + "\n\n"
            + qwen_base_sys
            + "\n\n"
            + tool_desc_text
        )
        messages = [
            {"role": "system", "content": full_qwen_system_prompt},
            {"role": "user", "content": qwen_user_prompt},
        ]
        model_name, base_url, api_key = _get_qwen_config(llm)

        # A. QWEN EXECUTION PATH (Local PyTorch / NVIDIA API / OpenAI-compatible API)
        if isinstance(llm, BaseLLMProvider):
            try:
                content = llm.generate_completion(
                    messages=messages,
                    tools=tool_schemas,
                    max_tokens=getattr(llm, 'max_tokens', None) or (COT_MAX_TOKENS if use_cot else 2000),
                    temperature=getattr(llm, 'temperature', 0.5) or 0.5,
                )
            except Exception as e:
                print(f"❌ BaseLLMProvider ({llm.provider_name}) generation failed: {e}")
                content = ""
        else:
            # Fallback cho LangChain ChatOpenAI object nguyên bản
            client = OpenAI(base_url=base_url, api_key=api_key)
            try:
                max_tokens_val = getattr(llm, 'max_tokens', None) or (COT_MAX_TOKENS if use_cot else 2000)
                resp = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=max_tokens_val,
                    temperature=getattr(llm, 'temperature', 0.5) or 0.5,
                )
                content = (resp.choices[0].message.content or "").strip()
            except Exception as api_err:
                print(f"⚠️ ChatCompletions API failed ({api_err}), attempting local raw completions fallback...")
                try:
                    tokenizer = _get_qwen_tokenizer(model_name)
                    prompt = tokenizer.apply_chat_template(messages, tools=tool_schemas, tokenize=False, add_generation_prompt=True)
                    resp = client.completions.create(
                        model=model_name,
                        prompt=prompt,
                        max_tokens=max_tokens_val,
                        temperature=getattr(llm, 'temperature', 0.5) or 0.5,
                        stop=["<|im_end|>"],
                    )
                    content = (resp.choices[0].text or "").strip()
                except Exception as fallback_err:
                    print(f"❌ Qwen generation failed: {fallback_err}")
                    content = ""
        
    # B. GEMINI/API EXECUTION PATH (LangChain tool binding / GeminiAPIProvider)
    else:
        gemini_user_prompt = HUMAN_PROMPT_TEMPLATE.format(
            design_instruction=design_instruction,
            **human_vars
        )
        messages = [
            {"role": "system", "content": generator_system_prompt},
            {"role": "user", "content": gemini_user_prompt}
        ]
        
        if isinstance(llm, BaseLLMProvider):
            content = llm.generate_completion(
                messages=messages,
                tools=[format_tool_for_qwen(t) for t in generator_tools] if getattr(llm, 'model_type', '') == 'qwen' else generator_tools,
                temperature=getattr(llm, 'temperature', 0.5) or 0.5,
            )
            response = None
        else:
            # Native LangChain LLM Fallback
            llm_with_tools = llm.bind_tools(generator_tools)
            response = llm_with_tools.invoke(messages)
        
    # 3. Parse JSON / Extract tool call
    tool_call_dict = None
    tool_plan = []

    if is_qwen or isinstance(llm, BaseLLMProvider):
        # Qwen path hoặc BaseLLMProvider: raw text completion / JSON format
        tool_plan = parse_tool_calls_json(content)
        state["raw_llm_response"] = content
    else:
        # Gemini path (LangChain response)
        state["raw_llm_response"] = getattr(response, "content", "") or str(response)
        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_plan = [
                {
                    "name": tc.get("name"),
                    "arguments": tc.get("args", {}),
                }
                for tc in response.tool_calls
            ]
            content = json.dumps({"tool_calls": tool_plan}, ensure_ascii=False)
        else:
            content = getattr(response, "content", "")
            tool_plan = parse_tool_calls_json(content)
            try:
                cleaned_text = content.strip()
                if "```json" in cleaned_text:
                    cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
                elif "```" in cleaned_text:
                    cleaned_text = cleaned_text.split("```")[1].split("```")[0].strip()

                parsed_json = json.loads(cleaned_text)
                if isinstance(parsed_json, list) and len(parsed_json) > 0:
                    parsed_json = parsed_json[0]

                if isinstance(parsed_json, dict) and "name" in parsed_json:
                    tool_call_dict = {
                        "name": parsed_json["name"],
                        "arguments": parsed_json.get("arguments") or parsed_json.get("args") or {}
                    }
            except Exception as parse_err:
                print(f"⚠️ Fallback JSON parsing failed: {parse_err}")
            
    for call in tool_plan:
        if call.get("name") != SEARCH_DDGS_TOOL.name:
            tool_call_dict = call
            break

    if not tool_call_dict:
        print("❌ You did NOT generate any function call. Setting default fallback.")
        tool_call_dict = {"name": "default_fallback", "arguments": {}}
        tool_plan = [tool_call_dict]
    else:
        # Save valid parsed tool call for retry memory
        state["last_valid_tool_call"] = tool_call_dict
        
    print(f"✅ Generated Tool Call: {tool_call_dict.get('name')}")
    state["current_tool_call"] = tool_call_dict
    state["current_tool_plan"] = tool_plan
    state["raw_llm_response"] = content
    
    # Save helper state variables for downstream nodes
    state["candidate_tools"] = generator_tools
    state["style_context_str"] = style_context_str
    state["design_instruction"] = design_instruction

    if slide_type == "TRANSITION_TOOLS":
        state["previous_transition_tool_call"] = tool_call_dict
    
    print(f"Time taken: {time.time() - start_time:.2f} seconds.")
    return state
