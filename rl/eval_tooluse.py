"""Offline metrics and CLI for SlideGen function-call responses."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TAG = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.IGNORECASE | re.DOTALL)
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
METRICS = (
    "parse_success",
    "format_exact",
    "tool_name_accuracy",
    "valid_tool_rate",
    "argument_key_precision",
    "argument_key_recall",
    "argument_value_f1",
    "arguments_exact",
    "exact_match",
    "has_extra_text",
    "response_chars",
    "missing_argument_count",
    "extra_argument_count",
)


def stable_holdout(samples: list[dict], ratio: float = 0.2, seed: int = 42) -> list[dict]:
    """Select a deterministic whole-document holdout, including for tiny ratios."""
    if not 0 <= ratio <= 1:
        raise ValueError("holdout ratio must be between 0 and 1")
    documents: dict[str, list[dict]] = defaultdict(list)
    for index, row in enumerate(samples):
        doc_id = str(row.get("doc_id", f"sample-{index}"))
        documents[doc_id].append(row)
    if not documents or ratio == 0:
        return []

    target_count = min(len(documents), max(1, round(len(documents) * ratio)))
    selected = set(
        sorted(
            documents,
            key=lambda doc_id: (
                hashlib.sha256(f"{seed}:{doc_id}".encode()).digest(),
                doc_id,
            ),
        )[:target_count]
    )
    return [
        row
        for index, row in enumerate(samples)
        if str(row.get("doc_id", f"sample-{index}")) in selected
    ]


def parse_prediction(text: str | None) -> dict[str, Any]:
    """Parse a JSON function call, optionally wrapped in a tool-call tag."""
    text = text or ""
    tagged = TAG.findall(text)
    candidates = list(reversed(tagged)) if tagged else [text.strip()]
    error = "no_json_object"
    for candidate in candidates:
        candidate = re.sub(
            r"^```(?:json)?\s*|\s*```$", "", candidate.strip(), flags=re.IGNORECASE
        )
        starts = [0, *(match.start() for match in re.finditer(r"\{", candidate))]
        for start in dict.fromkeys(starts):
            try:
                value, consumed = json.JSONDecoder().raw_decode(candidate[start:])
            except json.JSONDecodeError as exc:
                error = str(exc)
                continue
            if not isinstance(value, dict):
                continue
            arguments = value.get("arguments", {})
            call = {
                "name": value.get("name"),
                "arguments": arguments if isinstance(arguments, dict) else {},
            }
            has_extra_text = bool(
                candidate[:start].strip() or candidate[start + consumed :].strip()
            )
            if tagged and TAG.fullmatch(text.strip()) is None:
                has_extra_text = True
            exact = bool(
                re.fullmatch(
                    r"\s*<tool_call>\s*\{.*\}\s*</tool_call>\s*",
                    text,
                    re.DOTALL,
                )
            ) and not has_extra_text
            return {
                "call": call,
                "parse_error": None,
                "format_exact": exact,
                "has_extra_text": has_extra_text,
            }
    return {
        "call": None,
        "parse_error": error,
        "format_exact": False,
        "has_extra_text": bool(text.strip()),
    }


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        flattened = {}
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            flattened.update(flatten(child, child_prefix))
        return flattened
    if isinstance(value, list):
        flattened = {}
        for index, child in enumerate(value):
            flattened.update(flatten(child, f"{prefix}[{index}]"))
        return flattened
    return {prefix: value}


def equal(predicted: Any, expected: Any) -> bool:
    if isinstance(expected, float) and isinstance(predicted, (int, float)):
        return math.isclose(float(predicted), expected, rel_tol=1e-5, abs_tol=1e-6)
    if (
        isinstance(expected, str)
        and isinstance(predicted, str)
        and HEX.fullmatch(expected)
        and HEX.fullmatch(predicted)
    ):
        return expected.lower() == predicted.lower()
    return predicted == expected


def score_response(response: str, sample: dict, valid_tools=None) -> dict[str, Any]:
    parsed = parse_prediction(response)
    predicted = parsed["call"] or {"name": None, "arguments": {}}
    expected = sample["tool_call"]
    predicted_args = flatten(predicted["arguments"])
    expected_args = flatten(expected.get("arguments", {}))
    predicted_keys = set(predicted_args)
    expected_keys = set(expected_args)
    matched = sum(
        equal(predicted_args[key], expected_args[key])
        for key in predicted_keys & expected_keys
    )
    precision = (
        matched / len(predicted_keys)
        if predicted_keys
        else (1.0 if not expected_keys else 0.0)
    )
    recall = matched / len(expected_keys) if expected_keys else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    name_matches = predicted["name"] == expected["name"]
    arguments_match = predicted["arguments"] == expected.get("arguments", {})
    return {
        "parse_success": float(parsed["call"] is not None),
        "format_exact": float(parsed["format_exact"]),
        "tool_name_accuracy": float(name_matches),
        "valid_tool_rate": float(
            isinstance(predicted["name"], str)
            and bool(predicted["name"])
            and (valid_tools is None or predicted["name"] in valid_tools)
        ),
        "argument_key_precision": precision,
        "argument_key_recall": recall,
        "argument_value_f1": f1,
        "arguments_exact": float(arguments_match),
        "exact_match": float(name_matches and arguments_match),
        "extra_argument_count": len(predicted_keys - expected_keys),
        "missing_argument_count": len(expected_keys - predicted_keys),
        "response_chars": len(response or ""),
        "has_extra_text": float(parsed["has_extra_text"]),
        "parse_error": parsed["parse_error"],
        "predicted_tool": predicted["name"],
        "gold_tool": expected["name"],
        "category": sample.get("category", "unknown"),
    }


def bootstrap_ci(values: list[float], count: int = 2000, seed: int = 42) -> list[float]:
    if count < 1:
        raise ValueError("bootstrap count must be positive")
    if not values:
        return [0.0, 0.0]
    rng = random.Random(seed)
    means = sorted(
        sum(rng.choice(values) for _ in values) / len(values)
        for _ in range(count)
    )
    lower_index = int(0.025 * (count - 1))
    upper_index = int(0.975 * (count - 1))
    return [means[lower_index], means[upper_index]]


def summarize(rows: list[dict], bootstraps: int = 2000, seed: int = 42) -> dict[str, Any]:
    def mean(group: list[dict], key: str) -> float:
        return sum(float(row[key]) for row in group) / len(group) if group else 0.0

    overall = {key: mean(rows, key) for key in METRICS}
    overall["exact_match_ci95"] = bootstrap_ci(
        [row["exact_match"] for row in rows], bootstraps, seed
    )
    breakdown = {}
    for field in ("category", "gold_tool"):
        groups: dict[str, list[dict]] = defaultdict(list)
        for row in rows:
            groups[str(row[field])].append(row)
        breakdown[field] = {
            name: {
                "count": len(group),
                **{key: mean(group, key) for key in METRICS[:9]},
            }
            for name, group in sorted(groups.items())
        }

    confusion = Counter(
        (row["gold_tool"], str(row["predicted_tool"])) for row in rows
    )
    return {
        "sample_count": len(rows),
        "overall": overall,
        "breakdown": breakdown,
        "tool_confusion": [
            {"gold": gold, "predicted": predicted, "count": count}
            for (gold, predicted), count in confusion.most_common()
            if gold != predicted
        ],
        "parse_errors": dict(
            Counter(row["parse_error"] or "parsed" for row in rows)
        ),
    }


def paired_compare(
    rows: list[dict], baseline: list[dict], bootstraps: int = 2000, seed: int = 42
) -> dict[str, Any]:
    if len(rows) != len(baseline):
        raise ValueError("candidate and baseline counts differ")
    deltas = [
        candidate["exact_match"] - control["exact_match"]
        for candidate, control in zip(rows, baseline, strict=True)
    ]
    return {
        "exact_match_delta": statistics.fmean(deltas) if deltas else 0.0,
        "exact_match_delta_ci95": bootstrap_ci(deltas, bootstraps, seed),
        "candidate_wins": sum(delta > 0 for delta in deltas),
        "baseline_wins": sum(delta < 0 for delta in deltas),
        "ties": sum(delta == 0 for delta in deltas),
    }


def load_responses(path: str | Path) -> list[str]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Response file not found: {path}. Provide a JSON or JSONL file with --responses."
        )
    with path.open(encoding="utf-8") as response_file:
        if path.suffix.lower() == ".jsonl":
            data = [json.loads(line) for line in response_file if line.strip()]
        else:
            data = json.load(response_file)
    if isinstance(data, dict):
        data = data.get("responses", data.get("results"))
    if not isinstance(data, list):
        raise ValueError("Response file must contain a list or an object with responses/results")

    responses = []
    for index, item in enumerate(data):
        if isinstance(item, str):
            response = item
        elif isinstance(item, dict):
            response = item.get("response", item.get("completion", item.get("text")))
        else:
            response = None
        if not isinstance(response, str):
            raise ValueError(f"Response item {index} must be a string or contain response text")
        responses.append(response)
    return responses


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Score SlideGen function-call responses")
    parser.add_argument("--responses", required=True)
    parser.add_argument("--baseline_responses")
    parser.add_argument(
        "--data_path", default=str(ROOT / "rl/data/sft_function_call_dataset.json")
    )
    parser.add_argument("--output_dir")
    parser.add_argument(
        "--split",
        choices=("all", "holdout", "train", "eval", "test"),
        default="test",
    )
    parser.add_argument("--holdout_ratio", type=float, default=0.2)
    parser.add_argument("--eval_ratio", type=float, default=0.1)
    parser.add_argument("--test_ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max_samples", type=int)
    parser.add_argument("--bootstrap_samples", type=int, default=2000)
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    if args.max_samples is not None and args.max_samples < 1:
        raise ValueError("max_samples must be positive")
    if args.bootstrap_samples < 1:
        raise ValueError("bootstrap_samples must be positive")

    with open(args.data_path, encoding="utf-8") as dataset_file:
        samples = json.load(dataset_file)
    if not isinstance(samples, list) or any(not isinstance(row, dict) for row in samples):
        raise ValueError("Evaluation dataset must be a list of sample objects")

    if args.split == "holdout":
        selected = stable_holdout(samples, args.holdout_ratio, args.seed)
    elif args.split in {"train", "eval", "test"}:
        from rl.toolcall_data import split_by_doc

        selected = split_by_doc(
            samples, args.eval_ratio, args.test_ratio, args.seed
        )[args.split]
    else:
        selected = samples
    if args.max_samples is not None:
        selected = selected[: args.max_samples]

    responses = load_responses(args.responses)
    if len(responses) != len(selected):
        raise ValueError(f"expected {len(selected)} responses, got {len(responses)}")

    from rl.slidegen_adapter import TOOLS_DICT

    valid_tools = {
        tool.name for tools in TOOLS_DICT.values() for tool in tools
    }
    rows = [
        {
            "index": index,
            **score_response(response, sample, valid_tools),
            "doc_id": sample.get("doc_id"),
            "slide_index": sample.get("slide_index"),
            "response": response,
        }
        for index, (response, sample) in enumerate(
            zip(responses, selected, strict=True)
        )
    ]
    report = {
        "config": vars(args),
        "dataset": {"total": len(samples), "evaluated": len(selected)},
        "metrics": summarize(rows, args.bootstrap_samples, args.seed),
    }

    if args.baseline_responses:
        baseline_responses = load_responses(args.baseline_responses)
        if len(baseline_responses) != len(selected):
            raise ValueError("baseline response count differs from selected samples")
        baseline_rows = [
            score_response(response, sample, valid_tools)
            for response, sample in zip(baseline_responses, selected, strict=True)
        ]
        report["baseline"] = summarize(
            baseline_rows, args.bootstrap_samples, args.seed
        )
        report["paired_comparison"] = paired_compare(
            rows, baseline_rows, args.bootstrap_samples, args.seed
        )

    output_dir = Path(args.output_dir or ROOT / "rl/log/evaluation")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "evaluation_report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    predictions_path = output_dir / "predictions.jsonl"
    with predictions_path.open("w", encoding="utf-8") as predictions_file:
        for row in rows:
            predictions_file.write(json.dumps(row, ensure_ascii=False) + "\n")

    metrics = report["metrics"]["overall"]
    print(
        f"Evaluated {len(rows)} | parse={metrics['parse_success']:.3f} "
        f"tool={metrics['tool_name_accuracy']:.3f} "
        f"args_f1={metrics['argument_value_f1']:.3f} "
        f"exact={metrics['exact_match']:.3f}"
    )
    print(f"Report: {report_path}")
    print(f"Predictions: {predictions_path}")


if __name__ == "__main__":
    main()
