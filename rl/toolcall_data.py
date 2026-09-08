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

def _compact_value(value:Any):
    if isinstance(value,dict):
        keep={}
        for key in ("type","anyOf","enum","items","properties","required","default"):
            if key in value: keep[key]=_compact_value(value[key])
        return keep
    if isinstance(value,list): return [_compact_value(x) for x in value]
    return value

def compact_tool(tool:dict)->dict:
    fn=tool["function"]
    return {"type":"function","function":{
        "name":fn["name"],
        "parameters":{name:_compact_value(schema) for name,schema in fn.get("parameters",{}).items()},
    }}

def select_tools(sample:dict,tools_dict:dict,flat_tools:dict,seed=42,count=6):
    """Always include gold tool; choose deterministic same-category distractors."""
    correct=sample["tool_call"]["name"]
    names=[t.name for t in tools_dict.get(sample["category"],[]) if t.name in flat_tools and t.name!=correct]
    rng=random.Random(f"{seed}:{sample.get('doc_id')}:{sample.get('slide_index')}:{correct}")
    rng.shuffle(names)
    selected=([correct]+names[:max(0,count-1)]) if correct in flat_tools else list(flat_tools)[:count]
    return selected

def build_prompt(tokenizer,sample:dict,seed=42,tool_count=6,compact=True):
    from backend.workflows.slidegen_workflow.tools.tool_des_xml import TOOLS_DICT
    from backend.workflows.slidegen_workflow.utils.helper import format_tool_for_qwen
    from backend.workflows.slidegen_workflow.utils.prompts import QWEN_GENERATOR_HUMAN_TEMPLATE,QWEN_GENERATOR_SYSTEM_PROMPT
    flat={t.name:t for tools in TOOLS_DICT.values() for t in tools}
    names=select_tools(sample,TOOLS_DICT,flat,seed,tool_count)
    tools=[format_tool_for_qwen(flat[name]) for name in names]
    if compact: tools=[compact_tool(tool) for tool in tools]
    user=QWEN_GENERATOR_HUMAN_TEMPLATE.format(
        style_context=(sample.get("style_context") or "")[:500],
        design_instruction=(sample.get("design_instruction") or "")[:600],
        slide_content=(sample.get("slide_content") or sample.get("content",""))[:1200])
    messages=[{"role":"system","content":QWEN_GENERATOR_SYSTEM_PROMPT},{"role":"user","content":user}]
    prompt=tokenizer.apply_chat_template(messages,tools=tools,tokenize=False,add_generation_prompt=True)
    return prompt,names

def completion_text(sample:dict)->str:
    return f"<tool_call>{json.dumps(sample['tool_call'],ensure_ascii=False,separators=(',',':'))}</tool_call>"
