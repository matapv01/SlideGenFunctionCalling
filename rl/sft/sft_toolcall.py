"""Completion-only SlideGen SFT with LoRA and frozen-base KL regularization."""
from __future__ import annotations
import argparse,json,os,random,shutil,sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F
from datasets import Dataset
from dotenv import load_dotenv
from peft import LoraConfig,TaskType,get_peft_model
from transformers import (AutoModelForCausalLM,AutoTokenizer,EarlyStoppingCallback,
                          Trainer,TrainingArguments)

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
load_dotenv()
from backend.workflows.slidegen_workflow.utils.helper import QWEN_CHAT_TEMPLATE
from rl.common import LORA_ALPHA,LORA_DROPOUT,LORA_R,LORA_TARGET_MODULES,auto_select_gpu
from rl.run_artifacts import get_runtime_metadata,save_text_summary_image,start_run_logging,write_json
from rl.toolcall_data import build_prompt,completion_text,split_by_doc

def args_parser():
    p=argparse.ArgumentParser(description="SlideGen completion-only SFT + frozen-base KL")
    p.add_argument("--model_name",default=os.getenv("TRAINING_MODEL_ID","Qwen/Qwen3-4B-Instruct-2507"))
    p.add_argument("--data_path",default=str(ROOT/"rl/data/sft_function_call_dataset.json"))
    p.add_argument("--output_dir",default=os.getenv("SFT_OUTPUT_DIR","./qwen_slidegen_sft"))
    p.add_argument("--learning_rate",type=float,default=float(os.getenv("SFT_LEARNING_RATE","1e-5")))
    p.add_argument("--epochs",type=int,default=int(os.getenv("SFT_EPOCHS","3")))
    p.add_argument("--batch_size",type=int,default=int(os.getenv("SFT_BATCH_SIZE","1")))
    p.add_argument("--gradient_accumulation_steps",type=int,default=int(os.getenv("SFT_GRAD_ACCUM","16")))
    p.add_argument("--max_prompt_length",type=int,default=int(os.getenv("SFT_MAX_PROMPT_LENGTH","4096")))
    p.add_argument("--max_completion_length",type=int,default=int(os.getenv("SFT_MAX_COMPLETION_LENGTH","3072")))
    p.add_argument("--kl_coef",type=float,default=float(os.getenv("SFT_KL_COEF","0.03")))
    p.add_argument("--eval_ratio",type=float,default=.1);p.add_argument("--test_ratio",type=float,default=.1)
    p.add_argument("--seed",type=int,default=42);p.add_argument("--tool_count",type=int,default=6)
    p.add_argument("--early_stopping_patience",type=int,default=2)
    p.add_argument("--attention_only_lora",action=argparse.BooleanOptionalAction,default=False)
    p.add_argument("--gradient_checkpointing",action=argparse.BooleanOptionalAction,default=True)
    p.add_argument("--run_test_generation",action=argparse.BooleanOptionalAction,default=True)
    p.add_argument("--test_max_samples",type=int,default=None)
    return p.parse_args()

def encode_sample(sample,tokenizer,args):
    prompt,offered=build_prompt(tokenizer,sample,args.seed,args.tool_count,compact=True)
    answer=completion_text(sample)
    prompt_ids=tokenizer(prompt,add_special_tokens=False)["input_ids"]
    completion_ids=tokenizer(answer,add_special_tokens=False)["input_ids"]+[tokenizer.eos_token_id]
    if len(prompt_ids)>args.max_prompt_length:
        raise ValueError(f"Prompt {sample.get('doc_id')}/{sample.get('slide_index')} has {len(prompt_ids)} tokens, budget={args.max_prompt_length}")
    if len(completion_ids)>args.max_completion_length:
        raise ValueError(f"Completion {sample.get('doc_id')}/{sample.get('slide_index')} has {len(completion_ids)} tokens, budget={args.max_completion_length}")
    assert sample["tool_call"]["name"] in offered
    return {"input_ids":prompt_ids+completion_ids,
            "attention_mask":[1]*(len(prompt_ids)+len(completion_ids)),
            "labels":[-100]*len(prompt_ids)+completion_ids,
            "prompt_length":len(prompt_ids),"completion_length":len(completion_ids)}

@dataclass
class CompletionCollator:
    tokenizer:Any
    def __call__(self,features):
        width=max(len(x["input_ids"]) for x in features); pad=self.tokenizer.pad_token_id
        batch={"input_ids":[],"attention_mask":[],"labels":[]}
        for row in features:
            n=width-len(row["input_ids"])
            batch["input_ids"].append([pad]*n+row["input_ids"])
            batch["attention_mask"].append([0]*n+row["attention_mask"])
            batch["labels"].append([-100]*n+row["labels"])
        return {k:torch.tensor(v,dtype=torch.long) for k,v in batch.items()}

class SFTKLTrainer(Trainer):
    def __init__(self,*args,ref_model,kl_coef=0.03,**kwargs):
        super().__init__(*args,**kwargs)
        self.ref_model=ref_model
        self.kl_coef=kl_coef
        self._last_parts={}
    def compute_loss(self,model,inputs,return_outputs=False,num_items_in_batch=None):
        labels=inputs.pop("labels")
        completion_tokens=(labels!=-100).sum(dim=1)
        keep=int(completion_tokens.max().item())
        kwargs={"input_ids":inputs["input_ids"],"attention_mask":inputs["attention_mask"],"use_cache":False}
        # Qwen supports logits_to_keep and avoids materializing prompt-vocabulary logits.
        student=model(**kwargs,logits_to_keep=keep+1)
        student_logits=student.logits[:,-(keep+1):-1,:].float()
        targets=labels[:,-keep:]
        mask=targets!=-100
        ce=F.cross_entropy(student_logits.reshape(-1,student_logits.size(-1)),
                           targets.reshape(-1),ignore_index=-100)
        with torch.no_grad():
            teacher=self.ref_model(**kwargs,logits_to_keep=keep+1)
            teacher_logits=teacher.logits[:,-(keep+1):-1,:].float()
            teacher_logps=F.log_softmax(teacher_logits,dim=-1)
        student_logps=F.log_softmax(student_logits,dim=-1)
        token_kl=F.kl_div(student_logps,teacher_logps,reduction="none",log_target=True).sum(-1)
        kl=(token_kl*mask).sum()/mask.sum().clamp(min=1)
        loss=ce+self.kl_coef*kl
        self._last_parts={"ce_loss":float(ce.detach()),"base_kl":float(kl.detach())}
        return (loss,student) if return_outputs else loss
    def log(self,logs,*args,**kwargs):
        if self._last_parts: logs={**logs,**self._last_parts}
        return super().log(logs,*args,**kwargs)

def load_data(path):
    with open(path,encoding="utf-8") as f:return json.load(f)

def build_encoded_dataset(rows,tokenizer,args):
    return Dataset.from_list([encode_sample(row,tokenizer,args) for row in rows])

def generate_test(model,tokenizer,rows,args,valid_tools):
    from rl.sdft_official.eval_tooluse import score_response,summarize
    model.eval();results=[]
    limit=args.test_max_samples or len(rows)
    for i,sample in enumerate(rows[:limit]):
        prompt,_=build_prompt(tokenizer,sample,args.seed,args.tool_count,compact=True)
        encoded=tokenizer(prompt,return_tensors="pt",add_special_tokens=False).to(model.device)
        with torch.inference_mode():
            output=model.generate(**encoded,max_new_tokens=args.max_completion_length,do_sample=False,
                pad_token_id=tokenizer.pad_token_id,eos_token_id=tokenizer.eos_token_id)
        text=tokenizer.decode(output[0,encoded["input_ids"].shape[1]:],skip_special_tokens=True)
        results.append({"index":i,"doc_id":sample.get("doc_id"),"slide_index":sample.get("slide_index"),
                        "response":text,**score_response(text,sample,valid_tools)})
        print(f"Test generation {i+1}/{limit}")
    return {"metrics":summarize(results,1000,args.seed),"predictions":results}

def main():
    args=args_parser();auto_select_gpu();random.seed(args.seed);torch.manual_seed(args.seed)
    if not torch.cuda.is_available(): raise RuntimeError("SFT+KL requires CUDA for the student and frozen base model")
    use_bf16=torch.cuda.is_bf16_supported();dtype=torch.bfloat16 if use_bf16 else torch.float16
    tokenizer=AutoTokenizer.from_pretrained(args.model_name,trust_remote_code=True)
    tokenizer.chat_template=QWEN_CHAT_TEMPLATE;tokenizer.padding_side="left"
    tokenizer.pad_token=tokenizer.pad_token or tokenizer.eos_token
    samples=load_data(args.data_path);splits=split_by_doc(samples,args.eval_ratio,args.test_ratio,args.seed)
    if not splits["train"] or not splits["eval"] or not splits["test"]:
        raise ValueError(f"Empty data split: { {k:len(v) for k,v in splits.items()} }")
    encoded={k:build_encoded_dataset(v,tokenizer,args) for k,v in splits.items()}
    targets=LORA_TARGET_MODULES[:4] if args.attention_only_lora else LORA_TARGET_MODULES
    student=AutoModelForCausalLM.from_pretrained(args.model_name,torch_dtype=dtype,trust_remote_code=True)
    student=get_peft_model(student,LoraConfig(task_type=TaskType.CAUSAL_LM,r=LORA_R,lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,target_modules=targets,bias="none"))
    if args.gradient_checkpointing:
        student.gradient_checkpointing_enable()
        student.enable_input_require_grads()
    ref=AutoModelForCausalLM.from_pretrained(args.model_name,torch_dtype=dtype,trust_remote_code=True)
    ref.eval();ref.requires_grad_(False);ref.to(torch.device("cuda",torch.cuda.current_device()))
    run_id=datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir=ROOT/"rl/log/sft_toolcall"/f"run_{run_id}";log_dir.mkdir(parents=True,exist_ok=True)
    run_log=start_run_logging(log_dir)
    train_args=TrainingArguments(output_dir=args.output_dir,logging_dir=str(log_dir),
        learning_rate=args.learning_rate,num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,per_device_eval_batch_size=1,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        warmup_ratio=.1,lr_scheduler_type="cosine",max_grad_norm=1.0,
        logging_steps=1,eval_strategy="epoch",save_strategy="epoch",save_total_limit=2,
        load_best_model_at_end=True,metric_for_best_model="eval_loss",greater_is_better=False,
        bf16=use_bf16,fp16=not use_bf16,gradient_checkpointing=args.gradient_checkpointing,
        report_to="none",remove_unused_columns=False,seed=args.seed,data_seed=args.seed)
    trainer=SFTKLTrainer(model=student,ref_model=ref,kl_coef=args.kl_coef,args=train_args,
        train_dataset=encoded["train"],eval_dataset=encoded["eval"],
        data_collator=CompletionCollator(tokenizer),processing_class=tokenizer,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=args.early_stopping_patience)])
    manifest=get_runtime_metadata({"run_name":"sft_toolcall","run_id":run_id,"model_name":args.model_name,
      "data_path":args.data_path,"output_dir":args.output_dir,"config":vars(args),
      "split_samples":{k:len(v) for k,v in splits.items()},
      "split_docs":{k:len({x.get('doc_id') for x in v}) for k,v in splits.items()},
      "token_stats":{k:{"prompt_max":max(x["prompt_length"] for x in encoded[k]),
                        "completion_max":max(x["completion_length"] for x in encoded[k])} for k in encoded}})
    write_json(log_dir/"manifest.json",manifest)
    print(json.dumps(manifest["split_samples"],indent=2));trainer.train()
    final=Path(args.output_dir)/"final_adapter"
    if final.exists():shutil.rmtree(final)
    trainer.save_model(str(final));tokenizer.save_pretrained(final)
    history=trainer.state.log_history;write_json(log_dir/"metrics.json",history)
    manifest["best_metric"]=trainer.state.best_metric;manifest["best_checkpoint"]=trainer.state.best_model_checkpoint
    manifest["final_adapter"]=str(final.resolve())
    if args.run_test_generation:
        valid_tools={t.name for ts in __import__("backend.workflows.slidegen_workflow.tools.tool_des",fromlist=["TOOLS_DICT"]).TOOLS_DICT.values() for t in ts}
        test=generate_test(trainer.model,tokenizer,splits["test"],args,valid_tools)
        write_json(log_dir/"test_report.json",test["metrics"])
        with (log_dir/"test_predictions.jsonl").open("w",encoding="utf-8") as f:
            for row in test["predictions"]:f.write(json.dumps(row,ensure_ascii=False)+"\n")
        manifest["test_metrics"]=test["metrics"]["overall"]
    write_json(log_dir/"manifest.json",manifest)
    save_text_summary_image(log_dir/"training_summary.png","SlideGen SFT + Base KL",
      [{"title":"Result","body":json.dumps({"split":manifest["split_samples"],"best_eval_loss":manifest["best_metric"],
        "test":manifest.get("test_metrics")},ensure_ascii=False,indent=2)}],
      subtitle=f"Run {run_id}",footer=f"Log: {run_log.name}")
    print(f"Final adapter: {final}\nLogs: {log_dir}")

if __name__=="__main__":main()
