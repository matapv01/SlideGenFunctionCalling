"""Benchmark the frozen OCR/CV rules copied from ``slidegen-paper.ipynb``.

This is an offline PNG benchmark. It must not be confused with the production
executor and XML/browser overflow gates, which require generated XML artifacts.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from paddleocr import PaddleOCR
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from train_vit_multilabel import CRITERIA, load_split


RULE_CRITERIA = ["mau_nen", "size_chu", "de_nhau", "tran_chu"]
MARGIN = 2
CONTRAST_THRESHOLD = 4.5
MIN_BOX_AREA_RATIO = 0.0005
MIN_HEIGHT_RATIO = 0.023
OVERLAP_RATIO_THRESHOLD = 0.2
SUSPECT_HEIGHT_RATIO = 1.5
CROP_PADDING_RATIO = 0.15
CROP_PADDING_MIN = 8
ROW_GAP_RATIO = 0.6


def parse_args() -> argparse.Namespace:
    root = Path(__file__).parent / "experiments" / "train_test_protocol"
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parent / "data")
    parser.add_argument("--test-csv", type=Path, default=root / "data" / "test_dataset.csv")
    parser.add_argument("--output-dir", type=Path, default=root / "frozen_ocr_rules")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def valid_boxes(result, score_threshold: float):
    rows = []
    for item in result:
        polygons = item.get("dt_polys", [])
        texts = item.get("rec_texts", [None] * len(polygons))
        scores = item.get("rec_scores", [None] * len(polygons))
        for polygon, text, score in zip(polygons, texts, scores):
            if score is None or float(score) < score_threshold:
                continue
            if text is None or not str(text).strip():
                continue
            rows.append((np.asarray(polygon, dtype=np.float32), str(text), float(score)))
    return rows


def bounds(points, width: int, height: int):
    xs, ys = points[:, 0], points[:, 1]
    return (
        max(0, int(xs.min())),
        max(0, int(ys.min())),
        min(width, int(xs.max())),
        min(height, int(ys.max())),
    )


def box_height(points) -> float:
    return float((np.linalg.norm(points[0] - points[3]) + np.linalg.norm(points[1] - points[2])) / 2)


def relative_luminance(rgb):
    values = np.asarray(rgb, dtype=np.float64) / 255.0
    values = np.where(values <= 0.03928, values / 12.92, ((values + 0.055) / 1.055) ** 2.4)
    return float(0.2126 * values[0] + 0.7152 * values[1] + 0.0722 * values[2])


def contrast_ratio(first, second) -> float:
    l1, l2 = relative_luminance(first), relative_luminance(second)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def split_text_background(roi_rgb):
    if roi_rgb.size == 0:
        return None, None
    pixels = cv2.cvtColor(roi_rgb, cv2.COLOR_RGB2LAB).astype(np.float32).reshape(-1, 3)
    if len(pixels) < 60:
        return None, None
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5)
    try:
        _, labels, _ = cv2.kmeans(pixels, 2, None, criteria, 4, cv2.KMEANS_PP_CENTERS)
    except cv2.error:
        return None, None
    labels = labels.reshape(-1)
    rgb_pixels = roi_rgb.reshape(-1, 3)
    first, second = rgb_pixels[labels == 0], rgb_pixels[labels == 1]
    return (first, second) if len(first) < len(second) else (second, first)


def area(rect) -> int:
    return max(0, rect[2] - rect[0]) * max(0, rect[3] - rect[1])


def overlap_ratio(first, second) -> float:
    intersection = max(0, min(first[2], second[2]) - max(first[0], second[0])) * max(
        0, min(first[3], second[3]) - max(first[1], second[1])
    )
    smaller = min(area(first), area(second))
    return intersection / smaller if smaller else 0.0


def cluster_rows(rectangles):
    if not rectangles:
        return []
    median_height = max(1.0, float(np.median([rect[3] - rect[1] for rect in rectangles])))
    order = sorted(range(len(rectangles)), key=lambda i: (rectangles[i][1] + rectangles[i][3]) / 2)
    rows, current = [], [order[0]]
    previous_center = (rectangles[order[0]][1] + rectangles[order[0]][3]) / 2
    for index in order[1:]:
        center = (rectangles[index][1] + rectangles[index][3]) / 2
        if center - previous_center > median_height * ROW_GAP_RATIO:
            rows.append(current)
            current = [index]
        else:
            current.append(index)
        previous_center = center
    rows.append(current)
    return rows


def overlap_rectangles(first_pass, second_ocr, image, width, height):
    raw = [(bounds(points, width, height), text, score) for points, text, score in valid_boxes(first_pass, 0.1)]
    median_height = float(np.median([rect[3] - rect[1] for rect, _, _ in raw])) if raw else 0.0
    final_rectangles = []
    for rect, _, _ in raw:
        x1, y1, x2, y2 = rect
        if median_height <= 0 or y2 - y1 <= median_height * SUSPECT_HEIGHT_RATIO:
            final_rectangles.append(rect)
            continue
        padding = max(CROP_PADDING_MIN, int((y2 - y1) * CROP_PADDING_RATIO))
        px1, py1 = max(0, x1 - padding), max(0, y1 - padding)
        px2, py2 = min(width, x2 + padding), min(height, y2 + padding)
        crop = image[py1:py2, px1:px2]
        child_rows = valid_boxes(second_ocr.predict(crop), 0.1)
        local_rectangles = [bounds(points, px2 - px1, py2 - py1) for points, _, _ in child_rows]
        rows = cluster_rows(local_rectangles)
        if len(rows) <= 1:
            final_rectangles.append(rect)
            continue
        for row in rows:
            final_rectangles.append(
                (
                    min(local_rectangles[i][0] for i in row) + px1,
                    min(local_rectangles[i][1] for i in row) + py1,
                    max(local_rectangles[i][2] for i in row) + px1,
                    max(local_rectangles[i][3] for i in row) + py1,
                )
            )
    return final_rectangles


def evaluate_image(path: str, first_ocr, second_ocr):
    image = cv2.imread(path)
    if image is None:
        raise ValueError(f"Cannot read {path}")
    height, width = image.shape[:2]
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = first_ocr.predict(path)

    overflow = any(
        points[:, 0].min() < MARGIN
        or points[:, 1].min() < MARGIN
        or points[:, 0].max() > width - MARGIN
        or points[:, 1].max() > height - MARGIN
        for points, _, _ in valid_boxes(result, 0.5)
    )
    small_text = any(box_height(points) < height * MIN_HEIGHT_RATIO for points, _, _ in valid_boxes(result, 0.7))

    minimum_area = max(50, int(height * width * MIN_BOX_AREA_RATIO))
    bad_contrast = False
    contrast_values = []
    for points, _, _ in valid_boxes(result, 0.9):
        x1, y1, x2, y2 = bounds(points, width, height)
        if (x2 - x1) * (y2 - y1) < minimum_area:
            continue
        text_pixels, background_pixels = split_text_background(rgb[y1:y2, x1:x2])
        if text_pixels is None or len(text_pixels) < 20 or len(background_pixels) < 20:
            continue
        value = contrast_ratio(np.median(text_pixels, axis=0), np.median(background_pixels, axis=0))
        contrast_values.append(value)
        bad_contrast = bad_contrast or value < CONTRAST_THRESHOLD

    rectangles = overlap_rectangles(result, second_ocr, image, width, height)
    overlap = any(
        overlap_ratio(rectangles[i], rectangles[j]) > OVERLAP_RATIO_THRESHOLD
        for i in range(len(rectangles))
        for j in range(i + 1, len(rectangles))
    )
    return {
        "mau_nen": int(bad_contrast),
        "mau_chu": 0,
        "size_chu": int(small_text),
        "de_nhau": int(overlap),
        "tran_chu": int(overflow),
        "ocr_boxes": len(valid_boxes(result, 0.1)),
        "minimum_contrast": min(contrast_values) if contrast_values else None,
    }


def criterion_metrics(labels, predictions, names):
    result = {}
    for name in names:
        index = CRITERIA.index(name)
        result[name] = {
            "precision": float(precision_score(labels[:, index], predictions[:, index], zero_division=0)),
            "recall": float(recall_score(labels[:, index], predictions[:, index], zero_division=0)),
            "f1": float(f1_score(labels[:, index], predictions[:, index], zero_division=0)),
            "accuracy": float(accuracy_score(labels[:, index], predictions[:, index])),
        }
    indexes = [CRITERIA.index(name) for name in names]
    result["macro_covered"] = {
        "precision": float(precision_score(labels[:, indexes], predictions[:, indexes], average="macro", zero_division=0)),
        "recall": float(recall_score(labels[:, indexes], predictions[:, indexes], average="macro", zero_division=0)),
        "f1": float(f1_score(labels[:, indexes], predictions[:, indexes], average="macro", zero_division=0)),
    }
    return result


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = args.output_dir / "predictions.partial.jsonl"
    completed = {}
    if args.resume and progress_path.exists():
        for line in progress_path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            completed[row["local_path"]] = row

    frame = load_split(args.test_csv, args.data_dir)
    first_ocr = PaddleOCR(
        device=args.device,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )
    second_ocr = PaddleOCR(
        device=args.device,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        det_db_unclip_ratio=1.2,
        det_db_box_thresh=0.5,
    )
    started = time.perf_counter()
    for index, row in frame.iterrows():
        path = row["local_path"]
        if path in completed:
            continue
        output = {"local_path": path, **evaluate_image(path, first_ocr, second_ocr)}
        with progress_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(output, ensure_ascii=False) + "\n")
        completed[path] = output
        print(json.dumps({"processed": index + 1, "total": len(frame), "path": path}), flush=True)

    outputs = [completed[path] for path in frame["local_path"]]
    predictions = np.asarray([[row[name] for name in CRITERIA] for row in outputs], dtype=np.int64)
    labels = frame[CRITERIA].to_numpy(dtype=np.int64)
    slide_labels = (labels.sum(axis=1) > 0).astype(np.int64)
    slide_predictions = (predictions.sum(axis=1) > 0).astype(np.int64)
    result = {
        "scope": "offline frozen OCR/CV rules on rendered PNGs",
        "test_samples": len(frame),
        "covered_criteria": RULE_CRITERIA,
        "uncovered_criteria": ["mau_chu"],
        "fixed_thresholds": {
            "edge_margin_px": MARGIN,
            "wcag_contrast": CONTRAST_THRESHOLD,
            "minimum_text_height_ratio": MIN_HEIGHT_RATIO,
            "overlap_ratio": OVERLAP_RATIO_THRESHOLD,
        },
        "per_criterion": criterion_metrics(labels, predictions, RULE_CRITERIA),
        "slide_level": {
            "precision": float(precision_score(slide_labels, slide_predictions, zero_division=0)),
            "recall": float(recall_score(slide_labels, slide_predictions, zero_division=0)),
            "f1": float(f1_score(slide_labels, slide_predictions, zero_division=0)),
            "accuracy": float(accuracy_score(slide_labels, slide_predictions)),
        },
        "elapsed_seconds_this_run": time.perf_counter() - started,
    }
    (args.output_dir / "metrics.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    output_frame = frame[["path", "local_path", *CRITERIA]].copy()
    for index, name in enumerate(CRITERIA):
        output_frame[f"rule_prediction_{name}"] = predictions[:, index]
    output_frame["ocr_boxes"] = [row["ocr_boxes"] for row in outputs]
    output_frame["minimum_contrast"] = [row["minimum_contrast"] for row in outputs]
    output_frame.to_csv(args.output_dir / "predictions.csv", index=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
