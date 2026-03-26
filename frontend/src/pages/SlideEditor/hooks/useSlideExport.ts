import { useState } from "react";
import { api } from "@/lib/api";
import { useLanguage } from "@/contexts/LanguageContext";
import type { Slide } from "../types";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";

// ─── Helpers (mirror of webfix SlideCapture + cleanSlideContentForExport) ────

/**
 * Xóa các UI element của editor khỏi HTML content của slide.
 * Giống cleanSlideContentForExport() trong webfix SlideEditor.js
 */
function cleanSlideContent(content: string): string {
  if (!content) return '';

  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = content;

  tempDiv.querySelectorAll('.resize-handle').forEach(el => el.remove());
  tempDiv.querySelectorAll('.drag-handle').forEach(el => el.remove());
  tempDiv.querySelectorAll('.connector-control-point').forEach(el => el.remove());
  tempDiv.querySelectorAll('.smart-guide').forEach(el => el.remove());
  tempDiv.querySelectorAll('.distance-indicator').forEach(el => el.remove());

  tempDiv.querySelectorAll('.element').forEach(el => {
    el.classList.remove('selected', 'dragging', 'editing', 'hover');
    el.removeAttribute('contenteditable');
    (el as HTMLElement).style.outline = 'none';
    (el as HTMLElement).style.cursor = 'default';
  });

  return tempDiv.innerHTML;
}

/**
 * Tạo full standalone HTML page cho một slide.
 * Giống createCompleteHTML() trong webfix SlideCapture.js
 */
function createCompleteHTML(slide: Slide, canvasContent: string): string {
  const backgroundColor = slide.backgroundColor || 'white';
  const cleanedContent = cleanSlideContent(canvasContent);

  return `<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Slide</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      margin: 0; padding: 0;
      width: 1920px; height: 1080px;
      overflow: hidden;
      font-family: 'Inter', Arial, sans-serif;
    }
    .slide-container {
      position: relative;
      width: 1920px;
      height: 1080px;
      background: ${backgroundColor};
      overflow: hidden;
    }
    .element { position: absolute; user-select: none; }
    .element img, .element video {
      width: 100%; height: 100%; object-fit: cover; border-radius: inherit;
    }
    .resize-handle, .drag-handle, .connector-control-point,
    .smart-guide, .distance-indicator { display: none !important; }
    .element.selected { outline: none !important; box-shadow: none !important; }
    .element[contenteditable="true"] { cursor: default !important; outline: none !important; }
    .element::after, .element::before { display: none !important; }
  </style>
</head>
<body>
  <div class="slide-container">
    ${cleanedContent}
  </div>
</body>
</html>`;
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export interface ExportResult {
  download_url: string;
  message: string;
}

export const useSlideExport = () => {
  const { t } = useLanguage();
  const [isExporting, setIsExporting] = useState(false);
  const [exportResult, setExportResult] = useState<ExportResult | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);

  /**
   * Xuất tất cả slides thành một file PDF duy nhất.
   * Gửi full standalone HTML cho từng slide lên POST /api/v1/export/slides-pdf
   * Giống exportAllSlidesToPdf() trong webfix, dùng createCompleteHTML() để render đúng.
   */
  const exportAllSlidesToPdf = async (
    slides: Slide[],
    currentSlideIndex: number,
    slideCanvasRef: React.RefObject<SlideCanvasHandle>,
    _projectName: string
  ) => {
    if (!slides.length) throw new Error('Không có slide để xuất');

    setIsExporting(true);
    setExportError(null);
    setExportResult(null);

    try {
      const slidesData = slides.map((slide, index) => {
        // Slide đang active: lấy HTML từ live DOM (state mới nhất)
        // Slide khác: lấy từ content đã lưu trong elements[0].content
        const rawContent =
          index === currentSlideIndex
            ? slideCanvasRef.current?.getHTML() || slide.elements[0]?.content || ''
            : slide.elements[0]?.content || '';

        return {
          html_content: createCompleteHTML(slide, rawContent),
          slide_name: `slide_${index + 1}`,
        };
      });

      const result = await api.exportSlidesPdf(slidesData);

      if (result.success && result.download_url) {
        setExportResult({ download_url: result.download_url, message: result.message });
      } else {
        throw new Error(t.export_pdf_failed);
      }
    } catch (err: any) {
      setExportError(t.export_pdf_error);
      throw err;
    } finally {
      setIsExporting(false);
    }
  };

  /**
   * Chụp tất cả slides thành ảnh PNG và tải về dạng ZIP.
   * Gửi full standalone HTML lên POST /api/v1/capture/capture-slides-batch
   * Giống captureAllSlides() trong webfix SlideCapture.js
   */
  const captureAllSlides = async (
    slides: Slide[],
    currentSlideIndex: number,
    slideCanvasRef: React.RefObject<SlideCanvasHandle>,
    _projectName: string
  ) => {
    if (!slides.length) throw new Error(t.export_no_slides);

    setIsExporting(true);
    setExportError(null);
    setExportResult(null);

    try {
      const slidesData = slides.map((slide, index) => {
        const rawContent =
          index === currentSlideIndex
            ? slideCanvasRef.current?.getHTML() || slide.elements[0]?.content || ''
            : slide.elements[0]?.content || '';

        return {
          html_content: createCompleteHTML(slide, rawContent),
          slide_name: `slide_${index + 1}`,
        };
      });

      const result = await api.captureSlidesBatch(slidesData);

      if (result.success && result.download_url) {
        setExportResult({ download_url: result.download_url, message: result.message });
      } else {
        throw new Error(t.export_capture_failed);
      }
    } catch (err: any) {
      setExportError(t.export_capture_error);
      throw err;
    } finally {
      setIsExporting(false);
    }
  };

  const resetExport = () => {
    setExportResult(null);
    setExportError(null);
  };

  return {
    exportAllSlidesToPdf,
    captureAllSlides,
    isExporting,
    exportResult,
    exportError,
    resetExport,
  };
};
