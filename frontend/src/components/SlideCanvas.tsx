// File: frontend/src/components/SlideCanvas.tsx

import React, { useRef, useEffect, useImperativeHandle, forwardRef, useState, useLayoutEffect } from 'react';
import { SlideEditorLogic } from '@/lib/SlideLogicCore';

interface SlideCanvasProps {
  htmlContent: string;
  onElementSelect: (data: any) => void;
}

export interface SlideCanvasHandle {
  updateElement: (styles: any) => void;
  getHTML: () => string;
  undo: () => void;
  redo: () => void;
}

// Kích thước chuẩn thiết kế (Cố định)
const SLIDE_WIDTH = 1920;
const SLIDE_HEIGHT = 1080;

export const SlideCanvas = forwardRef<SlideCanvasHandle, SlideCanvasProps>((props, ref) => {
  const wrapperRef = useRef<HTMLDivElement>(null); // Khung bao ngoài (Responsive)
  const shadowHostRef = useRef<HTMLDivElement>(null); // Nơi chứa Shadow DOM
  const logicInstanceRef = useRef<SlideEditorLogic | null>(null);
  
  const [scale, setScale] = useState(1);

  // --- 1. LOGIC TÍNH SCALE TỰ ĐỘNG ---
  useLayoutEffect(() => {
    const handleResize = () => {
      if (!wrapperRef.current) return;
      
      const parentW = wrapperRef.current.clientWidth;
      const parentH = wrapperRef.current.clientHeight;
      const padding = 40; // Khoảng cách đệm

      // Tính tỷ lệ co giãn
      const scaleX = (parentW - padding) / SLIDE_WIDTH;
      const scaleY = (parentH - padding) / SLIDE_HEIGHT;
      
      // Chọn tỷ lệ nhỏ hơn để slide nằm lọt thỏm trong màn hình
      const newScale = Math.min(scaleX, scaleY); 
      setScale(newScale);
    };

    // Observer để bắt sự kiện resize div cha
    const ro = new ResizeObserver(handleResize);
    if (wrapperRef.current) ro.observe(wrapperRef.current);

    return () => ro.disconnect();
  }, []);

  // Cập nhật scale xuống Logic Core khi scale thay đổi
  useEffect(() => {
    if (logicInstanceRef.current && logicInstanceRef.current.setScale) {
        logicInstanceRef.current.setScale(scale);
    }
  }, [scale]);

  // Expose các method
  useImperativeHandle(ref, () => ({
    updateElement: (styles: any) => logicInstanceRef.current?.updateSelectedElementStyle(styles),
    getHTML: () => logicInstanceRef.current?.getHTML() || '',
    undo: () => logicInstanceRef.current?.undo(),
    redo: () => logicInstanceRef.current?.redo()
  }));

  // Trong file SlideCanvas.tsx

  const processHTML = (rawHTML: string): string => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(rawHTML, 'text/html');

    // 1. Xóa script cũ
    const scripts = doc.querySelectorAll('script');
    scripts.forEach(script => script.remove());

    // 2. Xử lý CSS
    const styleElements = Array.from(doc.querySelectorAll('style'));
    let collectedCSS = styleElements.map(s => s.textContent || '').join('\n');
    
    // Scope lại CSS
    collectedCSS = collectedCSS
        .replace(/\bbody\s*\{/g, '.slide-bg-wrapper {')
        .replace(/\bhtml\s*\{/g, ':host {')
        .replace(/\bbody\s+/g, '.slide-bg-wrapper ') // Thêm dòng này để bắt trường hợp "body, html"
        .replace(/\bhtml\s+/g, ':host ')             // Thêm dòng này để bắt trường hợp "body, html"
        .replace(/\.outer-wrapper\s*\{/g, '.slide-inner-wrapper {');

    // 3. Lấy nội dung
    const contentWrapper = doc.querySelector('.content-wrapper');
    let innerContent = '';
    if (contentWrapper) {
        innerContent = contentWrapper.innerHTML;
    } else {
        innerContent = doc.body.innerHTML;
    }

    // 4. CSS Reset & Fix (ĐÃ CẬP NHẬT ĐỂ KHÔNG MẤT MÀU NỀN)
    const baseShadowCSS = `
      :host { 
        display: block; 
        width: 1920px; 
        height: 1080px; 
        overflow: hidden;
        background-color: white; /* Mặc định là trắng nếu user không set màu */
      }
      
      .slide-bg-wrapper {
        width: 100%;
        height: 100%;
        position: relative;
        
        /* ĐÃ XÓA background-color: white ở đây để không ghi đè màu user */
        
        margin: 0 !important;
        padding: 0 !important; 
        overflow: hidden !important; 
        box-sizing: border-box !important;
      }

      .content-wrapper {
        width: 1920px;
        height: 1080px;
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%) !important;
        overflow: visible;
      }
      
      ::-webkit-scrollbar { display: none; }
    `;

    return `
      <style>
        ${collectedCSS} 
        ${baseShadowCSS} 
      </style>
      <div class="slide-bg-wrapper">
         <div class="content-wrapper">
            ${innerContent}
         </div>
      </div>
    `;
  };

  // Mount & Attach Shadow DOM
  useEffect(() => {
    if (!shadowHostRef.current) return;

    // Attach Shadow DOM (chỉ 1 lần)
    let shadowRoot = shadowHostRef.current.shadowRoot;
    if (!shadowRoot) {
        shadowRoot = shadowHostRef.current.attachShadow({ mode: 'open' });
    }

    // Inject HTML
    shadowRoot.innerHTML = processHTML(props.htmlContent);

    // Init Logic Core
    setTimeout(() => {
      if (logicInstanceRef.current) logicInstanceRef.current.destroy();
      
      try {
        logicInstanceRef.current = new SlideEditorLogic(shadowRoot, props.onElementSelect);
        
        // QUAN TRỌNG: Set scale ngay lập tức sau khi init
        if (logicInstanceRef.current.setScale) {
            logicInstanceRef.current.setScale(scale);
        }
      } catch (e) {
        console.error('Logic Init Failed', e);
      }
    }, 10);

  }, [props.htmlContent]);

  return (
    // 1. WRAPPER: Giới hạn vùng nhìn, cắt bỏ phần thừa
    <div 
      ref={wrapperRef} 
      className="w-full h-full bg-gray-100 flex items-center justify-center overflow-hidden relative"
    >
      {/* 2. STAGE: Kích thước thật (1920x1080) nhưng được Scale nhỏ lại */}
      <div 
        style={{
          width: SLIDE_WIDTH,
          height: SLIDE_HEIGHT,
          transform: `scale(${scale})`, // PHÉP THUẬT NẰM Ở ĐÂY
          transformOrigin: 'center center',
          boxShadow: '0 0 20px rgba(0,0,0,0.1)',
          flexShrink: 0
        }}
      >
        {/* 3. HOST: Nơi chứa Shadow DOM */}
        <div 
            ref={shadowHostRef}
            style={{ width: '100%', height: '100%' }}
        />
      </div>

      {/* Hiển thị % Zoom */}
      <div className="absolute bottom-4 right-4 bg-black/50 text-white px-2 py-1 rounded text-xs">
        {Math.round(scale * 100)}%
      </div>
    </div>
  );
});

SlideCanvas.displayName = "SlideCanvas";