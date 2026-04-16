"""Graph utilities for manual preprocessing workflow."""

def build_manual_workflow(*args, **kwargs):
	"""Lazy import for graph builder."""
	from backend.workflows.manual_workflow.graph.builder import build_manual_workflow as _build_manual_workflow

	return _build_manual_workflow(*args, **kwargs)

__all__ = ["build_manual_workflow"]
