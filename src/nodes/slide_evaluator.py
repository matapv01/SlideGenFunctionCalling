# File: src/nodes/slide_evaluator.py

import json
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from src.utils.helper import image_to_base64
from src.graph.stage import State, Evaluation
from src.utils.prompts import EVALUATION_PROMPT


def slide_evaluator(state: State) -> State:
    """
    Sử dụng VLM và with_structured_output
    để đảm bảo phản hồi có cấu trúc.
    """
    retry_count = state.get('retry_count', 0)
    idx = state['current_slide_index']
    print(f"\n---------------- Node Slide Evaluator (Slide thứ {idx + 1}, Retry attempt {retry_count}) using structured_output ----------------")

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

    # Build multimodal message (text + image)
    evaluation_prompt = ChatPromptTemplate.from_template(EVALUATION_PROMPT)
    formatted_prompt = evaluation_prompt.format(
        tool_call_output=json.dumps(recent_function_call, indent=2),
        previous_accepted_tool_call=json.dumps(previous_accepted_tool_call, indent=2)
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

    # Use structured output with the LLM
    llm = state['llm']

    while True:
        structured_llm = llm.with_structured_output(Evaluation)

        print("Sending request to VLM with structured_output...")
        response: Evaluation = structured_llm.invoke([vlm_message])

        print(f"Response: {response}")

        print(f"VLM Decision: {response.decision}")
        print(f"VLM Feedback: {response.feedback}")

        # if response['completion_tokens'] == 0:
        #     llm._rotate_key_and_recreate_instance()
        #     continue

        state['vlm_decision'] = response.decision
        state['vlm_feedback'] = response.feedback

        # Update retry count if decision is 'deny'
        if state['vlm_decision'] == 'deny':
            state['retry_count'] = retry_count + 1
            print(f"Slide rejected. Increasing retry_count to {state['retry_count']}")
        else:
            # Reset retry count on successful acceptance
            state['retry_count'] = 0
            print("Slide accepted.")

        return state
