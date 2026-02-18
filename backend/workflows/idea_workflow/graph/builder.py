# File: backend/workflows/idea_workflow/graph/builder.py

from langgraph.graph import StateGraph, END
from backend.workflows.idea_workflow.graph.stage import State
from backend.workflows.idea_workflow.nodes.structure_generator import generate_structure

def build_idea_workflow() -> StateGraph:
    """
    Xây dựng đồ thị cho luồng tạo ý tưởng (Idea Generation).
    Luồng: Start -> Generate Structure -> End
    """
    workflow = StateGraph(State)

    # Thêm node duy nhất
    workflow.add_node("generate_structure", generate_structure)

    # Định tuyến
    workflow.set_entry_point("generate_structure")
    workflow.add_edge("generate_structure", END)

    return workflow
