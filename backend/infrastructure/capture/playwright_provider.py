# File: backend/infrastructure/capture/playwright_capture.py

import os
from playwright.async_api import async_playwright
from backend.domain.ports.capture_provider import CaptureProvider
from backend.config import BROWSER_VIEWPORT_WIDTH, BROWSER_VIEWPORT_HEIGHT
import img2pdf
from PIL import Image
import uuid

class PlaywrightCaptureProvider(CaptureProvider):
    def __init__(self):
        self.viewport = {"width": BROWSER_VIEWPORT_WIDTH, "height": BROWSER_VIEWPORT_HEIGHT}

    async def generate_slide_from_html(self, html_content: str, output_path: str) -> str:
        """Chụp ảnh từ HTML content"""
        async with async_playwright() as p:
            # Tắt tăng tốc phần cứng GPU để tránh Chromium tranh chấp VRAM với PyTorch
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-gpu", "--disable-software-rasterizer"]
            )
            page = await browser.new_page(viewport=self.viewport)
            
            await page.set_content(html_content, wait_until="load")
            await page.evaluate(
                """
                async () => {
                    if (document.fonts?.ready) await document.fonts.ready;
                    await Promise.all(Array.from(document.images).map((image) => {
                        if (image.complete) return Promise.resolve();
                        return new Promise((resolve) => {
                            let finished = false;
                            const finish = () => {
                                if (finished) return;
                                finished = true;
                                resolve();
                            };
                            image.addEventListener("load", finish, { once: true });
                            image.addEventListener("error", finish, { once: true });
                            window.setTimeout(finish, 3000);
                        });
                    }));
                }
                """
            )
            
            # Đảm bảo thư mục tồn tại
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            await page.screenshot(path=output_path, full_page=False, clip={
                "x": 0, "y": 0,
                "width": self.viewport["width"], "height": self.viewport["height"]
            })
            
            await browser.close()
            return output_path

    async def capture_and_export_pdf(self, html_content: str, output_pdf_path: str) -> str:
        """Chụp ảnh và convert sang PDF (Single Slide)"""
        # Tạo file ảnh tạm
        temp_dir = os.path.dirname(output_pdf_path) or "."
        temp_png = os.path.join(temp_dir, f"temp_{uuid.uuid4().hex[:8]}.png")

        try:
            await self.generate_slide_from_html(html_content, temp_png)
            self._convert_image_to_pdf(temp_png, output_pdf_path)
            return output_pdf_path
        finally:
            if os.path.exists(temp_png):
                os.remove(temp_png)


    async def capture_slides_and_export_pdf(self, slides_data: list, output_pdf_path: str) -> str:
        """Chụp nhiều slide và ghép thành 1 file PDF"""
        temp_images = []
        temp_dir = os.path.dirname(output_pdf_path) or "."
        os.makedirs(temp_dir, exist_ok=True)

        try:
            for i, slide in enumerate(slides_data):
                html = slide.get('html_content')
                if not html: continue

                temp_img = os.path.join(temp_dir, f"temp_slide_{i}_{uuid.uuid4().hex[:8]}.png")
                await self.generate_slide_from_html(html, temp_img)
                temp_images.append(temp_img)

            if not temp_images:
                raise Exception("No slides captured for PDF export")

            self._convert_images_to_pdf(temp_images, output_pdf_path)
            return output_pdf_path
        finally:
            # Dọn dẹp ảnh tạm
            for img in temp_images:
                if os.path.exists(img):
                    try: os.remove(img)
                    except: pass


    # --- Helper Functions (Private) ---
    def _convert_image_to_pdf(self, image_path: str, pdf_path: str):
            with Image.open(image_path) as img:
                if img.mode != 'RGB': img = img.convert('RGB')
                pdf_bytes = img2pdf.convert(image_path)
                with open(pdf_path, 'wb') as f: f.write(pdf_bytes)


    def _convert_images_to_pdf(self, image_paths: list, pdf_path: str):
        valid_imgs = [p for p in image_paths if os.path.exists(p)]
        if not valid_imgs: raise Exception("No valid images found")
        pdf_bytes = img2pdf.convert(valid_imgs)
        with open(pdf_path, 'wb') as f: f.write(pdf_bytes)
