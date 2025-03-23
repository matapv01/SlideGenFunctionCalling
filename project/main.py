import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import zipfile
from slide_generator import process_slides

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

PROJECT_DIR = "/home/naver/Documents/Minh/SligenFunctionCalling/project"
STATIC_DIR = os.path.join(PROJECT_DIR, "static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
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
        raise HTTPException(status_code=500, detail="File index.html not found")

@app.post("/upload-docx/")
async def upload_docx(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file: {file.filename}")
        temp_file = f"temp_{file.filename}"
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Saved temp file: {temp_file}")

        output_folder = f"output_{file.filename.split('.')[0]}"
        os.makedirs(output_folder, exist_ok=True)
        logger.info(f"Created output folder: {output_folder}")

        logger.info("Starting slide processing...")
        html_files, png_files = process_slides(temp_file, output_folder)
        logger.info(f"Generated {len(html_files)} HTML files and {len(png_files)} PNG files")

        zip_path = f"{output_folder}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for html_file in html_files:
                zipf.write(html_file, os.path.basename(html_file))
            for png_file in png_files:
                zipf.write(png_file, os.path.basename(png_file))
        logger.info(f"Created ZIP file: {zip_path}")

        logger.info("Sending ZIP file to client")
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename="slides.zip"
        )
    except Exception as e:
        logger.error(f"Error processing DOCX: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing DOCX: {str(e)}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            logger.info(f"Cleaned up temp file: {temp_file}")
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
            logger.info(f"Cleaned up output folder: {output_folder}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)