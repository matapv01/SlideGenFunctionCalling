# %% [code] {"execution":{"iopub.status.busy":"2026-08-15T07:24:11.711832Z","iopub.execute_input":"2026-08-15T07:24:11.712119Z","iopub.status.idle":"2026-08-15T07:28:27.565192Z","shell.execute_reply.started":"2026-08-15T07:24:11.712093Z","shell.execute_reply":"2026-08-15T07:28:27.564410Z"}}
!pip install -q vllm fastapi uvicorn pydantic nest_asyncio

# %% [code] {"execution":{"iopub.status.busy":"2026-08-15T07:28:27.567019Z","iopub.execute_input":"2026-08-15T07:28:27.567755Z","iopub.status.idle":"2026-08-15T07:28:56.167369Z","shell.execute_reply.started":"2026-08-15T07:28:27.567721Z","shell.execute_reply":"2026-08-15T07:28:56.166424Z"}}
import os
import time
import threading
import subprocess
import re
import uuid
import asyncio
import nest_asyncio

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from vllm import AsyncEngineArgs, AsyncLLMEngine, SamplingParams

# Quan trọng: Cho phép chạy asyncio lồng nhau để FastAPI và vLLM hoạt động mượt trong Jupyter Notebook
nest_asyncio.apply()

HOST = "0.0.0.0"
PORT = 8000

# Bạn có thể đổi sang bản 7B/8B bất kỳ, ví dụ "Qwen/Qwen2.5-7B-Instruct"
LLM_MODEL_NAME = "Qwen/Qwen3-8B"

# SỬ DỤNG 2 GPU T4 (Khai báo Tensor Parallel Size = 2)
TENSOR_PARALLEL_SIZE = 2

# %% [code] {"execution":{"iopub.status.busy":"2026-08-15T07:28:56.168535Z","iopub.execute_input":"2026-08-15T07:28:56.169482Z","iopub.status.idle":"2026-08-15T07:32:55.613627Z","shell.execute_reply.started":"2026-08-15T07:28:56.169452Z","shell.execute_reply":"2026-08-15T07:32:55.612491Z"}}
from transformers import AutoTokenizer

print(f"[LOAD] Đang khởi tạo vLLM Engine trên {TENSOR_PARALLEL_SIZE} GPUs...")
engine_args = AsyncEngineArgs(
    model=LLM_MODEL_NAME,
    tensor_parallel_size=TENSOR_PARALLEL_SIZE,
    gpu_memory_utilization=0.90, # Dành 90% VRAM của 2 GPU cho trọng số và PagedAttention
    max_model_len=10000,          # Giới hạn context length để chống OOM
    trust_remote_code=True,
    # KÍCH HOẠT AUTOMATIC PREFIX CACHING
    enable_prefix_caching=True,
)
# # AsyncLLMEngine cho phép xử lý nhiều luồng request đổ về server cùng lúc
engine = AsyncLLMEngine.from_engine_args(engine_args)
print("[LOAD] Hoàn tất tải mô hình vLLM!")

print("[LOAD] Đang tải Tokenizer cho chat template và function calling...")
tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_NAME, trust_remote_code=True)
print("[LOAD] Hoàn tất tải Tokenizer!")

# %% [code] {"execution":{"iopub.status.busy":"2026-08-15T07:32:55.626216Z","iopub.execute_input":"2026-08-15T07:32:55.626988Z","iopub.status.idle":"2026-08-15T07:32:55.722571Z","shell.execute_reply.started":"2026-08-15T07:32:55.626946Z","shell.execute_reply":"2026-08-15T07:32:55.721486Z"}}
from typing import Optional, List, Dict, Any
import json
from fastapi.responses import StreamingResponse

class GenerateRequest(BaseModel):
    messages: Optional[List[Dict[str, Any]]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    prompt: Optional[str] = None
    max_length: int = 1024
    temperature: float = 0.7

app = FastAPI()

@app.post("/generate")
async def generate(req: GenerateRequest):
    request_id = str(uuid.uuid4())

    # 1. Xác định prompt cuối cùng đưa vào vLLM
    if req.messages:
        # Nếu có danh sách messages, dùng apply_chat_template chính thức của Qwen
        if req.tools:
            final_prompt = tokenizer.apply_chat_template(
                req.messages,
                tools=req.tools,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            final_prompt = tokenizer.apply_chat_template(
                req.messages,
                tokenize=False,
                add_generation_prompt=True
            )
    elif req.prompt:
        # Tương thích ngược với chuỗi prompt đơn giản
        final_prompt = req.prompt
    else:
        raise HTTPException(status_code=400, detail="Either 'messages' or 'prompt' must be provided.")

    sampling_params = SamplingParams(
        temperature=req.temperature,
        max_tokens=req.max_length
    )

    results_generator = engine.generate(final_prompt, sampling_params, request_id)

    async def stream():
        previous_text = ""
        try:
            async for request_output in results_generator:
                text = request_output.outputs[0].text
                delta = text[len(previous_text):]
                previous_text = text
                if delta:
                    # Mỗi dòng là 1 object JSON độc lập (NDJSON) -> giữ connection có data liên tục
                    yield json.dumps({"delta": delta}, ensure_ascii=False) + "\n"

            # Dòng cuối cùng báo hoàn tất, kèm full text để client không cần tự ghép lại nếu không muốn
            yield json.dumps({"done": True, "answer": previous_text.strip()}, ensure_ascii=False) + "\n"

        except Exception as e:
            yield json.dumps({"error": str(e)}, ensure_ascii=False) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson")

# %% [code] {"execution":{"iopub.status.busy":"2026-08-15T07:32:55.723998Z","iopub.execute_input":"2026-08-15T07:32:55.724583Z","iopub.status.idle":"2026-08-15T07:32:55.732378Z","shell.execute_reply.started":"2026-08-15T07:32:55.724497Z","shell.execute_reply":"2026-08-15T07:32:55.731303Z"}}
def start_cloudflare_tunnel(port):
    print("[CLOUDFLARE] Đang khởi tạo tunnel...")
    if not os.path.exists("./cloudflared"):
        print("[CLOUDFLARE] Đang tải cloudflared...")
        subprocess.run(["wget", "-q", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-O", "cloudflared"])
        subprocess.run(["chmod", "+x", "cloudflared"])
    
    proc = subprocess.Popen(["./cloudflared", "tunnel", "--url", f"http://localhost:{port}"], 
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    for line in iter(proc.stdout.readline, ""):
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            url = match.group(0)
            print(f"\n{'='*60}\nAPI URL: {url}\n{'='*60}\n")
            return url, proc
    return None, proc

# %% [code] {"execution":{"iopub.status.busy":"2026-08-15T07:32:55.733678Z","iopub.execute_input":"2026-08-15T07:32:55.734069Z","execution_failed":"2026-08-15T10:14:29.397Z"}}
import uvicorn
from uvicorn import Config, Server

if __name__ == "__main__":
    # 1. Kích hoạt Tunnel kết nối ra Internet TRƯỚC
    public_url, tunnel_proc = start_cloudflare_tunnel(PORT)
    
    # 2. Chạy Uvicorn TRỰC TIẾP trên Event Loop có sẵn của Kaggle
    if public_url:
        print("\n[INFO] SERVER ĐÃ SẴN SÀNG! ĐANG LẮNG NGHE REQUEST...\n")
        
        # Cấu hình Server
        config = Config(app, host=HOST, port=PORT, log_level="info")
        server = Server(config)
        
        # Lệnh await này sẽ block cell lại để duy trì server chạy mượt mà 
        # chung mâm (cùng Event Loop) với Kaggle và vLLM
        await server.serve()
        
    else:
        print("[ERROR] Không thể khởi tạo Cloudflare Tunnel.")

# %% [code]
