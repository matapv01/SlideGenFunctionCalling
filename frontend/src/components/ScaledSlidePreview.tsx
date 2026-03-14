import { useState, useEffect, useRef, useCallback } from "react";
import { cn } from "@/lib/utils";

// Slide dimensions (16:9 aspect ratio)
const SLIDE_WIDTH = 1920;
const SLIDE_HEIGHT = 1080;

interface ScaledSlidePreviewProps {
  html: string;
  title: string;
  className?: string;
}

export const ScaledSlidePreview = ({ html, title, className }: ScaledSlidePreviewProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(0.1);

  const updateScale = useCallback(() => {
    if (containerRef.current) {
      const containerWidth = containerRef.current.clientWidth;
      const containerHeight = containerRef.current.clientHeight;
      const newScale = Math.min(
        containerWidth / SLIDE_WIDTH,
        containerHeight / SLIDE_HEIGHT
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
    
    // Replace vw units with pixel equivalents (1vw = 19.2px for 1920px width)
    fixed = fixed.replace(/(\d+(?:\.\d+)?)\s*vw/gi, (_, num) => {
      return `${(parseFloat(num) * SLIDE_WIDTH / 100).toFixed(2)}px`;
    });
    
    // Replace vh units with pixel equivalents (1vh = 10.8px for 1080px height)
    fixed = fixed.replace(/(\d+(?:\.\d+)?)\s*vh/gi, (_, num) => {
      return `${(parseFloat(num) * SLIDE_HEIGHT / 100).toFixed(2)}px`;
    });
    
    // Replace vmin with the smaller value
    fixed = fixed.replace(/(\d+(?:\.\d+)?)\s*vmin/gi, (_, num) => {
      const minDim = Math.min(SLIDE_WIDTH, SLIDE_HEIGHT);
      return `${(parseFloat(num) * minDim / 100).toFixed(2)}px`;
    });
    
    // Replace vmax with the larger value
    fixed = fixed.replace(/(\d+(?:\.\d+)?)\s*vmax/gi, (_, num) => {
      const maxDim = Math.max(SLIDE_WIDTH, SLIDE_HEIGHT);
      return `${(parseFloat(num) * maxDim / 100).toFixed(2)}px`;
    });
    
    return fixed;
  };

  // Process HTML to fix viewport units and add base styles
  const processHtml = (htmlContent: string): string => {
    let processed = fixViewportUnits(htmlContent);
    
    // Add base styles to ensure full dimensions
    const baseStyles = `
      <style id="slide-base-styles">
        html, body {
          width: ${SLIDE_WIDTH}px !important;
          height: ${SLIDE_HEIGHT}px !important;
          margin: 0 !important;
          padding: 0 !important;
          overflow: hidden !important;
        }
      </style>
    `;

    // Case 1: full HTML document — inject base styles at the START of <head>
    // so the slide's own styles (coming later) can correctly override defaults
    if (processed.includes('</head>')) {
      return processed.replace(/<head([^>]*)>/i, `<head$1>${baseStyles}`);
    }

    // Case 2: fragment that starts with <body — inject before body tag
    if (processed.includes('<body')) {
      return processed.replace('<body', `${baseStyles}<body`);
    }

    // Case 3: fragment with <style> tags (CSS-preserved format from SlideCanvas.getHTML)
    // Move style tags to <head> so they scope the full document properly
    const styleTagRegex = /<style[^>]*>[\s\S]*?<\/style>/gi;
    const styleTags = processed.match(styleTagRegex) ?? [];
    if (styleTags.length > 0) {
      const bodyContent = processed.replace(styleTagRegex, '').trim();
      const extractedStyles = styleTags.join('\n');
      return `<!DOCTYPE html><html><head>${baseStyles}${extractedStyles}</head><body>${bodyContent}</body></html>`;
    }

    // Case 4: plain fragment — wrap in full doc
    return `<!DOCTYPE html><html><head>${baseStyles}</head><body>${processed}</body></html>`;
  };

  const processedHtml = processHtml(html);

  // Calculate scaled dimensions to fit in container
  const scaledWidth = SLIDE_WIDTH * scale;
  const scaledHeight = SLIDE_HEIGHT * scale;

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
              width: `${SLIDE_WIDTH}px`, 
              height: `${SLIDE_HEIGHT}px`,
              transform: `scale(${scale})`,
              transformOrigin: 'top left',
              position: 'absolute',
              top: 0,
              left: 0
            }}
            title={title}
            sandbox="allow-same-origin allow-scripts"
          />
        </div>
      </div>
    </div>
  );
};

export { SLIDE_WIDTH, SLIDE_HEIGHT };
