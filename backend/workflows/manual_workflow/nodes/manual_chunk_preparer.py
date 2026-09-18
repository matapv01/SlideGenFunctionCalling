from backend.workflows.manual_workflow.graph.stage import State
from backend.domain.canonical_chunks import normalize_canonical_chunks


def prepare_manual_chunks(state: State) -> State:
    """Normalize editor input before it is handed to the shared renderer."""
    normalized = normalize_canonical_chunks(
        state.get("slide_chunks", []),
        slide_positions=state.get("slide_positions", []),
        slide_context_maps=state.get("slide_context_maps", []),
        section_ids=state.get("section_ids", []),
    )
    state.update(normalized)
    return state
