# src/nodes/slide_generator.py

from src.graph.stage import State
from langchain_core.prompts import ChatPromptTemplate
from src.tools.tool_des import execute_tool
import json
from langchain_core.runnables import RunnableConfig # <-- 1. IMPORT
import time

SLIDEGEN_SYSTEM_PROMPT = """
# YOUR MISSION: Generate a single function call to create an excellent slide based on the provided content AND the creative plan.
# Your primary goal is to accurately translate the creative plan and content into a specific, well-parameterized function call.
# If you receive evaluation feedback, your #1 priority is to fix the mistakes from your last attempt by adjusting the function call parameters.

**INSTRUCTIONS FOR FUNCTION CALL GENERATION:**

1.  **Consult the Outline:** You will receive a `PRESENTATION OUTLINE` showing where the current slide fits. Use this to ensure your slide's tone and content logically connect with the rest of the presentation.  
    – **The current slide MUST be consistent with the slide immediately before it**, including tone, structure, and narrative flow.

2.  **Understand the Plan:** You will be given a `creative_plan` containing a `thought` (design direction) and an `action` (the required tool category). The tools available to you are limited to the category specified in the `action`.

3.  **Analyze the Content:** You are given the raw `slide_content`. All information from this content must be preserved and represented in the slide.

4.  **Select the Best Function:** From the available tools (defined by the plan's `action`), choose the single best function that matches the `thought` and the structure of the `slide_content`.

5.  **Populate Parameters Thoughtfully:**
    * Synthesize the `slide_content` into concise bullet points, titles, and descriptions suitable for a presentation slide. Do not copy raw text directly.
    * Use the `thought` from the creative plan to guide your choices for colors, titles, and other visual parameters.
    * Ensure all text arguments are in the correct language of the presentation.

6.  **Handle Retries:**
    * If `previous_evaluation` feedback exists, you MUST address the critique.
    * Prioritize adjusting the parameters of your `previous_function_call` to fix the noted issues. Do not change the function/tool unless the feedback explicitly states the chosen tool was fundamentally wrong.

7.  **HTML Formatting:** Use HTML tags like `<b>`, `<i>`, and `<span style='color:...'>` within text parameters to add emphasis and visual interest, as guided by the content's importance.

**Output Requirement:**
- Return exactly one syntactically correct function call and nothing else.
"""

HUMAN_PROMPT_TEMPLATE = """
---
**CONTEXT & PLAN**

*   **PRESENTATION OUTLINE (YOU ARE HERE):**
    {slide_context_map}

*   **Previous Accepted Slide (for style reference):**
    {previous_slide_function_call}

*   **Creative Plan for THIS Slide (Follow this!):**
    {slide_plan}

*   **Slide Content (Raw text to be used):**
    (Slide {slide_index}/{length_slide_chunks})
    {slide_content}

---
**RETRY INFORMATION (if applicable)**

*   **Your Last Attempt (The function call you must fix):**
    {previous_function_call}

*   **Feedback on Last Attempt (You MUST address these points):**
    {previous_evaluation}
---
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

    # Use the retriever to find the top k tools that match the 'thought'.
    retrieved_tools = tool_retriever.get_relevant_tools(
        category=tool_category,
        query=creative_thought,
        top_k=3 # Retrieve the k most relevant tools
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

    slidegen_prompt = ChatPromptTemplate.from_messages([
        ("system", SLIDEGEN_SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT_TEMPLATE)
    ])

    slide_generator_runnable = slidegen_prompt | llm_with_tools
    
    for attempt in range(1, 3): # Try up to 2 times
        print(f"  -> Attempt {attempt}/2 to generate tool call...")
        
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
                print(f"  -> Successfully generated HTML with tool: {tool_call_dict['name']}")
                end_time = time.time()
                print(f"  -> Slide generation took {end_time - start_time:.2f} seconds.")
                return state
            

        print("  -> Failed to get a valid tool call or execute it. Retrying...")

    print("ERROR: All attempts to generate slide failed. Creating a default HTML slide.")
    state['current_tool_call'] = {"name": "default_html", "arguments": {"content": current_text}}
    state['current_html_content'] = create_default_html(current_text)
    return state