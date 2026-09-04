# File: backend/workflows/slidegen_workflow/nodes/slide_evaluator.py

import json
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from backend.workflows.slidegen_workflow.utils.helper import image_to_base64
from backend.workflows.slidegen_workflow.graph.stage import State, Evaluation
from backend.workflows.slidegen_workflow.utils.prompts import EVALUATION_PROMPT
import os
import shutil
from functools import lru_cache
from backend.infrastructure.aesthetic.vit_aesthetic_provider import ViTAestheticProvider

@lru_cache(maxsize=1)
def get_vit_provider():
    model_path = os.getenv("AESTHETIC_REWARD_MODEL_PATH", "models/best_model_multilabel.pt")
    return ViTAestheticProvider(model_path=model_path, device="cpu")


def slide_evaluator(state: State, config: RunnableConfig) -> State:
    """
    Sá»­ dá»¥ng VLM vÃ  with_structured_output
    Ä‘áº£m báº£o pháº£n há»“i cÃ³ cáº¥u trÃºc.
    """
    retry_count = state.get('retry_count', 0)
    idx = state['current_slide_index']
    print(f"\n---------------- Node Slide Evaluator (Slide thá»© {idx + 1}, Retry attempt {retry_count}) using structured_output ----------------")

    # Get current tool call and image path
    recent_function_call = state.get('current_tool_call', None)
    previous_accepted_tool_call = state.get('previous_accepted_tool_call', None)
    current_image_path = state.get('current_image_path', None)
    previous_image_path = state.get('previous_image_path', None)

    # Initialize default values
    state['vlm_feedback'] = "No feedback provided."
    state['vlm_decision'] = "deny"

    # Validate required inputs
    if not recent_function_call or not current_image_path:
        print("Insufficient function call or image for evaluation. Denying.")
        state['vlm_feedback'] = "Cannot evaluate due to missing HTML code or slide image."
        state['retry_count'] = retry_count + 1
        return state

    # Get ViT Aesthetic Score
    try:
        vit_eval = get_vit_provider().evaluate(current_image_path)
        formatted_report = vit_eval.get("formatted_report", "")
        print(f"\n[*] ViT Aesthetic Evaluation:\n{formatted_report}\n")
        vit_score = formatted_report
    except Exception as e:
        print(f"Warning: ViT evaluation failed - {e}")
        vit_score = "N/A"

    # Gather previous errors
    previous_errors = ""
    if state.get('executor_decision') == 'fail':
        previous_errors += f"Executor Error: {state.get('executor_feedback', '')}\n"
    elif retry_count > 0 and state.get('vlm_decision') == 'deny':
        previous_errors += f"VLM Feedback from previous attempt: {state.get('vlm_feedback', '')}\n"
    
    if not previous_errors:
        previous_errors = "None"

    # Build multimodal message (text + image)
    evaluation_prompt = ChatPromptTemplate.from_template(EVALUATION_PROMPT)
    formatted_prompt = evaluation_prompt.format(
        tool_call_output=json.dumps(recent_function_call, indent=2),
        previous_accepted_tool_call=json.dumps(previous_accepted_tool_call, indent=2),
        vit_score=vit_score,
        previous_errors=previous_errors
    )

    message_content = [
        {"type": "text", "text": formatted_prompt}
    ]

    # Add image if available
    current_base64_image = image_to_base64(current_image_path)
    if current_base64_image:
        message_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{current_base64_image}"},
            "description": "current slide image"
        })
    else:
        print("Warning: Could not encode current slide image to base64")

    previous_base64_image = image_to_base64(previous_image_path)
    if previous_base64_image:
        message_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{previous_base64_image}"},
            "description": "previous slide image"
        })
    else:
        print("Warning: Could not encode previous slide image to base64")

    vlm_message = HumanMessage(content=message_content)

    # Use structured output with the VLM (planner_llm)
    configurable = config.get("configurable", {}) if config else {}
    vlm = configurable.get('planner_llm') or state.get('planner_llm') or configurable.get('llm')
    if not vlm:
        raise ValueError("VLM (planner_llm) instance not found for slide evaluator.")

    structured_llm = vlm.with_structured_output(Evaluation)

    print("Sending request to VLM with structured_output...")
    try:
        response: Evaluation = structured_llm.invoke([vlm_message])
    except Exception as eval_err:
        print(f"⚠️ VLM invoke exception: {eval_err}")
        response = None

    print(f"VLM Decision: {response.decision}")
    print(f"VLM Feedback: {response.feedback}")

    state['vlm_decision'] = response.decision
    state['vlm_feedback'] = response.feedback

    # Update retry count if decision is 'deny'
    if state['vlm_decision'] == 'deny':
        state['retry_count'] = retry_count + 1
        print(f"Slide rejected. Increasing retry_count to {state['retry_count']}")
        
        # Save failed image
        try:
            failed_dir = "static/output/failed_slides"
            os.makedirs(failed_dir, exist_ok=True)
            failed_filename = f"failed_slide_{idx + 1}_retry_{retry_count}.png"
            failed_filepath = os.path.join(failed_dir, failed_filename)
            shutil.copy(current_image_path, failed_filepath)
            print(f"Saved failed slide image to {failed_filepath}")
        except Exception as e:
            print(f"Warning: Could not save failed slide image - {e}")
    else:
        # Reset retry count on successful acceptance
        state['retry_count'] = 0
        print("Slide accepted.")

    return state

