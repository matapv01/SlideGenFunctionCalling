"""Manual preprocessing workflow package."""

def run_manual_workflow(*args, **kwargs):
	"""Lazy import to avoid loading heavy dependencies on package import."""
	from backend.workflows.manual_workflow.main import run_manual_workflow as _run_manual_workflow

	return _run_manual_workflow(*args, **kwargs)

__all__ = ["run_manual_workflow"]
