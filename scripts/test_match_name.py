import json

file_path=r"C:\vscode\SlideGen\scripts\test_cot_results.json"
try :
    with open(file_path,"r",encoding="utf-8") as f:
        data=json.load(f)
        print(type(data))
    dem=0
    for item in data: 
        if item['tool_name_match']: dem+=1
    print(dem)
    print("tool_name_match: "+str(dem/len(data)*100)+"%")

except FileNotFoundError:
    print(f"Không tìm thấy file: {file_path}")
except json.JSONDecodeError:
    print(f"Lỗi: File {file_path} không phải là định dạng JSON hợp lệ.")
except Exception as e:
    print(f"Đã xảy ra lỗi: {e}")
        