import json
import re
import logging
from typing import Dict, Any, List
from langchain_core.tools import Tool
from src.stage import State
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from src.tools.tool_des import execute_tool

SLIDEGEN_PROMPT = """
# Detect content language
language = "Vietnamese" if is_vietnamese(slide_content) else "English"

# Create a new slide that accurately conveys `slide_content`, fits the logical flow from the previous slide, 
# and maintains full design coherence across the deck.

INSTRUCTIONS FOR SMART SLIDE GENERATION

1. CONTENT ANALYSIS & SUMMARIZATION:
- Extract the key ideas from `slide_content`.
- Rewrite the content into a clear and concise form that's suitable for a slide.
- Avoid copy-pasting long text blocks. Use bullet points, sections, or summaries.

2. SLIDE FUNCTION SELECTION:
- Choose the most suitable slide function for the current content, considering:
    a. Content type (list, narrative, explanation, process, comparison, etc.)
    b. Optimal visual layout for comprehension and impact
    c. Narrative flow from the previous slide
- DO NOT default to the same slide function as before unless it fits naturally.
- Example slide functions include:
    + `make_bullet_slide` – for short points or key facts  
    + `make_two_column_slide` – for comparison or parallel ideas  
    + `make_text_slide` – for deep explanations or storytelling  
    + `make_image_with_caption_slide` – for visual explanations  

3. LANGUAGE:
- All output text must be in the detected language, matching the input content.

4. VISUAL & DESIGN CONSISTENCY:
Ensure that the new slide aligns stylistically with the previous one:
- Use matching:
    + Font size and style  
    + Bullet point formatting  
    + Text alignment and spacing  
    + Background, title alignment, text padding  
    + Color themes and visual tone  
- Avoid disruptive shifts like:
    + Sudden font downsizing (e.g. 14pt → 10pt)
    + Changing bullet type (e.g. dash → dot) without purpose
    + Inconsistent title placement (e.g. left-aligned → centered)

5. HTML SUPPORT (ONLY WHEN NECESSARY):
- You may insert basic HTML tags inside the content strings to fine-tune formatting — **only if justified**.
- Acceptable use-cases:
    + `<br>` to control line breaks in tightly packed content
    + `<b>`, `<i>` to highlight keywords or distinctions
    + `<ul>`, `<li>` only when necessary to override default bullet behavior
    + `<span style="font-size: Xpx">` for inline size correction — use carefully!
- HTML should **enhance clarity**, not clutter the slide or introduce inconsistency.
- Avoid overusing or nesting tags unless truly needed for alignment or visual balance.

6. SEMANTIC & LOGICAL CONTINUITY:
- If the previous slide introduced a concept, this one may expand, contrast, or illustrate.
- Make sure the tone, topic, and flow remain natural and progressive.
- The audience should feel the transition is smooth and meaningful.

7. PRESENTATION-READY STRUCTURE:
- Use whitespace wisely.
- Keep content digestible: avoid text-heavy layouts.
- Place title and content to guide the viewer's eye clearly.

INPUT CONTEXT:
- Previous slide content:
{previous_slide_content}

- Previous function call:
{previous_function_call}

- Current slide content:
{slide_content}

- Previous evaluation (if any):
{previous_evaluation}

OUTPUT REQUIREMENTS:
- A **single slide function call**, e.g. `make_bullet_slide(...)`, with parameters written entirely in the detected language.
- Slide must be:
    + Content-relevant  
    + Layout-appropriate  
    + Visually consistent  
    + Logically connected  
    + Clean and readable  
    + Enhanced (only if necessary) with minimal HTML for formatting
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
    previous_evaluation = state.get('vlm_feedback', "")
    
    print(f"--- Node: slide_generator (Slide {idx + 1}) ---")
    
    # Validate required inputs
    if not current_text:
        print("No slide text provided. Creating default slide.")
        current_text = "Default slide content"
    
    # Get LLM from state
    llm = state.get('llm')
    if not llm:
        print("Error: No LLM found in state")
        state['current_tool_call'] = {
            "name": "generate_academic_slide",
            "arguments": {"html_content": create_default_html(current_text)}
        }
        state['is_redundant'] = False
        return state
    
    # Get tools from state
    tools = state.get('tools', [])
    if not tools:
        print("Error: No tools found in state")
        state['current_tool_call'] = {
            "name": "generate_academic_slide", 
            "arguments": {"html_content": create_default_html(current_text)}
        }
        state['is_redundant'] = False
        return state
    
    try:
        print("Attempting to generate slide with LLM...")
        
        # Bind tools to LLM
        llm_with_tools = llm.bind_tools(tools)

        # Create and invoke the prompt
        slidegen_prompt = ChatPromptTemplate.from_template(SLIDEGEN_PROMPT)
        slide_generator_runnable = slidegen_prompt | llm_with_tools
        
        previous_slide_content = ""
        if previous_slide_context:
            previous_slide_content = previous_slide_context.get("content", "")

        response = slide_generator_runnable.invoke({
            "previous_slide_content": previous_slide_content,
            "previous_function_call": previous_function_call,
            "slide_content": current_text,
            "previous_evaluation": previous_evaluation
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
            
            # Update state with the tool call and HTML
            state['current_tool_call'] = tool_call_dict
            state['current_html_content'] = html_content
            
            print(f"Successfully executed tool: {tool_call_dict['name']}")
            print(f"Generated HTML length: {len(html_content)} characters")
            
        else:
            # Fallback: try to extract content from response or create default
            print("No tool calls found in response. Creating default slide.")
            
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
        
        # Check if content is too long (mark as redundant)
        if len(html_content) > 10000:
            state['is_redundant'] = True
            print(f"HTML content too long ({len(html_content)} characters). Marking slide as redundant.")
        else:
            state['is_redundant'] = False
                
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