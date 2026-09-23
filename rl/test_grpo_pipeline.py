from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
    tool_matches_image_mode,
)
from backend.workflows.slidegen_workflow.nodes.section_batch_orchestrator import (
    assign_layouts,
)
from backend.workflows.slidegen_workflow.tools.tool_des_xml import TOOLS_DICT
from rl.rewards.composite_reward import slidegen_composite_reward
from rl.train import _normalise_jobs, _split_documents
from scripts.generate_challenge_dataset import load_offline_documents


def test_offline_split_is_document_grouped():
    documents = load_offline_documents()
    train_documents, eval_documents = _split_documents(documents)
    train_ids = {doc[0]["source_doc_id"] for doc in train_documents}
    eval_ids = {doc[0]["source_doc_id"] for doc in eval_documents}
    assert train_ids.isdisjoint(eval_ids)
    assert len(train_documents) + len(eval_documents) == len(documents)


def test_layout_assignment_uses_only_no_image_tools():
    document = load_offline_documents()[0]
    jobs = _normalise_jobs(document)
    assigned = assign_layouts(
        {"slide_jobs": jobs},
        {"configurable": {"tools_dict": TOOLS_DICT, "tool_retriever": None}},
    )["slide_jobs"]
    by_name = {
        tool.name: tool
        for tools in TOOLS_DICT.values()
        for tool in tools
    }
    assert all(job.get("preferred_tool_name") for job in assigned)
    assert all(
        tool_matches_image_mode(by_name[job["preferred_tool_name"]], "none", 0)
        for job in assigned
    )


def test_wrong_assigned_tool_is_rejected_before_rendering():
    completion = (
        '<tool_call>{"name":"invented_tool","arguments":{"title":"x"}}'
        "</tool_call>"
    )
    assert slidegen_composite_reward(
        [""],
        [completion],
        assigned_tool_name=["expected_tool"],
        source_content=["x"],
        deck_style=[{}],
    ) == [-2.0]
