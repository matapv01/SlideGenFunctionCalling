"""Comprehensive offline metrics for SlideGen function-call responses."""
from __future__ import annotations
import argparse, hashlib, json, math, random, re, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TAG = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.I | re.S)
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
METRICS = ("parse_success","format_exact","tool_name_accuracy","valid_tool_rate",
           "argument_key_precision","argument_key_recall","argument_value_f1",
           "arguments_exact","exact_match","has_extra_text","response_chars",
           "missing_argument_count","extra_argument_count")

def stable_holdout(samples, ratio=.2, seed=42):
    """Document-level deterministic split, preventing same-deck leakage."""
    docs = defaultdict(list)
    for i, row in enumerate(samples):
        docs[str(row.get("doc_id", f"sample-{i}"))].append(row)
    out, limit = [], int(ratio * 10000)
    for doc, rows in docs.items():
        if int(hashlib.sha256(f"{seed}:{doc}".encode()).hexdigest()[:8], 16) % 10000 < limit:
            out.extend(rows)
    return out or samples[::max(1, round(1 / ratio))]

def parse_prediction(text):
    text = text or ""
    tagged = TAG.findall(text)
    candidates = list(reversed(tagged)) if tagged else [text.strip()]
    error = "no_json_object"
    for candidate in candidates:
        candidate = re.sub(r"^```(?:json)?\s*|\s*```$", "", candidate.strip(), flags=re.I)
        starts = [0] + [m.start() for m in re.finditer(r"\{", candidate)]
        for start in dict.fromkeys(starts):
            try:
                value, _ = json.JSONDecoder().raw_decode(candidate[start:])
                if isinstance(value, dict):
                    args = value.get("arguments", {})
                    call = {"name": value.get("name"), "arguments": args if isinstance(args, dict) else {}}
                    exact = bool(re.fullmatch(r"\s*<tool_call>\s*\{.*\}\s*</tool_call>\s*", text, re.S))
                    return {"call": call, "parse_error": None, "format_exact": exact}
            except json.JSONDecodeError as exc:
                error = str(exc)
    return {"call": None, "parse_error": error, "format_exact": False}

def flatten(value: Any, prefix=""):
    if isinstance(value, dict):
        out = {}
        for key, child in value.items():
            out.update(flatten(child, f"{prefix}.{key}" if prefix else str(key)))
        return out
    if isinstance(value, list):
        out = {}
        for i, child in enumerate(value):
            out.update(flatten(child, f"{prefix}[{i}]"))
        return out
    return {prefix: value}

def equal(pred, gold):
    if isinstance(gold, float) and isinstance(pred, (int, float)):
        return math.isclose(float(pred), gold, rel_tol=1e-5, abs_tol=1e-6)
    if isinstance(gold, str) and isinstance(pred, str) and HEX.match(gold) and HEX.match(pred):
        return gold.lower() == pred.lower()
    return pred == gold

def score_response(response, sample, valid_tools=None):
    parsed = parse_prediction(response)
    pred = parsed["call"] or {"name": None, "arguments": {}}
    gold = sample["tool_call"]
    pa, ga = flatten(pred["arguments"]), flatten(gold.get("arguments", {}))
    pk, gk = set(pa), set(ga)
    matched = sum(equal(pa[k], ga[k]) for k in pk & gk)
    precision = matched / len(pk) if pk else (1.0 if not gk else 0.0)
    recall = matched / len(gk) if gk else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    name_ok = pred["name"] == gold["name"]
    args_ok = pred["arguments"] == gold.get("arguments", {})
    return {"parse_success": float(parsed["call"] is not None), "format_exact": float(parsed["format_exact"]),
      "tool_name_accuracy": float(name_ok), "valid_tool_rate": float(bool(pred["name"]) and (valid_tools is None or pred["name"] in valid_tools)),
      "argument_key_precision": precision, "argument_key_recall": recall, "argument_value_f1": f1,
      "arguments_exact": float(args_ok), "exact_match": float(name_ok and args_ok),
      "extra_argument_count": len(pk-gk), "missing_argument_count": len(gk-pk),
      "response_chars": len(response or ""), "has_extra_text": float(not parsed["format_exact"]),
      "parse_error": parsed["parse_error"], "predicted_tool": pred["name"],
      "gold_tool": gold["name"], "category": sample.get("category", "unknown")}

def bootstrap_ci(values, count=2000, seed=42):
    if not values: return [0.0, 0.0]
    rng = random.Random(seed)
    means = sorted(sum(rng.choice(values) for _ in values)/len(values) for _ in range(count))
    return [means[int(.025*(count-1))], means[int(.975*(count-1))]]

def summarize(rows, bootstraps=2000, seed=42):
    mean = lambda group, key: sum(float(r[key]) for r in group)/len(group) if group else 0.0
    overall = {key: mean(rows, key) for key in METRICS}
    overall["exact_match_ci95"] = bootstrap_ci([r["exact_match"] for r in rows], bootstraps, seed)
    breakdown = {}
    for field in ("category", "gold_tool"):
        groups = defaultdict(list)
        for row in rows: groups[str(row[field])].append(row)
        breakdown[field] = {name: {"count": len(group), **{k: mean(group,k) for k in METRICS[:9]}}
                            for name, group in sorted(groups.items())}
    confusion = Counter((r["gold_tool"], str(r["predicted_tool"])) for r in rows)
    return {"sample_count": len(rows), "overall": overall, "breakdown": breakdown,
      "tool_confusion": [{"gold":a,"predicted":b,"count":n} for (a,b),n in confusion.most_common() if a != b],
      "parse_errors": dict(Counter(r["parse_error"] or "parsed" for r in rows))}

def paired_compare(rows, baseline, bootstraps=2000, seed=42):
    if len(rows) != len(baseline): raise ValueError("candidate and baseline counts differ")
    delta = [a["exact_match"]-b["exact_match"] for a,b in zip(rows,baseline)]
    return {"exact_match_delta": statistics.fmean(delta) if delta else 0.0,
      "exact_match_delta_ci95": bootstrap_ci(delta,bootstraps,seed),
      "candidate_wins":sum(x>0 for x in delta),"baseline_wins":sum(x<0 for x in delta),"ties":sum(x==0 for x in delta)}

def load_responses(path):
    if not Path(path).is_file():
        raise FileNotFoundError(f"Response file not found: {path}. Generate it first with generate_eval_responses.py; see rl/README.md")
    with open(path, encoding="utf-8") as f:
        data = [json.loads(x) for x in f if x.strip()] if path.endswith(".jsonl") else json.load(f)
    if isinstance(data, dict): data = data.get("responses", data.get("results", []))
    return [x if isinstance(x,str) else x.get("response",x.get("completion",x.get("text",""))) for x in data]

def main():
    p=argparse.ArgumentParser(description="Score SlideGen function-call responses")
    p.add_argument("--responses",required=True); p.add_argument("--baseline_responses")
    p.add_argument("--data_path",default=str(ROOT/"rl/data/sft_function_call_dataset.json"))
    p.add_argument("--output_dir"); p.add_argument("--split",choices=("all","holdout","train","eval","test"),default="test")
    p.add_argument("--holdout_ratio",type=float,default=.2)
    p.add_argument("--eval_ratio",type=float,default=.1); p.add_argument("--test_ratio",type=float,default=.1)
    p.add_argument("--seed",type=int,default=42)
    p.add_argument("--max_samples",type=int); p.add_argument("--bootstrap_samples",type=int,default=2000)
    args=p.parse_args()
    samples=json.load(open(args.data_path,encoding="utf-8"))
    if args.split=="holdout": selected=stable_holdout(samples,args.holdout_ratio,args.seed)
    elif args.split in {"train","eval","test"}:
        from rl.toolcall_data import split_by_doc
        selected=split_by_doc(samples,args.eval_ratio,args.test_ratio,args.seed)[args.split]
    else: selected=samples
    if args.max_samples: selected=selected[:args.max_samples]
    responses=load_responses(args.responses)
    if len(responses)!=len(selected): raise ValueError(f"expected {len(selected)} responses, got {len(responses)}")
    from backend.workflows.slidegen_workflow.tools.tool_des_xml import TOOLS_DICT
    valid={tool.name for tools in TOOLS_DICT.values() for tool in tools}
    rows=[{"index":i,**score_response(r,s,valid),"doc_id":s.get("doc_id"),"slide_index":s.get("slide_index"),"response":r}
          for i,(r,s) in enumerate(zip(responses,selected))]
    report={"config":vars(args),"dataset":{"total":len(samples),"evaluated":len(selected)},
            "metrics":summarize(rows,args.bootstrap_samples,args.seed)}
    if args.baseline_responses:
        baseline=load_responses(args.baseline_responses)
        if len(baseline)!=len(selected): raise ValueError("baseline response count differs")
        br=[score_response(r,s,valid) for r,s in zip(baseline,selected)]
        report["baseline"]=summarize(br,args.bootstrap_samples,args.seed)
        report["paired_comparison"]=paired_compare(rows,br,args.bootstrap_samples,args.seed)
    out=Path(args.output_dir or ROOT/"rl/log/evaluation")
    out.mkdir(parents=True,exist_ok=True)
    (out/"evaluation_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    with (out/"predictions.jsonl").open("w",encoding="utf-8") as f:
        for row in rows: f.write(json.dumps(row,ensure_ascii=False)+"\n")
    m=report["metrics"]["overall"]
    print(f"Evaluated {len(rows)} | parse={m['parse_success']:.3f} tool={m['tool_name_accuracy']:.3f} args_f1={m['argument_value_f1']:.3f} exact={m['exact_match']:.3f}")
    print(f"Report: {out/'evaluation_report.json'}")

if __name__=="__main__": main()
