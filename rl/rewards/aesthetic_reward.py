import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.workflows.slidegen_workflow.tools.tool_des_xml import execute_tool
from backend.workflows.slidegen_workflow.utils.helper import render_xml_to_png, parse_tool_call_json
from backend.infrastructure.aesthetic.vit_aesthetic_provider import ViTAestheticProvider

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
reward_model_path = os.path.join(project_root, "best_model_pairwise.pt")
if not os.path.exists(reward_model_path):
    reward_model_path = os.path.join(project_root, "rl", "model", "best_model_pairwise.pt")

reward_device_str = os.getenv("REWARD_MODEL_DEVICE", "cpu")
aesthetic = ViTAestheticProvider(model_path=reward_model_path, device=reward_device_str)


def slide_aesthetics_reward(prompts, completions, **kwargs):
    rewards = []
    temp_dir = os.path.join(project_root, "rl", "temp_rl_renders")
    os.makedirs(temp_dir, exist_ok=True)

    error_count = 0
    sample_errors = []

    for idx, completion in enumerate(completions):
        temp_img_path = os.path.join(temp_dir, f"render_{idx}.png")
        try:
            tool_call = parse_tool_call_json(completion)
            if not tool_call:
                rewards.append(0.0)
                continue

            xml_content = execute_tool(tool_call)
            if not xml_content:
                rewards.append(0.0)
                continue

            render_xml_to_png(xml_content, temp_img_path)
            score = aesthetic.evaluate(temp_img_path)

            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
            rewards.append(score)

        except Exception as e:
            error_count += 1
            if len(sample_errors) < 3:
                sample_errors.append(f"Gen {idx}: {str(e)}")
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
            rewards.append(0.0)

    scores_str = " ".join(f"{s:.3f}" for s in rewards)
    n_valid = sum(1 for s in rewards if s > 0)
    print(f"  [Aesthetic Reward] valid={n_valid}/{len(rewards)} scores=[{scores_str}]")
    return rewards
