import React from "react";
import type { Slide } from "../types";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";
import { useSlideExport } from "../hooks/useSlideExport";
import { api } from "@/lib/api";

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  slides: Slide[];
  currentSlideIndex: number;
  slideCanvasRef: React.RefObject<SlideCanvasHandle>;
  projectName: string;
}

export const ExportModal = ({
  isOpen,
  onClose,
  slides,
  currentSlideIndex,
  slideCanvasRef,
  projectName,
}: ExportModalProps) => {
  const { exportAllSlidesToPdf, captureAllSlides, isExporting, exportResult, exportError, resetExport } =
    useSlideExport();

  const handleExport = async (type: 'pdf' | 'images') => {
    try {
      if (type === 'pdf') {
        await exportAllSlidesToPdf(slides, currentSlideIndex, slideCanvasRef, projectName);
      } else {
        await captureAllSlides(slides, currentSlideIndex, slideCanvasRef, projectName);
      }
    } catch {
      // error already set in hook state
    }
  };

  const handleClose = () => {
    resetExport();
    onClose();
  };

  // Xây URL tải file từ download_url trả về bởi backend
  const getFullDownloadUrl = (downloadUrl: string) => {
    const filename = downloadUrl.split('/').pop() || '';
    return api.downloadCaptureUrl(filename);
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
        background: 'rgba(0,0,0,0.75)', display: 'flex',
        justifyContent: 'center', alignItems: 'center', zIndex: 10000,
      }}
      onClick={(e) => { if (e.target === e.currentTarget) handleClose(); }}
    >
      <div style={{
        background: 'white', borderRadius: 12, padding: 30, width: 460,
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
      }}>

        {/* ── Trạng thái: Thành công ── */}
        {exportResult ? (
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 52, marginBottom: 16 }}>✅</div>
            <h2 style={{ margin: '0 0 8px', color: '#2d3748' }}>Xuất thành công!</h2>
            <p style={{ color: '#718096', marginBottom: 24, fontSize: 14 }}>{exportResult.message}</p>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
              <a
                href={getFullDownloadUrl(exportResult.download_url)}
                download
                style={{ textDecoration: 'none' }}
              >
                <button style={{
                  padding: '12px 20px', background: 'linear-gradient(135deg,#667eea,#764ba2)',
                  color: 'white', border: 'none', borderRadius: 8, cursor: 'pointer',
                  fontWeight: 600, fontSize: 14,
                }}>
                  💾 Tải về
                </button>
              </a>
              <button
                onClick={handleClose}
                style={{
                  padding: '12px 20px', background: '#e2e8f0', color: '#4a5568',
                  border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: 14,
                }}
              >
                Đóng
              </button>
            </div>
          </div>

        ) : isExporting ? (
          /* ── Trạng thái: Đang xử lý ── */
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <div style={{ fontSize: 52, marginBottom: 16 }}>⏳</div>
            <h2 style={{ color: '#2d3748', marginBottom: 8 }}>Đang xuất slides...</h2>
            <p style={{ color: '#718096', fontSize: 14 }}>
              Đang xử lý {slides.length} slide{slides.length > 1 ? 's' : ''}
            </p>
          </div>

        ) : exportError ? (
          /* ── Trạng thái: Lỗi ── */
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 52, marginBottom: 16 }}>❌</div>
            <h2 style={{ margin: '0 0 8px', color: '#e53e3e' }}>Xuất thất bại</h2>
            <p style={{ color: '#718096', marginBottom: 24, fontSize: 14 }}>{exportError}</p>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
              <button
                onClick={resetExport}
                style={{
                  padding: '12px 20px', background: 'linear-gradient(135deg,#667eea,#764ba2)',
                  color: 'white', border: 'none', borderRadius: 8, cursor: 'pointer',
                  fontWeight: 600, fontSize: 14,
                }}
              >
                Thử lại
              </button>
              <button
                onClick={handleClose}
                style={{
                  padding: '12px 20px', background: '#e2e8f0', color: '#4a5568',
                  border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: 14,
                }}
              >
                Đóng
              </button>
            </div>
          </div>

        ) : (
          /* ── Trạng thái: Chọn định dạng ── */
          <>
            <h2 style={{ margin: '0 0 6px', color: '#2d3748' }}>Xuất Slides</h2>
            <p style={{ color: '#718096', marginBottom: 20, fontSize: 14 }}>
              {slides.length} slide{slides.length > 1 ? 's' : ''} · Chọn định dạng xuất:
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 20 }}>
              <button
                onClick={() => handleExport('pdf')}
                style={{
                  textAlign: 'left', padding: 15,
                  border: '1.5px solid #e2e8f0', borderRadius: 8,
                  background: 'white', cursor: 'pointer', transition: 'all 0.15s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = '#667eea';
                  e.currentTarget.style.background = '#f7fafc';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = '#e2e8f0';
                  e.currentTarget.style.background = 'white';
                }}
              >
                <div style={{ fontWeight: 600, color: '#2d3748', marginBottom: 4 }}>📄 Xuất PDF</div>
                <div style={{ fontSize: 13, color: '#718096' }}>Ghép tất cả slides thành một file PDF</div>
              </button>

              <button
                onClick={() => handleExport('images')}
                style={{
                  textAlign: 'left', padding: 15,
                  border: '1.5px solid #e2e8f0', borderRadius: 8,
                  background: 'white', cursor: 'pointer', transition: 'all 0.15s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = '#667eea';
                  e.currentTarget.style.background = '#f7fafc';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = '#e2e8f0';
                  e.currentTarget.style.background = 'white';
                }}
              >
                <div style={{ fontWeight: 600, color: '#2d3748', marginBottom: 4 }}>🖼️ Xuất hình ảnh</div>
                <div style={{ fontSize: 13, color: '#718096' }}>Chụp từng slide thành ảnh PNG, tải về dạng ZIP</div>
              </button>
            </div>

            <div style={{ textAlign: 'right' }}>
              <button
                onClick={handleClose}
                style={{
                  padding: '8px 16px', border: 'none',
                  background: '#e2e8f0', color: '#4a5568',
                  borderRadius: 6, cursor: 'pointer', fontSize: 14,
                }}
              >
                Hủy
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
