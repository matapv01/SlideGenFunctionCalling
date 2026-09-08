import json,torch
from pathlib import Path
from types import SimpleNamespace
from transformers import AutoTokenizer
from backend.workflows.slidegen_workflow.utils.helper import QWEN_CHAT_TEMPLATE
from rl.sft.sft_toolcall import SFTKLTrainer,encode_sample
from rl.toolcall_data import split_by_doc

class TinyLM(torch.nn.Module):
    def __init__(self,vocab=32):
        super().__init__();self.emb=torch.nn.Embedding(vocab,8);self.head=torch.nn.Linear(8,vocab)
    def forward(self,input_ids,attention_mask=None,use_cache=False,logits_to_keep=None):
        logits=self.head(self.emb(input_ids))
        if logits_to_keep:logits=logits[:,-logits_to_keep:]
        return SimpleNamespace(logits=logits)

def test_split_has_no_document_leakage():
    rows=[{"doc_id":d,"slide_index":i} for d in range(50) for i in range(2)]
    split=split_by_doc(rows,.1,.1,42)
    docs={k:{x["doc_id"] for x in v} for k,v in split.items()}
    assert docs["train"].isdisjoint(docs["eval"]|docs["test"])
    assert docs["eval"].isdisjoint(docs["test"])
    assert sum(map(len,split.values()))==len(rows)

def test_sft_kl_loss_is_finite_and_backpropagates():
    trainer=object.__new__(SFTKLTrainer);trainer.ref_model=TinyLM();trainer.kl_coef=.03;trainer._last_parts={}
    student=TinyLM()
    inputs={"input_ids":torch.tensor([[1,2,3,4],[0,5,6,7]]),
            "attention_mask":torch.tensor([[1,1,1,1],[0,1,1,1]]),
            "labels":torch.tensor([[-100,-100,3,4],[-100,-100,6,7]])}
    loss=SFTKLTrainer.compute_loss(trainer,student,inputs)
    assert torch.isfinite(loss);loss.backward()
    assert student.head.weight.grad is not None
    assert trainer._last_parts.keys()=={"ce_loss","base_kl"}
