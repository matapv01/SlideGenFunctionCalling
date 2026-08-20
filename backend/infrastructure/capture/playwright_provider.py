# File: backend/infrastructure/capture/playwright_capture.py

import os
from playwright.async_api import async_playwright
from backend.domain.ports.capture_provider import CaptureProvider
from backend.config import (
    BROWSER_PREVIEW_URL,
    BROWSER_DEVICE_SCALE_FACTOR,
    BROWSER_VIEWPORT_HEIGHT,
    BROWSER_VIEWPORT_WIDTH,
)
import img2pdf
from PIL import Image
import uuid

class PlaywrightCaptureProvider(CaptureProvider):
    def __init__(self):
        self.viewport = {"width": BROWSER_VIEWPORT_WIDTH, "height": BROWSER_VIEWPORT_HEIGHT}
        self.device_scale_factor = BROWSER_DEVICE_SCALE_FACTOR
        self.preview_url = BROWSER_PREVIEW_URL

    async def _wait_for_page_assets(self, page) -> None:
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
                        window.setTimeout(finish, 5000);
                    });
                }));
            }
            """
        )

    async def _prepare_xml_preview_page(
        self,
        page,
        xml_content: str,
        slide_index: int,
        *,
        wait_images: bool = True,
    ) -> None:
        """Load the same frontend preview used for the final PNG capture."""
        response = await page.goto(self.preview_url, wait_until="domcontentloaded")
        if response is not None and not response.ok:
            raise RuntimeError(
                f"XML preview page returned HTTP {response.status}: {self.preview_url}"
            )

        await page.wait_for_function(
            "window.__slidegenXmlPreviewAppReady === true",
            timeout=30000,
        )
        await page.evaluate(
            """
            (payload) => {
                window.dispatchEvent(
                    new CustomEvent("slidegen:xml-preview", { detail: payload })
                );
            }
            """,
            {"xml": xml_content, "slideIndex": slide_index},
        )
        await page.locator('[data-xml-preview-status="ready"]').wait_for(
            state="attached",
            timeout=30000,
        )
        if wait_images:
            await self._wait_for_page_assets(page)
        else:
            await page.evaluate(
                """
                async () => {
                    if (document.fonts?.ready) await document.fonts.ready;
                }
                """
            )
        await page.wait_for_timeout(100 if wait_images else 50)

    async def generate_slide_from_html(self, html_content: str, output_path: str) -> str:
        """Chụp ảnh từ HTML content"""
        async with async_playwright() as p:
            # Tắt tăng tốc phần cứng GPU để tránh Chromium tranh chấp VRAM với PyTorch
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-gpu", "--disable-software-rasterizer"]
            )
            page = await browser.new_page(
                viewport=self.viewport,
                device_scale_factor=self.device_scale_factor,
            )
            
            await page.set_content(html_content, wait_until="load")
            await self._wait_for_page_assets(page)
            
            # Đảm bảo thư mục tồn tại
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            await page.screenshot(path=output_path, full_page=False, clip={
                "x": 0, "y": 0,
                "width": self.viewport["width"], "height": self.viewport["height"]
            })
            
            await browser.close()
            return output_path

    async def generate_slide_from_xml_web(
        self,
        xml_content: str,
        output_path: str,
        slide_index: int = 0,
    ) -> str:
        """Render XML in the frontend preview route and capture that web page."""
        if not xml_content:
            raise ValueError("XML content is empty")
        if not self.preview_url:
            raise ValueError("BROWSER_PREVIEW_URL is not configured")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-gpu", "--disable-software-rasterizer"],
            )
            page = await browser.new_page(
                viewport=self.viewport,
                device_scale_factor=self.device_scale_factor,
            )
            try:
                await self._prepare_xml_preview_page(
                    page,
                    xml_content,
                    slide_index,
                    wait_images=False,
                )

                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                await page.screenshot(
                    path=output_path,
                    full_page=False,
                    clip={
                        "x": 0,
                        "y": 0,
                        "width": self.viewport["width"],
                        "height": self.viewport["height"],
                    },
                )
                return output_path
            finally:
                await browser.close()

    async def measure_xml_overflow(
        self,
        xml_content: str,
        slide_index: int = 0,
    ) -> dict:
        """Measure text against the rendered DOM used by XML PNG capture."""
        if not xml_content:
            raise ValueError("XML content is empty")
        if not self.preview_url:
            raise ValueError("BROWSER_PREVIEW_URL is not configured")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-gpu", "--disable-software-rasterizer"],
            )
            page = await browser.new_page(
                viewport=self.viewport,
                device_scale_factor=self.device_scale_factor,
            )
            try:
                await self._prepare_xml_preview_page(page, xml_content, slide_index)
                return await page.evaluate(
                    """
                    () => {
                        const canvas = document.querySelector('[data-xml-slide-canvas="true"]');
                        if (!canvas) throw new Error("XML slide canvas was not found");

                        const canvasRect = canvas.getBoundingClientRect();
                        const logicalWidth = canvas.offsetWidth || canvasRect.width || 1;
                        const logicalHeight = canvas.offsetHeight || canvasRect.height || 1;
                        const scaleX = canvasRect.width / logicalWidth || 1;
                        const scaleY = canvasRect.height / logicalHeight || 1;
                        const toLogicalX = (value) => value / scaleX;
                        const toLogicalY = (value) => value / scaleY;
                        const tolerance = 1.5;

                        const union = (rects) => {
                            if (!rects.length) return null;
                            return rects.reduce((result, rect) => ({
                                left: Math.min(result.left, rect.left),
                                top: Math.min(result.top, rect.top),
                                right: Math.max(result.right, rect.right),
                                bottom: Math.max(result.bottom, rect.bottom),
                            }), {
                                left: rects[0].left,
                                top: rects[0].top,
                                right: rects[0].right,
                                bottom: rects[0].bottom,
                            });
                        };

                        const uniqueLines = (rects) => {
                            const tops = [];
                            rects.forEach((rect) => {
                                if (!tops.some((top) => Math.abs(top - rect.top) <= 2)) {
                                    tops.push(rect.top);
                                }
                            });
                            return tops.length;
                        };

                        const boxes = Array.from(
                            document.querySelectorAll('[data-xml-textbox="true"]'),
                        )
                            .map((box) => {
                                const content = box.querySelector('[data-xml-text-content="true"]');
                                if (!content || !content.textContent?.trim()) return null;

                                const boxRect = box.getBoundingClientRect();
                                const textRects = [];
                                const walker = document.createTreeWalker(
                                    content,
                                    NodeFilter.SHOW_TEXT,
                                );
                                let textNode = walker.nextNode();
                                while (textNode) {
                                    if (textNode.textContent?.trim()) {
                                        const range = document.createRange();
                                        range.selectNodeContents(textNode);
                                        textRects.push(...Array.from(range.getClientRects()));
                                    }
                                    textNode = walker.nextNode();
                                }
                                const visibleTextRects = textRects
                                    .filter((rect) => rect.width > 0 && rect.height > 0);
                                const textRect = union(visibleTextRects);
                                const reasons = [];
                                const outsideCanvas =
                                    boxRect.left < canvasRect.left - tolerance ||
                                    boxRect.top < canvasRect.top - tolerance ||
                                    boxRect.right > canvasRect.right + tolerance ||
                                    boxRect.bottom > canvasRect.bottom + tolerance;

                                if (outsideCanvas) reasons.push("slide_boundary");
                                if (textRect && (
                                    textRect.left < boxRect.left - tolerance ||
                                    textRect.right > boxRect.right + tolerance
                                )) reasons.push("text_width");
                                if (textRect && (
                                    textRect.top < boxRect.top - tolerance ||
                                    textRect.bottom > boxRect.bottom + tolerance
                                )) reasons.push("text_height");

                                const maxLinesValue = box.getAttribute("data-xml-max-lines");
                                const maxLines = maxLinesValue ? Number(maxLinesValue) : null;
                                const lineCount = uniqueLines(visibleTextRects);
                                if (maxLines && lineCount > maxLines) reasons.push("max_lines");

                                return {
                                    id: box.getAttribute("data-xml-element-id") || "unknown-textbox",
                                    x: toLogicalX(boxRect.left - canvasRect.left),
                                    y: toLogicalY(boxRect.top - canvasRect.top),
                                    width: toLogicalX(boxRect.width),
                                    height: toLogicalY(boxRect.height),
                                    text_width: textRect
                                        ? toLogicalX(textRect.right - textRect.left)
                                        : 0,
                                    text_height: textRect
                                        ? toLogicalY(textRect.bottom - textRect.top)
                                        : 0,
                                    line_count: lineCount,
                                    max_lines: maxLines,
                                    reasons: [...new Set(reasons)],
                                    overflow: reasons.length > 0,
                                    has_math_field: Boolean(box.querySelector("math-field, math-span")),
                                    measurement_source: "playwright",
                                };
                            })
                            .filter(Boolean);

                        return {
                            checked_boxes: boxes.length,
                            overflowing_boxes: boxes.filter((box) => box.overflow).length,
                            boxes,
                            measurement_source: "playwright",
                        };
                    }
                    """,
                )
            finally:
                await browser.close()

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
