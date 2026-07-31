"""Compatibility exports for the rule-based image tool-plan executor.

Image search queries are now generated in the same LLM response as the final
slide HTML tool. This module intentionally contains no planner-LLM path.
"""

from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
    ToolPlanError,
    execute_image_search_plan,
    get_image_targets_in_order,
    validate_tool_plan,
)

__all__ = [
    "ToolPlanError",
    "execute_image_search_plan",
    "get_image_targets_in_order",
    "validate_tool_plan",
]
