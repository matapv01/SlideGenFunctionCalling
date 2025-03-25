import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse  # StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import tempfile
from slide_generator import process_slides

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

PROJECT_DIR = "/home/naver/Documents/Minh/SligenFunctionCalling/github/project"  # Consider using environment variable
STATIC_DIR = os.path.join(PROJECT_DIR, "static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Consider more specific origins, like ["*"] in dev, but restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
            logger.info("Serving index.html")
            return f.read()
    except FileNotFoundError:
        logger.error("File index.html not found")
        raise HTTPException(status_code=404, detail="index.html not found")  # 404 is more appropriate
    except Exception as e: # Catch other possible errors
        logger.exception("Error reading index.html")
        raise HTTPException(status_code=500, detail="Internal Server Error")
@app.post("/upload-docx/")
async def upload_docx(file: UploadFile = File(...)):
    # 1. Lưu file DOCX.
    temp_dir = tempfile.TemporaryDirectory()  # Không dùng `with` ở đây.
    try:
        temp_file = os.path.join(temp_dir.name, file.filename)
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Saved temp file: {temp_file}")

        # 2. Tạo output_folder.
        output_folder = os.path.join(temp_dir.name, "output_Test")
        os.makedirs(output_folder, exist_ok=True)
        logger.info(f"Created output folder: {output_folder}")

        # 3. Gọi process_slides.
        logger.info("Starting slide processing...")
        zip_path = process_slides(temp_file, output_folder)
        logger.info(f"Generated ZIP file: {zip_path}")

        # 4. Kiểm tra sự tồn tại.
        if not os.path.exists(zip_path):
            raise HTTPException(status_code=500, detail="ZIP file was not created.")

        # 5. Trả về StreamingResponse.
        logger.info("Sending ZIP file to client")

        def iterfile():  # Tạo một generator function
            try:
                with open(zip_path, "rb") as zip_file:
                    while chunk := zip_file.read(8192):  # Đọc từng chunk 8KB
                        yield chunk
            finally:
                temp_dir.cleanup()  # Dọn dẹp *sau khi* stream xong.

        return StreamingResponse(
            iterfile(),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=slides.zip"},
        )
    except Exception as e:
        logger.exception(f"Error processing DOCX: {e}")
        temp_dir.cleanup() # dọn dẹp khi có lỗi
        raise HTTPException(status_code=500, detail=f"Error processing DOCX: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)