from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import os
import shutil
from workflow import main_workflow
import uvicorn


app = FastAPI()

@app.post("/process/")
async def process_docx(
    router_flags: bool = Form(True),
    file: UploadFile = File(...),
):
    # Tạo thư mục tạm để lưu file upload
    input_folder = "uploads"
    output_folder = "outputs"
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    # Lưu file upload
    input_path = os.path.join(input_folder, file.filename)
    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Gọi hàm xử lý
    try:
        result_zip = main_workflow(
            router_flags=router_flags,
            docx_file=input_path,
            output_folder=output_folder
        )
        return FileResponse(
            path=result_zip,
            filename=os.path.basename(result_zip),
            media_type="application/zip"
        )
    except Exception as e:
        return {"error": str(e)}
    
if __name__ == "__main__":
    uvicorn.run(
        "main:app",   # <--- thay bằng tên file chứa app của bạn
        host="127.0.0.1",
        port=8000,
        reload=True
    )
