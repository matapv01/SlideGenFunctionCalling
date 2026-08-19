# File: backend/workflows/slidegen_workflow/nodes/slide_evaluator.py

import os
import shutil
import json
from langchain_core.runnables import RunnableConfig
from backend.workflows.slidegen_workflow.graph.stage import State
from backend.infrastructure.aesthetic.vit_aesthetic_provider import get_vit_evaluator


def slide_evaluator(state: State, config: RunnableConfig) -> State:
    """
    Sử dụng ViT Multi-label model để đánh giá slide.
    """
    retry_count = state.get('retry_count', 0)
    idx = state['current_slide_index']
    print(f"\n---------------- Node Slide Evaluator (Slide thứ {idx + 1}, Retry attempt {retry_count}) using ViT Model ----------------")

    # Get current image path
    current_image_path = state.get('current_image_path', None)

    # Initialize default values
    state['vlm_feedback'] = "No feedback provided."
    state['vlm_decision'] = "deny"

    # Validate required inputs
    if not current_image_path:
        print("Insufficient image for evaluation. Denying.")
        state['vlm_feedback'] = "Cannot evaluate due to missing slide image."
        state['retry_count'] = retry_count + 1
        return state

    print(f"Sending request to ViT Evaluator for image: {current_image_path}")
    
    vit_evaluator = get_vit_evaluator()
    is_accept, errors, detailed_scores = vit_evaluator.evaluate(current_image_path)

    print(f"ViT Scores: {json.dumps(detailed_scores, indent=2, ensure_ascii=False)}")
    
    if is_accept:
        decision = "accept"
        feedback = "The slide is beautiful and has no errors. Great job!"
    else:
        decision = "deny"
        feedback = f"Slide has aesthetic errors: {', '.join(errors)}. Please adjust the layout, font size, or color contrast."
        
        # Save a copy of the rejected slide for comparison
        try:
            dir_name = os.path.dirname(current_image_path)
            base_name = os.path.basename(current_image_path)
            name, ext = os.path.splitext(base_name)
            rejected_path = os.path.join(dir_name, f"{name}_rejected_retry_{retry_count}{ext}")
            shutil.copy2(current_image_path, rejected_path)
            print(f"Lưu lại slide bị lỗi để so sánh tại: {rejected_path}")
        except Exception as e:
            print(f"Không thể lưu slide lỗi: {e}")

    print(f"ViT Decision: {decision}")
    print(f"ViT Feedback: {feedback}")

    state['vlm_decision'] = decision
    state['vlm_feedback'] = feedback

    # Update retry count if decision is 'deny'
    if state['vlm_decision'] == 'deny':
        state['retry_count'] = retry_count + 1
        print(f"Slide rejected. Increasing retry_count to {state['retry_count']}")
    else:
        # Reset retry count on successful acceptance
        state['retry_count'] = 0
        print("Slide accepted.")

    return state
