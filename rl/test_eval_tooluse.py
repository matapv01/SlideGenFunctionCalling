import json
import sys

import pytest

from rl.eval_tooluse import (
    load_responses,
    main,
    parse_prediction,
    score_response,
    stable_holdout,
)
from rl.toolcall_data import split_by_doc

SAMPLE = {
    "category": "INTRO_TOOLS",
    "doc_id": 1,
    "tool_call": {
        "name": "make_slide",
        "arguments": {
            "title": "Hi",
            "color": "#FFFFFF",
            "size": 1.0,
        },
    },
}


def test_parse_tagged_and_raw_json():
    value = {"name": "make_slide", "arguments": {"title": "Hi"}}
    tagged = parse_prediction(f"<tool_call>{json.dumps(value)}</tool_call>")
    raw = parse_prediction(json.dumps(value))

    assert tagged["call"] == value
    assert raw["call"] == value


def test_score_separates_tool_and_arguments():
    response = (
        '<tool_call>{"name":"make_slide","arguments":'
        '{"title":"Hi","color":"#ffffff","extra":2}}</tool_call>'
    )
    result = score_response(response, SAMPLE, {"make_slide"})

    assert result["tool_name_accuracy"] == 1
    assert result["argument_key_recall"] == 2 / 3
    assert result["extra_argument_count"] == 1
    assert result["exact_match"] == 0


def test_invalid_output_is_scored_not_crashed():
    result = score_response("not json", SAMPLE)
    assert result["parse_success"] == 0


def test_raw_json_is_not_misclassified_as_extra_text():
    call = json.dumps(SAMPLE["tool_call"])
    raw_result = score_response(call, SAMPLE)
    prefixed_result = score_response(f"Here is the call: {call}", SAMPLE)
    trailing_text = score_response(f"<tool_call>{call} trailing</tool_call>", SAMPLE)
    non_string_tool = score_response(
        '<tool_call>{"name":[],"arguments":{}}</tool_call>', SAMPLE, {"make_slide"}
    )

    assert raw_result["format_exact"] == 0
    assert raw_result["has_extra_text"] == 0
    assert prefixed_result["has_extra_text"] == 1
    assert trailing_text["format_exact"] == 0
    assert trailing_text["has_extra_text"] == 1
    assert non_string_tool["valid_tool_rate"] == 0


def test_holdout_is_deterministic_and_document_grouped():
    samples = [
        {"doc_id": doc_id, "slide_index": slide_index}
        for doc_id in range(20)
        for slide_index in range(2)
    ]
    result = stable_holdout(samples, 0.2, 42)

    assert result == stable_holdout(samples, 0.2, 42)
    document_ids = {row["doc_id"] for row in result}
    assert all(
        sum(row["doc_id"] == doc_id for row in result) == 2
        for doc_id in document_ids
    )


def test_tiny_holdout_ratio_still_selects_whole_documents():
    samples = [
        {"doc_id": doc_id, "slide_index": slide_index}
        for doc_id in range(20)
        for slide_index in range(2)
    ]
    selected = stable_holdout(samples, ratio=0.00001, seed=42)

    assert len(selected) == 2
    assert len({row["doc_id"] for row in selected}) == 1


def test_document_split_partitions_every_row_once():
    samples = [
        {"doc_id": doc_id, "slide_index": slide_index}
        for doc_id in range(30)
        for slide_index in range(2)
    ]
    splits = split_by_doc(samples, eval_ratio=0.2, test_ratio=0.2, seed=42)

    split_documents = [
        {row["doc_id"] for row in rows} for rows in splits.values()
    ]
    assert all(
        split_documents[left].isdisjoint(split_documents[right])
        for left in range(len(split_documents))
        for right in range(left + 1, len(split_documents))
    )
    assert sorted(
        (row["doc_id"], row["slide_index"])
        for rows in splits.values()
        for row in rows
    ) == sorted((row["doc_id"], row["slide_index"]) for row in samples)
    with pytest.raises(ValueError, match="must not exceed 1"):
        split_by_doc(samples, eval_ratio=0.7, test_ratio=0.4)


def test_load_responses_accepts_jsonl_records_and_rejects_bad_shapes(tmp_path):
    response_file = tmp_path / "responses.jsonl"
    response_file.write_text(
        '{"completion":"first"}\n"second"\n', encoding="utf-8"
    )
    assert load_responses(response_file) == ["first", "second"]

    malformed = tmp_path / "malformed.json"
    malformed.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="must contain a list"):
        load_responses(malformed)


def test_evaluator_cli_writes_report_and_paired_comparison(tmp_path, monkeypatch):
    data_file = tmp_path / "dataset.json"
    response_file = tmp_path / "responses.json"
    baseline_file = tmp_path / "baseline.json"
    output_dir = tmp_path / "evaluation"
    data_file.write_text(json.dumps([SAMPLE]), encoding="utf-8")
    response_file.write_text(
        json.dumps(
            [
                '<tool_call>{"name":"make_slide","arguments":'
                '{"title":"Hi","color":"#FFFFFF","size":1.0}}</tool_call>'
            ]
        ),
        encoding="utf-8",
    )
    baseline_file.write_text(json.dumps(["not json"]), encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "eval_tooluse",
            "--responses",
            str(response_file),
            "--baseline_responses",
            str(baseline_file),
            "--data_path",
            str(data_file),
            "--split",
            "all",
            "--output_dir",
            str(output_dir),
            "--bootstrap_samples",
            "20",
        ],
    )

    main()

    report = json.loads((output_dir / "evaluation_report.json").read_text())
    predictions = (output_dir / "predictions.jsonl").read_text().splitlines()
    assert report["metrics"]["overall"]["exact_match"] == 1.0
    assert report["paired_comparison"]["exact_match_delta"] == 1.0
    assert len(predictions) == 1
