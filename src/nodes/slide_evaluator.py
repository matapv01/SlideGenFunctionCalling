# /app/src/nodes/slide_evaluator.py (FIXED VERSION)

import logging
import base64
import json
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from src.stage import State
import time

EVALUATION_PROMPT = """
Evaluate the following slide based on these criteria:
Improved Prompt for Slide Content Evaluation
Please evaluate the slide according to the following detailed criteria. Assess not only the design and formatting, but also whether the content is placed in a suitable location, the meaning is clear, and the message supports the intended purpose of the slide.

1. Title
    - Is the title clearly stating the main idea or topic of the slide (e.g., "Market Overview" instead of "Slide 2")?
    - Is the title placed in a prominent location (typically top center or top left)?
    - Is the font at least 4–6 points larger than the body text?
    - Is the title meaningful, concise, and contextually aligned with the slide's content?

Evaluate if the title actually reflects the core message of the slide and is not generic.

2. Text Content
    - Is the font size at least 18 pt to ensure readability from a distance?
    - Does the text contrast clearly with the background (e.g., white on dark, black on light)?
    - Are sentences clear, concise (no more than 2 lines), and easy to scan?
    - Is the use of bullet points or short paragraphs (max 5 lines) applied effectively?
    - Is spelling, grammar, and punctuation correct?
    - Does the content logically support the purpose of the slide (informative, persuasive, etc.)?
    - Are the main points prioritized and placed in the most logical order?

Check if the content is relevant, well-organized, and presented in a way that supports comprehension and focus.

3. Layout and Content Placement
    - Are all elements (title, text, images, charts) well-aligned and not overlapping or cut off?
    - Is there sufficient white space to reduce visual clutter?
    - Are different content blocks clearly separated?
    - Are the most important messages placed in visually strong positions (top-left, center)?
    - Does the slide guide the viewer's eye naturally (top → bottom or left → right)?

Evaluate how effectively the layout guides the viewer and if content is located where it naturally makes sense to appear.

4. Visuals and Images (if any)
    - Are images directly relevant to the content and purpose of the slide?
    - Are they high quality (not blurry or pixelated)?
    - Are images placed so they do not obscure or distract from text?
    - Do images enhance understanding or visual appeal, not just decoration?

Assess if images help reinforce or explain the content — not just filler.

5. Overall Visual Design
    - Are no more than 2–3 font types used?
    - Is the color scheme limited to 3–4 harmonious colors?
    - Are there minimal and tasteful transitions or animations?
    - Is the slide clean and easy to scan, with visual emphasis on key messages?
    - Is the visual hierarchy clear (title > main points > supporting text)?

Consider if the overall aesthetic supports clarity and avoids distraction.

6. Consistency with Other Slides (if applicable)
    - Are the background, font style, size, and color consistent with previous slides?
    - Is the layout structure (title placement, content areas) consistent?
    - Do the design choices support a cohesive narrative across slides?

Check whether this slide feels like part of a unified deck or visually disconnected.

Additional Evaluation Dimensions (Newly Added)
    - Content Meaning Accuracy: Does the text or visual element truly represent what it intends to convey? Is it logically accurate in the context?
    - Slide Purpose Fit: Does the slide serve its intended purpose (inform, compare, convince, summarize)? Does every element contribute to that goal?
    - Redundancy Check: Are there any duplicate or unnecessary elements that could be removed without losing meaning?

In addition, if a previous slide is available, evaluate consistency between the current and previous slides in the following aspects:
- Background color
- Text color
- Font size
- Font family

Current tool call:  
{tool_call_output}

If you deny the slide:
- Generate feedback explaining what needs to be improved
- You MAY suggest modifications to the slide content **only if necessary**, such as:
  - The content is too long and overcrowds the slide
  - The content lacks clarity or is not well structured for presentation
  - The content does not match the selected slide layout appropriately

Allowed modifications include:
- Trimming or summarizing overly long paragraphs
- Splitting complex content into simpler bullets
- Improving clarity, structure, or conciseness

However, do NOT remove or alter the **core message** of the content. Preserve its intent and essential meaning.

Provide detailed feedback on what works well and what needs improvement, then make your final decision.
"""

class Evaluation(BaseModel):
    """
    An object containing detailed feedback and final decision about the slide.
    """
    feedback: str = Field(description="Detailed analysis of what's good and what needs improvement in the slide. Provide specific suggestions to make the slide better.")
    decision: Literal["accept", "deny"] = Field(description="Final decision. 'accept' if slide is good, 'deny' if it needs to be redone.")

def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logging.error(f"Error encoding image to base64: {image_path}, Error: {e}")
        return ""

def slide_evaluator(state: State) -> State:
    """
    Node for slide evaluation: Uses VLM and with_structured_output to ensure
    structured and reliable output.
    """
    retry_count = state.get('retry_count', 0)
    idx = state['current_slide_index']
    print(f"\n---------------- Executing Node: slide_evaluator (Slide {idx + 1}, Retry attempt {retry_count}) using structured_output ----------------")
    time.sleep(20)

    # Get current tool call and image path
    recent_function_call = state.get('current_tool_call', None)
    image_path = state.get('current_image_path', '')

    # Initialize default values
    state['vlm_feedback'] = "No feedback provided."
    state['vlm_decision'] = "deny"

    # Validate required inputs
    if not recent_function_call or not image_path:
        print("Insufficient function call or image for evaluation. Denying.")
        state['vlm_feedback'] = "Cannot evaluate due to missing HTML code or slide image."
        state['retry_count'] = retry_count + 1
        return state

    # Build multimodal message (text + image)
    try:
        evaluation_prompt = ChatPromptTemplate.from_template(EVALUATION_PROMPT)
        formatted_prompt = evaluation_prompt.format(
            tool_call_output=json.dumps(recent_function_call, indent=2)
        )
        
        message_content = [
            {"type": "text", "text": formatted_prompt}
        ]

        # Add image if available
        base64_image = image_to_base64(image_path)
        if base64_image:
            message_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
            })
        else:
            print("Warning: Could not encode image to base64")
        
        vlm_message = HumanMessage(content=message_content)

        # Use structured output with the LLM
        llm = state['llm']
        structured_llm = llm.with_structured_output(Evaluation)

        print("Sending request to VLM with structured_output...")
        response: Evaluation = structured_llm.invoke([vlm_message])
        
        print(f"VLM Decision: {response.decision}")
        print(f"VLM Feedback: {response.feedback}")

        state['vlm_decision'] = response.decision
        state['vlm_feedback'] = response.feedback

    except Exception as e:
        print(f"Critical error when calling VLM with structured_output: {e}")
        state['vlm_decision'] = "deny"
        state['vlm_feedback'] = f"System error occurred during evaluation: {str(e)}"

    # Update retry count if decision is 'deny'
    if state['vlm_decision'] == 'deny':
        state['retry_count'] = retry_count + 1
        print(f"Slide rejected. Increasing retry_count to {state['retry_count']}")
    else:
        # Reset retry count on successful acceptance
        state['retry_count'] = 0
        print("Slide accepted.")
    
    return state