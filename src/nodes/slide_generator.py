# src/nodes/slide_generator.py

from src.graph.stage import State
from langchain_core.prompts import ChatPromptTemplate
from src.tools.tool_des import execute_tool
import json
from langchain_core.runnables import RunnableConfig # <-- 1. IMPORT
from src.utils.config import TOOL_RETRIEVER_TOP_K, SLIDE_GENERATION_MAX_RETRIES
import time

# === SLIDE TYPE SPECIFIC PROMPTS ===

INTRO_PROMPT = """
🎯 **INTRO SLIDE** - This is the TITLE SLIDE of the entire presentation!

**FONT SIZES (MANDATORY):**
* Title: 120-140px (HUGE - readable from back of room!)
* Subtitle: 50-60px
* If tool has title_size param → set to 120px minimum

**COLOR CONTRAST (CRITICAL - SLIDE WILL BE REJECTED IF UNREADABLE):**
🚨 TEXT MUST POP OUT FROM BACKGROUND - EXTREME CONTRAST REQUIRED! 🚨

* ONLY USE THESE SAFE COMBINATIONS:
  ✅ #FFFFFF (pure white) on #000000 (black)
  ✅ #FFFFFF (pure white) on #1a4b8c (dark blue)
  ✅ #FFFFFF (pure white) on #2c3e50 (dark navy)
  ✅ #000000 (pure black) on #FFFFFF (white)
  ✅ #000000 (pure black) on #F8F9FA (off-white)
  ✅ #1a1a1a (near black) on #ECF0F1 (light gray)

* ABSOLUTELY FORBIDDEN COMBINATIONS:
  ❌ #555555 on #333333 (gray on dark gray - INVISIBLE!)
  ❌ #CCCCCC on #FFFFFF (light gray on white - CAN'T READ!)
  ❌ #3498db on #5DADE2 (blue on light blue - SAME COLOR!)
  ❌ #444444 on #666666 (dark gray on gray - TOO SIMILAR!)
  ❌ #2c3e50 on #34495e (navy on navy - BLENDS IN!)
  ❌ ANY text color that looks similar to background

* MANDATORY RULE: 
  - Background DARK? → Text MUST be #FFFFFF (white)
  - Background LIGHT? → Text MUST be #000000 (black)
  - Background COLORED? → Text MUST be #FFFFFF (white)
  - NO EXCEPTIONS! When in doubt, use white on dark or black on light!

**IMAGE SELECTION:**
* Extract the MAIN TOPIC from content (AI, business, technology, etc.)
* Use: `https://picsum.photos/seed/TOPIC/1600/900` where TOPIC is the main subject
* Examples based on content:
  - AI/Technology → seed/technology/1600/900
  - Business/Strategy → seed/business/1600/900
  - Education/Learning → seed/education/1600/900
  - Nature/Environment → seed/nature/1600/900

**CONSISTENCY:**
* Review PREVIOUS SLIDE to match overall tone and style

**FORMATTING:** Use HTML tags for emphasis. Generate ONE function call only.
"""

TRANSITION_PROMPT = """
🎯 **TRANSITION SLIDE** - Section divider between major topics!

**FONT SIZES:**
* Main text: 70-90px (bold, centered)

**COLOR CONTRAST (CRITICAL - TRANSITION MUST BE HIGHLY VISIBLE):**
🚨 HUGE SECTION TITLE MUST BE READABLE FROM ACROSS THE ROOM! 🚨

* MANDATORY SAFE COMBINATIONS (PICK ONE):
  ✅ #FFFFFF (pure white) on #000000 (black)
  ✅ #FFFFFF (pure white) on #1a4b8c (dark blue)
  ✅ #FFFFFF (pure white) on #2c3e50 (dark navy)
  ✅ #000000 (pure black) on #FFFFFF (white)
  ✅ #000000 (pure black) on #F8F9FA (off-white)

* STRICTLY FORBIDDEN (WILL BE REJECTED):
  ❌ #555555 on #333333 (gray on gray - INVISIBLE!)
  ❌ #CCCCCC on #FFFFFF (too light - CAN'T READ!)
  ❌ #3498db on #5DADE2 (blue on blue - SAME COLOR!)
  ❌ #2c3e50 on #34495e (navy on navy - BLENDS!)
  ❌ Any colored text on colored background
  ❌ Any text within 5 shades of background

* SIMPLE RULE: White text on dark OR Black text on light - NOTHING ELSE!

**IMAGE SELECTION:**
* Extract the SECTION TOPIC from the heading (e.g., "Data Analysis" → seed/data/1600/900)
* Use: `https://picsum.photos/seed/SECTION_TOPIC/1600/900` where SECTION_TOPIC is the heading

**CONSISTENCY WITH PREVIOUS TRANSITION (CRITICAL):**
{previous_transition_context}

**CONTENT FORMATTING CONSISTENCY:**
* If previous transition used numbering (1., 2., 3.), continue the sequence
* If previous used bullet points, use bullet points
* If previous had no numbering, don't add numbering
* Match font sizes, colors, and text alignment EXACTLY
* Keep the same visual hierarchy and spacing

**FORMATTING:** Bold, centered text. Generate ONE function call only.
"""

CONTENT_PROMPT = """
🎯 **CONTENT SLIDE** - Main informational slide with details.

**FONT SIZES:**
* Title: 48-56px
* Body text: 32-38px
* Bullets: use • or numbered lists

**COLOR CONTRAST (CRITICAL - READABILITY IS PRIORITY #1):**
🚨 TEXT MUST BE READABLE FROM 5 METERS AWAY - NO EXCEPTIONS! 🚨

* MANDATORY TEXT COLOR RULES (FOLLOW EXACTLY):
  1. If background is DARK (black, navy, dark blue, dark gray):
     → Main text MUST be #FFFFFF (pure white)
     → Secondary text MUST be #E0E0E0 or lighter
     
  2. If background is LIGHT (white, light gray, light blue, cream):
     → Main text MUST be #000000 or #1a1a1a (pure black/near black)
     → Secondary text MUST be #333333 or darker
     
  3. If background is COLORED (blue, purple, green, etc.):
     → ALWAYS use #FFFFFF (white) text
     → NEVER use colored text on colored background

* STRICT CONTRAST REQUIREMENTS:
  ✅ CORRECT EXAMPLES:
     - #FFFFFF text on #1a1a1a background
     - #000000 text on #FFFFFF background
     - #FFFFFF text on #3498db background
     - #000000 text on #F8F9FA background
     
  ❌ ABSOLUTELY FORBIDDEN (WILL BE REJECTED):
     - #555555 text on #333333 background (gray on gray)
     - #CCCCCC text on #FFFFFF background (too light)
     - #444444 text on #666666 background (similar shades)
     - #3498db text on #5DADE2 background (blue on blue)
     - #e74c3c text on #EC7063 background (red on red)
     - ANY text color within 5 shades of background color

* HIGHLIGHT COLOR RULES:
  - On white/light bg: Use ONLY #e74c3c (red), #3498db (blue), #f39c12 (orange), #9b59b6 (purple)
  - On dark bg: Use ONLY #FFFFFF with bold weight, or very bright colors (#00FF00, #FFFF00)
  - NEVER use pastel, muted, or similar tones to background

**KEY PHRASE HIGHLIGHTING (MANDATORY):**
* Identify 2-4 KEY PHRASES in the content (important terms, concepts)
* Wrap them with: `<span style="color: COLOR; font-weight: bold;">phrase</span>`

* HIGHLIGHT COLOR RULES (CRITICAL):
  {highlight_instruction}
  
  ON WHITE/LIGHT BACKGROUNDS - Use these BRIGHT colors:
  ✅ #e74c3c (bright red)
  ✅ #3498db (bright blue) 
  ✅ #f39c12 (bright orange)
  ✅ #9b59b6 (bright purple)
  ✅ #16a085 (teal)
  
  ON DARK BACKGROUNDS - Use white with bold:
  ✅ #FFFFFF (white) + font-weight: bold
  ✅ #FFD700 (gold) for emphasis
  ✅ #00FF00 (bright green) for success
  
  NEVER USE on any background:
  ❌ Pastel colors (#E8DAEF, #D5F4E6, #FAD7A0)
  ❌ Light colors on light bg (#CCCCCC on #FFFFFF)
  ❌ Dark colors on dark bg (#333333 on #000000)
  ❌ Similar shade to background

* Example: "AI can help with <span style=\"color: #e74c3c; font-weight: bold;\">automation</span>"

**IMAGE SELECTION:**
* Extract KEY CONCEPT from slide content
* Use: `https://picsum.photos/seed/KEY_CONCEPT/1600/900` where KEY_CONCEPT is the main concept
* Be specific: "machine learning" → seed/machinelearning/1600/900

**CONSISTENCY:**
* Match tone, pacing, and visual style with PREVIOUS SLIDE
* Keep the same level of detail density

**FORMATTING:** Use HTML tags, bullet points. Generate ONE function call only.
"""

THANK_YOU_PROMPT = """
🎯 **THANK YOU SLIDE** - Final closing slide!

**FONT SIZES:**
* Main text: 70-80px (centered)
* Simple and professional

**COLOR CONTRAST (CRITICAL - FINAL IMPRESSION MUST BE CLEAR):**
⚠️ This is the last slide - make it READABLE! ⚠️

* SAFE CHOICES:
  ✅ #FFFFFF on #2c3e50 (white on navy)
  ✅ #000000 on #FFFFFF (black on white)
  ✅ #FFFFFF on #000000 (white on black)

* DO NOT USE:
  ❌ Colored text on colored backgrounds
  ❌ Gray tones on gray tones
  ❌ Anything that's not obviously high contrast

**IMAGE SELECTION:**
* Use generic positive theme: seed/success/1600/900 or seed/celebration/1600/900
* Or use gradient: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`

**FORMATTING:** Centered, clean design. Generate ONE function call only.
"""

TEAM_PROMPT = """
🎯 **TEAM SLIDE** - Team introduction or contact info.

**FONT SIZES:**
* Names: 40-48px
* Roles: 28-32px

**COLOR CONTRAST (MANDATORY - NAMES MUST BE READABLE):**
⚠️ People's names deserve CLEAR visibility! ⚠️

* USE ONLY:
  ✅ #000000 (black) or #2c3e50 (navy) on #FFFFFF (white)
  ✅ #FFFFFF (white) on #2c3e50 (navy) or #000000 (black)

* NEVER:
  ❌ Medium colors on medium colors
  ❌ Subtle color differences

**IMAGE SELECTION:**
* Use: seed/team/1600/900 or seed/people/1600/900

**FORMATTING:** Clean layout with emphasis. Generate ONE function call only.
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
**CONTEXT:**
{slide_context_map}

**PREVIOUS SLIDE (maintain consistency with this!):**
{previous_slide_function_call}

**PLAN:**
{slide_plan}

**CONTENT (Slide {slide_index}/{length_slide_chunks}):**
{slide_content}

**RETRY (if any):**
{previous_function_call}
{previous_evaluation}
"""

def create_default_html(content_text: str) -> str:
    """Create default HTML when unable to get from LLM"""
    if not content_text:
        content_text = "Default slide content"
    
    lines = content_text.split('\n')
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
    
    for attempt in range(1, SLIDE_GENERATION_MAX_RETRIES + 1):
        print(f"  -> Attempt {attempt}/{SLIDE_GENERATION_MAX_RETRIES} to generate tool call...")
        
        response = slide_generator_runnable.invoke({
            "slide_context_map": current_context_map,
            "previous_slide_function_call": json.dumps(previous_slide_function_call, indent=2),
            "slide_plan": json.dumps(current_plan, indent=2),
            "slide_content": current_text,
            "previous_function_call": json.dumps(previous_function_call, indent=2),
            "previous_evaluation": previous_evaluation,
            "slide_index": idx + 1,
            "length_slide_chunks": length_slide_chunks
        })
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_call = response.tool_calls[0]
            tool_call_dict = {"name": tool_call["name"], "arguments": tool_call["args"]}
            
            html_content = execute_tool(tool_call_dict)
            if html_content:
                state['current_tool_call'] = tool_call_dict
                state['current_html_content'] = html_content
                
                # Extract and save highlight color if this is the first CONTENT slide
                if slide_type == 'CONTENT_TOOLS' and 'highlight_color' not in state:
                    # Try to extract color from generated HTML
                    import re
                    color_match = re.search(r'color:\s*(#[0-9a-fA-F]{6})', html_content)
                    if color_match:
                        extracted_color = color_match.group(1)
                        state['highlight_color'] = extracted_color
                        print(f"  -> ✅ Extracted and saved highlight color: {extracted_color}")
                    else:
                        print(f"  -> ⚠️ No color found in HTML, will let next slide choose")
                
                # Save transition tool call for future transitions
                if slide_type == 'TRANSITION_TOOLS':
                    state['previous_transition_tool_call'] = tool_call_dict
                    print(f"  -> 🔄 Saved transition tool for consistency: {tool_call_dict['name']}")
                
                print(f"  -> Successfully generated HTML with tool: {tool_call_dict['name']}")
                end_time = time.time()
                print(f"  -> Slide generation took {end_time - start_time:.2f} seconds.")
                return state
            

        print("  -> Failed to get a valid tool call or execute it. Retrying...")

    print("ERROR: All attempts to generate slide failed. Creating a default HTML slide.")
    state['current_tool_call'] = {"name": "default_html", "arguments": {"content": current_text}}
    state['current_html_content'] = create_default_html(current_text)
    return state