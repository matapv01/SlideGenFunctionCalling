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
import re
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
IMAGE_DIR = os.path.join(PROJECT_DIR, "Image")  # Thư mục chứa hình ảnh

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

def clear_temp_dir(temp_dir: str):
    if os.path.exists(temp_dir):
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Không thể xóa {file_path}: {e}")

@app.post("/api/upload-docx")
async def upload_docx(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.docx'):
            raise HTTPException(status_code=400, detail="Chỉ chấp nhận file DOCX")
         
        temp_path = os.path.join(TEMP_DIR, file.filename)

        # Xoá toàn bộ file/thư mục trong thư mục tạm
        clear_temp_dir(TEMP_DIR)
        
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
            
            # Sửa đường dẫn hình ảnh trong nội dung để hiển thị trên web
            def fix_web_image_path(match):
                src_value = match.group(1)
                # Nếu là đường dẫn tương đối (như Picture2.png), chuyển thành API endpoint
                if not src_value.startswith('/') and not src_value.startswith('http'):
                    return f'src="/api/images/{src_value}"'
                return match.group(0)
            
            content = re.sub(r'src="([^"]*)"', fix_web_image_path, content)
            
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
            
            # Sửa đường dẫn hình ảnh trong nội dung để hiển thị trên web
            def fix_web_image_path(match):
                src_value = match.group(1)
                # Nếu là đường dẫn tương đối (như Picture2.png), chuyển thành API endpoint
                if not src_value.startswith('/') and not src_value.startswith('http'):
                    return f'src="/api/images/{src_value}"'
                return match.group(0)
            
            content = re.sub(r'src="([^"]*)"', fix_web_image_path, content)
            
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
    driver = None
    try:
        # Tạo timestamp duy nhất cho thư mục tạm
        import time
        timestamp = str(int(time.time()))
        temp_folder = os.path.join(TEMP_DIR, f"pdf_{timestamp}")
        
        # Tạo thư mục tạm
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
        os.makedirs(temp_folder, exist_ok=True)
        
        logger.info(f"Đã tạo thư mục tạm: {temp_folder}")
        
        # Cấu hình Chrome cho chế độ headless
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--hide-scrollbars')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        image_files = []
        for i, slide in enumerate(slides, 1):
            try:
                html_path = os.path.join(temp_folder, f'slide_{i:02d}.html')
                logger.info(f"Đang tạo file HTML: {html_path}")
                
                # Xử lý nội dung slide để sửa đường dẫn hình ảnh
                slide_content = slide["content"]
                
                # Sửa đường dẫn hình ảnh: chuyển tất cả đường dẫn thành file URL tuyệt đối
                def fix_image_path(match):
                    src_value = match.group(1)
                    
                    # Nếu đã là file URL tuyệt đối, giữ nguyên
                    if src_value.startswith('file://'):
                        return match.group(0)
                    
                    # Nếu là API endpoint (như /api/images/Picture2.png), trích xuất tên file
                    if src_value.startswith('/api/images/'):
                        image_filename = src_value.split('/')[-1]
                        image_path = os.path.join(IMAGE_DIR, image_filename)
                        if os.path.exists(image_path):
                            abs_path = os.path.abspath(image_path)
                            result = f'src="file:///{abs_path.replace(os.sep, "/")}"'
                            logger.info(f"Chuyển đổi đường dẫn API {src_value} thành {result}")
                            return result
                        else:
                            logger.warning(f"Không tìm thấy file hình ảnh: {image_path}")
                    
                    # Nếu bắt đầu với /static/, chuyển thành đường dẫn tuyệt đối
                    elif src_value.startswith('/static/'):
                        abs_path = os.path.abspath(os.path.join(STATIC_DIR, src_value.lstrip("/static/")))
                        if os.path.exists(abs_path):
                            result = f'src="file:///{abs_path.replace(os.sep, "/")}"'
                            logger.info(f"Chuyển đổi đường dẫn static {src_value} thành {result}")
                            return result
                        else:
                            logger.warning(f"Không tìm thấy file static: {abs_path}")
                    
                    # Nếu là đường dẫn tương đối (như Picture2.png), giả định nó ở thư mục Image
                    elif not src_value.startswith('/') and not src_value.startswith('http'):
                        image_path = os.path.join(IMAGE_DIR, src_value)
                        if os.path.exists(image_path):
                            abs_path = os.path.abspath(image_path)
                            result = f'src="file:///{abs_path.replace(os.sep, "/")}"'
                            logger.info(f"Chuyển đổi đường dẫn tương đối {src_value} thành {result}")
                            return result
                        else:
                            logger.warning(f"Không tìm thấy file hình ảnh tương đối: {image_path}")
                    
                    # Nếu là URL HTTP tuyệt đối, giữ nguyên
                    elif src_value.startswith('http'):
                        return match.group(0)
                    
                    # Ghi log các trường hợp không xử lý được
                    logger.warning(f"Đường dẫn hình ảnh không xử lý được: {src_value}")
                    return match.group(0)
                
                slide_content = re.sub(r'src="([^"]*)"', fix_image_path, slide_content)
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(f'''<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                margin: 0;
                padding: 20px;
                width: 1920px;
                height: 1080px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: Arial, sans-serif;
                background: white;
            }}
            .slide-content {{
                width: 100%;
                height: 100%;
                padding: 40px;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }}
            img {{
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
                display: block;
            }}
            .image-area img {{
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
                display: block;
            }}
            .slide-container img {{
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
                display: block;
            }}
        </style>
    </head>
    <body>
        <div class="slide-content">
            {slide_content}
        </div>
    </body>
</html>''')
                
                # Đặt timeout cho việc tải trang
                driver.set_page_load_timeout(30)
                
                # Tải file HTML
                file_url = f'file:///{html_path.replace(os.sep, "/")}'
                logger.info(f"Đang tải URL: {file_url}")
                driver.get(file_url)
                
                # Đợi trang tải xong và hình ảnh được render
                await asyncio.sleep(3)
                
                # Thực thi JavaScript để đảm bảo tất cả hình ảnh đã được tải
                driver.execute_script("""
                    return new Promise((resolve) => {
                        let images = document.getElementsByTagName('img');
                        let loadedCount = 0;
                        let totalImages = images.length;
                        
                        if (totalImages === 0) {
                            resolve();
                            return;
                        }
                        
                        for (let img of images) {
                            if (img.complete) {
                                loadedCount++;
                            } else {
                                img.onload = () => {
                                    loadedCount++;
                                    if (loadedCount === totalImages) {
                                        resolve();
                                    }
                                };
                                img.onerror = () => {
                                    loadedCount++;
                                    if (loadedCount === totalImages) {
                                        resolve();
                                    }
                                };
                            }
                        }
                        
                        if (loadedCount === totalImages) {
                            resolve();
                        }
                        
                        // Timeout sau 5 giây
                        setTimeout(resolve, 5000);
                    });
                """)
                
                # Đợi thêm để đảm bảo mọi thứ được render
                await asyncio.sleep(1)
                
                # Chụp ảnh màn hình
                image_path = os.path.join(temp_folder, f'slide_{i:02d}.png')
                driver.save_screenshot(image_path)
                
                # Kiểm tra ảnh chụp đã được tạo
                if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
                    image_files.append(image_path)
                    logger.info(f"Đã lưu ảnh chụp: {image_path}")
                else:
                    logger.error(f"Thất bại khi tạo ảnh chụp: {image_path}")
                    
            except Exception as slide_error:
                logger.error(f"Lỗi khi xử lý slide {i}: {slide_error}")
                continue
        
        if driver:
            driver.quit()
            driver = None
        
        if not image_files:
            raise HTTPException(status_code=500, detail="Không có ảnh chụp nào được tạo")
        
        # Chuyển đổi hình ảnh thành PDF
        pdf_path = os.path.join(TEMP_DIR, f'slides_{timestamp}.pdf')
        logger.info(f"Đang tạo PDF: {pdf_path}")
        
        # img2pdf.convert mong đợi danh sách đường dẫn file hình ảnh dưới dạng chuỗi
        pdf_bytes = img2pdf.convert(image_files)
        
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        
        # Kiểm tra PDF đã được tạo
        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
            raise HTTPException(status_code=500, detail="Thất bại khi tạo file PDF")
        
        logger.info(f"PDF đã được tạo thành công: {pdf_path}")
        
        response = FileResponse(
            pdf_path,
            filename="slides.pdf",
            media_type='application/pdf'
        )
        return response
        
    except Exception as e:
        logger.exception(f"Lỗi khi xuất PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Dọn dẹp tài nguyên
        if driver:
            try:
                driver.quit()
            except:
                pass
        
        if temp_folder and os.path.exists(temp_folder):
            try:
                shutil.rmtree(temp_folder)
            except Exception as cleanup_error:
                logger.warning(f"Thất bại khi dọn dẹp thư mục tạm: {cleanup_error}")

@app.get("/api/images/{image_name}")
async def get_image(image_name: str):
    """Endpoint để phục vụ hình ảnh từ thư mục Image"""
    try:
        image_path = os.path.join(IMAGE_DIR, image_name)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Không tìm thấy hình ảnh")
        return FileResponse(image_path)
    except Exception as e:
        logger.exception(f"Lỗi khi phục vụ hình ảnh {image_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)