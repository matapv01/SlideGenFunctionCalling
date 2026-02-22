import React, { useRef, useEffect, useImperativeHandle, forwardRef } from 'react';
import { SlideEditorLogic } from '@/lib/SlideLogicCore';

interface SlideCanvasProps {
  htmlContent: string;
  onElementSelect: (data: any) => void;
  zoom?: number;
}

export interface SlideCanvasHandle {
  updateElement: (styles: any) => void;
  getHTML: () => string;
  undo: () => void;
  redo: () => void;
}

export const SlideCanvas = forwardRef<SlideCanvasHandle, SlideCanvasProps>((props, ref) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const shadowRootRef = useRef<ShadowRoot | null>(null);
  const logicInstanceRef = useRef<SlideEditorLogic | null>(null);

  // Expose các method cho component cha (SlideEditor.tsx) gọi
  useImperativeHandle(ref, () => ({
    updateElement: (styles: any) => {
      logicInstanceRef.current?.updateSelectedElementStyle(styles);
    },
    getHTML: () => {
      return logicInstanceRef.current?.getHTML() || '';
    },
    undo: () => {
      logicInstanceRef.current?.undo();
    },
    redo: () => {
      logicInstanceRef.current?.redo();
    }
  }));

  // Xử lý HTML & CSS Isolation
  const processHTML = (rawHTML: string): string => {
    console.log('[SlideCanvas] Processing HTML...');
    
    // Parse HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(rawHTML, 'text/html');
    
    // --- 1. Thu thập tất cả CSS ---
    const styleElements = Array.from(doc.querySelectorAll('style'));
    let collectedCSS = styleElements.map(s => s.textContent || '').join('\n');
    
    // Regex đổi scope CSS để nó chạy đúng trong Shadow DOM
    // Đổi 'body' -> '.slide-bg-wrapper' (class bao ngoài)
    // Đổi 'html' -> ':host'
    collectedCSS = collectedCSS
      .replace(/\bbody\s*\{/g, '.slide-bg-wrapper {')
      .replace(/\bhtml\s*\{/g, ':host {')
      .replace(/\bbody\s+/g, '.slide-bg-wrapper ') // body selector với combinator
      .replace(/\bhtml\s+/g, ':host ');
    
    // --- 2. Xóa các thẻ style khỏi body để tránh duplicate ---
    styleElements.forEach(s => s.remove());
    
    // --- 3. Lấy nội dung body ---
    let bodyContent = doc.body.innerHTML;
    
    // Nếu không có gì trong body, fallback
    if (!bodyContent.trim()) {
      bodyContent = '<div class="slide-container" style="width: 100%; height: 100%; min-height: 1080px;"><p>Empty slide</p></div>';
    }
    
    // --- 4. Thêm CSS base cho Shadow DOM ---
    const baseShadowCSS = `
      :host {
        display: block;
        width: 100%;
        height: 100%;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      }
      
      .slide-bg-wrapper {
        width: 100%;
        height: 100%;
        min-height: 1080px;
        position: relative;
        overflow: hidden;
      }
      
      .slide-container {
        width: 100%;
        height: 100%;
        position: relative;
      }
      
      /* Selection UI Styles */
      .editor-overlay {
        box-sizing: border-box;
      }
      
      .resize-handle {
        pointer-events: auto !important;
      }
      
      .smart-guide {
        opacity: 0.7;
      }
      
      /* Đảm bảo các element có thể interact */
      [data-selectable="true"] {
        cursor: move;
      }
      
      /* ContentEditable Styles */
      [contenteditable="true"]:focus {
        outline: 2px dashed #3b82f6;
        outline-offset: 2px;
        cursor: text !important;
      }
      
      [contenteditable="true"]:empty:before {
        content: attr(data-placeholder);
        color: #999;
      }
    `;
    
    // --- 5. Tạo HTML hoàn chỉnh ---
    return `
      <style>
        ${baseShadowCSS}
        ${collectedCSS}
      </style>
      <div class="slide-bg-wrapper">
        ${bodyContent}
      </div>
    `;
  };

  useEffect(() => {
    if (!containerRef.current) return;

    console.log('[SlideCanvas] Mounting with content:', props.htmlContent.substring(0, 100) + '...');

    // Attach Shadow DOM (chỉ 1 lần)
    if (!shadowRootRef.current) {
      try {
        shadowRootRef.current = containerRef.current.attachShadow({ mode: 'open' });
        console.log('[SlideCanvas] Shadow DOM attached');
      } catch (e) {
        console.error('[SlideCanvas] Failed to attach shadow DOM:', e);
        return;
      }
    }

    // Inject Content đã xử lý
    try {
      const processedHTML = processHTML(props.htmlContent);
      shadowRootRef.current.innerHTML = processedHTML;
      console.log('[SlideCanvas] HTML injected into Shadow DOM');
    } catch (e) {
      console.error('[SlideCanvas] Failed to process/inject HTML:', e);
      return;
    }

    // Đợi một tick để DOM render xong
    setTimeout(() => {
      // Khởi tạo Logic Core (Cắm logic JS cũ vào môi trường Shadow DOM)
      if (logicInstanceRef.current) {
        logicInstanceRef.current.destroy();
      }
      
      try {
        logicInstanceRef.current = new SlideEditorLogic(
          shadowRootRef.current!, 
          props.onElementSelect
        );
        console.log('[SlideCanvas] Logic Core initialized');
      } catch (e) {
        console.error('[SlideCanvas] Failed to initialize Logic Core:', e);
      }
    }, 10);

    return () => {
      if (logicInstanceRef.current) {
        logicInstanceRef.current.destroy();
        logicInstanceRef.current = null;
      }
    };
  }, [props.htmlContent]); // Re-init khi đổi slide khác

  // Update zoom nếu có
  useEffect(() => {
    if (containerRef.current && props.zoom !== undefined) {
      containerRef.current.style.transform = `scale(${props.zoom})`;
      containerRef.current.style.transformOrigin = 'top left';
    }
  }, [props.zoom]);

  return (
    <div 
      ref={containerRef} 
      className="w-full h-full bg-white shadow-2xl"
      style={{ 
        isolation: 'isolate', // CSS property giúp tăng cường isolation
        width: '1920px',
        height: '1080px',
        minWidth: '1920px',
        minHeight: '1080px',
        position: 'relative'
      }}
    />
  );
});

SlideCanvas.displayName = "SlideCanvas";
