import os
import sys
import json
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.workflows.slidegen_workflow.tools.tool_des_xml import execute_tool
from backend.workflows.slidegen_workflow.utils.helper import render_xml_to_png, parse_tool_call_json, sanitize_to_placeholders
from backend.infrastructure.embedding.dinov2_provider import DINOv2EmbeddingProvider

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
embedder = DINOv2EmbeddingProvider(device="cpu")


def visual_consistency_reward(prompts, completions, previous_slide_embedding, **kwargs):
    rewards = []
    temp_dir = os.path.join(project_root, "rl", "temp_rl_renders")
    os.makedirs(temp_dir, exist_ok=True)

    for idx, completion in enumerate(completions):
        temp_img_path = os.path.join(temp_dir, f"consistency_render_{idx}.png")
        try:
            tool_call = parse_tool_call_json(completion)
            if not tool_call:
                rewards.append(0.0)
                continue

            sanitized = sanitize_to_placeholders(tool_call)
            xml_content = execute_tool(sanitized)
            if not xml_content:
                rewards.append(0.0)
                continue

            render_xml_to_png(xml_content, temp_img_path)
            curr_embedding = embedder.get_embedding_np(temp_img_path)
            prev_embedding = np.array(previous_slide_embedding[idx])

            prev_norm = np.linalg.norm(prev_embedding)
            if prev_norm == 0:
                # First slide in deck has no previous slide to compare consistency with — give full score
                sim_score = 1.0
            else:
                dot = np.dot(curr_embedding, prev_embedding)
                norm = np.linalg.norm(curr_embedding) * prev_norm
                sim_score = float(dot / norm) if norm > 0 else 0.0
                sim_score = max(0.0, min(1.0, sim_score))

            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
            rewards.append(sim_score)

        except Exception:
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
            rewards.append(0.0)

    scores_str = " ".join(f"{s:.3f}" for s in rewards)
    print(f"  [Consistency Reward] scores=[{scores_str}]")
    return rewards
