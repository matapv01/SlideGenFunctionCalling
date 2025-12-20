# src/nodes/slide_generator.py

from src.graph.stage import State
from langchain_core.prompts import ChatPromptTemplate
from src.tools.tool_des import execute_tool
import json
from langchain_core.runnables import RunnableConfig
from src.utils.config import TOOL_RETRIEVER_TOP_K, SLIDE_GENERATION_MAX_RETRIES
import time

# === SLIDE TYPE SPECIFIC PROMPTS ===

INTRO_PROMPT = """
🎯 INTRO SLIDE - Title slide, first impression!

**CRITICAL: TEXT COLOR MUST BE EASY TO READ!**
⚠️ Dark background (#000, #1a1a1a, #2c3e50) → Use #FFFFFF or very light text
⚠️ Light background (#FFF, #f8f9fa, #ecf0f1) → Use #000000 or very dark text
❌ NEVER: Gray on gray, #555 on #333, #ddd on #fff, colored text on colored bg

**RULES:**
1. CONTENT: Short title + brief subtitle. No fluff!
2. HTML: Use <br> or <p> for line breaks ONLY
   ❌ NO lists, NO <b>, <i>, <em>, <strong>, NO style attributes
3. IMAGE: Use https://picsum.photos/seed/[NUMBER]/1600/900 where NUMBER is 100-999
   ⚠️ MUST use NUMERIC seed (e.g., seed/347/1600/900) NOT text! Text seeds cause 404s!
4. MATCH previous slide's style

Generate clean, HIGHLY READABLE function call.
"""

TRANSITION_PROMPT = """
🎯 TRANSITION SLIDE - Section divider!

**CRITICAL: TEXT COLOR MUST BE INSTANTLY READABLE!**
⚠️ Dark background → #FFFFFF (white) text preferred
⚠️ Light background → #000000 (black) text preferred
❌ NEVER: Medium colors, gray tones, similar shades

**RULES:**
1. CONTENT: 3-6 words ONLY
2. HTML: Use <br> or <p> for line breaks ONLY
   ❌ NO lists, NO <b>, <i>, <em>, <strong>, NO style attributes
3. IMAGE: Use https://picsum.photos/seed/[NUMBER]/1600/900 where NUMBER is 100-999
   ⚠️ MUST use NUMERIC seed (e.g., seed/523/1600/900) NOT text! Text seeds cause 404s!
4. CONSISTENCY: {previous_transition_context}

Generate BOLD, ULTRA-VISIBLE function call.
"""

CONTENT_PROMPT = """
🎯 CONTENT SLIDE - Main information!

**CRITICAL: TEXT COLOR MUST BE EASY TO READ VS BACKGROUND!**
⚠️ Dark background (#000, #1a1a1a, #2c3e50) → #FFFFFF or very light text
⚠️ Light background (#FFF, #f8f9fa, #ecf0f1) → #000000 or very dark text
❌ FORBIDDEN: Gray on gray, #555 on #333, #ccc on #fff, colored text on colored bg

**RULES:**
1. HIGHLIGHT 2-3 key phrases ONLY:
   {highlight_instruction}
   Example: "AI improves <span style="font-weight: bold;">efficiency</span> by 80%"
   ⚠️ ONLY use <span style="font-weight:bold"> for KEY PHRASES!
2. HTML: Use <br> or <p> for line breaks ONLY
   ❌ NO lists (<ul>, <ol>, <li>), NO <b>, <i>, <em>, <strong>, <u>!
   ❌ NO style attributes except for key phrase highlights!
3. CONTENT: 
   - **MAXIMUM CONCISENESS**: Use telegraphic style (drop "the", "a", "is"). Shortest possible wording.
   - **SLIDE FORMAT**: Use brief bullet points or keywords. NO long sentences.
   - **KEY INFO**: Keep only the core message, numbers, and technical terms.
4. IMAGE: Use https://picsum.photos/seed/[NUMBER]/1600/900 where [NUMBER] is an integer and in the range of 100-999
   ⚠️ MUST use NUMERIC seed (e.g., seed/789/1600/900) NOT text! Text seeds cause 404s!

Generate READABLE, professional function call.
"""

#    Example: "AI improves <span style="color: #e74c3c; font-weight: bold;">efficiency</span> by 80%"
#    ⚠️ ONLY use <span style="color:... font-weight:bold"> for KEY PHRASES!

THANK_YOU_PROMPT = """
🎯 THANK YOU SLIDE - Final closing!

**CRITICAL: TEXT MUST BE CRYSTAL CLEAR!**
⚠️ Dark background → #FFFFFF (white) text
⚠️ Light background → #000000 (black) text
❌ NO colored text, NO gray tones, NO low contrast

**RULES:**
1. CONTENT: "Thank You" ONLY
2. IMAGE: seed/success/1600/900 or gradient

Generate simple, HIGHLY VISIBLE function call.
"""

TEAM_PROMPT = """
🎯 TEAM SLIDE - Team intro!

**CRITICAL: NAMES MUST BE EASY TO READ!**
⚠️ Dark background → #FFFFFF (white) text for names
⚠️ Light background → #000000 (black) text for names
❌ NEVER: Gray tones, colored text, low contrast

**RULES:**
1. CONTENT: Name + role only
2. HTML: Use <br> or <p> for line breaks ONLY
   ❌ NO lists, NO <b>, <i>, <em>, <strong>, NO style attributes!
3. IMAGE: Use https://picsum.photos/seed/[NUMBER]/1600/900 where NUMBER is 100-999
   ⚠️ MUST use NUMERIC seed (e.g., seed/456/1600/900) NOT text! Text seeds cause 404s!

Generate professional, READABLE function call.
"""

# Map slide types to their specific prompts
SLIDE_TYPE_PROMPTS = {
    'INTRO_TOOLS': INTRO_PROMPT,
    'TRANSITION_TOOLS': TRANSITION_PROMPT,
    'CONTENT_TOOLS': CONTENT_PROMPT,
    'THANK_YOU_TOOLS': THANK_YOU_PROMPT,
    'TEAM_TOOLS': TEAM_PROMPT,
}

HUMAN_PROMPT_TEMPLATE = """
CONTEXT: {slide_context_map}

PREVIOUS SLIDE (match this style!): {previous_slide_function_call}

DESIGN PLAN: {slide_plan}

SLIDE {slide_index}/{length_slide_chunks} CONTENT:
{slide_content}

YOUR PREVIOUS ATTEMPT:
{previous_function_call}

EVALUATION OF PREVIOUS ATTEMPT:
{previous_evaluation}
"""

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
    content = '<br>'.join(lines[1:]) if len(lines) > 1 else content_text
    
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
        <div class="content">{content}</div>
    </div>
</body>
</html>"""
    return html


def generate_slide(state: State, config: RunnableConfig) -> State: # <-- 2. ADD CONFIG
    """
    Node for slide generation: Uses an LLM to generate a tool call based on a plan.
    """
    print("\n---------------- Executing Node: slide_generator ----------------")
    start_time = time.time()
    # --- 3. GET RESOURCES FROM CONFIG ---
    configurable = config["configurable"]
    llm = configurable.get('llm')
    tool_retriever = configurable.get('tool_retriever') # <-- Get the retriever
    all_tools_dict = configurable.get('tools_dict', {}) # Get the full dict as a fallback
    if not llm:
        raise ValueError("LLM instance not found in config.")

    # --- GET DYNAMIC DATA FROM STATE ---
    idx = state['current_slide_index']
    current_text = state.get("current_slide_text", "")
    previous_function_call = state.get('current_tool_call', {})
    previous_evaluation = state.get('vlm_feedback', "No evaluation yet.")
    length_slide_chunks = state.get('length_slide_chunks', 0)
    previous_slide_function_call = state.get('previous_accepted_tool_call', {})
    slide_plans = state.get('slide_plans', [])
    slide_context_maps = state.get('slide_context_maps', [])

    print(f"--- Generating slide {idx + 1}/{length_slide_chunks} ---")
    
    if not current_text:
        print("WARNING: No slide text provided. Using default.")
        current_text = "Default slide content"
    
    if not slide_plans or idx >= len(slide_plans):
        raise ValueError(f"Missing slide plan for slide index {idx}.")
        
    if not slide_context_maps or idx >= len(slide_context_maps):
        raise ValueError(f"Missing slide context map for slide index {idx}.")

    # Get the plan for the current slide
    current_plan = slide_plans[idx]
    current_context_map = slide_context_maps[idx]
    tool_category = current_plan.get('action', 'CONTENT_TOOLS')
    creative_thought = current_plan.get('thought', '') # This is our query!

    print(f"  -> Using plan with action: '{tool_category}'")
    print(f"  -> Creative thought (query): '{creative_thought[:200]}...'")

    # SPECIAL HANDLING FOR TRANSITION SLIDES: Reuse the same tool for consistency
    if tool_category == 'TRANSITION_TOOLS' and 'previous_transition_tool_call' in state:
        # Get the tool that was used for the previous transition
        prev_transition_tool_name = state['previous_transition_tool_call'].get('name')
        if prev_transition_tool_name:
            # Find the exact same tool from the dict
            all_transition_tools = all_tools_dict.get('TRANSITION_TOOLS', [])
            matching_tool = next((t for t in all_transition_tools if t.name == prev_transition_tool_name), None)
            
            if matching_tool:
                my_tools = [matching_tool]  # Use ONLY this tool
                print(f"  -> 🔄 REUSING previous transition tool for consistency: {prev_transition_tool_name}")
            else:
                print(f"  -> ⚠️ Previous transition tool '{prev_transition_tool_name}' not found. Falling back to retrieval.")
                retrieved_tools = tool_retriever.get_relevant_tools(
                    category=tool_category,
                    query=creative_thought,
                    top_k=TOOL_RETRIEVER_TOP_K
                )
                my_tools = retrieved_tools if retrieved_tools else all_tools_dict.get(tool_category, [])
        else:
            # No tool name found, use retrieval
            retrieved_tools = tool_retriever.get_relevant_tools(
                category=tool_category,
                query=creative_thought,
                top_k=TOOL_RETRIEVER_TOP_K
            )
            my_tools = retrieved_tools if retrieved_tools else all_tools_dict.get(tool_category, [])
    else:
        # Normal retrieval for non-transition slides or first transition
        retrieved_tools = tool_retriever.get_relevant_tools(
            category=tool_category,
            query=creative_thought,
            top_k=TOOL_RETRIEVER_TOP_K
        )
        
        if not retrieved_tools:
            print(f"  -> WARNING: Could not retrieve any tools. Falling back to all tools in category '{tool_category}'.")
            my_tools = all_tools_dict.get(tool_category, [])
        else:
            my_tools = retrieved_tools
            print(f"  -> Retrieved {len(my_tools)} relevant tools: {[tool.name for tool in my_tools]}")

    if not my_tools:
         # Final fallback if category is empty
        print(f"  -> CRITICAL WARNING: No tools found for category '{tool_category}'. Using default content tools.")
        my_tools = all_tools_dict.get('CONTENT_TOOLS', [])

    llm_with_tools = llm.bind_tools(my_tools)

    # Get slide type and corresponding prompt
    slide_type = current_plan.get('action', 'CONTENT_TOOLS')
    
    # Prepare system prompt based on slide type
    if slide_type == 'CONTENT_TOOLS':
        # Handle highlight color for content slides
        if 'highlight_color' in state:
            # Already have a color - instruct to use it
            highlight_instruction = f"- MUST use this color: {state['highlight_color']} (maintain consistency!)"
        else:
            # First content slide - let LLM choose
            highlight_instruction = "- This is the FIRST content slide - choose ONE color from the list and use it consistently"
        
        system_prompt = CONTENT_PROMPT.format(highlight_instruction=highlight_instruction)
    
    elif slide_type == 'TRANSITION_TOOLS':
        # Handle previous transition context
        previous_transition = state.get('previous_transition_tool_call', {})
        if previous_transition:
            prev_tool_name = previous_transition.get('name', 'unknown')
            prev_args = previous_transition.get('arguments', {})
            
            # Format arguments as readable text (avoiding JSON braces that confuse LangChain)
            args_text = "\n".join([f"    - {key}: {value}" for key, value in prev_args.items()])
            
            # Extract key styling info from previous transition
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
        system_prompt = SLIDE_TYPE_PROMPTS.get(slide_type, CONTENT_PROMPT)
    
    slidegen_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", HUMAN_PROMPT_TEMPLATE)
    ])

    slide_generator_runnable = slidegen_prompt | llm_with_tools
    
    retry_feedback = ""

    MAX_REMAKE = 3

    for attempt in range(1, MAX_REMAKE + 1):
        print(f"🔁 Function-call generation attempt {attempt}/{MAX_REMAKE}")

        print("-" * 100)
        print("Current slide content:")
        print(current_text)
        print("-" * 100)

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

        # ❌ 1. No tool call
        if not hasattr(response, "tool_calls") or not response.tool_calls:
            error_msg = "You did NOT generate any function call."
            print(f"❌ {error_msg}")
            retry_feedback += f"\n❌ PREVIOUS ERROR: {error_msg}"
            continue

        tool_call = response.tool_calls[0]
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})

        tool_lookup = {t.name: t for t in my_tools}

        # ❌ 2. Tool not callable
        if tool_name not in tool_lookup:
            error_msg = f"Tool '{tool_name}' is NOT AVAILABLE. Valid tools are: {list(tool_lookup.keys())}"
            print(f"❌ {error_msg}")
            retry_feedback += f"\n❌ PREVIOUS ERROR: {error_msg}"
            continue

        tool_call_dict = {
            "name": tool_name,
            "arguments": tool_args
        }

        # ❌ 3. Execution failure
        try:
            html_content = execute_tool(tool_call_dict)
        except Exception as e:
            error_msg = f"Tool '{tool_name}' CRASHED during execution: {e}"
            print(f"❌ {error_msg}")
            retry_feedback += f"\n❌ PREVIOUS ERROR: {error_msg}"
            continue

        # ❌ 4. Empty output
        if not html_content:
            error_msg = f"Tool '{tool_name}' returned EMPTY output."
            print(f"❌ {error_msg}")
            retry_feedback += f"\n❌ PREVIOUS ERROR: {error_msg}"
            continue

        # ✅ SUCCESS
        print(f"✅ Tool '{tool_name}' executed successfully")

        state["current_tool_call"] = tool_call_dict
        state["current_html_content"] = html_content

        if slide_type == "TRANSITION_TOOLS":
            state["previous_transition_tool_call"] = tool_call_dict

        return state

    # ❌ ALL ATTEMPTS FAILED - Return default HTML to avoid crashing the graph
    print(f"❌ ALL {MAX_REMAKE} attempts failed for slide {idx + 1}. Generating default slide.")
    default_html = create_default_html(current_text)
    state["current_html_content"] = default_html
    state["current_tool_call"] = {"name": "default_fallback", "arguments": {}}
    
    return state