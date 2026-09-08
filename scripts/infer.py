import os
import sys
import json
import torch
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.workflows.slidegen_workflow.tools.tool_des_xml import TOOLS_DICT, execute_tool
from backend.workflows.slidegen_workflow.utils.helper import render_xml_to_png, format_tool_for_qwen, parse_tool_call_json

base_model_id = os.getenv("TRAINING_MODEL_ID", "Qwen/Qwen2.5-Coder-0.5B-Instruct")
adapter_path = os.getenv("LORA_ADAPTER_PATH", "")

if not adapter_path:
    checkpoints_dir = os.path.join(os.path.dirname(__file__), "..", "rl", "qwen_slidegen_grpo")
    if os.path.exists(checkpoints_dir):
        checkpoints = [
            os.path.join(checkpoints_dir, d)
            for d in os.listdir(checkpoints_dir)
            if d.startswith("checkpoint-") and os.path.isdir(os.path.join(checkpoints_dir, d))
        ]
        if checkpoints:
            checkpoints.sort(key=lambda x: int(x.split("checkpoint-")[-1]))
            adapter_path = checkpoints[-1]

print(f"Base model ID: {base_model_id}")
if adapter_path:
    print(f"LoRA adapter detected: {adapter_path}")
else:
    print("No LoRA adapter found. Running inference with base model only.")

if "CUDA_VISIBLE_DEVICES" not in os.environ:
    import subprocess
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,nounits,noheader"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2
        )
        free_mems = [int(x) for x in res.stdout.strip().split("\n") if x.strip().isdigit()]
        if free_mems:
            best_gpu = free_mems.index(max(free_mems))
            os.environ["CUDA_VISIBLE_DEVICES"] = str(best_gpu)
            print(f"[System] Automatically selected GPU {best_gpu} with the most free VRAM ({free_mems[best_gpu]} MiB).")
        else:
            os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    except Exception:
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

tokenizer = AutoTokenizer.from_pretrained(base_model_id)
tokenizer.pad_token = tokenizer.eos_token

flat_tools = {}
for category, tools_list in TOOLS_DICT.items():
    for tool in tools_list:
        flat_tools[tool.name] = tool

candidate_tool_names = [
    "generate_split_content_slide_xml", "generate_bullet_content_slide_xml",
    "generate_two_ideas_slide_xml", "generate_three_ideas_slide_xml",
    "generate_problem_slide_xml", "generate_implementation_timeline_slide_xml",
    "generate_content_creation_slide_xml"
]
selected_tools = [format_tool_for_qwen(flat_tools[name]) for name in candidate_tool_names if name in flat_tools]
print(f"Loaded {len(selected_tools)} candidate tools.")

torch_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
print("Loading base model...")
model = AutoModelForCausalLM.from_pretrained(base_model_id, torch_dtype=torch_dtype, device_map="auto")

if adapter_path:
    print(f"Loading LoRA weights from '{adapter_path}'...")
    model = PeftModel.from_pretrained(model, adapter_path)

print("Model loaded successfully!")

prompt = os.getenv("INFER_PROMPT", "Hãy thiết kế slide giới thiệu về tập đoàn FPT. Nội dung: thành lập năm 1988, dẫn đầu lĩnh vực công nghệ thông tin và chuyển đổi số tại Việt Nam. Sử dụng layout tiêu đề và các gạch đầu dòng.")
messages = [
    {"role": "system", "content": ""},
    {"role": "user", "content": prompt}
]

text = tokenizer.apply_chat_template(messages, tools=selected_tools, tokenize=False, add_generation_prompt=True)

print("\n--- Sending Input Prompt ---")
print(prompt)
print("----------------------------")

inputs = tokenizer([text], return_tensors="pt").to(device)

print("Running model generation...")
with torch.no_grad():
    generated_ids = model.generate(**inputs, max_new_tokens=512, do_sample=False, repetition_penalty=1.2)

generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, generated_ids)]
response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

print("\n--- Model Response ---")
print(response)
print("----------------------")

try:
    print("\nParsing model response to render slide...")
    tool_call = parse_tool_call_json(response)
    if not tool_call:
        print("Failed to parse tool call from response.")
        sys.exit(1)

    if tool_call.get("name"):
        tool_call["name"] = tool_call["name"].strip().lower().replace(" ", "_")

    arguments = tool_call.get("arguments", {})
    if isinstance(arguments, dict):
        tool_call["arguments"] = {k: v for k, v in arguments.items() if v is not None}

    print(f"Parsed tool call: {json.dumps(tool_call, indent=2, ensure_ascii=False)}")

    xml_content = execute_tool(tool_call)
    if xml_content:
        xml_path = os.path.join(os.path.dirname(__file__), "infer_output.xml")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        print(f"-> Saved XML layout to: {xml_path}")

        png_path = os.path.join(os.path.dirname(__file__), "infer_output.png")
        render_xml_to_png(xml_content, png_path)
        print(f"-> Captured slide image to: {png_path}")
        print("\nSUCCESS! Check 'scripts/infer_output.png' or 'scripts/infer_output.xml'!")
    else:
        print("Failed to execute tool (returned empty XML).")
except Exception as e:
    print(f"Failed to parse or render slide: {e}")
