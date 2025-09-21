from src.graph.stage import State
from langchain_core.prompts import ChatPromptTemplate
from src.tools.tool_des import execute_tool

SLIDEGEN_SYSTEM_PROMPT = """
# YOUR MISSION: Generate a single function call to create a slide from current_slide_content. The slide must be clear, well-structured, visually consistent, and logically connected.
# Your primary goal is to create a slide that is accurate, visually consistent, and logically sound. If you are given evaluation feedback, your #1 priority is to fix the mistakes from your last attempt.

INSTRUCTIONS FOR SMART SLIDE GENERATION

1. Content Preparation
    - Input only contains current_slide_content.
    - No need to compare with or remove duplicates from a previous slide.
    - Focus solely on transforming the current content into slide-ready form.

2. Content Analysis & Synthesis
    - Preserve all information — do not omit or lose details.
    - Present content concisely, in a slide-friendly way (bullet points, short phrases).
    - Do not copy raw text directly; rephrase for clarity and readability.

3. Strategic Slide Function Selection
    - Choose the slide type that best matches the structure and quantity of the current content.
    - Adjust the function’s parameters carefully to ensure the slide is aesthetically pleasing and effective in communication.

    - If previous_evaluation and previous_tool_call exists, you must fix errors by adjusting the parameters of the previous tool call follow the feedback of previous_evaluation (e.g., rephrasing text, resizing, reformatting).
    - You should fix parameters of previous_tool_call based on previous_evaluation feedback (don't change tool_name, just adjust parameters), avoid call other tool_name unless strictly necessary (e.g., when the previous function type is fundamentally unsuitable for the content).
    - If no feedback is provided, select the function type that best matches the content.

4. Design Consistency
    - The new slide must stay visually aligned with the presentation’s style.
    - Use the previous tool call as style inspiration, but avoid directly replicating it.
    - Maintain coherence in fonts, alignment, bullet style, and spacing.

5. HTML Highlighting & Formatting
    - Key phrases must be highlighted for emphasis, using a combination of:
        + <b> for bold
        + <i> for italics
        + Color tags (e.g., <span style="color:...">)
    - Follow the highlighting style seen in the previous tool call for consistency.
    - You may also use tags to adjust alignment or structure if needed.

6. Logical Continuity
    - Each new slide must connect smoothly to the previous one.
    - Do not repeat content from the previous slide.
    - Ensure a clear narrative flow (elaboration, contrast, examples, etc.).

Output Requirement:
    - Return exactly one syntactically correct function call and nothing else.
    - All text arguments must be in the correct language of the presentation.
    - The slide must be comprehensive, structured, visually consistent, and logically coherent.
"""

HUMAN_PROMPT_TEMPLATE = """
---
INPUT CONTEXT FOR THIS TASK:

- **Previous slide function call:** (the previous slide function call accepted)
{previous_slide_function_call}

- **Current slide content:** (Current slide index is {slide_index}/{length_slide_chunks} total slides. The raw text for the new slide. Process this.)
{slide_content}

- **Previous function call:** (CRITICAL INPUT: On the first try, there will be no function call below. On a retry, this is *your own last failed attempt* and is the object you must fix based on feedback, while still using it as a style guide.)
{previous_function_call}

- **Previous evaluation (if any):** (Critique of your last attempt (`previous_function_call`). If this exists, you MUST address the problems it describes.)
{previous_evaluation}

---
"""

def create_default_html(content_text: str) -> str:
    """Create default HTML when unable to get from LLM"""
    if not content_text:
        content_text = "Default slide content"
    
    # Extract title from first line or use default
    lines = content_text.split('\n')
    title = lines[0] if lines else "Slide"
    content = '<br>'.join(lines[1:]) if len(lines) > 1 else content_text
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .slide {{
            width: 800px;
            height: 600px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            padding: 40px;
            position: relative;
        }}
        .title {{
            font-size: 32px;
            color: #2c3e50;
            margin-bottom: 30px;
            text-align: center;
        }}
        .content {{
            font-size: 24px;
            line-height: 1.5;
            color: #34495e;
        }}
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

def slide_generator(state: State) -> State:
    """
    Node for slide generation: Uses LLM to create slides from text content by calling appropriate tools.
    """
    print("\n---------------- Executing Node: slide_generator ----------------")

    idx = state['current_slide_index']
    current_text = state.get("current_slide_text", "")
    previous_slide_context = state.get('previous_slide_context', {})
    previous_function_call = state.get('current_tool_call', {})
    previous_evaluation = state.get('vlm_feedback', "not evaluate yet")
    current_slide_index = state.get('current_slide_index', 0)
    length_slide_chunks = state.get('length_slide_chunks', 0)
    previous_slide_function_call = state.get('previous_accepted_tool_call', {})


    print(f"--- Node: slide_generator (Slide {idx + 1}) ---")
    
    # Validate required inputs
    if not current_text:
        print("No slide text provided. Creating default slide.")
        current_text = "Default slide content"
    
    # Get LLM from state
    llm = state.get('llm')
    
    # Get tools from state
    tools = state.get('tools', [])
    
    indexTry = 0
    while True:
        indexTry += 1
        print(f"Attempting {indexTry} times to generate slide with LLM...")
        print(f"Current slide index: {current_slide_index + 1} of {length_slide_chunks}")
        # Kiểm tra LLM có sẵn không
        if llm is None:
            print("ERROR: LLM is None in state. Cannot proceed with slide generation.")
            break
            
        # Kiểm tra tools có sẵn không
        if not tools:
            print("WARNING: No tools found in state. Using empty tool list.")
            tools = {}
            
        # Bind tools to LLM
        if current_slide_index + 1 == 1:
            my_tools = tools.get('INTRO_TOOLS', [])
        if current_slide_index + 1 == 2:
            my_tools = tools.get('TEAM_TOOLS', []) + tools.get('TRANSITION_TOOLS', []) + tools.get('CONTENT_TOOLS', [])
        if current_slide_index + 1 >= 3:
            my_tools = tools.get('TRANSITION_TOOLS', []) + tools.get('CONTENT_TOOLS', [])
        if current_slide_index + 1 == length_slide_chunks:
            my_tools = tools.get('THANK_YOU_TOOLS', [])
        
        llm_with_tools = llm.bind_tools(my_tools)

        # REFACTOR: Using from_messages for better structure
        slidegen_prompt = ChatPromptTemplate.from_messages([
            ("system", SLIDEGEN_SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT_TEMPLATE)
        ])

        slide_generator_runnable = slidegen_prompt | llm_with_tools
        
        previous_slide_content = ""
        if previous_slide_context:
            previous_slide_content = previous_slide_context.get("content", "")

        response = slide_generator_runnable.invoke({
            "previous_slide_content": previous_slide_content,
            "previous_function_call": previous_function_call,
            "slide_content": current_text,
            "previous_evaluation": previous_evaluation,
            "slide_index": current_slide_index + 1,
            "length_slide_chunks": length_slide_chunks,
            "previous_slide_function_call": previous_slide_function_call
        })
        
        print(f"LLM response type: {type(response)}")

        if response.usage_metadata['output_tokens'] == 0 or (hasattr(response, 'error') ):
            # llm._rotate_key_and_recreate_instance()
            continue

        # Check if response has tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_call = response.tool_calls[0]  # Get first tool call
            print(f"LLM called tool: {tool_call}")
            
            # Convert tool call to dictionary format expected by execute_tool
            tool_call_dict = {
                "name": tool_call["name"],
                "arguments": tool_call["args"]
            }
            
            # Execute the tool to get HTML
            html_content = execute_tool(tool_call_dict)
            if html_content is None:
                print(f"Failed to generate HTML for tool call: {tool_call_dict}")
                print("Generator retrying function calling")
                continue

            # Update state with the tool call and HTML
            state['current_tool_call'] = tool_call_dict
            state['current_html_content'] = html_content
            
            print(f"Successfully executed tool: {tool_call_dict['name']}")
            print(f"Generated HTML length: {len(html_content)} characters")
            return state