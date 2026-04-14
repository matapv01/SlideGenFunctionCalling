from typing import Any, Dict, List

from backend.workflows.manual_workflow.graph.stage import State
from backend.workflows.shared.context_map_utils import build_slide_context_maps


def prepare_manual_chunks(state: State) -> State:
	"""Normalize manual chunks and ensure context maps are aligned."""
	slide_chunks = state.get("slide_chunks", [])

	if not slide_chunks:
		state["slide_chunks"] = []
		state["slide_context_maps"] = []
		return state

	slide_context_maps = state.get("slide_context_maps", [])
	if not slide_context_maps or len(slide_context_maps) != len(slide_chunks):
		state["slide_context_maps"] = build_slide_context_maps(
			slide_chunks,
			intro_mode="first_slide",
		)

	state["slide_chunks"] = slide_chunks
	return state