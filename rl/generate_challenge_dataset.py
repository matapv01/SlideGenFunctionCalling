import os
import sys
import json
import random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Đảm bảo PYTHONPATH nhận diện được backend của dự án
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT

# Load các biến môi trường
load_dotenv()

# Xây dựng bảng tra cứu nhanh tên tool sang đối tượng LangChain Tool thật
flat_tools = {}
for category, tools_list in TOOLS_DICT.items():
    for tool in tools_list:
        flat_tools[tool.name] = tool

def format_tool_for_qwen(tool):
    """Chuyển đổi một LangChain tool sang định dạng JSON Schema mà Qwen yêu cầu"""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.args
        }
    }

# Khởi tạo mô hình Gemini từ OpenAI API Gateway của Google
api_key = os.getenv("GEMINI_API_KEY")
base_url = os.getenv("GEMINI_API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
model_name = os.getenv("GEMINI_GENERATION_MODEL", "gemini-2.5-pro")

if not api_key or "AIzaSy" not in api_key:
    print("[WARNING] GEMINI_API_KEY in .env seems invalid. The script will try to run, but calls might fail.")
    print("Please make sure to supply a valid Google Gemini API Key.")

# Khởi tạo OpenAI client (kết nối qua Gemini compatible endpoint)
try:
    generator_llm = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model_name,
        temperature=0.7,
        max_tokens=8192,
        model_kwargs={"response_format": {"type": "json_object"}}
    )
except Exception as e:
    print(f"[ERROR] Failed to initialize Gemini LLM Client: {e}")
    sys.exit(1)

def generate_base_topics_batch(batch_idx, batch_size=40):
    """Gọi Gemini để sinh ra một danh sách các chủ đề tiếng Việt thô kèm nội dung chi tiết"""
    print(f"Calling Gemini ({model_name}) to generate Base Topics Batch {batch_idx} ({batch_size} topics)...")
    
    prompt = (
        f"Bạn là chuyên gia xây dựng dữ liệu. Hãy tạo ra đúng {batch_size} chủ đề khác nhau bằng TIẾNG VIỆT 100% "
        "với nội dung thô phong phú, thực tế về Việt Nam hoặc các chủ đề kinh tế, kỹ thuật phổ biến. "
        "Các chủ đề phải đa dạng: Doanh nghiệp VN (FPT, VinFast, Viettel, VNG, Masan...), Lịch sử & Địa lý (Điện Biên Phủ, Cố đô Huế, "
        "Vịnh Hạ Long, văn hóa ẩm thực...), Giáo dục, Y tế, Công nghệ mới (AI, Blockchain, chuyển đổi số).\n\n"
        "Định dạng đầu ra BẮT BUỘC là một đối tượng JSON thô duy nhất chứa khóa 'topics' là một danh sách, mỗi phần tử gồm:\n"
        "- 'name': Tên chủ đề ngắn gọn (ví dụ: 'Hành trình VinFast vươn toàn cầu', 'Chiến thắng Điện Biên Phủ')\n"
        "- 'dense_paragraph': Một đoạn văn thô dài, nhiều chi tiết, hơi rườm rà (khoảng 150-250 từ) để thách thức mô hình tóm tắt.\n"
        "- 'bullets': Danh sách 3-5 gạch đầu dòng gồm thông tin cốt lõi ngắn gọn.\n"
        "- 'data_points': Chuỗi biểu diễn dữ liệu thống kê qua các năm hoặc chỉ số (ví dụ: '2021: 15 tỷ USD, 2022: 22 tỷ USD, 2023: 31 tỷ USD')\n"
        "- 'milestones': Danh sách 3-4 cột mốc thời gian hoặc các bước của quy trình (ví dụ: 'Bước 1: Nghiên cứu, Bước 2: Thử nghiệm, Bước 3: Triển khai thương mại')\n"
        "- 'comparison': Cặp nội dung so sánh song song đối lập (ví dụ: 'Sản xuất truyền thống: Tốn thời gian, chi phí nhân công cao; Sản xuất tự động hóa: Nhanh chóng, độ chính xác tuyệt đối, giảm 40% chi phí')\n\n"
        "Lưu ý: Chỉ trả về JSON thô không chứa markdown blocks (```json ... ```)."
    )
    
    try:
        response = generator_llm.invoke(prompt)
        text = response.content.strip()
        
        # Làm sạch markdown blocks nếu có
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        data = json.loads(text)
        return data.get("topics", [])
    except Exception as e:
        print(f"Error generating Base Topics Batch {batch_idx}: {e}")
        return []

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sinh dữ liệu thử thách tiếng Việt cho SlideGen RL")
    parser.add_argument("--debug", action="store_true", help="Chạy thử nghiệm giới hạn số mẫu nhỏ")
    parser.add_argument("--limit", type=int, default=10, help="Số lượng mẫu tối đa khi debug")
    args = parser.parse_args()

    # Xác định số lượng mẫu
    target_samples = 1000
    if args.debug:
        target_samples = args.limit
        print(f"[DEBUG MODE] Generating only {target_samples} samples.")
    else:
        print(f"Starting dataset generation process to reach {target_samples} samples.")

    # 1. Sinh danh sách các chủ đề thô qua Gemini
    # Để có 1000 mẫu cuối cùng qua nhân bản (5 biến thể/chủ đề), chúng ta cần 200 chủ đề gốc
    needed_base_topics = (target_samples + 4) // 5
    base_topics = []
    
    import concurrent.futures

    batch_size = 5
    if args.debug:
        needed_base_topics = (target_samples + 4) // 5
        batch_size = max(2, needed_base_topics)
        
    num_batches = (needed_base_topics + batch_size - 1) // batch_size
    print(f"Acquiring {needed_base_topics} base topics via {num_batches} batches in parallel (Max 8 workers)...")
    
    base_topics = []
    
    def fetch_batch_with_retry(idx):
        max_retries = 3
        for attempt in range(max_retries):
            topics = generate_base_topics_batch(batch_idx=idx, batch_size=batch_size)
            if topics:
                return topics
            print(f"Batch {idx} failed (attempt {attempt + 1}/{max_retries}), retrying...")
        print(f"[ERROR] Batch {idx} failed after {max_retries} attempts.")
        return []
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_batch_with_retry, i) for i in range(1, num_batches + 1)]
        for future in concurrent.futures.as_completed(futures):
            topics = future.result()
            if topics:
                base_topics.extend(topics)
                print(f"-> Thread complete. Acquired {len(topics)} topics. Total so far: {len(base_topics)}/{needed_base_topics}")

    if not base_topics:
        print("[ERROR] Failed to generate any base topics. Cannot proceed.")
        sys.exit(1)

    # Đảm bảo cắt đúng số lượng cần thiết
    base_topics = base_topics[:needed_base_topics]
    print(f"\nSuccessfully generated {len(base_topics)} base topics from Gemini.")
    print("Beginning programmatic synthesis & augmentation into 5 challenge variations...")

    # 2. Sinh biến thể để đạt 1000 mẫu
    dataset = []
    
    # Định nghĩa các tool groups thực tế để gán cho từng layout
    layout_candidates = {
        "dense": ["generate_classic_content_slide", "generate_content_slide", "generate_split_layout_list_slide"],
        "concise": ["generate_split_layout_list_slide", "generate_icon_list_slide", "generate_classic_content_slide"],
        "chart": ["generate_bar_chart_slide_2", "generate_pie_chart_slide_1", "generate_line_chart_slide_2", "generate_classic_content_slide"],
        "process": ["generate_process_steps_slide", "generate_comparison_slide", "generate_icon_list_slide"],
        "compare": ["generate_comparison_slide", "generate_split_layout_list_slide", "generate_classic_content_slide"]
    }

    for topic in base_topics:
        name = topic.get("name", "Chủ đề chưa đặt tên")
        dense = topic.get("dense_paragraph", "")
        bullets = topic.get("bullets", [])
        data_points = topic.get("data_points", "")
        milestones = topic.get("milestones", [])
        comparison = topic.get("comparison", "")

        # Thử thách 1: Văn bản dài dòng phức tạp (Cần rút gọn/tóm tắt)
        if dense:
            user_prompt = (
                f"Hãy thiết kế một slide trình bày chi tiết về: {name}.\n"
                f"Nội dung thô của tài liệu: \"{dense}\".\n"
                f"Yêu cầu: Hãy đọc kỹ và chắt lọc ra các luận điểm cực kỳ ngắn gọn để đưa vào slide."
            )
            # Chọn schemas thật
            candidates = [format_tool_for_qwen(flat_tools[t_name]) for t_name in layout_candidates["dense"] if t_name in flat_tools]
            dataset.append({
                "system_prompt": "",
                "user_prompt": user_prompt,
                "tools": candidates
            })

        # Thử thách 2: Ngắn gọn xúc tích dạng gạch đầu dòng (List Layout)
        if bullets:
            bullets_str = "\n- ".join(bullets)
            user_prompt = (
                f"Tạo slide tóm tắt các điểm chính sau về {name}:\n"
                f"- {bullets_str}\n"
                f"Yêu cầu: Sử dụng layout chia hai cột hoặc danh sách có icon để hiển thị."
            )
            candidates = [format_tool_for_qwen(flat_tools[t_name]) for t_name in layout_candidates["concise"] if t_name in flat_tools]
            dataset.append({
                "system_prompt": "",
                "user_prompt": user_prompt,
                "tools": candidates
            })

        # Thử thách 3: Trích xuất số liệu / Vẽ biểu đồ (Chart Layout)
        if data_points:
            user_prompt = (
                f"Hãy thiết kế một slide báo cáo số liệu thống kê cho: {name}.\n"
                f"Thông tin số liệu thu thập được: {data_points}.\n"
                f"Yêu cầu: Hãy trình bày số liệu này bằng biểu đồ cột hoặc biểu đồ tròn trực quan để khán giả dễ nắm bắt."
            )
            candidates = [format_tool_for_qwen(flat_tools[t_name]) for t_name in layout_candidates["chart"] if t_name in flat_tools]
            dataset.append({
                "system_prompt": "",
                "user_prompt": user_prompt,
                "tools": candidates
            })

        # Thử thách 4: Quy trình các bước tuần tự (Process/Timeline Layout)
        if milestones:
            milestones_str = " -> ".join(milestones)
            user_prompt = (
                f"Hãy dựng slide trình bày quy trình các bước hoặc lộ trình phát triển của {name}.\n"
                f"Các mốc cụ thể bao gồm: {milestones_str}.\n"
                f"Yêu cầu: Hãy gọi hàm layout Quy trình các bước (process steps) để thể hiện dòng thời gian tuần tự."
            )
            candidates = [format_tool_for_qwen(flat_tools[t_name]) for t_name in layout_candidates["process"] if t_name in flat_tools]
            dataset.append({
                "system_prompt": "",
                "user_prompt": user_prompt,
                "tools": candidates
            })

        # Thử thách 5: So sánh đối lập/Song song (Comparison Layout)
        if comparison:
            user_prompt = (
                f"Thiết kế slide phân tích và so sánh đối chiếu về {name}.\n"
                f"Chi tiết nội dung so sánh: {comparison}.\n"
                f"Yêu cầu: Thể hiện bằng layout so sánh chia hai phần đối xứng song song."
            )
            candidates = [format_tool_for_qwen(flat_tools[t_name]) for t_name in layout_candidates["compare"] if t_name in flat_tools]
            dataset.append({
                "system_prompt": "",
                "user_prompt": user_prompt,
                "tools": candidates
            })

    # Đảm bảo cắt đúng số lượng
    dataset = dataset[:target_samples]
    
    # 3. Ghi dữ liệu ra tệp JSON
    output_path = os.path.join(os.path.dirname(__file__), "slidegen_challenge_dataset.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
        
    print(f"\n[Dataset Gen] SUCCESS! Generated {len(dataset)} challenge prompts and saved to {output_path}!")

if __name__ == "__main__":
    main()
