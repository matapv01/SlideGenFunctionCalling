from langgraph.graph import StateGraph

from backend.workflows.manual_workflow.graph.stage import State
from backend.workflows.manual_workflow.nodes.manual_chunk_preparer import prepare_manual_chunks


def build_manual_workflow() -> StateGraph:
    """Build manual preprocessing workflow graph."""
    workflow = StateGraph(State)

    workflow.add_node("prepare_manual_chunks", prepare_manual_chunks)

    workflow.set_entry_point("prepare_manual_chunks")
    workflow.set_finish_point("prepare_manual_chunks")

    return workflow
