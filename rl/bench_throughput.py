"""Measure GRPO rollout and update throughput for the configured policy.

Usage: BENCH_TAG=baseline python rl/bench_throughput.py
Env: BENCH_GEN_BATCHES (e.g. "4,16"), BENCH_NEW_TOKENS, BENCH_TRAIN_SEQS, BENCH_PROMPTS_JSON.
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch

from rl import train


def _sync_time() -> float:
    torch.cuda.synchronize()
    return time.perf_counter()


def main() -> None:
    tag = os.getenv("BENCH_TAG", "run")
    rows = json.loads(Path(os.environ["BENCH_PROMPTS_JSON"]).read_text(encoding="utf-8"))
    gen_batches = [int(x) for x in os.getenv("BENCH_GEN_BATCHES", "4,16").split(",") if x]
    new_tokens = int(os.getenv("BENCH_NEW_TOKENS", "384"))
    train_seqs = int(os.getenv("BENCH_TRAIN_SEQS", "4"))
    num_generations = int(os.getenv("NUM_GENERATIONS", "4"))

    started = time.perf_counter()
    model, tokenizer, _, _ = train._load_model(revision=train.MODEL_REVISION)
    tokenizer.padding_side = "left"
    result = {"tag": tag, "load_seconds": round(time.perf_counter() - started, 1)}
    linear_attn = next(m for m in model.modules() if type(m).__name__.endswith("GatedDeltaNet"))
    result["gated_delta_impl"] = getattr(getattr(linear_attn, "chunk_gated_delta_rule", None), "__module__", "?")
    result["experts_impl"] = getattr(model.config, "_experts_implementation_internal", None) or getattr(
        model.config.get_text_config(), "_experts_implementation_internal", None)

    model.eval()
    for batch in gen_batches:
        prompts = [row["prompt"] for row in rows[: max(1, batch // num_generations)]]
        prompts = [p for p in prompts for _ in range(num_generations)][:batch]
        inputs = tokenizer(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        torch.cuda.reset_peak_memory_stats()
        with torch.no_grad():
            model.generate(**inputs, max_new_tokens=8, min_new_tokens=8, do_sample=True, use_cache=True)
            begin = _sync_time()
            out = model.generate(
                **inputs, max_new_tokens=new_tokens, min_new_tokens=new_tokens, do_sample=True,
                temperature=1.0, top_p=0.95, top_k=0, use_cache=True,
            )
            seconds = _sync_time() - begin
        generated = (out.shape[1] - inputs["input_ids"].shape[1]) * out.shape[0]
        result[f"gen_b{batch}"] = {
            "seconds": round(seconds, 1),
            "tokens_per_s": round(generated / seconds, 1),
            "seconds_per_completion": round(seconds / batch, 2),
            "prompt_tokens": int(inputs["input_ids"].shape[1]),
            "peak_gib": round(torch.cuda.max_memory_allocated() / 2**30, 1),
        }
        print(json.dumps(result), flush=True)
        del out, inputs
        torch.cuda.empty_cache()

    model.train()
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.config.use_cache = False
    prompt = rows[0]["prompt"]
    ids = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)["input_ids"]
    completion = torch.randint(1000, 20000, (1, 320))
    sequence = torch.cat([ids, completion], dim=1).cuda()
    torch.cuda.reset_peak_memory_stats()
    times = []
    for _ in range(train_seqs + 1):
        begin = _sync_time()
        logits = model(input_ids=sequence, logits_to_keep=completion.shape[1] + 1).logits
        loss = torch.nn.functional.cross_entropy(
            logits[:, :-1].float().reshape(-1, logits.shape[-1]), sequence[:, -completion.shape[1]:].reshape(-1)
        )
        loss.backward()
        times.append(_sync_time() - begin)
        del logits, loss
    model.zero_grad(set_to_none=True)
    result["train_fwd_bwd"] = {
        "seconds_per_sequence": round(sum(times[1:]) / train_seqs, 2),
        "sequence_tokens": int(sequence.shape[1]),
        "peak_gib": round(torch.cuda.max_memory_allocated() / 2**30, 1),
    }
    print("BENCH_RESULT " + json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
