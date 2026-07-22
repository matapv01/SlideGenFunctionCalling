"""Generate deterministic SlideGen evaluation responses from a base model or PEFT adapter."""
from __future__ import annotations
import argparse, json, random, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.workflows.slidegen_workflow.utils.helper import QWEN_CHAT_TEMPLATE
from rl.sdft_official.eval_tooluse import stable_holdout
from rl.toolcall_data import build_prompt, split_by_doc

def parse_args():
    p=argparse.ArgumentParser(description="Generate responses for SlideGen evaluation")
    p.add_argument("--model_path",required=True,help="Hugging Face model ID/path or PEFT adapter path")
    p.add_argument("--output",required=True,help="Output JSONL")
    p.add_argument("--data_path",default=str(ROOT/"rl/data/sft_function_call_dataset.json"))
    p.add_argument("--split",choices=("all","holdout","train","eval","test"),default="test")
    p.add_argument("--holdout_ratio",type=float,default=.2)
    p.add_argument("--eval_ratio",type=float,default=.1); p.add_argument("--test_ratio",type=float,default=.1)
    p.add_argument("--seed",type=int,default=42)
    p.add_argument("--max_samples",type=int); p.add_argument("--batch_size",type=int,default=2)
    p.add_argument("--max_prompt_length",type=int,default=4096)
    p.add_argument("--max_new_tokens",type=int,default=3072)
    p.add_argument("--temperature",type=float,default=0.0); p.add_argument("--device_map",default="auto")
    return p.parse_args()

def load_model(path, device_map):
    import torch
    from peft import PeftConfig, PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer
    adapter=Path(path,"adapter_config.json").exists()
    base=PeftConfig.from_pretrained(path).base_model_name_or_path if adapter else path
    tokenizer=AutoTokenizer.from_pretrained(path if Path(path).exists() else base,trust_remote_code=True,padding_side="left")
    tokenizer.pad_token=tokenizer.pad_token or tokenizer.eos_token
    tokenizer.truncation_side="left"
    dtype=torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else (
        torch.float16 if torch.cuda.is_available() else torch.float32)
    model=AutoModelForCausalLM.from_pretrained(base,torch_dtype=dtype,device_map=device_map,trust_remote_code=True)
    if adapter: model=PeftModel.from_pretrained(model,path)
    model.eval()
    return model,tokenizer,base,adapter

def build_prompts(samples,tokenizer,seed):
    tokenizer.chat_template=QWEN_CHAT_TEMPLATE
    return [build_prompt(tokenizer,sample,seed,tool_count=6,compact=True)[0] for sample in samples]

def main():
    import torch
    args=parse_args()
    with open(args.data_path,encoding="utf-8") as f: samples=json.load(f)
    if args.split=="holdout": selected=stable_holdout(samples,args.holdout_ratio,args.seed)
    elif args.split in {"train","eval","test"}: selected=split_by_doc(samples,args.eval_ratio,args.test_ratio,args.seed)[args.split]
    else: selected=samples
    if args.max_samples: selected=selected[:args.max_samples]
    model,tokenizer,base,is_adapter=load_model(args.model_path,args.device_map)
    prompts=build_prompts(selected,tokenizer,args.seed)
    output=Path(args.output); output.parent.mkdir(parents=True,exist_ok=True)
    written=0
    with output.open("w",encoding="utf-8") as f:
        for start in range(0,len(prompts),args.batch_size):
            batch=prompts[start:start+args.batch_size]
            lengths=[len(tokenizer(x,add_special_tokens=False)["input_ids"]) for x in batch]
            if max(lengths)>args.max_prompt_length:
                raise ValueError(f"Prompt exceeds budget: max={max(lengths)}, budget={args.max_prompt_length}")
            encoded=tokenizer(batch,return_tensors="pt",padding=True,add_special_tokens=False).to(model.device)
            before=time.perf_counter()
            kwargs={"max_new_tokens":args.max_new_tokens,"do_sample":args.temperature>0,
                    "pad_token_id":tokenizer.pad_token_id,"eos_token_id":tokenizer.eos_token_id}
            if args.temperature>0: kwargs["temperature"]=args.temperature
            with torch.inference_mode(): generated=model.generate(**encoded,**kwargs)
            elapsed=(time.perf_counter()-before)/len(batch)
            width=encoded["input_ids"].shape[1]
            texts=tokenizer.batch_decode(generated[:,width:],skip_special_tokens=True)
            for offset,text in enumerate(texts):
                sample=selected[start+offset]
                row={"index":start+offset,"doc_id":sample.get("doc_id"),"slide_index":sample.get("slide_index"),
                     "category":sample.get("category"),"response":text.strip(),"latency_seconds":elapsed,
                     "model_path":args.model_path,"base_model":base,"is_adapter":is_adapter}
                f.write(json.dumps(row,ensure_ascii=False)+"\n"); f.flush(); written+=1
            print(f"Generated {written}/{len(selected)}")
    print(f"Saved: {output}")

if __name__=="__main__": main()
