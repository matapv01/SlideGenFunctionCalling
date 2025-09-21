import logging
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import tempfile
import zipfile
import uvicorn
import re
import json
import subprocess
from typing import List
import asyncio
import uuid
from datetime import datetime
    

from io import BytesIO
from pydantic import BaseModel

# Import capture module
from capture import SlideCapture

# Pydantic models for capture API
class CaptureSlideRequest(BaseModel):
    html_content: str
    slide_name: str = "slide"

class CaptureMultipleSlidesRequest(BaseModel):
    slides: List[dict]

# Simple HTML Converter class để thay thế HTMLConverter đã bị xóa
class HTMLConverter:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.converter_js = os.path.join(project_dir, "converter.js")
        self.node_modules = os.path.join(project_dir, "node_modules")
        
    def convert_slides_batch(self, input_folder, output_folder):
        """Convert HTML slides using Node.js converter.js"""
        os.makedirs(output_folder, exist_ok=True)
        
        result = {'success': [], 'failed': []}
        html_files = [f for f in os.listdir(input_folder) if f.endswith('.html')]
        
        for html_file in html_files:
            try:
                input_path = os.path.join(input_folder, html_file)
                output_path = os.path.join(output_folder, f"converted_{html_file}")
                
                # Run converter.js với nhiều phương pháp encoding backup
                cmd = ['node', self.converter_js, input_path, output_path]
                
                # Thử UTF-8 trước
                try:
                    process = subprocess.run(
                        cmd, 
                        cwd=self.project_dir, 
                        capture_output=True, 
                        text=True, 
                        timeout=30,
                        encoding='utf-8',
                        errors='ignore'
                    )
                except UnicodeDecodeError:
                    # Nếu UTF-8 lỗi, thử với cp1252 và ignore errors
                    try:
                        process = subprocess.run(
                            cmd, 
                            cwd=self.project_dir, 
                            capture_output=True, 
                            text=True, 
                            timeout=30,
                            encoding='cp1252',
                            errors='ignore'
                        )
                    except UnicodeDecodeError:
                        # Nếu vẫn lỗi, dùng bytes mode
                        process = subprocess.run(
                            cmd, 
                            cwd=self.project_dir, 
                            capture_output=True, 
                            timeout=30
                        )
                        # Convert bytes to string nếu cần
                        if hasattr(process, 'stdout') and isinstance(process.stdout, bytes):
                            process.stdout = process.stdout.decode('utf-8', errors='ignore')
                        if hasattr(process, 'stderr') and isinstance(process.stderr, bytes):
                            process.stderr = process.stderr.decode('utf-8', errors='ignore')
                
                if process.returncode == 0:
                    result['success'].append(html_file)
                    logger.info(f"Successfully converted: {html_file}")
                else:
                    result['failed'].append(html_file)
                    logger.warning(f"Conversion failed for {html_file}: {process.stderr}")
                    
            except subprocess.TimeoutExpired:
                result['failed'].append(html_file)
                logger.error(f"Conversion timeout for {html_file}")
            except Exception as e:
                result['failed'].append(html_file)
                logger.error(f"Error converting {html_file}: {e}")
                
        logger.info(f"Conversion completed: {len(result['success'])} success, {len(result['failed'])} failed")
        return result
    
    def check_dependencies(self):
        """Check if Node.js and dependencies are available"""
        try:
            subprocess.run(['node', '--version'], capture_output=True, check=True)
            return os.path.exists(self.converter_js) and os.path.exists(self.node_modules)
        except:
            return False
    
    def get_conversion_status(self, html_folder, converted_folder):
        """Get conversion status"""
        if not os.path.exists(converted_folder):
            return "not_converted"
        
        html_files = [f for f in os.listdir(html_folder) if f.endswith('.html')]
        converted_files = [f for f in os.listdir(converted_folder) if f.endswith('.html')]
        
        if len(converted_files) >= len(html_files):
            return "completed"
        elif len(converted_files) > 0:
            return "partial"
        else:
            return "not_converted"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(PROJECT_DIR, "static")
IMAGE_DIR = os.path.join(PROJECT_DIR, "Image")

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
CAPTURES_DIR = os.path.join(STATIC_DIR, "captures")

for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR, CAPTURES_DIR]:
    os.makedirs(directory, exist_ok=True)

# Optional: allow disabling the converter at runtime. If disabled or if
# initialization fails we keep html_converter as None and skip conversion
# steps. This is useful for deployments without Node/puppeteer.
DISABLE_CONVERTER = os.environ.get('DISABLE_CONVERTER', '0').lower() in ('1', 'true', 'yes')  # Mặc định BẬT converter

if DISABLE_CONVERTER:
    logger.info('DISABLE_CONVERTER set: converter functionality is disabled')
    html_converter = None
else:
    try:
        html_converter = HTMLConverter(PROJECT_DIR)
        logger.info('HTMLConverter initialized successfully')
    except Exception as e:
        logger.warning('Failed to initialize HTMLConverter, disabling converter: %s', e)
        html_converter = None

# Initialize capture system
try:
    slide_capture = SlideCapture()
    logger.info('SlideCapture initialized successfully')
except Exception as e:
    logger.warning('Failed to initialize SlideCapture: %s', e)
    slide_capture = None

@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail=f"File not found: {index_path}")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/edit", response_class=HTMLResponse)
async def read_edit_page(source: str = None, project: str = None):
    """
    Serve the editor page. If `project` is provided and the project's output
    folder contains slides, inject the slides JSON into the page so the
    editor can load them without relying on client-side localStorage.
    """
    edit_path = os.path.join(PROJECT_DIR, "edit.html")  # edit.html ở thư mục root, không phải static
    if not os.path.exists(edit_path):
        raise HTTPException(status_code=404, detail=f"File not found: {edit_path}")

    with open(edit_path, "r", encoding="utf-8") as f:
        html = f.read()

    # If project is supplied, try to build slides and inject into the page.
    if project:
        try:
            output_folder = os.path.join(OUTPUT_DIR, project)
            if os.path.exists(output_folder):
                slides = build_slides_from_output(output_folder)
                # Prepare a small script to set localStorage before other scripts run
                slides_json = json.dumps(slides).replace('</', '<\/')
                snippet = f"<script>localStorage.setItem('generatedSlides', JSON.stringify({slides_json})); localStorage.setItem('slidesSource', 'project-{project}');</script>"
                # Inject snippet immediately after opening <body> tag
                body_open = re.search(r"<body[^>]*>", html, flags=re.IGNORECASE)
                if body_open:
                    insert_pos = body_open.end()
                    html = html[:insert_pos] + snippet + html[insert_pos:]
                else:
                    # Fallback: prepend to document
                    html = snippet + html
        except Exception as e:
            logger.warning('Failed to inject project slides into edit page: %s', e)

    return HTMLResponse(content=html, status_code=200)


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


def build_slides_from_output(output_folder: str):
    slides = []
    
    # Ưu tiên sử dụng converted slides nếu có
    converted_dir = os.path.join(output_folder, 'converted')
    html_dir = os.path.join(output_folder, 'html')
    png_dir = os.path.join(output_folder, 'png')
    
    # Chọn thư mục HTML để sử dụng
    source_html_dir = converted_dir if os.path.exists(converted_dir) else html_dir
    use_converted = os.path.exists(converted_dir)
    
    if not os.path.exists(source_html_dir):
        raise FileNotFoundError("Thư mục HTML không tồn tại trong kết quả")

    logger.info(f"Building slides from {'converted' if use_converted else 'original'} HTML directory")
    
    html_files = sorted([f for f in os.listdir(source_html_dir) if f.endswith('.html')])
    for index, html_file in enumerate(html_files):
        html_path = os.path.join(source_html_dir, html_file)
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Sửa đường dẫn hình ảnh đơn giản
        import re
        content = re.sub(r'src="([^"]*)"', lambda m: f'src="/api/images/{m.group(1)}"' if not m.group(1).startswith(('http', '/', 'data:')) else m.group(0), content)

        # Extract metadata từ HTML để phục vụ editor
        slide_metadata = extract_slide_metadata(content, html_file)

        # Tìm preview image - có thể cần adjust tên file cho converted slides
        preview_url = None
        if use_converted and html_file.startswith('converted_'):
            # Tìm PNG file tương ứng với slide gốc
            original_name = html_file.replace('converted_', '')
            png_file = original_name.replace('.html', '.png')
        else:
            png_file = html_file.replace('.html', '.png')
            
        png_path = os.path.join(png_dir, png_file)
        if os.path.exists(png_path):
            relative_path = os.path.relpath(png_path, STATIC_DIR)
            preview_url = f"/static/{relative_path.replace(os.sep, '/')}"

        slides.append({
            "content": content,
            "type": "html" if not use_converted else "html_absolute",
            "isConverted": use_converted,
            "preview": preview_url,
            "title": slide_metadata.get("title", f"Slide {index + 1}"),
            "backgroundColor": slide_metadata.get("backgroundColor", "white"),
            "elements": slide_metadata.get("elements", []),
            "metadata": slide_metadata
        })
    return slides


def extract_slide_metadata(html_content: str, filename: str):
    """Extract metadata từ HTML content để editor sử dụng - phiên bản đơn giản"""
    metadata = {
        "title": filename.replace('.html', '').replace('slide_', 'Slide '),
        "backgroundColor": "white",
        "elements": []
    }
    
    try:
        # Extract title từ h1, h2 tags
        import re
        title_match = re.search(r'<h[12][^>]*>([^<]+)</h[12]>', html_content, re.IGNORECASE)
        if title_match:
            metadata["title"] = title_match.group(1).strip()
        
        # Extract background color từ body style
        bg_match = re.search(r'background(?:-color)?:\s*([^;]+)', html_content)
        if bg_match:
            metadata["backgroundColor"] = bg_match.group(1).strip()
            
    except Exception as e:
        logger.warning(f"Error extracting metadata from {filename}: {e}")
    
    return metadata


@app.post("/api/upload-docx")
async def upload_docx(file: UploadFile = File(...)):
    """
    Xử lý DOCX trực tiếp trong frontend, bypass backend để tránh RuntimeWarning
    """
    # Import os module với alias để tránh conflict
    import os as os_module
    
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file DOCX")

    # Tạo project name từ filename
    project_name = os_module.path.splitext(file.filename)[0]
    output_folder = os_module.path.join(OUTPUT_DIR, project_name)
    if os_module.path.exists(output_folder):
        try:
            shutil.rmtree(output_folder)
        except PermissionError as pe:
            logger.warning(f"Permission error removing existing folder: {pe}")
            # Try to create a folder with timestamp appended instead
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            project_name = f"{project_name}_{timestamp}"
            logger.info(f"Using alternative project name: {project_name}")
            output_folder = os_module.path.join(OUTPUT_DIR, project_name)
        except Exception as e:
            logger.error(f"Error removing existing project folder: {e}")
            # Continue with existing folder but clean it instead
            for item in os_module.listdir(output_folder):
                item_path = os_module.path.join(output_folder, item)
                try:
                    if os_module.path.isfile(item_path):
                        os_module.unlink(item_path)
                    elif os_module.path.isdir(item_path):
                        # Skip the problematic 'converted' folder
                        if item != "converted":
                            shutil.rmtree(item_path, ignore_errors=True)
                except Exception as e:
                    logger.warning(f"Could not remove {item_path}: {e}")
    
    # Make sure the output folder exists
    os_module.makedirs(output_folder, exist_ok=True)
    
    # Lưu file DOCX tạm thời
    temp_path = os_module.path.join(TEMP_DIR, file.filename)
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Gọi workflow trực tiếp thay vì qua Backend API
        logger.info(f"🤖 Processing DOCX directly via workflow: {file.filename}")
        
        # Import và chạy workflow trong thread pool để tránh block
        import sys
        
        # Thêm parent directory vào sys.path để import được workflow
        parent_dir = os_module.path.dirname(PROJECT_DIR)
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
        
        # Import workflow function
        try:
            from workflow import process_slides_with_langgraph
            
            # Chạy workflow trong thread pool để tránh async conflict
            import concurrent.futures
            
            def run_workflow():
                try:
                    # Create our own structure that fully bypasses the workflow's directory creation
                    import tempfile
                    
                    # Create master temp dir that will be used instead of output_folder
                    temp_workflow_dir = tempfile.mkdtemp(prefix="slidegen_workflow_")
                    logger.info(f"Created temporary workflow directory: {temp_workflow_dir}")
                    
                    # Pre-create all required subdirectories to avoid permission issues
                    html_dir = os.path.join(temp_workflow_dir, "html")
                    png_dir = os.path.join(temp_workflow_dir, "png") 
                    debug_dir = os.path.join(temp_workflow_dir, "temp_debug")
                    debug_html_dir = os.path.join(debug_dir, "html")
                    
                    for dir_path in [html_dir, png_dir, debug_dir, debug_html_dir]:
                        try:
                            os.makedirs(dir_path, exist_ok=True)
                            logger.info(f"Created directory: {dir_path}")
                        except Exception as e:
                            logger.warning(f"Could not create directory {dir_path}: {e}")
                    
                    try:
                        # Process in the temporary directory
                        logger.info(f"Running workflow with temp directory: {temp_workflow_dir}")
                        result = process_slides_with_langgraph(
                            router_flags=True,
                            docx_file=temp_path,
                            output_folder=temp_workflow_dir
                        )
                        
                        # Check if the result is a message or path
                        if isinstance(result, str):
                            if "được lưu tại:" in result or "hoàn thành" in result.lower():
                                # Try to extract path from message
                                import re
                                path_match = re.search(r'(?:được lưu tại:|saved at:)\s*(.+)', result)
                                if path_match:
                                    zip_path = path_match.group(1).strip()
                                    if os.path.exists(zip_path):
                                        logger.info(f"Found zip file from message: {zip_path}")
                                        result_zip = zip_path
                                    else:
                                        # Look for zip files in the temp dir
                                        zip_files = [f for f in os.listdir(temp_workflow_dir) 
                                                    if f.endswith('.zip')]
                                        if zip_files:
                                            result_zip = os.path.join(temp_workflow_dir, zip_files[0])
                                            logger.info(f"Using found zip file: {result_zip}")
                                        else:
                                            logger.error("No zip files found in temp directory")
                                            return None
                                else:
                                    # Still search for zip files
                                    zip_files = [f for f in os.listdir(temp_workflow_dir) 
                                                if f.endswith('.zip')]
                                    if zip_files:
                                        result_zip = os.path.join(temp_workflow_dir, zip_files[0])
                                        logger.info(f"Using found zip file: {result_zip}")
                                    else:
                                        logger.error("No path in message and no zip files found")
                                        return None
                            else:
                                # Just use the string as a path if it points to a zip file
                                if os.path.exists(result) and result.endswith('.zip'):
                                    result_zip = result
                                else:
                                    # Last resort: search for any zip files
                                    zip_files = [f for f in os.listdir(temp_workflow_dir) 
                                                if f.endswith('.zip')]
                                    if zip_files:
                                        result_zip = os.path.join(temp_workflow_dir, zip_files[0])
                                    else:
                                        logger.error(f"Unknown result format: {result}")
                                        return None
                        else:
                            # If result is not a string (None or other), search for zip files
                            zip_files = [f for f in os.listdir(temp_workflow_dir) 
                                        if f.endswith('.zip')]
                            if zip_files:
                                result_zip = os.path.join(temp_workflow_dir, zip_files[0])
                            else:
                                # Check html and png dirs for content
                                if os.path.exists(html_dir) and len(os.listdir(html_dir)) > 0:
                                    # Create zip file from html and png contents
                                    result_zip = os.path.join(temp_workflow_dir, "slides.zip")
                                    with zipfile.ZipFile(result_zip, 'w') as zipf:
                                        # Add HTML files
                                        for file in os.listdir(html_dir):
                                            zipf.write(os.path.join(html_dir, file), 
                                                     os.path.join("html", file))
                                        # Add PNG files if they exist
                                        if os.path.exists(png_dir):
                                            for file in os.listdir(png_dir):
                                                zipf.write(os.path.join(png_dir, file),
                                                         os.path.join("png", file))
                                else:
                                    logger.error("Workflow did not produce any output")
                                    return None
                        
                        # Copy to a permanent location
                        final_zip = os.path.join(TEMP_DIR, f"slides_result_{uuid.uuid4().hex[:8]}.zip")
                        try:
                            shutil.copy2(result_zip, final_zip)
                            logger.info(f"Copied result to: {final_zip}")
                            return final_zip
                        except Exception as copy_error:
                            logger.error(f"Error copying result: {copy_error}")
                            return result_zip
                            
                    except Exception as e:
                        logger.error(f"Error in workflow processing: {e}")
                        return None
                        
                except Exception as e:
                    logger.error(f"Workflow setup error: {e}")
                    return None
            
            # Chạy trong thread pool
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result_zip = await loop.run_in_executor(executor, run_workflow)
            
            if result_zip and os_module.path.exists(result_zip):
                logger.info(f"✅ Successfully processed DOCX via direct workflow: {file.filename}")
                
                # Copy ZIP content to output folder
                final_zip_path = os_module.path.join(output_folder, f"{project_name}_slides.zip")
                try:
                    # First copy the zip file
                    shutil.copy2(result_zip, final_zip_path)
                    
                    # Then extract contents carefully to avoid permission errors
                    try:
                        with zipfile.ZipFile(final_zip_path, 'r') as zip_ref:
                            # Create html directory first to ensure it exists
                            html_dir = os_module.path.join(output_folder, "html")
                            os_module.makedirs(html_dir, exist_ok=True)
                            
                            # Extract files individually to handle permission issues
                            for file_info in zip_ref.infolist():
                                try:
                                    # Skip directories that might cause permission issues
                                    if file_info.filename.endswith('/') or 'temp_debug' in file_info.filename:
                                        continue
                                        
                                    # Extract to output folder
                                    zip_ref.extract(file_info, output_folder)
                                except PermissionError as pe:
                                    logger.warning(f"Permission error extracting {file_info.filename}: {pe}")
                                except Exception as e:
                                    logger.warning(f"Error extracting {file_info.filename}: {e}")
                            
                            logger.info(f"Successfully extracted ZIP contents to {output_folder}")
                    except Exception as e:
                        logger.error(f"Error extracting ZIP: {e}")
                except Exception as e:
                    logger.error(f"Error copying ZIP file: {e}")
            else:
                raise Exception("Workflow did not produce valid output")
                
        except ImportError as ie:
            logger.error(f"Cannot import workflow: {ie}")
            raise Exception("Workflow module not available")
            
    except Exception as e:
        logger.error(f"🚨 Error in direct workflow processing: {e}")
        # Fallback: sử dụng HTML mẫu như trước
        logger.warning("⚠️  FALLBACK: Direct workflow failed, using sample HTML slides...")
        
        # Tạo thư mục html trong output_folder (fallback)
        html_folder = os_module.path.join(output_folder, "html")
        os_module.makedirs(html_folder, exist_ok=True)
        
        # Copy các HTML mẫu vào thư mục html của project
        sample_html_dir = os_module.path.join(STATIC_DIR, "sample_html")
        if os_module.path.exists(sample_html_dir):
            html_files = sorted([f for f in os_module.listdir(sample_html_dir) if f.endswith('.html')])
            for html_file in html_files:
                src_path = os_module.path.join(sample_html_dir, html_file)
                dst_path = os_module.path.join(html_folder, html_file)
                shutil.copy2(src_path, dst_path)
                logger.info(f"📋 Copied sample slide: {html_file}")
            logger.warning(f"⚠️  Using {len(html_files)} sample slides instead of AI-generated content")
        else:
            logger.warning("📂 Sample HTML directory not found, creating default slides")
            # Tạo slide mặc định nếu không có mẫu
            default_slide = """<!DOCTYPE html>
<html lang="vi">
<head><meta charset="UTF-8"><title>Default Slide</title></head>
<body style="padding:40px; font-family:Arial; background:linear-gradient(45deg,#667eea,#764ba2); color:white;">
<h1 style="text-align:center;">Slide mặc định</h1>
<p style="text-align:center; font-size:18px;">Nội dung được tạo từ tài liệu: {}</p>
</body></html>""".format(file.filename)
            
            with open(os_module.path.join(html_folder, "slide1.html"), "w", encoding="utf-8") as f:
                f.write(default_slide)
    
    finally:
        # Cleanup temp file
        if os_module.path.exists(temp_path):
            os_module.remove(temp_path)

    # Xác định html_folder để convert - cho cả trường hợp thành công và fallback
    html_folder = os_module.path.join(output_folder, "html")

    # Bước convert HTML slides to absolute positioning - GIỮ NGUYÊN
    converted_folder = os_module.path.join(output_folder, "converted")
    
    if html_converter is not None and os_module.path.exists(html_folder):
        logger.info("Converting sample HTML slides to absolute positioning...")
        try:
            # Make sure converted folder exists with proper permissions
            os_module.makedirs(converted_folder, exist_ok=True)
            conversion_result = html_converter.convert_slides_batch(html_folder, converted_folder)
            logger.info(f"Conversion completed: {len(conversion_result['success'])} success, {len(conversion_result['failed'])} failed")
        except PermissionError as pe:
            logger.error(f"Permission error creating converted folder: {pe}")
            logger.warning("Using original HTML slides due to conversion permission error")
            conversion_result = {"success": [], "failed": []}
        except Exception as e:
            logger.error(f"Error during conversion: {e}")
            logger.warning("Using original HTML slides due to conversion error")
            conversion_result = {"success": [], "failed": []}
    else:
        if not os_module.path.exists(html_folder):
            logger.warning('No HTML folder present to convert')
        else:
            logger.info('HTML converter not available - skipping conversion and using original HTML')
    
    # Build slides từ output folder - GIỮ NGUYÊN
    slides = build_slides_from_output(output_folder)

    # Trả về dữ liệu slide để front-end lưu và redirect sang trang edit - GIỮ NGUYÊN
    return JSONResponse(content={"slides": slides, "project_name": project_name})


@app.post("/api/upload-zip")
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file ZIP")

    temp_path = os.path.join(TEMP_DIR, file.filename)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    project_name = os.path.splitext(file.filename)[0]
    output_folder = os.path.join(OUTPUT_DIR, project_name)
    
    if os.path.exists(output_folder):
        try:
            shutil.rmtree(output_folder)
        except PermissionError as pe:
            logger.warning(f"Permission error removing existing folder: {pe}")
            # Try to create a folder with timestamp appended instead
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            project_name = f"{project_name}_{timestamp}"
            logger.info(f"Using alternative project name: {project_name}")
            output_folder = os.path.join(OUTPUT_DIR, project_name)
        except Exception as e:
            logger.error(f"Error removing existing project folder: {e}")
            # Continue with existing folder but clean it instead
            for item in os.listdir(output_folder):
                item_path = os.path.join(output_folder, item)
                try:
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        # Skip the problematic 'converted' folder
                        if item != "converted":
                            shutil.rmtree(item_path, ignore_errors=True)
                except Exception as e:
                    logger.warning(f"Could not remove {item_path}: {e}")
    
    # Make sure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    with zipfile.ZipFile(temp_path, 'r') as zip_ref:
        zip_ref.extractall(output_folder)

    slides = build_slides_from_output(output_folder)

    os.remove(temp_path)

    return JSONResponse(content={"slides": slides})


@app.get("/api/images/{image_name}")
async def get_image(image_name: str):
    image_path = os.path.join(IMAGE_DIR, image_name)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Không tìm thấy hình ảnh")
    return FileResponse(image_path)


@app.post("/api/convert-slides")
async def convert_slides(data: dict):
    """
    API để convert HTML slides sang absolute positioning
    Body: {"project_name": "tên_project"}
    """
    try:
        project_name = data.get("project_name")
        if not project_name:
            raise HTTPException(status_code=400, detail="Missing project_name")
        
        output_folder = os.path.join(OUTPUT_DIR, project_name)
        if not os.path.exists(output_folder):
            raise HTTPException(status_code=404, detail="Project not found")
        
        html_folder = os.path.join(output_folder, "html")
        converted_folder = os.path.join(output_folder, "converted")
        
        if not os.path.exists(html_folder):
            raise HTTPException(status_code=404, detail="HTML folder not found")
        
        # Thực hiện conversion
        if html_converter is None:
            raise HTTPException(status_code=503, detail="Converter is not available in this deployment")

        logger.info(f"Converting slides for project: {project_name}")
        try:
            # Make sure converted folder exists with proper permissions
            os.makedirs(converted_folder, exist_ok=True)
            conversion_result = html_converter.convert_slides_batch(html_folder, converted_folder)
            
            return JSONResponse(content={
                "success": True,
                "conversion_result": conversion_result,
                "message": f"Converted {len(conversion_result['success'])} slides successfully"
            })
        except PermissionError as pe:
            logger.error(f"Permission error creating converted folder: {pe}")
            raise HTTPException(status_code=500, detail=f"Permission error: {str(pe)}")
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversion API error: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@app.get("/api/conversion-status/{project_name}")
async def get_conversion_status(project_name: str):
    """
    Kiểm tra trạng thái conversion của một project
    """
    try:
        output_folder = os.path.join(OUTPUT_DIR, project_name)
        if not os.path.exists(output_folder):
            raise HTTPException(status_code=404, detail="Project not found")
        
        html_folder = os.path.join(output_folder, "html")
        converted_folder = os.path.join(output_folder, "converted")
        
        if not os.path.exists(html_folder):
            raise HTTPException(status_code=404, detail="HTML folder not found")
        
        if html_converter is None:
            raise HTTPException(status_code=503, detail="Converter is not available in this deployment")

        status = html_converter.get_conversion_status(html_folder, converted_folder)
        
        return JSONResponse(content={
            "project_name": project_name,
            "status": status,
            "has_converted": os.path.exists(converted_folder)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check API error: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@app.get("/api/converter-health")
async def check_converter_health():
    """
    Kiểm tra sức khỏe của converter system
    """
    try:
        if html_converter is None:
            return JSONResponse(content={
                "healthy": False,
                "message": "Converter is disabled or not initialized in this deployment"
            })

        health_status = {
            "dependencies_ok": html_converter.check_dependencies(),
            "converter_js_exists": os.path.exists(html_converter.converter_js),
            "node_modules_exists": os.path.exists(html_converter.node_modules)
        }
        
        all_ok = all(health_status.values())
        
        return JSONResponse(content={
            "healthy": all_ok,
            "details": health_status,
            "message": "Converter system is ready" if all_ok else "Converter system has issues"
        })
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(content={
            "healthy": False,
            "error": str(e),
            "message": "Health check failed"
        })


# ========================== SLIDE CAPTURE API ==========================

@app.post("/api/capture-slide")
async def capture_slide(request: CaptureSlideRequest):
    """Capture single slide from HTML content"""
    try:
        if slide_capture is None:
            raise HTTPException(status_code=503, detail="Slide capture system not available")
        
        html_content = request.html_content
        slide_name = request.slide_name
        
        if not html_content:
            raise HTTPException(status_code=400, detail="No HTML content provided")
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{slide_name}_{timestamp}_{uuid.uuid4().hex[:8]}.png"
        output_path = os.path.join(CAPTURES_DIR, filename)
        
        # Generate slide image
        logger.info(f"📸 Capturing slide: {slide_name}")
        await slide_capture.generate_slide_from_html(html_content, output_path)
        
        # Return URLs relative to static directory
        relative_path = os.path.relpath(output_path, STATIC_DIR)
        
        return JSONResponse(content={
            'success': True,
            'image_url': f'/static/{relative_path.replace(os.sep, "/")}',
            'download_url': f'/api/download-capture/{filename}',
            'message': f'Slide "{slide_name}" captured successfully',
            'filename': filename
        })
    
    except Exception as e:
        logger.error(f"Error capturing slide: {e}")
        return JSONResponse(
            content={'success': False, 'error': str(e)},
            status_code=500
        )


@app.post("/api/capture-slides-batch")
async def capture_slides_batch(request: CaptureMultipleSlidesRequest):
    """Capture multiple slides and return as ZIP"""
    try:
        if slide_capture is None:
            raise HTTPException(status_code=503, detail="Slide capture system not available")
        
        slides_data = request.slides
        
        if not slides_data:
            raise HTTPException(status_code=400, detail="No slides data provided")
        
        # Create ZIP file in memory
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            successful_slides = []
            
            for i, slide_data in enumerate(slides_data):
                html_content = slide_data.get('html_content')
                slide_name = slide_data.get('slide_name', f'slide_{i+1}')
                
                if html_content:
                    # Create temporary file
                    temp_filename = f"temp_{uuid.uuid4().hex[:8]}.png"
                    temp_path = os.path.join(CAPTURES_DIR, temp_filename)
                    
                    try:
                        logger.info(f"📸 Capturing slide {i+1}/{len(slides_data)}: {slide_name}")
                        await slide_capture.generate_slide_from_html(html_content, temp_path)
                        
                        # Add to ZIP
                        zip_filename = f"{slide_name.replace(' ', '_')}.png"
                        zip_file.write(temp_path, zip_filename)
                        successful_slides.append(slide_name)
                        
                        # Clean up temp file
                        os.remove(temp_path)
                        
                    except Exception as e:
                        logger.error(f"Error capturing slide {i+1}: {e}")
                        continue
        
        if not successful_slides:
            raise HTTPException(status_code=500, detail="No slides could be captured")
        
        zip_buffer.seek(0)
        
        # Save ZIP file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"slides_capture_{timestamp}.zip"
        zip_path = os.path.join(CAPTURES_DIR, zip_filename)
        
        with open(zip_path, 'wb') as f:
            f.write(zip_buffer.getvalue())
        
        logger.info(f"✅ Successfully captured {len(successful_slides)} slides to ZIP")
        
        return JSONResponse(content={
            'success': True,
            'download_url': f'/api/download-capture/{zip_filename}',
            'message': f'Captured {len(successful_slides)} slides successfully',
            'filename': zip_filename,
            'captured_slides': successful_slides
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch capture: {e}")
        return JSONResponse(
            content={'success': False, 'error': str(e)},
            status_code=500
        )


@app.get("/api/download-capture/{filename}")
async def download_capture(filename: str):
    """Download captured slide or ZIP file"""
    try:
        file_path = os.path.join(CAPTURES_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            file_path, 
            filename=filename,
            media_type='application/octet-stream'
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/capture-health")
async def check_capture_health():
    """Check capture system health"""
    try:
        if slide_capture is None:
            return JSONResponse(content={
                "healthy": False,
                "message": "Slide capture system not initialized"
            })
        
        # Check if captures directory exists and is writable
        captures_writable = os.access(CAPTURES_DIR, os.W_OK)
        
        # Try to import playwright to check if it's available
        try:
            from playwright.async_api import async_playwright
            playwright_available = True
        except ImportError:
            playwright_available = False
        
        health_status = {
            "captures_dir_exists": os.path.exists(CAPTURES_DIR),
            "captures_dir_writable": captures_writable,
            "playwright_available": playwright_available,
            "captures_dir_path": CAPTURES_DIR
        }
        
        all_ok = all([
            health_status["captures_dir_exists"],
            health_status["captures_dir_writable"],
            health_status["playwright_available"]
        ])
        
        return JSONResponse(content={
            "healthy": all_ok,
            "details": health_status,
            "message": "Capture system is ready" if all_ok else "Capture system has issues"
        })
        
    except Exception as e:
        logger.error(f"Capture health check error: {e}")
        return JSONResponse(content={
            "healthy": False,
            "error": str(e),
            "message": "Capture health check failed"
        })


# ========================== PDF EXPORT API ==========================

@app.post("/api/export-slide-pdf")
async def export_slide_pdf(request: CaptureSlideRequest):
    """Export single slide directly to PDF"""
    try:
        if slide_capture is None:
            raise HTTPException(status_code=503, detail="Slide capture system not available")
        
        html_content = request.html_content
        slide_name = request.slide_name
        
        if not html_content:
            raise HTTPException(status_code=400, detail="No HTML content provided")
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{slide_name}_{timestamp}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(CAPTURES_DIR, filename)
        
        # Generate slide PDF
        logger.info(f"📄 Exporting slide to PDF: {slide_name}")
        await slide_capture.capture_and_export_pdf(html_content, output_path)
        
        return JSONResponse(content={
            'success': True,
            'download_url': f'/api/download-capture/{filename}',
            'message': f'Slide "{slide_name}" exported to PDF successfully',
            'filename': filename
        })
    
    except Exception as e:
        logger.error(f"Error exporting slide to PDF: {e}")
        return JSONResponse(
            content={'success': False, 'error': str(e)},
            status_code=500
        )


@app.post("/api/export-slides-pdf")
async def export_slides_pdf(request: CaptureMultipleSlidesRequest):
    """Export multiple slides to a single PDF"""
    try:
        if slide_capture is None:
            raise HTTPException(status_code=503, detail="Slide capture system not available")
        
        slides_data = request.slides
        
        if not slides_data:
            raise HTTPException(status_code=400, detail="No slides data provided")
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"slides_export_{timestamp}.pdf"
        output_path = os.path.join(CAPTURES_DIR, filename)
        
        # Export slides to PDF
        logger.info(f"📄 Exporting {len(slides_data)} slides to PDF")
        await slide_capture.capture_slides_and_export_pdf(slides_data, output_path)
        
        logger.info(f"✅ Successfully exported {len(slides_data)} slides to PDF")
        
        return JSONResponse(content={
            'success': True,
            'download_url': f'/api/download-capture/{filename}',
            'message': f'Exported {len(slides_data)} slides to PDF successfully',
            'filename': filename
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting slides to PDF: {e}")
        return JSONResponse(
            content={'success': False, 'error': str(e)},
            status_code=500
        )


# ========================== END CAPTURE API ==========================


if __name__ == "__main__":
    print("🌐 Starting SlideGen Web Frontend...")
    print("🚀 Frontend URL: http://127.0.0.1:3000")
    print("📡 Backend API: http://127.0.0.1:8000")
    print("📸 Capture API: http://127.0.0.1:3000/api/capture-*")
    print("🔍 Capture Health: http://127.0.0.1:3000/api/capture-health")
    print("🧪 Run tests: python test_backend.py")
    
    uvicorn.run("main_web:app", host="0.0.0.0", port=3000)
