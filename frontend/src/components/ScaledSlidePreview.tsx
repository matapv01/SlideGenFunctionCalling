import { useState, useEffect, useRef, useCallback } from "react";
import { cn } from "@/lib/utils";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "@/pages/SlideEditor/constants";

interface ScaledSlidePreviewProps {
  html: string;
  title: string;
  className?: string;
}

// Inline script that runs inside the preview iframe to render [data-type="equation"] elements
const EQUATION_RENDER_SCRIPT = `
<script>
  (function() {
    function renderEquations() {
      var equations = document.querySelectorAll('[data-type="equation"]');
      if (!equations.length) return;

      // Try to use the already-registered math-field custom element
      function tryRender() {
        equations.forEach(function(node) {
          if (node.querySelector('math-field')) return; // already rendered
          var latex = node.getAttribute('data-latex') || '';
          node.innerHTML = '';
          var mf = document.createElement('math-field');
          mf.setAttribute('read-only', '');
          mf.style.cssText = 'width:fit-content;max-width:100%;min-height:60px;border:none;background:transparent;font-size:inherit;color:inherit;outline:none;';
          mf.value = latex;
          node.appendChild(mf);
        });
      }

      if (customElements.get('math-field')) {
        tryRender();
      } else {
        customElements.whenDefined('math-field').then(tryRender).catch(function(){});
        // Also schedule a retry as fallback
        setTimeout(tryRender, 800);
        setTimeout(tryRender, 2000);
      }
    }

    // Run on DOMContentLoaded and also immediately in case already loaded
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', renderEquations);
    } else {
      renderEquations();
    }
  })();
<\/script>
`;

export const ScaledSlidePreview = ({ html, title, className }: ScaledSlidePreviewProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(0.1);

  const updateScale = useCallback(() => {
    if (containerRef.current) {
      const containerWidth = containerRef.current.clientWidth;
      const containerHeight = containerRef.current.clientHeight;
      const newScale = Math.min(
        containerWidth / CANVAS_WIDTH,
        containerHeight / CANVAS_HEIGHT
      );
      setScale(newScale);
    }
  }, []);

  useEffect(() => {
    updateScale();
    
    const observer = new ResizeObserver(updateScale);
    if (containerRef.current) {
      observer.observe(containerRef.current);
    }
    
    return () => observer.disconnect();
  }, [updateScale]);

  // Replace viewport units with fixed pixel values
  const fixViewportUnits = (htmlContent: string): string => {
    let fixed = htmlContent;
    fixed = fixed.replace(/(\d+(?:\.\d+)?)\s*vw/gi, (_, num) =>
      `${(parseFloat(num) * CANVAS_WIDTH / 100).toFixed(2)}px`
    );
    fixed = fixed.replace(/(\d+(?:\.\d+)?)\s*vh/gi, (_, num) =>
      `${(parseFloat(num) * CANVAS_HEIGHT / 100).toFixed(2)}px`
    );
    fixed = fixed.replace(/(\d+(?:\.\d+)?)\s*vmin/gi, (_, num) =>
      `${(parseFloat(num) * Math.min(CANVAS_WIDTH, CANVAS_HEIGHT) / 100).toFixed(2)}px`
    );
    fixed = fixed.replace(/(\d+(?:\.\d+)?)\s*vmax/gi, (_, num) =>
      `${(parseFloat(num) * Math.max(CANVAS_WIDTH, CANVAS_HEIGHT) / 100).toFixed(2)}px`
    );
    return fixed;
  };

  // Process HTML to fix viewport units and add base styles + equation rendering
  const processHtml = (htmlContent: string): string => {
    let processed = fixViewportUnits(htmlContent);

    const baseInjection = `
      <style id="slide-base-styles">
        html, body {
          width: ${CANVAS_WIDTH}px !important;
          height: ${CANVAS_HEIGHT}px !important;
          margin: 0 !important;
          padding: 0 !important;
          overflow: hidden !important;
        }
        math-field {
          display: inline-block;
          vertical-align: middle;
          border: none;
          background: transparent;
          font-size: inherit;
          color: inherit;
          outline: none;
        }
        [data-type="equation"] {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 30px;
          overflow: visible;
          position: relative;
        }
        [data-type="equation"] math-field {
          width: fit-content;
          max-width: 100%;
        }
      </style>
      <script type="module">
        // Attempt to load MathLive from our local assets
        try {
          const ml = await import('/node_modules/mathlive/dist/mathlive.min.mjs');
          const absoluteFontsUrl = new URL('./fonts', document.baseURI).toString();
          if (ml && ml.setOptions) ml.setOptions({ fontsDirectory: absoluteFontsUrl });
          else if (window.MathLive && window.MathLive.setOptions) window.MathLive.setOptions({ fontsDirectory: absoluteFontsUrl });
        } catch(e) { 
          // Fallback to CDN if local fails
          try {
            const ml = await import('https://unpkg.com/mathlive@0.109.0/dist/mathlive.min.mjs');
            if (ml && ml.setOptions) ml.setOptions({ fontsDirectory: 'https://unpkg.com/mathlive@0.109.0/dist/fonts' });
          } catch(e2) { console.warn('MathLive load failed', e2); }
        }

        // After MathLive is loaded, apply read-only and fill structured equation divs
        function renderMath() {
          // 1. Structured equation divs without math-field yet
          document.querySelectorAll('[data-type="equation"]:not(:has(math-field))').forEach(function(node) {
            var latex = node.getAttribute('data-latex') || '';
            node.innerHTML = '';
            var mf = document.createElement('math-field');
            mf.setAttribute('read-only', 'true');
            mf.style.cssText = 'width:fit-content;max-width:100%;min-height:30px;border:none;background:transparent;font-size:inherit;color:inherit;outline:none;';
            mf.value = latex;
            node.appendChild(mf);
          });

          // 2. Make all math-fields read-only (including inline ones from LLM)
          document.querySelectorAll('math-field').forEach(function(mf) {
            mf.setAttribute('read-only', 'true');
          });
        }
        renderMath();
      <\/script>
      ${EQUATION_RENDER_SCRIPT}
    `;

    // Case 1: full HTML document — inject at START of <head>
    if (processed.includes('</head>')) {
      return processed.replace(/<head([^>]*)>/i, `<head$1>${baseInjection}`);
    }

    // Case 2: fragment that starts with <body
    if (processed.includes('<body')) {
      return processed.replace('<body', `${baseInjection}<body`);
    }

    // Case 3: fragment with <style> tags (CSS-preserved format from SlideCanvas.getHTML)
    const styleTagRegex = /<style[^>]*>[\s\S]*?<\/style>/gi;
    const styleTags = processed.match(styleTagRegex) ?? [];
    if (styleTags.length > 0) {
      const bodyContent = processed.replace(styleTagRegex, '').trim();
      const extractedStyles = styleTags.join('\n');
      return `<!DOCTYPE html><html><head>${baseInjection}${extractedStyles}</head><body>${bodyContent}</body></html>`;
    }

    // Case 4: plain fragment — wrap in full doc
    return `<!DOCTYPE html><html><head>${baseInjection}</head><body>${processed}</body></html>`;
  };

  const processedHtml = processHtml(html);

  const scaledWidth = CANVAS_WIDTH * scale;
  const scaledHeight = CANVAS_HEIGHT * scale;

  return (
    <div ref={containerRef} className={cn("relative overflow-hidden", className)}>
      <div className="absolute inset-0 flex items-center justify-center">
        <div
          style={{
            width: `${scaledWidth}px`,
            height: `${scaledHeight}px`,
            overflow: 'hidden',
            position: 'relative'
          }}
        >
          <iframe
            srcDoc={processedHtml}
            className="border-0 pointer-events-none"
            tabIndex={-1}
            style={{ 
              width: `${CANVAS_WIDTH}px`, 
              height: `${CANVAS_HEIGHT}px`,
              transform: `scale(${scale})`,
              transformOrigin: 'top left',
              position: 'absolute',
              top: 0,
              left: 0
            }}
            title={title}
            sandbox="allow-scripts"
          />
        </div>
      </div>
    </div>
  );
};
