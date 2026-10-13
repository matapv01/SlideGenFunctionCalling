"""Measure how much text each layout field can hold before it overflows, by running the layout itself.

For every XML tool, start from the example arguments in its schema, then binary-search the longest
Vietnamese filler text each text field accepts without the static overflow analyzer (after the
pipeline's auto-fit) reporting an overflow or a box leaving the slide. The result is written to
rl/data/tool_text_capacity.json and surfaced to the generator as "at most ~N characters" hints.

Usage: python scripts/probe_tool_capacity.py
"""

from __future__ import annotations

import ast
import contextlib
import copy
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.workflows.slidegen_workflow.utils.xml_autofit import fit_xml_text  # noqa: E402
from backend.workflows.slidegen_workflow.utils.xml_overflow import analyze_xml_root  # noqa: E402
from rl.slidegen_adapter import TOOLS_DICT, execute_tool  # noqa: E402

OUTPUT = ROOT / "rl" / "data" / "tool_text_capacity.json"
SKIP_KEY = re.compile(r"color|url|image|icon|font|opacity|align|type$|_id$", re.IGNORECASE)
FILLER = ("Việt Nam phát triển kinh tế bền vững nhờ đổi mới sáng tạo và hội nhập quốc tế sâu rộng "
          "trong nhiều lĩnh vực quan trọng của đời sống xã hội hiện đại ngày nay ").split()
UPPER, SAFETY, MAX_ITEMS = 1200, 0.85, 12


def _filler(length: int) -> str:
    words, size = [], 0
    index = 0
    while size < length:
        word = FILLER[index % len(FILLER)]
        words.append(word)
        size += len(word) + 1
        index += 1
    return " ".join(words)[:length].rstrip()


def _example(description: str | None):
    match = re.search(r"example:\s*(.+)$", description or "", flags=re.DOTALL)
    if not match:
        return None
    raw = match.group(1).strip()
    try:
        return ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return raw.strip("'\"")


def _is_prose(value) -> bool:
    return isinstance(value, str) and len(value) >= 3 and not re.fullmatch(r"[\d\s.,%$+\-/:]+", value)


def _leaves(arguments: dict) -> list[tuple[str, str | None]]:
    """(field, subfield) pairs holding prose; subfield is set for lists of objects."""
    found = []
    for key, value in arguments.items():
        if SKIP_KEY.search(key):
            continue
        if _is_prose(value):
            found.append((key, None))
        elif isinstance(value, list) and value:
            if all(_is_prose(item) for item in value):
                found.append((key, None))
            elif all(isinstance(item, dict) for item in value):
                for sub in value[0]:
                    if not SKIP_KEY.search(sub) and all(_is_prose(item.get(sub)) for item in value):
                        found.append((key, sub))
    return found


def _with_length(arguments: dict, field: str, sub: str | None, length: int) -> dict:
    probe = copy.deepcopy(arguments)
    text = _filler(length)
    value = probe[field]
    if isinstance(value, str):
        probe[field] = text
    elif sub is None:
        probe[field] = [text for _ in value]
    else:
        for item in value:
            item[sub] = text
    return probe


def _overflows(name: str, arguments: dict) -> bool:
    with contextlib.redirect_stdout(io.StringIO()):
        xml = execute_tool({"name": name, "arguments": arguments})
    xml, _ = fit_xml_text(xml)
    return any(record["overflow"] for record in analyze_xml_root(ET.fromstring(xml)))


def probe_tool(tool) -> dict:
    arguments = {}
    for key, field in tool.args_schema.model_fields.items():
        example = _example(field.description)
        if example is not None and not re.search(r"color|url", key, re.IGNORECASE):
            arguments[key] = example
    result = {}
    try:
        baseline_overflow = _overflows(tool.name, arguments)
    except Exception as error:  # noqa: BLE001
        return {"_error": str(error)[:200]}
    for field, sub in _leaves(arguments):
        low, high = 0, UPPER
        try:
            if not _overflows(tool.name, _with_length(arguments, field, sub, UPPER)):
                continue  # effectively unbounded: no hint needed
            while high - low > 4:
                middle = (low + high) // 2
                if _overflows(tool.name, _with_length(arguments, field, sub, middle)):
                    high = middle
                else:
                    low = middle
        except Exception:  # noqa: BLE001
            continue
        if low < 8:
            continue  # the example layout itself is already overflowing; no reliable measurement
        value = arguments[field]
        entry = {"max_chars": int(low * SAFETY // 5 * 5)}
        if isinstance(value, list):
            entry["per_item"] = True
            entry["items"] = len(value)
        result[field if sub is None else f"{field}.{sub}"] = entry
    if baseline_overflow:
        result["_baseline_overflow"] = True
    return result


def _with_count(arguments: dict, field: str, count: int) -> dict:
    probe = copy.deepcopy(arguments)
    items = probe[field]
    probe[field] = [copy.deepcopy(items[index % len(items)]) for index in range(count)]
    return probe


def probe_item_counts(tool, arguments: dict) -> dict:
    """Largest number of example-sized items each list field holds before the layout overflows."""
    counts = {}
    for field, value in arguments.items():
        if SKIP_KEY.search(field) or not isinstance(value, list) or not value:
            continue
        if not (all(_is_prose(item) for item in value) or all(isinstance(item, dict) for item in value)):
            continue
        best = None
        for count in range(1, MAX_ITEMS + 1):
            try:
                if _overflows(tool.name, _with_count(arguments, field, count)):
                    break
            except Exception:  # noqa: BLE001
                break
            best = count
        if best is not None and best < MAX_ITEMS:
            counts[field] = best
    return counts


def joint_factor(tool, arguments: dict, capacity: dict) -> float:
    """Shrink every measured capacity by one factor until all fields fit at the same time."""
    def filled(factor: float) -> dict:
        probe = copy.deepcopy(arguments)
        for path, entry in capacity.items():
            field, _, sub = path.partition(".")
            probe = _with_length(probe, field, sub or None, max(4, int(entry["max_chars"] * factor)))
        return probe

    try:
        if not _overflows(tool.name, filled(1.0)):
            return 1.0
        low, high = 0.2, 1.0
        if _overflows(tool.name, filled(low)):
            return low
        while high - low > 0.04:
            middle = (low + high) / 2
            if _overflows(tool.name, filled(middle)):
                high = middle
            else:
                low = middle
        return low
    except Exception:  # noqa: BLE001
        return 1.0


def _example_arguments(tool) -> dict:
    arguments = {}
    for key, field in tool.args_schema.model_fields.items():
        example = _example(field.description)
        if example is not None and not re.search(r"color|url", key, re.IGNORECASE):
            arguments[key] = example
    return arguments


def main() -> None:
    capacity = {}
    for tools in TOOLS_DICT.values():
        for tool in tools:
            entry = probe_tool(tool)
            fields = {k: v for k, v in entry.items() if isinstance(v, dict)}
            arguments = _example_arguments(tool)
            # Individually measured capacities overstate what fits when every field is long at once.
            factor = joint_factor(tool, arguments, fields) if fields else 1.0
            for value in fields.values():
                value["max_chars"] = max(5, int(value["max_chars"] * factor // 5 * 5))
            for field, count in probe_item_counts(tool, arguments).items():
                entry.setdefault(field, {})["max_items"] = count
            capacity[tool.name] = entry
            print(tool.name, round(factor, 2), {k: v for k, v in entry.items() if isinstance(v, dict)}, flush=True)
    OUTPUT.write_text(json.dumps(capacity, ensure_ascii=False, indent=1), encoding="utf-8")
    hinted = sum(isinstance(v, dict) for tool in capacity.values() for v in tool.values())
    print(f"{len(capacity)} tools, {hinted} fields with a measured capacity -> {OUTPUT}")


if __name__ == "__main__":
    main()
