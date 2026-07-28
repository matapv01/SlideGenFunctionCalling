import sys
try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        print("❌ Lỗi: Chưa cài đặt thư viện 'duckduckgo-search'. Vui lòng chạy: pip install duckduckgo-search")
        sys.exit(1)

def test_duckduckgo():
    print("🔍 Đang thử kết nối tới DuckDuckGo Image Search từ Docker...")
    print("🌍 Truy vấn thử nghiệm: 'lionel messi'")
    
    try:
        with DDGS() as ddgs:
            # Chỉ lấy 3 kết quả đầu tiên
            results = list(ddgs.images("lionel messi", max_results=3))
            
            if results:
                print("\n✅ KẾT QUẢ: IP CỦA BẠN BÌNH THƯỜNG (KHÔNG BỊ CHẶN)!")
                print(f"Đã tìm thấy {len(results)} ảnh:")
                for idx, res in enumerate(results, 1):
                    print(f"  {idx}. {res.get('image')}")
            else:
                print("\n⚠️ KẾT QUẢ: IP KHÔNG BỊ CHẶN, NHƯNG KHÔNG CÓ ẢNH NÀO TRẢ VỀ.")
                
    except Exception as e:
        print("\n❌ KẾT QUẢ: IP CỦA BẠN ĐÃ BỊ DUCKDUCKGO CHẶN!")
        print(f"Chi tiết lỗi: {e}")
        
        if "403" in str(e) or "Ratelimit" in str(e):
            print("\n👉 Nguyên nhân: DuckDuckGo đã chặn IP này vì nghi ngờ là Bot hoặc bị gọi quá nhiều lần (Lỗi 403 Ratelimit).")
        elif "Timeout" in str(e):
            print("\n👉 Nguyên nhân: Không thể kết nối tới DuckDuckGo (Quá thời gian chờ). Có thể bị chặn ở cấp độ mạng.")

if __name__ == "__main__":
    test_duckduckgo()
