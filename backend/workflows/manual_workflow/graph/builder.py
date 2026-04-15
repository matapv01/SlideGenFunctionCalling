from langgraph.graph import StateGraph

from backend.workflows.manual_workflow.graph.stage import State
from backend.workflows.manual_workflow.nodes.manual_chunk_preparer import prepare_manual_chunks
from backend.workflows.manual_workflow.nodes.structure_approver import approve_manual_structure
from backend.workflows.manual_workflow.nodes.structure_updater import update_manual_structure


def build_manual_workflow() -> StateGraph:
    """Build manual preprocessing workflow graph."""
    workflow = StateGraph(State)

    workflow.add_node("prepare_manual_chunks", prepare_manual_chunks)

    workflow.set_entry_point("prepare_manual_chunks")
    workflow.set_finish_point("prepare_manual_chunks")

    return workflow


def build_manual_approve_workflow() -> StateGraph:
    """Build manual approve workflow graph (tree structure -> approved chunks)."""
    workflow = StateGraph(State)

    workflow.add_node("approve_manual_structure", approve_manual_structure)

    workflow.set_entry_point("approve_manual_structure")
    workflow.set_finish_point("approve_manual_structure")

    return workflow


def build_manual_update_workflow() -> StateGraph:
    """Build manual update workflow graph (editor tree -> persisted structure file)."""
    workflow = StateGraph(State)

    workflow.add_node("update_manual_structure", update_manual_structure)

    workflow.set_entry_point("update_manual_structure")
    workflow.set_finish_point("update_manual_structure")

    return workflow
