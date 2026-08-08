# File: rl/rollout_processor.py

import os
from backend.config import EXECUTOR_MAX_RETRIES
from backend.workflows.slidegen_workflow.tools.tool_des import execute_tool
from backend.workflows.slidegen_workflow.utils.helper import (
    render_html_to_png,
    sanitize_to_placeholders,
)
from backend.workflows.slidegen_workflow.nodes.slide_generator import generate_slide
from backend.workflows.slidegen_workflow.nodes.tool_call_executor import tool_call_executor
from backend.infrastructure.embedding.dinov2_provider import DINOv2EmbeddingProvider
from rl.run_artifacts import save_contact_sheet, write_json

def log_node(step_num: int, doc_idx: int, si: str, node: str, msg: str):
    print(f"  [Step {step_num} Doc {doc_idx} Slide {si}] {node} → {msg}")


def process_doc(
    doc_slides: list,
    step_num: int,
    doc_idx: int,
    grpo_config: dict,
    data_dir: str = "./rl/data",
    embedding_provider=None,
) -> list:
    """
    Mỗi slide đã có đầy đủ các trường pre-computed từ dataset_with_candidate_tools.json.
    Gọi trực tiếp generate_slide() và tool_call_executor() đúng như production workflow.
    """
    prompts_data = []
    prev_embedding = [0.0] * 768
    rendered_paths = []
    render_dir = os.path.join(data_dir, f"step_{step_num:04d}", "renders", f"doc_{doc_idx}")
    os.makedirs(render_dir, exist_ok=True)

    if embedding_provider is None:
        try:
            device = grpo_config.get("configurable", {}).get("device", "cpu")
            embedding_provider = DINOv2EmbeddingProvider(device=device)
        except Exception:
            embedding_provider = None

    for si, slide in enumerate(doc_slides):
        action        = slide.get("action") or slide.get("category") or "CONTENT_TOOLS"
        slide_content = slide.get("slide_content", "")
        thought       = slide.get("thought") or slide_content[:300]

        # Xây dựng state chuẩn cho slide_generator + tool_call_executor
        state = {
            "current_slide_index": si,
            "last_processed_slide_index": -1,
            "length_slide_chunks": max(5, len(doc_slides)),
            "current_slide_text": slide_content,
            "current_slide_plan": {
                "action": action,
                "thought": thought,
            },
            "current_slide_context_map": slide.get("style_context", ""),
            "design_instruction": slide.get("design_instruction", ""),
            "candidate_tools": slide.get("candidate_tools", []),
            "use_cot": True,
            "retry_count": 0,
            "executor_feedback": "",
            "executor_decision": "fail",
        }

        # Vòng lặp Generator ↔ Executor
        prompt = ""
        for attempt in range(1, EXECUTOR_MAX_RETRIES + 1):
            # 1. Gọi Node: slide_generator
            state = generate_slide(state, grpo_config)
            prompt = state.get("raw_llm_prompt", "") or state.get("raw_llm_response", "")
            tool_call = state.get("current_tool_call", {})
            log_node(step_num, doc_idx, str(si), "LLM", f"attempt {attempt}/{EXECUTOR_MAX_RETRIES} → {tool_call.get('name', 'NO_CALL')}")

            # 2. Gọi Node: tool_call_executor
            state = tool_call_executor(state, grpo_config)
            decision = state.get("executor_decision")

            if decision == "pass":
                log_node(step_num, doc_idx, str(si), "Executor", f"PASS → {tool_call.get('name')}")
                break
            else:
                log_node(step_num, doc_idx, str(si), "Executor", f"FAIL attempt {attempt} — {state.get('executor_feedback', '')[:80]}")

        # Lấy kết quả cuối từ state
        real_html = state.get("current_html_content")
        tool_call = state.get("current_tool_call", {})

        # Append prompt cho GRPO và embedding của slide trước
        prompts_data.append({
            "prompt": prompt,
            "previous_slide_embedding": prev_embedding,
        })

        if real_html:
            real_path = os.path.join(render_dir, f"slide_{si:03d}_real.png")
            try:
                render_html_to_png(real_html, real_path)
                rendered_paths.append(real_path)
                log_node(step_num, doc_idx, str(si), "Render", "OK")
            except Exception as e:
                log_node(step_num, doc_idx, str(si), "Render", f"FAILED ({e})")

            if tool_call:
                sanitized = sanitize_to_placeholders(tool_call)
                sanitized_html = execute_tool(sanitized)
                if sanitized_html and embedding_provider:
                    sanitized_path = os.path.join(render_dir, f"slide_{si:03d}_sanitized.png")
                    try:
                        render_html_to_png(sanitized_html, sanitized_path)
                        rendered_paths.append(sanitized_path)
                        prev_embedding = embedding_provider.get_embedding(sanitized_path)
                        log_node(step_num, doc_idx, str(si), "Embed", "OK")
                    except Exception as e:
                        log_node(step_num, doc_idx, str(si), "Embed", f"FAILED ({e})")

    overview_path = os.path.join(render_dir, "overview.png")
    save_contact_sheet(
        rendered_paths,
        overview_path,
        title=f"GRPO Step {step_num:04d} / Doc {doc_idx} Render Overview",
        subtitle=f"{len(doc_slides)} slides, {len(rendered_paths)} rendered images",
        columns=4,
        thumb_size=(420, 236),
    )
    write_json(
        os.path.join(render_dir, "summary.json"),
        {
            "step": step_num,
            "doc_idx": doc_idx,
            "slide_count": len(doc_slides),
            "prompt_count": len(prompts_data),
            "rendered_images": rendered_paths,
            "overview_path": overview_path,
        },
    )
    log_node(step_num, doc_idx, "-", "Done", f"{len(doc_slides)} slides, {len(rendered_paths)} renders")
    return prompts_data
