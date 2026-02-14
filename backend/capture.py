import asyncio
from playwright.async_api import async_playwright
import os
import img2pdf
from PIL import Image
import uuid


class SlideCapture:
    def __init__(self):
        self.viewport = {"width": 1920, "height": 1080}

    async def generate_slide_from_html(self, html_content, output_path="screenshot.png"):
        """Generate slide from HTML content"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport=self.viewport)
            await page.set_content(html_content)
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

            await page.screenshot(path=output_path, full_page=False, clip={
                "x": 0,
                "y": 0,
                "width": self.viewport["width"],
                "height": self.viewport["height"]
            })
            await browser.close()
            return output_path

    async def capture_and_export_pdf(self, html_content, output_pdf_path):
        """Capture slide from HTML and directly export as PDF"""
        # Create temporary PNG file
        temp_png = f"temp_{uuid.uuid4().hex[:8]}.png"
        temp_dir = os.path.dirname(output_pdf_path) if os.path.dirname(output_pdf_path) else "."
        temp_png_path = os.path.join(temp_dir, temp_png)

        try:
            # Capture screenshot
            await self.generate_slide_from_html(html_content, temp_png_path)

            # Convert PNG to PDF
            self.convert_image_to_pdf(temp_png_path, output_pdf_path)

            return output_pdf_path
        finally:
            # Clean up temporary file
            if os.path.exists(temp_png_path):
                os.remove(temp_png_path)

    def convert_image_to_pdf(self, image_path, pdf_path):
        """Convert single image to PDF"""
        try:
            # Open and process image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (for JPEG compatibility)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Create PDF from image
                pdf_bytes = img2pdf.convert(image_path)

                # Write PDF file
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_bytes)

            return pdf_path
        except Exception as e:
            raise Exception(f"Error converting image to PDF: {str(e)}")

    def convert_images_to_pdf(self, image_paths, pdf_path):
        """Convert multiple images to a single PDF"""
        try:
            # Validate all image files exist
            valid_images = []
            for img_path in image_paths:
                if os.path.exists(img_path):
                    valid_images.append(img_path)
            if not valid_images:
                raise Exception("No valid image files found")
            # Create PDF from multiple images
            pdf_bytes = img2pdf.convert(valid_images)
            # Write PDF file
            with open(pdf_path, 'wb') as f:
                f.write(pdf_bytes)

            return pdf_path
        except Exception as e:
            raise Exception(f"Error converting images to PDF: {str(e)}")

    async def capture_slides_and_export_pdf(self, slides_data, output_pdf_path):
        """Capture multiple slides and export as single PDF"""
        temp_images = []
        temp_dir = os.path.dirname(output_pdf_path) if os.path.dirname(output_pdf_path) else "."

        try:
            # Capture all slides as images
            for i, slide_data in enumerate(slides_data):
                html_content = slide_data.get('html_content')

                if html_content:
                    # Create temporary image file
                    temp_img = f"temp_slide_{i+1}_{uuid.uuid4().hex[:8]}.png"
                    temp_img_path = os.path.join(temp_dir, temp_img)

                    # Capture slide
                    await self.generate_slide_from_html(html_content, temp_img_path)
                    temp_images.append(temp_img_path)

            if not temp_images:
                raise Exception("No slides could be captured")

            # Convert all images to PDF
            self.convert_images_to_pdf(temp_images, output_pdf_path)

            return output_pdf_path
        finally:
            # Clean up temporary files
            for temp_img in temp_images:
                if os.path.exists(temp_img):
                    os.remove(temp_img)


# Sample HTML for testing
stringHtml = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KẾ HOẠCH KINH DOANH <br> <b>INNOTECH SOLUTIONS</b> <br> <span style='font-size: 0.6em; font-weight: normal;'><i>Giải pháp Công nghệ Đột phá cho Tương lai 2024-2028</i></span></title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,500&family=Montserrat:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root { font-size: 16px; }
        body, html {
            margin: 0; padding: 0; height: 100%; width: 100%;
            font-family: 'Montserrat', sans-serif;
            overflow: hidden;
            background-color: #FCFCFC;
        }

        .slide-container {
            width: 100%; height: 100vh;
            display: flex; align-items: center; justify-content: center;
            padding: 4vw; box-sizing: border-box;
        }

        .content-wrapper {
            display: flex; align-items: center; justify-content: center;
            width: 100%; max-width: 75rem; /* 1200px */
        }

        /* Image Section with Decorative Frame */
        .image-section {
            flex: 1;
            position: relative;
            height: 28rem; /* 448px */
        }
        .accent-bg {
            position: absolute;
            top: 0;
            left: 0;
            width: 90%;
            height: 90%;
            background-color: #EAD6D6;
            z-index: 1;
        }
        .main-image {
            position: absolute;
            bottom: 0;
            right: 0;
            width: 90%;
            height: 90%;
            object-fit: cover;
            z-index: 2;
            box-shadow: 0 1rem 2rem rgba(0,0,0,0.1);
        }

        /* Text Section */
        .text-section {
            flex: 1;
            padding-left: 5rem;
        }

        .main-title {
            font-family: 'Playfair Display', serif;
            font-size: 3.5rem;
            font-weight: 500;
            font-style: italic;
            color: #1F2937;
            margin: 0 0 1.5rem 0;
            line-height: 1.2;
        }

        .subtitle {
            font-size: 0.875rem;
            font-weight: 600;
            color: #B48E8E;
            text-transform: uppercase;
            letter-spacing: 0.2em;
            margin-bottom: 2rem;
        }

        .agenda-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .agenda-item {
            font-size: 1.1rem;
            color: #4B5563;
            margin-bottom: 1rem;
        }

        /* Responsive Design */
        @media (max-width: 56.25em) { /* 900px */
            .text-section { padding-left: 3rem; }
            .main-title { font-size: 3rem; }
            .agenda-item { font-size: 1rem; }
        }
        @media (max-width: 48em) { /* 768px */
            .content-wrapper { flex-direction: column; }
            .image-section { width: 80%; height: 20rem; margin-bottom: 3rem; }
            .text-section { width: 80%; padding-left: 0; text-align: center; }
        }
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="content-wrapper">
            <div class="image-section">
                <div class="accent-bg"></div>
                <img src="https://images.unsplash.com/photo-1484417894907-623942c8ee29?q=80&w=2832&auto=format&fit=crop" alt="Workspace" class="main-image">
            </div>
            <div class="text-section">
                <h1 class="main-title">KẾ HOẠCH KINH DOANH <br> <b>INNOTECH SOLUTIONS</b> <br> <span style='font-size: 0.6em; font-weight: normal;'><i>Giải pháp Công nghệ Đột phá cho Tương lai 2024-2028</i></span></h1>
                <h3 class="subtitle">MỤC LỤC</h3>
                <ul class="agenda-list">
                    <li class='agenda-item'>Tóm tắt dự án</li>
                    <li class='agenda-item'>Tổng quan về Innovatech Solutions</li>
                    <li class='agenda-item'>Tầm nhìn và Sứ mệnh</li>
                    <li class='agenda-item'>Phân tích Thị trường và Đối thủ cạnh tranh</li>
                    <li class='agenda-item'>Mục tiêu Chiến lược</li>
                    <li class='agenda-item'>Lộ trình Phát triển Sản phẩm/Dịch vụ</li>
                    <li class='agenda-item'>Dự phóng Tài chính</li>
                    <li class='agenda-item'>Lời cảm ơn</li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
"""


async def take_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.set_content(stringHtml)
        # Chụp với kích thước cố định thay vì full_page để tránh phần trắng
        await page.screenshot(path="screenshot.png", full_page=False, clip={
            "x": 0,
            "y": 0,
            "width": 1920,
            "height": 1080
        })
        await browser.close()

# If in a Jupyter notebook or async context, run this instead of asyncio.run():
if __name__ == "__main__":
    # Test with sample HTML
    capture = SlideCapture()
    asyncio.run(capture.generate_slide_from_html(stringHtml, "screenshot.png"))
    print("Screenshot taken and saved as 'screenshot.png'.")
