import json
import re
import logging
from typing import Dict, Any, List
from langchain_core.tools import Tool
from src.stage import State
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from src.tools.tool_des import execute_tool

SLIDEGEN_SYSTEM_PROMPT = """
# YOUR MISSION: Generate a single, perfect slide function call for the `current_slide_content`.
# Your primary goal is to create a slide that is accurate, visually consistent, and logically sound. If you are given evaluation feedback, your #1 priority is to fix the mistakes from your last attempt.

INSTRUCTIONS FOR SMART SLIDE GENERATION

1. CONTENT DE-DUPLICATION & PREPARATION:
- **First, compare `current_slide_content` with `previous_slide_content`.**
- **Identify and REMOVE any text from `current_slide_content` that is a direct repetition of content already on the previous slide.** The remaining unique text is your new working content for this slide.

2. CONTENT ANALYSIS & LOSSLESS SYNTHESIS:
- **Core Principle: Rephrase for clarity, but do not omit information.**
- Analyze the de-duplicated content to identify every unique point, idea, and piece of data.
- **Your goal is a comprehensive summary.** Structure the content concisely using bullet points or short phrases, but you MUST include all distinct information from the source text.
- DO NOT simply copy-paste raw text. Transform it into a polished, slide-friendly format.

3. STRATEGIC SLIDE FUNCTION SELECTION & CORRECTION:
- **Core Principle: The layout must serve the content. If `previous_evaluation` exists, you MUST correct your previous choice.**
- **If `previous_evaluation` is provided:**
    - It means your `previous_function_call` was flawed. Analyze the feedback carefully.
    - Your new function call MUST address the critique. This might involve changing the slide function entirely (e.g., from `make_text_slide` to `make_bullet_slide`), rephrasing the content, or adjusting formatting.
- **If no feedback is provided:**
    - Select the single best slide function based on your synthesized content. Consider the content's nature (list, comparison, narrative), the amount of text, and the narrative flow.
- Available functions include: `make_bullet_slide`, `make_two_column_slide`, `make_text_slide`, `make_image_with_caption_slide`, `make_quote_slide`.

4. VISUAL & DESIGN COHERENCE:
- **Core Principle: The new slide must feel like part of the same presentation.**
- **Use the `previous_function_call` as your definitive style guide.**
- **This is true for BOTH first attempts and retries.** The `previous_function_call` always contains the design template (fonts, alignment, etc.) that you must follow.
- MAINTAIN a consistent style for: Fonts (family, size), bullet point style, text alignment, and spacing.
- AVOID jarring visual shifts.

5. STRATEGIC HTML FORMATTING (Use Sparingly):
- **Core Principle: Use HTML for subtle enhancement, not for layout.**
- Use tags like `<b>`, `<i>`, and `<br>` only to improve readability.
- Use with extreme caution: `<ul>/<li>` or `<span style="...">`, typically only if correcting a specific issue from `previous_evaluation`.

6. SEMANTIC & LOGICAL CONTINUITY:
- **Core Principle: Ensure a smooth narrative flow.**
- The new slide must be a logical next step from `previous_slide_content` (e.g., an elaboration, a contrast, an example).

OUTPUT REQUIREMENTS:

- Your response must be a **single, syntactically correct function call** and nothing else.
- All text arguments in the function call must be in the detected language.
- **Final Check:** Ensure the slide is comprehensive, well-structured, visually consistent, logically connected, and directly addresses any feedback.
"""

HUMAN_PROMPT_TEMPLATE = """
---
INPUT CONTEXT FOR THIS TASK:

- **Previous slide content:** (The text from the preceding slide in the presentation. Used for de-duplication and context.)
{previous_slide_content}

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
        try:
            print(f"Attempting {indexTry}/3 to generate slide with LLM...")
            print(f"Current slide index: {current_slide_index + 1} of {length_slide_chunks}")
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
                "length_slide_chunks": length_slide_chunks
            })
            
            print(f"LLM response type: {type(response)}")
            
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
            else:
                if indexTry < 3:
                    print(f"No tool calls found in response. retrying with slide generation {indexTry}/3.")
                    continue

                # Fallback: try to extract content from response or create default
                print(f"No tool calls found in response ({indexTry}/3). Creating default slide.")

                # Try to use response content if available
                if hasattr(response, 'content') and response.content:
                    # Try to extract meaningful content from the response
                    response_text = response.content
                    if len(response_text) > 50:  # If there's substantial content
                        current_text = response_text
                
                html_content = create_default_html(current_text)
                
                # Create a default tool call
                tool_call_dict = {
                    "name": "generate_academic_slide",
                    "arguments": {
                        "title": current_text.split('\n')[0] if '\n' in current_text else current_text[:50],
                        "description": current_text
                    }
                }
                
                html_content = execute_tool(tool_call_dict)

                
                state['current_tool_call'] = tool_call_dict
                state['current_html_content'] = html_content
                print("Created default slide using generate_academic_slide")
            
        
            print("Default slide created successfully.")
            return state
        except Exception as e:
            logging.error(f"Error in slide generation: {e}")
            print(f"Error in slide generation: {e}")
            
            # Create default HTML on error
            html_content = create_default_html(current_text)
            
            # Create default tool call
            tool_call_dict = {
                "name": "generate_academic_slide",
                "arguments": {
                    "title": "Error",
                    "description": f"Error generating slide: {str(e)}"
                }
            }
            
        try:
            html_content = execute_tool(tool_call_dict)
        except:
            # If even the default tool fails, use basic HTML
            pass
            
        state['current_tool_call'] = tool_call_dict
        state['current_html_content'] = html_content 
        state['is_redundant'] = False
        print("Created error slide due to exception")
        
    return state