import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import tempfile
import zipfile
import uvicorn
from slide_generator import process_slides  # Giả định hàm xử lý DOCX từ slide_generator.py
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import img2pdf
import asyncio

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(PROJECT_DIR, "static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")
OUTPUT_DIR = os.path.join(STATIC_DIR, "output")
TEMP_DIR = os.path.join(STATIC_DIR, "temp")

for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        index_path = os.path.join(STATIC_DIR, "index.html")
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"File not found: {index_path}")
        with open(index_path, "r", encoding="utf-8") as f:
            logger.info(f"Serving index.html from {index_path}")
            return f.read()
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Error reading index.html: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/api/upload-docx")
async def upload_docx(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.docx'):
            raise HTTPException(status_code=400, detail="Chỉ chấp nhận file DOCX")
        temp_path = os.path.join(TEMP_DIR, file.filename)
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        output_folder = os.path.join(OUTPUT_DIR, os.path.splitext(file.filename)[0])
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
        os.makedirs(output_folder)
        process_slides(temp_path, output_folder)
        zip_files = [f for f in os.listdir(output_folder) if f.endswith('.zip')]
        if not zip_files:
            raise FileNotFoundError("Không tìm thấy file ZIP kết quả")
        zip_path = os.path.join(output_folder, zip_files[0])
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)
        slides = []
        html_dir = os.path.join(output_folder, 'html')
        png_dir = os.path.join(output_folder, 'png')
        if not os.path.exists(html_dir):
            raise FileNotFoundError("Thư mục 'html' không tồn tại trong file ZIP")
        html_files = sorted([f for f in os.listdir(html_dir) if f.endswith('.html')])
        for html_file in html_files:
            html_path = os.path.join(html_dir, html_file)
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            png_file = html_file.replace('.html', '.png')
            png_path = os.path.join(png_dir, png_file)
            preview_url = None
            if os.path.exists(png_path):
                relative_path = os.path.relpath(png_path, STATIC_DIR)
                preview_url = f"/static/{relative_path.replace(os.sep, '/')}"
            slides.append({
                "content": content,
                "type": "html",
                "preview": preview_url
            })
        os.remove(temp_path)
        os.remove(zip_path)
        return JSONResponse(content={"slides": slides})
    except Exception as e:
        logger.exception(f"Error processing DOCX file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-zip")
async def upload_zip(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Chỉ chấp nhận file ZIP")
        temp_path = os.path.join(TEMP_DIR, file.filename)
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        output_folder = os.path.join(OUTPUT_DIR, os.path.splitext(file.filename)[0])
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
        os.makedirs(output_folder)
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)
        slides = []
        html_dir = os.path.join(output_folder, 'html')
        png_dir = os.path.join(output_folder, 'png')
        if not os.path.exists(html_dir):
            raise FileNotFoundError("Thư mục 'html' không tồn tại trong file ZIP")
        html_files = sorted([f for f in os.listdir(html_dir) if f.endswith('.html')])
        for html_file in html_files:
            html_path = os.path.join(html_dir, html_file)
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            png_file = html_file.replace('.html', '.png')
            png_path = os.path.join(png_dir, png_file)
            preview_url = None
            if os.path.exists(png_path):
                relative_path = os.path.relpath(png_path, STATIC_DIR)
                preview_url = f"/static/{relative_path.replace(os.sep, '/')}"
            slides.append({
                "content": content,
                "type": "html",
                "preview": preview_url
            })
        os.remove(temp_path)
        return JSONResponse(content={"slides": slides})
    except Exception as e:
        logger.exception(f"Error processing ZIP file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/save-slides")
async def save_slides(slides: List[dict]):
    try:
        timestamp = tempfile.gettempdir().split(os.sep)[-1]
        output_folder = os.path.join(OUTPUT_DIR, f"edited_slides_{timestamp}")
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
        os.makedirs(output_folder)
        html_folder = os.path.join(output_folder, "html")
        os.makedirs(html_folder, exist_ok=True)
        for i, slide in enumerate(slides, 1):
            file_name = f"slide_{i:02d}"
            html_path = os.path.join(html_folder, f"{file_name}.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(slide["content"])
        zip_filename = f"slides_{timestamp}.zip"
        zip_path = os.path.join(OUTPUT_DIR, zip_filename)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_folder)
                    zipf.write(file_path, arcname)
        return FileResponse(zip_path, filename=zip_filename)
    except Exception as e:
        logger.exception(f"Error saving slides: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export-pdf")
async def export_pdf(slides: List[dict]):
    temp_folder = None
    try:
        timestamp = tempfile.gettempdir().split(os.sep)[-1]
        temp_folder = os.path.join(TEMP_DIR, f"pdf_{timestamp}")
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
        os.makedirs(temp_folder)
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        image_files = []
        for i, slide in enumerate(slides, 1):
            html_path = os.path.join(temp_folder, f'slide_{i:02d}.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(f'''
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <meta charset="UTF-8">
                            <style>
                                body {{
                                    margin: 0;
                                    padding: 20px;
                                    width: 1920px;
                                    height: 1080px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                }}
                                .slide-content {{
                                    width: 100%;
                                    height: 100%;
                                    padding: 40px;
                                }}
                            </style>
                        </head>
                        <body>
                            <div class="slide-content">
                                {slide["content"]}
                            </div>
                        </body>
                    </html>
                ''')
            # Tăng thời gian chờ tải trang
            driver.set_page_load_timeout(300)  # 5 phút
            driver.get(f'file:///{html_path}')
            # Đợi thêm để đảm bảo trang tải xong
            await asyncio.sleep(1)
            image_path = os.path.join(temp_folder, f'slide_{i:02d}.png')
            driver.save_screenshot(image_path)
            image_files.append(image_path)
        
        driver.quit()
        
        pdf_path = os.path.join(TEMP_DIR, f'slides_{timestamp}.pdf')
        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert(image_files))
        
        response = FileResponse(
            pdf_path,
            filename="slides.pdf",
            media_type='application/pdf'
        )
        return response
    except Exception as e:
        logger.exception(f"Error exporting PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_folder and os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)