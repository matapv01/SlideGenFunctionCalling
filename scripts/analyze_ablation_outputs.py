#!/usr/bin/env python3
"""Analyze paired ViT warnings, XML complexity, and lexical retention by mode."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from backend.workflows.slidegen_workflow.utils.xml_overflow import analyze_xml_root


MODES = ("full", "no_planner", "no_retriever", "no_planner_no_retriever")
CRITERIA = ("background_color", "text_color", "font_size", "overlap", "text_overflow")
TOKEN_RE = re.compile(r"[^\W_]+(?:[-'][^\W_]+)*", re.UNICODE)
NUMBER_RE = re.compile(r"(?<!\w)\d+(?:[.,]\d+)*(?:\s*%)?")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    return parser.parse_args()


def flatten_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from flatten_strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from flatten_strings(nested)


def tokens(text: str) -> list[str]:
    return [token.casefold() for token in TOKEN_RE.findall(text) if len(token) >= 2]


def multiset_recall(source: list[str], generated: list[str]) -> float | None:
    if not source:
        return None
    source_counts, generated_counts = Counter(source), Counter(generated)
    matched = sum(min(count, generated_counts[token]) for token, count in source_counts.items())
    return matched / sum(source_counts.values())


def number_recall(source: str, generated: str) -> float | None:
    expected = set(NUMBER_RE.findall(source))
    if not expected:
        return None
    observed = set(NUMBER_RE.findall(generated))
    return len(expected & observed) / len(expected)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def float_attr(element: ET.Element, name: str) -> float | None:
    try:
        return float(element.get(name, ""))
    except (TypeError, ValueError):
        return None


def text_box_overlap_count(root: ET.Element) -> int:
    boxes = []
    for element in root.iter():
        if local_name(element.tag) not in {"textbox", "text"}:
            continue
        values = [float_attr(element, name) for name in ("x", "y", "width", "height")]
        if any(value is None for value in values):
            continue
        x, y, width, height = values
        if width <= 0 or height <= 0:
            continue
        boxes.append((x, y, x + width, y + height))

    overlaps = 0
    for index, first in enumerate(boxes):
        for second in boxes[index + 1 :]:
            intersection_width = max(0.0, min(first[2], second[2]) - max(first[0], second[0]))
            intersection_height = max(0.0, min(first[3], second[3]) - max(first[1], second[1]))
            intersection = intersection_width * intersection_height
            if intersection <= 0:
                continue
            first_area = (first[2] - first[0]) * (first[3] - first[1])
            second_area = (second[2] - second[0]) * (second[3] - second[1])
            if intersection / min(first_area, second_area) >= 0.05:
                overlaps += 1
    return overlaps


def out_of_bounds_count(root: ET.Element) -> int:
    width = float(root.get("width", 1600))
    height = float(root.get("height", 900))
    count = 0
    for element in root.iter():
        values = [float_attr(element, name) for name in ("x", "y", "width", "height")]
        if any(value is None for value in values):
            continue
        x, y, element_width, element_height = values
        if x < 0 or y < 0 or x + element_width > width + 0.5 or y + element_height > height + 0.5:
            count += 1
    return count


def safe_mean(values: Iterable[float | None]) -> float | None:
    kept = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    return statistics.fmean(kept) if kept else None


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def rank(values: list[float]) -> np.ndarray:
    order = np.argsort(values)
    ranks = np.empty(len(values), dtype=float)
    start = 0
    while start < len(values):
        end = start
        while end + 1 < len(values) and values[order[end + 1]] == values[order[start]]:
            end += 1
        ranks[order[start : end + 1]] = (start + end) / 2.0
        start = end + 1
    return ranks


def spearman(rows: list[dict[str, Any]], first: str, second: str) -> float | None:
    pairs = [
        (float(row[first]), float(row[second]))
        for row in rows
        if row.get(first) not in (None, "") and row.get(second) not in (None, "")
    ]
    if len(pairs) < 3:
        return None
    x, y = zip(*pairs)
    rx, ry = rank(list(x)), rank(list(y))
    if np.std(rx) == 0 or np.std(ry) == 0:
        return None
    return float(np.corrcoef(rx, ry)[0, 1])


def contact_sheet(root: Path, rows: list[dict[str, Any]], output_path: Path) -> None:
    flagged = sorted(
        (row for row in rows if not int(row["pass"])),
        key=lambda row: max(float(row[f"probability_{criterion}"]) for criterion in CRITERIA),
        reverse=True,
    )
    columns = 4
    tile_width, image_height, label_height = 360, 203, 76
    rows_count = math.ceil(len(flagged) / columns)
    canvas = Image.new("RGB", (columns * tile_width, rows_count * (image_height + label_height)), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=16)
    small = ImageFont.load_default(size=13)
    for index, row in enumerate(flagged):
        x = (index % columns) * tile_width
        y = (index // columns) * (image_height + label_height)
        image_path = root / "evaluation_input" / row["relative_path"]
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            image.thumbnail((tile_width - 8, image_height - 8))
            canvas.paste(image, (x + (tile_width - image.width) // 2, y + 4))
        active = [
            f"{criterion[:3]}={float(row[f'probability_{criterion}']):.2f}"
            for criterion in CRITERIA
            if int(row[f"prediction_{criterion}"])
        ]
        draw.text((x + 6, y + image_height + 3), f"{row['deck']} / {row['slide']}", fill="black", font=font)
        draw.text((x + 6, y + image_height + 27), "  ".join(active), fill="#a21c1c", font=small)
        draw.text(
            (x + 6, y + image_height + 49),
            f"chars={row['generated_text_chars']} elems={row['element_count']} ruleOF={row['rule_overflow_boxes']}",
            fill="#333333",
            font=small,
        )
        draw.rectangle((x, y, x + tile_width - 1, y + image_height + label_height - 1), outline="#b8bec7")
    canvas.save(output_path)


def main() -> None:
    args = parse_args()
    root = args.run_root.resolve()
    output_dir = root / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    predictions_path = root / "vit_evaluation" / "predictions.csv"
    predictions = list(csv.DictReader(predictions_path.open(encoding="utf-8")))
    prediction_by_key = {(row["deck"], row["slide"]): row for row in predictions}

    source_chunks: dict[str, list[Any]] = {}
    for state_path in (root / "decks").glob("*/preprocessed_state.json"):
        source_chunks[state_path.parent.name] = json.loads(state_path.read_text(encoding="utf-8"))["slide_chunks"]

    rows: list[dict[str, Any]] = []
    for xml_path in sorted((root / "decks").glob("*/*/output/xml/*.xml")):
        relative = xml_path.relative_to(root / "decks")
        document, mode, _, _, filename = relative.parts
        slide_number = int(re.search(r"(\d+)", xml_path.stem).group(1))
        prediction = prediction_by_key[(f"{document}/{mode}", f"slide_{slide_number}.png")]
        tree = ET.parse(xml_path)
        xml_root = tree.getroot()
        elements = list(xml_root.iter())
        tag_counts = Counter(local_name(element.tag) for element in elements)
        generated_text = " ".join(
            " ".join(element.itertext())
            for element in elements
            if local_name(element.tag) in {"textbox", "text"}
        )
        chunk = source_chunks[document][slide_number - 1]
        source_text = " ".join(flatten_strings(chunk))
        overflow_records = analyze_xml_root(xml_root)
        font_sizes = [
            float_attr(element, "size")
            for element in elements
            if local_name(element.tag) in {"textbox", "text"} and float_attr(element, "size") is not None
        ]
        row: dict[str, Any] = {
            "document": document,
            "mode": mode,
            "slide_number": slide_number,
            "deck": prediction["deck"],
            "slide": prediction["slide"],
            "relative_path": prediction["relative_path"],
            "pass": int(prediction["pass"]),
            "predicted_defect_count": int(prediction["predicted_defect_count"]),
            "mean_defect_probability": safe_mean(
                float(prediction[f"probability_{criterion}"]) for criterion in CRITERIA
            ),
            "element_count": len(elements) - 1,
            "textbox_count": tag_counts["textbox"] + tag_counts["text"],
            "image_count": tag_counts["image"],
            "svg_count": tag_counts["svg"],
            "shape_count": tag_counts["shape"],
            "line_count": tag_counts["line"],
            "chart_count": sum(tag_counts[tag] for tag in ("chart", "plot", "table")),
            "generated_text_chars": len(generated_text),
            "generated_tokens": len(tokens(generated_text)),
            "source_tokens": len(tokens(source_text)),
            "lexical_token_recall": multiset_recall(tokens(source_text), tokens(generated_text)),
            "number_recall": number_recall(source_text, generated_text),
            "minimum_font_size": min(font_sizes) if font_sizes else None,
            "small_font_boxes_lt18": sum(size < 18 for size in font_sizes),
            "rule_overflow_boxes": sum(record["overflow"] for record in overflow_records),
            "rule_textbox_overlaps": text_box_overlap_count(xml_root),
            "out_of_bounds_elements": out_of_bounds_count(xml_root),
        }
        for criterion in CRITERIA:
            row[f"probability_{criterion}"] = float(prediction[f"probability_{criterion}"])
            row[f"prediction_{criterion}"] = int(prediction[f"prediction_{criterion}"])
        row["hard_overflow_defect"] = int(row["rule_overflow_boxes"] > 0)
        row["hybrid_defect"] = int(
            row["predicted_defect_count"] > 0 or row["hard_overflow_defect"]
        )
        row["hybrid_pass"] = 1 - row["hybrid_defect"]
        rows.append(row)

    mode_rows = []
    for mode in MODES:
        selected = [row for row in rows if row["mode"] == mode]
        mode_rows.append(
            {
                "mode": mode,
                "slides": len(selected),
                "pass_count": sum(row["pass"] for row in selected),
                "pass_rate": safe_mean(row["pass"] for row in selected),
                "hybrid_pass_count": sum(row["hybrid_pass"] for row in selected),
                "hybrid_pass_rate": safe_mean(row["hybrid_pass"] for row in selected),
                "mean_defect_probability": safe_mean(row["mean_defect_probability"] for row in selected),
                "predicted_defect_labels": sum(row["predicted_defect_count"] for row in selected),
                "mean_elements": safe_mean(row["element_count"] for row in selected),
                "mean_textboxes": safe_mean(row["textbox_count"] for row in selected),
                "mean_images": safe_mean(row["image_count"] for row in selected),
                "mean_text_chars": safe_mean(row["generated_text_chars"] for row in selected),
                "mean_minimum_font_size": safe_mean(row["minimum_font_size"] for row in selected),
                "mean_lexical_token_recall": safe_mean(row["lexical_token_recall"] for row in selected),
                "mean_number_recall": safe_mean(row["number_recall"] for row in selected),
                "slides_with_rule_overflow": sum(row["rule_overflow_boxes"] > 0 for row in selected),
                "rule_overflow_boxes": sum(row["rule_overflow_boxes"] for row in selected),
                "slides_with_textbox_overlap": sum(row["rule_textbox_overlaps"] > 0 for row in selected),
                "out_of_bounds_elements": sum(row["out_of_bounds_elements"] for row in selected),
                **{
                    f"vit_{criterion}_flags": sum(row[f"prediction_{criterion}"] for row in selected)
                    for criterion in CRITERIA
                },
            }
        )

    paired_rows = []
    by_position = defaultdict(dict)
    for row in rows:
        by_position[(row["document"], row["slide_number"])][row["mode"]] = row
    for mode in MODES[1:]:
        pairs = [(values["full"], values[mode]) for values in by_position.values() if "full" in values and mode in values]
        paired_rows.append(
            {
                "comparison": f"{mode} - full",
                "pairs": len(pairs),
                "full_fail_variant_pass": sum(not full["pass"] and variant["pass"] for full, variant in pairs),
                "full_pass_variant_fail": sum(full["pass"] and not variant["pass"] for full, variant in pairs),
                "both_pass": sum(full["pass"] and variant["pass"] for full, variant in pairs),
                "both_fail": sum(not full["pass"] and not variant["pass"] for full, variant in pairs),
                "mean_delta_defect_probability": safe_mean(
                    variant["mean_defect_probability"] - full["mean_defect_probability"]
                    for full, variant in pairs
                ),
                "mean_delta_text_chars": safe_mean(
                    variant["generated_text_chars"] - full["generated_text_chars"]
                    for full, variant in pairs
                ),
                "mean_delta_lexical_recall": safe_mean(
                    variant["lexical_token_recall"] - full["lexical_token_recall"]
                    for full, variant in pairs
                    if variant["lexical_token_recall"] is not None and full["lexical_token_recall"] is not None
                ),
            }
        )

    correlation_features = (
        "element_count", "textbox_count", "image_count", "svg_count",
        "generated_text_chars", "minimum_font_size", "small_font_boxes_lt18",
        "rule_overflow_boxes", "rule_textbox_overlaps", "out_of_bounds_elements",
    )
    correlations = {
        feature: {
            "mean_defect_probability": spearman(rows, feature, "mean_defect_probability"),
            "overlap_probability": spearman(rows, feature, "probability_overlap"),
            "overflow_probability": spearman(rows, feature, "probability_text_overflow"),
        }
        for feature in correlation_features
    }

    result = {
        "scope": {"documents": 3, "modes": 4, "slides": len(rows)},
        "mode_summary": mode_rows,
        "paired_comparison": paired_rows,
        "spearman_correlations": correlations,
        "notes": {
            "lexical_token_recall": "Multiset recall of case-folded alphanumeric source-chunk tokens in XML textbox text; it does not measure paraphrase equivalence.",
            "rule_overflow": "Static XML text-box measurement from the frozen pipeline utility, not a human label.",
            "rule_textbox_overlaps": "Exploratory axis-aligned textbox intersections covering at least 5% of the smaller box. This is not a production hard rule and is excluded from hybrid decisions.",
            "hybrid_pass": "Logical OR of the frozen ViT defect decision and the production static text-overflow rule on final XML. Executor/schema-invalid candidates were already rejected during generation.",
        },
    }
    write_csv(output_dir / "slide_features.csv", rows)
    write_csv(output_dir / "mode_summary.csv", mode_rows)
    write_csv(output_dir / "paired_comparison.csv", paired_rows)
    (output_dir / "analysis.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    contact_sheet(root, rows, output_dir / "flagged_contact_sheet.png")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
