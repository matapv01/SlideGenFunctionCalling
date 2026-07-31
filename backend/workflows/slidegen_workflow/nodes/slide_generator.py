# File: backend/workflows/slidegen_workflow/nodes/slide_generator.py

import json
import time
from openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from transformers import AutoTokenizer

from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.tools.tool_des import execute_tool_plan, TOOLS_DICT
from backend.workflows.slidegen_workflow.tools.ddgs_tool import SEARCH_DDGS_TOOL
from backend.config import MAX_REMAKE, TOOL_RETRIEVER_TOP_K
from backend.workflows.slidegen_workflow.utils.prompts import (
    QWEN_GENERATOR_SYSTEM_PROMPT,
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




def _get_qwen_tokenizer(model_name: str):
    if model_name not in _tokenizer_cache:
        tok = AutoTokenizer.from_pretrained(model_name)
        tok.chat_template = QWEN_CHAT_TEMPLATE
        tok.pad_token = tok.eos_token
        _tokenizer_cache[model_name] = tok
    return _tokenizer_cache[model_name]


def _get_qwen_config(llm):
    """Extract (model_name, base_url) from any LLM wrapper."""
    if hasattr(llm, 'model_name'):
        return llm.model_name, getattr(llm, 'openai_api_base', None)
    if hasattr(llm, 'model'):
        return llm.model, getattr(llm, 'base_url', None)
    return 'Qwen/Qwen3-8B', None

def _check_is_qwen(llm) -> bool:
    """Helper to detect if the loaded LLM is a Qwen variant."""
    model_name = ""
    for attr in ["model", "model_name", "model_id"]:
        if hasattr(llm, attr):
            model_name = str(getattr(llm, attr)).lower()
            break
    return "qwen" in model_name

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
    current_text = state.get("current_slide_text", "")
    current_plan = state.get('current_slide_plan')
    current_context_map = state.get('current_slide_context_map')
    previous_evaluation = state.get('vlm_feedback', "No evaluation yet.")
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
    qwen_system_prompt = (
        QWEN_GENERATOR_SYSTEM_PROMPT
        + "\n\n"
        + generator_system_prompt
        + "\n\n"
        + IMAGE_SEARCH_EXECUTION_PLAN_RULES
    )
    human_template = HUMAN_PROMPT_TEMPLATE
    generator_tools = [SEARCH_DDGS_TOOL, *my_tools]
            
    is_qwen = _check_is_qwen(llm)
    print(f"  -> Model Mode: {'LOCAL QWEN' if is_qwen else 'GEMINI / API'}")
    
    retry_feedback = ""
    
    for attempt in range(1, MAX_REMAKE + 1):
        print(f"🔁 Slide generation attempt {attempt}/{MAX_REMAKE}")
        
        # Format human prompt variables
        human_vars = {
            "slide_context_map": current_context_map,
            "previous_slide_function_call": style_context_str,
            "recent_tools": recent_tools_str,
            "slide_plan": json.dumps(current_plan, indent=2),
            "slide_content": current_text,
            "previous_function_call": json.dumps(previous_function_call, indent=2),
            "previous_evaluation": previous_evaluation + retry_feedback,
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

            if retry_feedback:
                qwen_user_prompt += f"\n\n[PREVIOUS ERROR TO CORRECT]\n{retry_feedback}"

            # Format with apply_chat_template using QWEN_CHAT_TEMPLATE (matches training format)
            messages = [
                {"role": "system", "content": qwen_system_prompt},
                {"role": "user", "content": qwen_user_prompt},
            ]
            model_name, base_url = _get_qwen_config(llm)
            tokenizer = _get_qwen_tokenizer(model_name)
            prompt = tokenizer.apply_chat_template(messages, tools=tool_schemas, tokenize=False, add_generation_prompt=True)

            # Call Qwen via raw completions endpoint (avoids server-side template override)
            client = OpenAI(base_url=base_url, api_key=getattr(llm, 'openai_api_key', 'not-needed'))
            resp = client.completions.create(
                model=model_name,
                prompt=prompt,
                max_tokens=max(getattr(llm, 'max_tokens', 1024) or 1024, 1536),
                temperature=getattr(llm, 'temperature', 0.5) or 0.5,
                stop=["<|im_end|>"],
            )
            content = (resp.choices[0].text or "").strip()
            
        # B. GEMINI/API EXECUTION PATH (LangChain tool binding)
        else:
            gemini_vars = {**human_vars, "design_instruction": design_instruction}
            llm_with_tools = llm.bind_tools(generator_tools)
            slidegen_prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", human_template)
            ])
            slide_generator_runnable = slidegen_prompt | llm_with_tools
            response = slide_generator_runnable.invoke(gemini_vars)
            
        # 3. Parse the complete ordered plan: Search 1..N, then HTML tool.
        tool_calls = []

        if is_qwen:
            # Qwen path: raw text from completions endpoint
            tool_calls = parse_tool_calls_json(content)
        else:
            # Gemini path: structured tool calls
            if hasattr(response, "tool_calls") and response.tool_calls:
                tool_calls = [
                    {
                        "name": tc.get("name"),
                        "arguments": tc.get("args", {}),
                    }
                    for tc in response.tool_calls
                ]
            else:
                content = getattr(response, "content", "")
                tool_calls = parse_tool_calls_json(content)

        if not tool_calls:
            error_msg = "You did NOT generate an ordered tool-call plan."
            print(f"❌ {error_msg}")
            retry_feedback += f"\n❌ PREVIOUS ERROR: {error_msg}"
            continue

        print(
            f"\n🤖 [GENERATOR OUTPUT] Slide {idx + 1} — {len(tool_calls)} tool call(s):\n"
            + json.dumps(tool_calls, indent=2, ensure_ascii=False)
        )

        html_tool_call = tool_calls[0]
        tool_name = html_tool_call["name"]
        tool_lookup = {t.name: t for t in my_tools}
        
        # Validation checks
        if tool_name not in tool_lookup:
            error_msg = f"Tool '{tool_name}' is NOT AVAILABLE. Valid tools are: {list(tool_lookup.keys())}"
            print(f"❌ {error_msg}")
            retry_feedback += f"\n❌ PREVIOUS ERROR: {error_msg}"
            continue
            
        try:
            # Execute Search 1..N, rule-map their URLs, then render HTML.
            html_content, final_tool_call, search_history = execute_tool_plan(
                tool_calls,
                tool_lookup=tool_lookup,
            )
        except Exception as e:
            error_msg = f"Tool plan for '{tool_name}' is invalid or crashed: {e}"
            print(f"❌ {error_msg}")
            retry_feedback += f"\n❌ PREVIOUS ERROR: {error_msg}"
            continue
            
        if not html_content:
            error_msg = f"Tool '{tool_name}' returned EMPTY output."
            print(f"❌ {error_msg}")
            retry_feedback += f"\n❌ PREVIOUS ERROR: {error_msg}"
            continue
            
        # Success
        original_html_call = tool_calls[0]   # bản gốc từ LLM (image_url = "") — HTML tool FIRST
        search_calls = tool_calls[1:]        # search_ddgs_images calls từ LLM — AFTER

        state["current_tool_plan"] = tool_calls
        state["current_search_history"] = search_history
        state["current_tool_call"] = original_html_call
        state["current_html_content"] = html_content

        # Lưu từng search call thành key riêng: current_image_tool_call_1, _2, ...
        for _i, _call in enumerate(search_calls, start=1):
            state[f"current_image_tool_call_{_i}"] = _call
        
        # Record tool usage for temporal decay tracking
        tool_retriever.record_tool_usage(
            category=tool_category,
            tool_name=tool_name,
            slide_index=idx
        )

        if slide_type == "TRANSITION_TOOLS":
            state["previous_transition_tool_call"] = final_tool_call
        
        # Save things that used to be saved by slide_preparer to state, just in case they are used downstream
        state["candidate_tools"] = my_tools
        state["style_context_str"] = style_context_str
        state["design_instruction"] = design_instruction
        
        break
        
    else:
        # ❌ ALL ATTEMPTS FAILED - Return default HTML to avoid crashing the graph
        print(f"❌ ALL {MAX_REMAKE} attempts failed for slide {idx + 1}. Generating default slide.")
        default_html = create_default_html(current_text)
        state["current_html_content"] = default_html
        state["current_tool_call"] = {"name": "default_fallback", "arguments": {}}
    
    print(f"Time taken: {time.time() - start_time:.2f} seconds.")
    return state
