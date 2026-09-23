import json
from rl.eval_tooluse import paired_compare, parse_prediction, score_response, stable_holdout, summarize
SAMPLE={"category":"INTRO_TOOLS","doc_id":1,"tool_call":{"name":"make_slide","arguments":{"title":"Hi","color":"#FFFFFF","size":1.0}}}
def test_parse_tagged_and_raw_json():
    value={"name":"make_slide","arguments":{"title":"Hi"}}
    assert parse_prediction(f"<tool_call>{json.dumps(value)}</tool_call>")["call"]==value
    assert parse_prediction(json.dumps(value))["call"]==value
def test_score_separates_tool_and_arguments():
    r=score_response('<tool_call>{"name":"make_slide","arguments":{"title":"Hi","color":"#ffffff","extra":2}}</tool_call>',SAMPLE,{"make_slide"})
    assert r["tool_name_accuracy"]==1 and r["argument_key_recall"]==2/3 and r["extra_argument_count"]==1 and r["exact_match"]==0
def test_invalid_output_is_scored_not_crashed():
    assert score_response("not json",SAMPLE)["parse_success"]==0
def test_holdout_is_deterministic_and_document_grouped():
    data=[{"doc_id":d,"slide_index":s} for d in range(20) for s in range(2)]
    result=stable_holdout(data,.2,42)
    assert result==stable_holdout(data,.2,42)
    assert all(sum(x["doc_id"]==d for x in result)==2 for d in {x["doc_id"] for x in result})
def test_summary_and_paired_comparison():
    good=score_response('<tool_call>{"name":"make_slide","arguments":{"title":"Hi","color":"#FFFFFF","size":1.0}}</tool_call>',SAMPLE)
    bad=score_response("bad",SAMPLE)
    assert summarize([good,bad],100,1)["overall"]["exact_match"]==.5
    assert paired_compare([good],[bad],100,1)["exact_match_delta"]==1
