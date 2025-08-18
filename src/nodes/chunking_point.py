import logging
import base64
import json
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from src.graph.stage import State
import time


SLIDEGEN_SYSTEM_PROMPT = """
# YOUR MISSION: INTELLIGENT CONTENT ANALYSIS & SPLITTING
# This is the core of your task. You must understand the difference between **Metadata** and **Content**.

    **Definitions:**
    -   **Metadata:** Titles, subtitles, section headings (e.g., "Introduction:", "Chapter 2:", "Key Findings"). Its purpose is to introduce the content that follows.
    -   **Content:** The actual information, such as paragraphs, bullet points, or lists that elaborate on the metadata.

    **The Golden Rule of Splitting:**
    **METADATA AND ITS DIRECTLY RELATED CONTENT MUST STAY TOGETHER ON THE SAME SLIDE.**
    -   You are **NEVER** allowed to put a title on one slide and its first paragraph or first bullet point on the next slide. This is a critical error.
    -   A "semantic block" for a slide is defined as a cluster of (Metadata + its associated Content).

    **Your Splitting Process:**
    1.  **Identify Clusters:** Scan the 'Current raw content' to identify these "Metadata + Content" clusters.
    2.  **Assign to Slide:** Select **one complete cluster** for the current slide.
        *   **Correct Example:** If the content is "Title: The Sun. The sun is a star...", your slide **must** contain both the title and the first sentence/paragraph.
        *   **WRONG Example:** Putting "Title: The Sun" on one slide and "The sun is a star..." on the next is **forbidden**.
    3.  **Handle Overflow:** If the content *within that single cluster* is too long for one slide (e.g., a title with 10 bullet points), you then split the **Content part only**.
        *   **Correct Splitting:**
            *   Slide 1: Title + Bullet points 1-4.
            *   `remaining_content`: Bullet points 5-10 (You can optionally repeat the title here for context on the next slide).
    4.  **Place Excess Clusters:** Any other complete clusters found in the raw content should be moved entirely to `remaining_content`.
        *   **Example:**
            *   Input: "Section 1: ... (content for S1) ... Section 2: ... (content for S2) ..."
            *   Slide 1: Contains all of "Section 1: ... (content for S1) ...".
            *   `remaining_content`: "Section 2: ... (content for S2) ...".
    
    If the content is new, proceed.
    - Analyze `slide_content` to find the main semantic block.
    - Summarize it concisely.
    - If there's excess content, place it in the `remaining_content` field. Ensure this content is TRULY new and does not repeat what will be on the current slide.

"""

HUMAN_PROMPT_TEMPLATE = """
---
INPUT CONTEXT FOR THIS TASK:

- **Current slide content:** (Current slide index is {slide_index}/{length_slide_chunks} total slides. The raw text for the new slide. Process this.)
{slide_content}

---
"""

class ChunkingPoint(BaseModel):
    """
    """
    content: str = Field(description="Detailed analysis of what's good and what needs improvement in the slide. Provide specific suggestions to make the slide better.")
    decision: Literal["accept", "deny"] = Field(description="Final decision. 'accept' if slide is good, 'deny' if it needs to be redone.")
def chunking_point(state: State) -> State:
    """
    Node for slide generation: Uses LLM to create slides from text content by calling appropriate tools.
    """
    print("\n---------------- Executing Node: chunking_point ----------------")

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