import json
from backend.workflows.slidegen_workflow.tools.ddgs_tool import search_ddgs_images

print("🤖 [LLM Simulation] Đang phân tích yêu cầu của người dùng...")
print("👤 Yêu cầu: 'Tìm cho tôi 3 bức ảnh về phong cảnh thiên nhiên đẹp'")

# 1. Đây là cục JSON mà con AI (LLM) sẽ sinh ra sau khi đọc tool_des.py
llm_generated_json = """
{
  "query": "lionel messi portrait action shot",
  "max_results": 3
}
"""

print(f"\n🤖 [LLM Simulation] AI quyết định gọi hàm bằng JSON sau:\n{llm_generated_json}")

# 2. Hệ thống (Code của chúng ta) sẽ parse JSON này thành Dictionary
try:
    function_args = json.loads(llm_generated_json)
    
    print("⚙️ [System] Bắt đầu gọi hàm search_ddgs_images...")
    
    # 3. Dùng dấu ** để unpack dictionary thành các tham số truyền vào hàm
    result = search_ddgs_images(**function_args)
    
    # 4. In kết quả trả về
    urls = json.loads(result)
    print("\n--- KẾT QUẢ TỪ API ---")
    if urls:
        print(f"✅ Đã tải thành công {len(urls)} ảnh!")
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
    else:
        print("❌ Không có ảnh (hoặc bị chặn).")

except Exception as e:
    print(f"❌ Lỗi hệ thống: {e}")
