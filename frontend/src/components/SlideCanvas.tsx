import React, { useRef, useEffect, useImperativeHandle, forwardRef } from 'react';
import { SlideEditorLogic } from '@/lib/SlideLogicCore';

interface SlideCanvasProps {
  slideId: string;
  htmlContent: string;
  backgroundColor?: string;
  onElementSelect?: (data: any) => void;
  onChange?: () => void;
  zoom?: number;
  /** When true, only renders the slide — no drag/resize/edit logic is initialized */
  readOnly?: boolean;
}

export interface SlideCanvasHandle {
  updateElement: (styles: any) => void;
  getHTML: () => string;
  undo: () => void;
  redo: () => void;
  execFormat: (command: string, value?: string) => void;
  getSelectedZIndex: () => number;
  getMaxZIndex: () => number;
  injectElement: (html: string) => void;
  saveHistory: (silent?: boolean) => void;
  reselectById: (id: string) => void;
}

export const SlideCanvas = forwardRef<SlideCanvasHandle, SlideCanvasProps>((props, ref) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const shadowRootRef = useRef<ShadowRoot | null>(null);
  const logicInstanceRef = useRef<SlideEditorLogic | null>(null);
  // Store slide-specific CSS so it can be round-tripped when saving
  const slideCSSRef = useRef<string>('');

  // Use refs so SlideEditorLogic always calls the latest callbacks without needing re-init
  const onElementSelectRef = useRef<(data: any) => void>(props.onElementSelect);
  const onChangeRef = useRef<(() => void) | undefined>(props.onChange);
  const zoomRef = useRef<number>(props.zoom ?? 1);
  // Update refs on every render (no deps needed — this is intentional)
  onElementSelectRef.current = props.onElementSelect;
  onChangeRef.current = props.onChange;
  zoomRef.current = props.zoom ?? 1;
  
  // Apply background to container (like Legacy: applyDirectBackground)
  useEffect(() => {
    console.log('🎨 [SlideCanvas useEffect] backgroundColor changed to:', props.backgroundColor);
    if (containerRef.current && props.backgroundColor) {
      containerRef.current.style.background = props.backgroundColor;
      console.log('🎨 Applied background to canvas:', props.backgroundColor);
    } else {
      console.warn('⚠️ [SlideCanvas] Cannot apply background:', {
        hasContainer: !!containerRef.current,
        backgroundColor: props.backgroundColor
      });
    }
  }, [props.backgroundColor]);

  // Expose các method cho component cha (SlideEditor.tsx) gọi
  useImperativeHandle(ref, () => ({
    updateElement: (styles: any) => {
      logicInstanceRef.current?.updateSelectedElementStyle(styles);
    },
    getHTML: () => {
      const canvasHTML = logicInstanceRef.current?.getHTML() || '';
      // Prepend slide-specific CSS so it survives save/reload cycles.
      // Re-remap Shadow DOM selectors back to standard CSS selectors so the
      // stored html_content works correctly in a normal iframe/browser context.
      const css = slideCSSRef.current;
      if (css && css.trim()) {
        const standardCSS = css
          .replace(/\.slide-bg-wrapper\s*\{/g, 'body {')
          .replace(/\.slide-bg-wrapper\b/g, 'body')
          .replace(/:host\s*\{/g, 'html {')
          .replace(/:host\b/g, 'html');
        return `<style>${standardCSS}</style>\n${canvasHTML}`;
      }
      return canvasHTML;
    },
    undo: () => {
      logicInstanceRef.current?.undo();
    },
    redo: () => {
      logicInstanceRef.current?.redo();
    },
    execFormat: (command: string, value?: string) => {
      logicInstanceRef.current?.execFormat(command, value ?? null);
    },
    getSelectedZIndex: () => {
      return logicInstanceRef.current?.getSelectedZIndex() ?? 0;
    },
    getMaxZIndex: () => {
      return logicInstanceRef.current?.getMaxZIndex() ?? 0;
    },
    injectElement: (html: string) => {
      logicInstanceRef.current?.injectElement(html);
    },
    saveHistory: (silent = false) => {
      logicInstanceRef.current?.saveHistory(silent);
    },
    reselectById: (id: string) => {
      logicInstanceRef.current?.reselectById(id);
    },
  }));

  // Xử lý HTML & CSS Isolation
  const processHTML = (rawHTML: string, isReadOnly = false): string => {
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
    
    // Persist CSS so getHTML() can prepend it when saving
    slideCSSRef.current = collectedCSS;
    
    // --- 2. Xóa các thẻ style khỏi body để tránh duplicate ---
    styleElements.forEach(s => s.remove());
    
    // --- 3. Auto-enhance elements from converter HTML (like Legacy version) ---
    const tempContainer = document.createElement('div');
    tempContainer.innerHTML = doc.body.innerHTML;
    
    Array.from(tempContainer.children).forEach(el => {
      if (!(el instanceof HTMLElement)) return;
      if (el.nodeType !== 1) return; // Skip non-element nodes
      
      const tag = el.tagName.toLowerCase();
      // Skip non-visual elements
      if (['style', 'script', 'link', 'meta', 'svg'].includes(tag)) return;
      
      // Check both inline style property and style attribute
      const computedStyle = window.getComputedStyle(el);
      const hasAbsolutePosition = computedStyle.position === 'absolute' || 
        computedStyle.position === 'fixed' ||
        (el.getAttribute('style')?.includes('position: absolute')) ||
        (el.getAttribute('style')?.includes('position:absolute'));
      
      if (hasAbsolutePosition) {
        // Add .element class if missing
        if (!el.classList.contains('element')) {
          el.classList.add('element');
          console.log('➕ [SlideCanvas] Auto-added .element class to:', tag);
        }
        
        // Auto-detect and set data-type if missing
        if (!el.dataset.type) {
          let elementType: 'text' | 'image' | 'video' | 'shape' = 'shape'; // default
          
          const hasImage = el.querySelector('img') || tag === 'img';
          const hasVideo = el.querySelector('video') || tag === 'video';
          const textContent = el.textContent?.trim() || '';
          const hasSignificantText = textContent.length > 3; // At least 4 characters
          
          // Explicit text tags always get text type if they have content
          const explicitTextTags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'li', 'blockquote', 'pre', 'a'];
          
          // DIV only becomes text if it has significant text AND no background/decorative styling
          const isDivWithText = tag === 'div' && hasSignificantText;
          const hasBackgroundStyling = el.style.background || el.style.backgroundColor ||
            el.style.backgroundImage || el.style.borderRadius;
          
          if (hasImage) {
            elementType = 'image';
          } else if (hasVideo) {
            elementType = 'video';
          } else if (explicitTextTags.includes(tag) && hasSignificantText) {
            // Explicit text tags with content are always text
            elementType = 'text';
          } else if (isDivWithText && !hasBackgroundStyling) {
            // DIV with text and no decorative styling
            elementType = 'text';
          } else if (hasSignificantText && !hasBackgroundStyling) {
            // Any element with text and no decoration
            elementType = 'text';
          } else {
            // Everything else is a shape (decorative elements, backgrounds, etc.)
            elementType = 'shape';
          }
          
          el.dataset.type = elementType;
          console.log('🏷️ [SlideCanvas] Auto-set data-type:', elementType, 'for', tag, `(text: "${textContent.substring(0, 30)}...")`);
        }
        
        // Add contenteditable ONLY for text elements (not in read-only/presentation mode)
        if (!isReadOnly && el.dataset.type === 'text' && !el.hasAttribute('contenteditable')) {
          el.setAttribute('contenteditable', 'true');
          console.log('✏️ [SlideCanvas] Auto-added contenteditable to:', tag);
        }
        
        // Generate unique ID if missing
        if (!el.id) {
          el.id = `element_${el.dataset.type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          console.log('🆔 [SlideCanvas] Generated ID:', el.id);
        }
      }
    });
    
    // In read-only mode (presentation/preview): strip any editor-only artifacts
    // that may have been baked into previously-saved HTML.
    if (isReadOnly) {
      tempContainer.querySelectorAll('.resize-handle, .drag-handle, .smart-guide').forEach(el => el.remove());
      tempContainer.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
      tempContainer.querySelectorAll('[contenteditable]').forEach(el => el.removeAttribute('contenteditable'));
      tempContainer.querySelectorAll('[data-selectable]').forEach(el => el.removeAttribute('data-selectable'));
      tempContainer.querySelectorAll('[data-guide-key]').forEach(el => el.removeAttribute('data-guide-key'));
      tempContainer.querySelectorAll<HTMLElement>('*').forEach(el => {
        if (el.style && el.style.cursor === 'move') el.style.removeProperty('cursor');
      });
    }

    // Get enhanced body content
    let bodyContent = tempContainer.innerHTML;
    
    // Nếu không có gì trong body, fallback
    if (!bodyContent.trim()) {
      bodyContent = '<div style="width: 100%; height: 100%; min-height: 1080px; position: relative;"></div>';
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
      
      /* Selection UI Styles (Legacy-style with animation) */
      ${isReadOnly ? '' : `
      .element.selected {
        outline: 3px solid #3b82f6 !important;
        outline-offset: 2px;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2),
                    0 8px 30px rgba(59, 130, 246, 0.4) !important;
        animation: selectedPulse 2s ease-in-out infinite;
      }
      
      @keyframes selectedPulse {
        0%, 100% {
          box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2),
                      0 8px 30px rgba(59, 130, 246, 0.4);
        }
        50% {
          box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4),
                      0 8px 35px rgba(59, 130, 246, 0.6);
        }
      }
      
      /* Resize Handles */
      .resize-handle {
        position: absolute;
        width: 12px;
        height: 12px;
        background: white;
        border: 2px solid #3b82f6;
        border-radius: 50%;
        display: none;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
        z-index: 100;
        pointer-events: auto !important;
      }
      
      .element.selected .resize-handle {
        display: block;
      }
      
      .resize-handle:hover {
        transform: scale(1.2);
        background: #3b82f6;
        border-color: white;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
      }
      
      .resize-handle.tl {
        top: -8px;
        left: -8px;
        cursor: nwse-resize;
      }
      
      .resize-handle.tr {
        top: -8px;
        right: -8px;
        cursor: nesw-resize;
      }
      
      .resize-handle.bl {
        bottom: -8px;
        left: -8px;
        cursor: nesw-resize;
      }
      
      .resize-handle.br {
        bottom: -8px;
        right: -8px;
        cursor: nwse-resize;
      }
      
      /* Drag Handle — hidden, element is draggable directly */
      .drag-handle {
        display: none !important;
      }
      `}
      
      .smart-guide {
        opacity: 0.7;
      }
      
      /* Đảm bảo các element có thể interact */
      ${isReadOnly ? '' : `
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
      `}
      ${isReadOnly ? `
      /* Read-only: disable all pointer interactions */
      * { pointer-events: none !important; cursor: default !important; }
      ` : ''}
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
      const processedHTML = processHTML(props.htmlContent, props.readOnly);
      shadowRootRef.current.innerHTML = processedHTML;
      console.log('[SlideCanvas] HTML injected into Shadow DOM');
    } catch (e) {
      console.error('[SlideCanvas] Failed to process/inject HTML:', e);
      return;
    }

    // Skip editor logic in read-only mode — just render the HTML
    if (props.readOnly) return;

    // Đợi một tick để DOM render xong
    setTimeout(() => {
      // Khởi tạo Logic Core (Cắm logic JS cũ vào môi trường Shadow DOM)
      if (logicInstanceRef.current) {
        logicInstanceRef.current.destroy();
      }
      
      try {
        logicInstanceRef.current = new SlideEditorLogic(
          shadowRootRef.current!,
          // Stable lambdas — always call the latest callback via ref
          (data: any) => onElementSelectRef.current?.(data),
          () => onChangeRef.current?.()
        );
        // Apply current zoom immediately so drag/resize scale is correct from the start
        logicInstanceRef.current.setScale(zoomRef.current);
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
  }, [props.slideId, props.readOnly]); // Re-init only when switching to a different slide

  // For readOnly instances (thumbnails/previews): re-inject when htmlContent changes.
  // The editor (readOnly=false) must NOT do this — it would overwrite live user edits.
  useEffect(() => {
    if (!props.readOnly || !shadowRootRef.current) return;
    shadowRootRef.current.innerHTML = processHTML(props.htmlContent, true);
  }, [props.htmlContent]); // eslint-disable-line react-hooks/exhaustive-deps

  // Sync zoom to logic instance so drag/resize deltas are correctly scaled.
  // (The outer CanvasArea wrapper already applies the CSS transform — we must
  // NOT apply it again here or the canvas would be double-scaled.)
  useEffect(() => {
    if (props.zoom !== undefined) {
      logicInstanceRef.current?.setScale(props.zoom);
    }
  }, [props.zoom]);

  return (
    <div 
      ref={containerRef} 
      className="w-full h-full bg-white shadow-2xl"
      style={{ 
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
