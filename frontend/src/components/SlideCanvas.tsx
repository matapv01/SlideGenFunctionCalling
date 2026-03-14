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
  canUndo: () => boolean;
  canRedo: () => boolean;
  execFormat: (command: string, value?: string) => void;
  getSelectedZIndex: () => number;
  getMaxZIndex: () => number;
  injectElement: (html: string) => void;
  deleteElement: (id?: string) => void;
  duplicateElement: (id?: string) => void;
  copySelectedElement: (id?: string) => boolean;
  pasteElement: () => void;
  bringToFront: (id?: string) => void;
  sendToBack: (id?: string) => void;
  isTextEditing: () => boolean;
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

  // Apply fallback background to host element (visible when slide CSS has no bg)
  useEffect(() => {
    if (props.backgroundColor && containerRef.current) {
      containerRef.current.style.background = props.backgroundColor;
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
    canUndo: () => logicInstanceRef.current?.canUndo() ?? false,
    canRedo: () => logicInstanceRef.current?.canRedo() ?? false,
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
    deleteElement: (id?: string) => {
      logicInstanceRef.current?.deleteElement(id ?? null);
    },
    duplicateElement: (id?: string) => {
      logicInstanceRef.current?.duplicateElement(id ?? null);
    },
    copySelectedElement: (id?: string) => {
      return logicInstanceRef.current?.copySelectedElement(id ?? null) ?? false;
    },
    pasteElement: () => {
      logicInstanceRef.current?.pasteElement();
    },
    bringToFront: (id?: string) => {
      logicInstanceRef.current?.bringToFront(id ?? null);
    },
    sendToBack: (id?: string) => {
      logicInstanceRef.current?.sendToBack(id ?? null);
    },
    isTextEditing: () => {
      return !!logicInstanceRef.current?.isEditingText;
    },
    saveHistory: (silent = false) => {
      logicInstanceRef.current?.saveHistory(silent);
    },
    reselectById: (id: string) => {
      logicInstanceRef.current?.reselectById(id);
    },
  }));

  // The converter's resize JS (var(--scale,1)) doesn't execute via innerHTML.
  // Fallback for readOnly mode: set --scale from measured dimensions.
  const applyConverterScaleFallback = (shadowRoot: ShadowRoot) => {
    setTimeout(() => {
      const cw = shadowRoot.querySelector('.content-wrapper') as HTMLElement | null;
      if (!cw) return;
      const w = cw.offsetWidth;
      const h = cw.offsetHeight;
      if (w > 0 && h > 0) {
        const scale = Math.min(1920 / w, 1080 / h);
        cw.style.transform = `translate(-50%, -50%) scale(${scale})`;
      }
    }, 50);
  };

  /**
   * Parse a CSS rule body into a key→value map.
   * E.g. "margin: 0; background: red;" → { margin: "0", background: "red" }
   */
  const parseCSSProperties = (ruleBody: string): Record<string, string> => {
    const props: Record<string, string> = {};
    // Split on semicolons, but be careful with values that contain parentheses
    // (like linear-gradient) — those don't contain semicolons so simple split works.
    const parts = ruleBody.split(';');
    for (const part of parts) {
      const trimmed = part.trim();
      if (!trimmed) continue;
      const colonIdx = trimmed.indexOf(':');
      if (colonIdx <= 0) continue;
      const key = trimmed.substring(0, colonIdx).trim();
      const value = trimmed.substring(colonIdx + 1).trim();
      if (key && value) {
        props[key] = value;
      }
    }
    return props;
  };

  // Xử lý HTML & CSS Isolation
  const processHTML = (rawHTML: string, isReadOnly = false): string => {
    // Fix viewport units to absolute pixels (vw/vh refer to page viewport in Shadow DOM)
    const fixedHTML = rawHTML
      .replace(/(\d+(?:\.\d+)?)\s*vw/gi, (_, n) => `${(parseFloat(n) * 1920 / 100).toFixed(2)}px`)
      .replace(/(\d+(?:\.\d+)?)\s*vh/gi, (_, n) => `${(parseFloat(n) * 1080 / 100).toFixed(2)}px`)
      .replace(/(\d+(?:\.\d+)?)\s*vmin/gi, (_, n) => `${(parseFloat(n) * 1080 / 100).toFixed(2)}px`)
      .replace(/(\d+(?:\.\d+)?)\s*vmax/gi, (_, n) => `${(parseFloat(n) * 1920 / 100).toFixed(2)}px`);

    // Parse HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(fixedHTML, 'text/html');

    // --- 1. Collect all CSS ---
    const styleElements = Array.from(doc.querySelectorAll('style'));
    let collectedCSS = styleElements.map(s => s.textContent || '').join('\n');

    // --- 2. Extract ALL body {} properties BEFORE remapping ---
    // Merge all body rules (later properties win = CSS cascade).
    // This replaces the fragile regex-based background-only extraction.
    const mergedBodyProps: Record<string, string> = {};
    const bodyRuleRegex = /\bbody\s*\{([^}]+)\}/g;
    let bodyMatch;
    while ((bodyMatch = bodyRuleRegex.exec(collectedCSS)) !== null) {
      const parsed = parseCSSProperties(bodyMatch[1]);
      Object.assign(mergedBodyProps, parsed); // later values overwrite
    }

    // Apply overrides matching ScaledSlidePreview's base styles:
    // html, body { margin: 0 !important; padding: 0 !important; overflow: hidden !important }
    mergedBodyProps['margin'] = '0';
    mergedBodyProps['padding'] = '0';
    mergedBodyProps['overflow'] = 'hidden';
    // Ensure wrapper fills the host element
    mergedBodyProps['position'] = 'relative';
    mergedBodyProps['width'] = '100%';
    mergedBodyProps['height'] = '100%';
    mergedBodyProps['min-height'] = '1080px';
    mergedBodyProps['box-sizing'] = 'border-box';

    // Build inline style string from merged body properties
    const wrapperInlineStyle = Object.entries(mergedBodyProps)
      .map(([k, v]) => `${k}:${v}`)
      .join(';');

    // --- 3. Remap CSS selectors for Shadow DOM ---
    // body {} → .slide-bg-wrapper {} (class on wrapper div)
    // html {} → :host
    // body .child → .slide-bg-wrapper .child (descendant combinator)
    collectedCSS = collectedCSS
      .replace(/\bbody\s*\{/g, '.slide-bg-wrapper {')
      .replace(/\bhtml\s*\{/g, ':host {')
      .replace(/\bbody\s+/g, '.slide-bg-wrapper ')
      .replace(/\bhtml\s+/g, ':host ');

    // Persist CSS for getHTML() round-trip
    slideCSSRef.current = collectedCSS;

    // --- 4. Remove style elements from body to avoid duplicates ---
    styleElements.forEach(s => s.remove());

    // --- 5. Auto-enhance elements from converter HTML ---
    const tempContainer = document.createElement('div');
    tempContainer.innerHTML = doc.body.innerHTML;

    Array.from(tempContainer.children).forEach(el => {
      if (!(el instanceof HTMLElement)) return;
      if (el.nodeType !== 1) return;

      const tag = el.tagName.toLowerCase();
      if (['style', 'script', 'link', 'meta', 'svg'].includes(tag)) return;

      const computedStyle = window.getComputedStyle(el);
      const hasAbsolutePosition = computedStyle.position === 'absolute' ||
        computedStyle.position === 'fixed' ||
        (el.getAttribute('style')?.includes('position: absolute')) ||
        (el.getAttribute('style')?.includes('position:absolute'));

      if (hasAbsolutePosition) {
        if (!el.classList.contains('element')) {
          el.classList.add('element');
        }

        if (!el.dataset.type) {
          let elementType: 'text' | 'image' | 'video' | 'shape' = 'shape';

          const hasImage = el.querySelector('img') || tag === 'img';
          const hasVideo = el.querySelector('video') || tag === 'video';
          const textContent = el.textContent?.trim() || '';
          const hasSignificantText = textContent.length > 3;

          const explicitTextTags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'li', 'blockquote', 'pre', 'a'];
          const isDivWithText = tag === 'div' && hasSignificantText;
          const hasBackgroundStyling = el.style.background || el.style.backgroundColor ||
            el.style.backgroundImage || el.style.borderRadius;

          if (hasImage) {
            elementType = 'image';
          } else if (hasVideo) {
            elementType = 'video';
          } else if (explicitTextTags.includes(tag) && hasSignificantText) {
            elementType = 'text';
          } else if (isDivWithText && !hasBackgroundStyling) {
            elementType = 'text';
          } else if (hasSignificantText && !hasBackgroundStyling) {
            elementType = 'text';
          } else {
            elementType = 'shape';
          }

          el.dataset.type = elementType;
        }

        if (!isReadOnly && el.dataset.type === 'text' && !el.hasAttribute('contenteditable')) {
          el.setAttribute('contenteditable', 'true');
        }

        if (!el.id) {
          el.id = `element_${el.dataset.type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        }
      }
    });

    // In read-only mode: strip editor-only artifacts
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

    let bodyContent = tempContainer.innerHTML;

    if (!bodyContent.trim()) {
      bodyContent = '<div style="width: 100%; height: 100%; min-height: 1080px; position: relative;"></div>';
    }

    // --- 6. Build Shadow DOM CSS ---
    // baseShadowCSS only handles :host and editor UI — body/wrapper styling is ALL inline.
    const baseShadowCSS = `
      :host {
        display: block;
        width: 100%;
        height: 100%;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      }

      .slide-container {
        width: 100%;
        height: 100%;
        position: relative;
      }

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

      .resize-handle.tl { top: -8px; left: -8px; cursor: nwse-resize; }
      .resize-handle.tr { top: -8px; right: -8px; cursor: nesw-resize; }
      .resize-handle.bl { bottom: -8px; left: -8px; cursor: nesw-resize; }
      .resize-handle.br { bottom: -8px; right: -8px; cursor: nwse-resize; }

      .drag-handle { display: none !important; }
      `}

      .smart-guide { opacity: 0.7; }

      ${isReadOnly ? '' : `
      [data-selectable="true"] { cursor: move; }

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
      * { pointer-events: none !important; cursor: default !important; }
      ` : ''}
    `;

    // --- 7. ReadOnly: compute content-wrapper scale from CSS dimensions ---
    let scaleOverrideCSS = '';
    if (isReadOnly) {
      const allCwMatches = [...collectedCSS.matchAll(/\.content-wrapper\s*\{([^}]+)\}/gs)];
      for (const m of allCwMatches) {
        const ruleBody = m[1];
        const wMatch = ruleBody.match(/\bwidth\s*:\s*([\d.]+)px/);
        const hMatch = ruleBody.match(/\bheight\s*:\s*([\d.]+)px/);
        if (wMatch && hMatch) {
          const cwW = parseFloat(wMatch[1]);
          const cwH = parseFloat(hMatch[1]);
          if (cwW > 0 && cwH > 0) {
            const scale = Math.min(1920 / cwW, 1080 / cwH);
            scaleOverrideCSS = `
      .content-wrapper {
        transform: translate(-50%, -50%) scale(${scale.toFixed(6)}) !important;
      }`;
          }
        }
      }
    }

    // --- 8. Assemble final Shadow DOM HTML ---
    // The wrapper div gets ALL merged body properties as inline styles.
    // This avoids any CSS cascade issues between baseShadowCSS and collectedCSS.
    // collectedCSS is still included so descendant selectors (body .child → .slide-bg-wrapper .child)
    // and non-body rules (.content-wrapper, .outer-wrapper, element classes) continue to work.
    return `
      <style>
        ${baseShadowCSS}
        ${collectedCSS}
        ${scaleOverrideCSS}
      </style>
      <div class="slide-bg-wrapper" style="${wrapperInlineStyle}">
        ${bodyContent}
      </div>
    `;
  };

  useEffect(() => {
    if (!containerRef.current) return;

    // Attach Shadow DOM (once)
    if (!shadowRootRef.current) {
      try {
        shadowRootRef.current = containerRef.current.attachShadow({ mode: 'open' });
      } catch (e) {
        console.error('[SlideCanvas] Failed to attach shadow DOM:', e);
        return;
      }
    }

    // Inject processed HTML
    try {
      const processedHTML = processHTML(props.htmlContent, props.readOnly);
      shadowRootRef.current.innerHTML = processedHTML;
      if (props.readOnly) applyConverterScaleFallback(shadowRootRef.current);
    } catch (e) {
      console.error('[SlideCanvas] Failed to process/inject HTML:', e);
      return;
    }

    // Skip editor logic in read-only mode
    if (props.readOnly) return;

    // Wait one tick for DOM to render
    setTimeout(() => {
      if (logicInstanceRef.current) {
        logicInstanceRef.current.destroy();
      }

      try {
        logicInstanceRef.current = new SlideEditorLogic(
          shadowRootRef.current!,
          (data: any) => onElementSelectRef.current?.(data),
          () => onChangeRef.current?.()
        );
        logicInstanceRef.current.setScale(zoomRef.current);
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
  }, [props.slideId, props.readOnly]);

  // For readOnly instances: re-inject when htmlContent changes.
  useEffect(() => {
    if (!props.readOnly || !shadowRootRef.current) return;
    shadowRootRef.current.innerHTML = processHTML(props.htmlContent, true);
    applyConverterScaleFallback(shadowRootRef.current);
  }, [props.htmlContent]); // eslint-disable-line react-hooks/exhaustive-deps

  // Sync zoom to logic instance
  useEffect(() => {
    if (props.zoom !== undefined) {
      logicInstanceRef.current?.setScale(props.zoom);
    }
  }, [props.zoom]);

  return (
    <div
      ref={containerRef}
      className="w-full h-full shadow-2xl"
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
