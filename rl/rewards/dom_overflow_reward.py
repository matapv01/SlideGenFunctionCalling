"""Deterministic XML overflow and text-box collision reward."""

from __future__ import annotations
import concurrent.futures
import os

import xml.etree.ElementTree as ET

from backend.workflows.slidegen_workflow.utils.xml_overflow import analyze_xml_root
from rl.slidegen_adapter import execute_tool, parse_tool_call_json


_PENALTY_WEIGHTS = {
    "text_width": 0.20,
    "text_height": 0.25,
    "max_lines": 0.20,
    "slide_boundary": 0.40,
    "bbox_collision": 0.25,
}


def _overlap_ratio(first: dict, second: dict) -> float:
    left = max(first["x"], second["x"])
    top = max(first["y"], second["y"])
    right = min(first["x"] + first["width"], second["x"] + second["width"])
    bottom = min(first["y"] + first["height"], second["y"] + second["height"])
    if right <= left or bottom <= top:
        return 0.0
    intersection = (right - left) * (bottom - top)
    smaller = min(first["width"] * first["height"], second["width"] * second["height"])
    return intersection / smaller if smaller > 0 else 0.0


def _check_xml_issues(xml_content: str) -> list[dict]:
    root = ET.fromstring(xml_content)
    records = analyze_xml_root(root)
    issues = [
        {"type": reason, "textbox": record["id"]}
        for record in records
        for reason in record["reasons"]
    ]
    for index, first in enumerate(records):
        for second in records[index + 1 :]:
            # Tiny edge intersections are common due to rounding; material text
            # overlap is not.
            if _overlap_ratio(first, second) > 0.05:
                issues.append(
                    {
                        "type": "bbox_collision",
                        "textbox": first["id"],
                        "other": second["id"],
                    }
                )
    return issues


def _score_completion(completion: str) -> tuple[float, int]:
    try:
        tool_call = parse_tool_call_json(completion)
        if not tool_call:
            return -1.0, 1
        xml_content = execute_tool(tool_call)
        issues = _check_xml_issues(xml_content)
        penalty = min(
            2.0,
            sum(_PENALTY_WEIGHTS.get(issue["type"], 0.10) for issue in issues),
        )
        return max(-1.0, 1.0 - penalty), len(issues)
    except Exception:
        return -1.0, 1


def dom_overflow_reward(prompts, completions, **kwargs):
    del prompts, kwargs
    workers = max(
        1,
        min(int(os.getenv("RL_REWARD_CPU_WORKERS", "16")), len(completions) or 1),
    )
    if completions:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            scored = list(executor.map(_score_completion, completions))
    else:
        scored = []

    rewards = [score for score, _ in scored]
    issue_counts = [count for _, count in scored]
    print(
        f"  [XML Overflow Reward] workers={workers} issues={issue_counts} "
        f"scores=[{' '.join(f'{score:.3f}' for score in rewards)}]"
    )
    return rewards
