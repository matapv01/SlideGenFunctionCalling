"""Shared deterministic data/prompt utilities for SlideGen tool-call training and eval."""
from __future__ import annotations
import hashlib, json, random
from collections import defaultdict
from typing import Any

def split_by_doc(samples:list[dict],eval_ratio=.1,test_ratio=.1,seed=42):
    """Stable document-level train/eval/test split."""
    groups=defaultdict(list)
    for i,row in enumerate(samples): groups[str(row.get("doc_id",f"sample-{i}"))].append(row)
    out={"train":[],"eval":[],"test":[]}
    for doc,rows in groups.items():
        value=int(hashlib.sha256(f"{seed}:{doc}".encode()).hexdigest()[:8],16)%10000/10000
        key="test" if value<test_ratio else ("eval" if value<test_ratio+eval_ratio else "train")
        out[key].extend(rows)
    return out

_SCHEMA_MAPPING_KEYS = {
    "$defs",
    "definitions",
    "dependentSchemas",
    "patternProperties",
    "properties",
}
_SCHEMA_LIST_KEYS = {"allOf", "anyOf", "oneOf", "prefixItems"}
_SCHEMA_SINGLE_KEYS = {
    "additionalProperties",
    "contentSchema",
    "contains",
    "else",
    "if",
    "items",
    "not",
    "propertyNames",
    "then",
    "unevaluatedItems",
    "unevaluatedProperties",
}


def _compact_schema(schema: Any) -> Any:
    """Drop verbose schema annotations without deleting user-defined field names."""
    if not isinstance(schema, dict):
        return schema

    compacted = {}
    for key, value in schema.items():
        if key in {"description", "title"}:
            continue
        if key in _SCHEMA_MAPPING_KEYS and isinstance(value, dict):
            compacted[key] = {
                name: _compact_schema(child) for name, child in value.items()
            }
        elif key in _SCHEMA_LIST_KEYS and isinstance(value, list):
            compacted[key] = [_compact_schema(child) for child in value]
        elif key in _SCHEMA_SINGLE_KEYS:
            if isinstance(value, list):
                compacted[key] = [_compact_schema(child) for child in value]
            else:
                compacted[key] = _compact_schema(value)
        elif key == "dependencies" and isinstance(value, dict):
            compacted[key] = {
                name: _compact_schema(child) if isinstance(child, dict) else child
                for name, child in value.items()
            }
        else:
            # Defaults/examples and extension data are values, not schemas.
            compacted[key] = value
    return compacted


def _compact_value(value: Any):
    """Backward-compatible name for schema-aware compaction."""
    return _compact_schema(value)

def compact_tool(tool: dict) -> dict:
    function = tool["function"]
    parameters = function.get("parameters", {})
    return {
        "type": "function",
        "function": {
            "name": function["name"],
            "parameters": _compact_schema(parameters),
        },
    }

def select_tools(sample:dict,tools_dict:dict,flat_tools:dict,seed=42,count=6):
    """Always include gold tool; choose deterministic same-category distractors."""
    correct=sample["tool_call"]["name"]
    names=[t.name for t in tools_dict.get(sample["category"],[]) if t.name in flat_tools and t.name!=correct]
    rng=random.Random(f"{seed}:{sample.get('doc_id')}:{sample.get('slide_index')}:{correct}")
    rng.shuffle(names)
    selected=([correct]+names[:max(0,count-1)]) if correct in flat_tools else list(flat_tools)[:count]
    return selected

def build_prompt(tokenizer,sample:dict,seed=42,tool_count=6,compact=True):
    from rl.slidegen_adapter import (
        TOOLS_DICT,
        QWEN_GENERATOR_SYSTEM_PROMPT,
        build_generator_human_prompt,
        format_tool_for_qwen,
    )
    flat={t.name:t for tools in TOOLS_DICT.values() for t in tools}
    correct=sample["tool_call"]["name"]
    names=select_tools(sample,TOOLS_DICT,flat,seed,tool_count)
    tools=[format_tool_for_qwen(flat[name]) for name in names]
    if compact: tools=[compact_tool(tool) for tool in tools]
    design = (sample.get("design_instruction") or "")[:600]
    user = build_generator_human_prompt(
        deck_style_contract=(sample.get("style_context") or "")[:500],
        slide_topic=(sample.get("slide_topic") or sample.get("content") or "")[:160],
        slide_plan=design,
        design_instruction=design,
        slide_content=(sample.get("slide_content") or sample.get("content", ""))[:1200],
        assigned_tool_name=correct,
        slide_index=int(sample.get("slide_index", 0)),
        deck_length=int(sample.get("deck_length", 1)),
    )
    messages = [
        {"role": "system", "content": QWEN_GENERATOR_SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]
    prompt = tokenizer.apply_chat_template(
        messages,
        tools=tools,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    return prompt, names

def completion_text(sample:dict)->str:
    return f"<tool_call>{json.dumps(sample['tool_call'],ensure_ascii=False,separators=(',',':'))}</tool_call>"
