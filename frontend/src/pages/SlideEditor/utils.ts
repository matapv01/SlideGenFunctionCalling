import type { SlideElement } from "./types";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "./constants";

// --- Helper: Convert px string to number ---
export const pxToNum = (val: string | null): number => 
  val ? parseFloat(val.replace("px", "")) : 0;

// --- Helper: Parse HTML to SlideElements ---
export const parseHtmlToElements = (html: string): { 
  elements: SlideElement[]; 
  backgroundColor: string; 
  defs?: string;
} => {
  // 1. Create a temporary hidden container to render HTML for accurate measurements
  const tempContainer = document.createElement('div');
  tempContainer.style.position = 'fixed';
  tempContainer.style.top = '-9999px';
  tempContainer.style.left = '-9999px';
  tempContainer.style.width = `${CANVAS_WIDTH}px`;
  tempContainer.style.height = `${CANVAS_HEIGHT}px`;
  tempContainer.style.visibility = 'hidden';
  tempContainer.innerHTML = html;
  
  document.body.appendChild(tempContainer);

  // 2. Extract background color
  let backgroundColor = "#ffffff";
  const computedBg = window.getComputedStyle(tempContainer).backgroundColor;
  if (computedBg && computedBg !== 'rgba(0, 0, 0, 0)' && computedBg !== 'transparent') {
    backgroundColor = computedBg;
  }
  
  // Check for background in child container
  const container = tempContainer.querySelector('.slide-container') as HTMLElement;
  if (container) {
    const containerBg = window.getComputedStyle(container).backgroundColor;
    if (containerBg && containerBg !== 'rgba(0, 0, 0, 0)' && containerBg !== 'transparent') {
      backgroundColor = containerBg;
    }
  }
  
  // 3. Extract SVG definitions (e.g., clipPaths)
  let defs = '';
  const svgElements = tempContainer.querySelectorAll('svg');
  svgElements.forEach(svg => {
    if (svg.querySelector('defs')) {
      defs += svg.outerHTML;
      svg.remove();
    }
  });

  const extractedElements: SlideElement[] = [];
  const tempRect = tempContainer.getBoundingClientRect();
  
  // 4. Get all child elements to convert to SlideElements
  const allElements = Array.from(tempContainer.querySelectorAll('*'));
  
  // Filter out non-visible structural elements
  const visibleElements = allElements.filter(el => {
    const element = el as HTMLElement;
    if (['SCRIPT', 'STYLE', 'LINK', 'META', 'HEAD'].includes(element.tagName)) return false;
    
    const computed = window.getComputedStyle(element);
    if (computed.display === 'none' || computed.visibility === 'hidden') return false;
    
    return true;
  });

  // Process elements with absolute positioning first
  const absoluteElements = visibleElements.filter(el => {
    const computed = window.getComputedStyle(el as HTMLElement);
    return computed.position === 'absolute' || computed.position === 'fixed';
  });

  if (absoluteElements.length > 0) {
    absoluteElements.forEach((el, idx) => {
      const element = el as HTMLElement;
      const computed = window.getComputedStyle(element);
      const tagName = element.tagName.toLowerCase();
      
      // --- Get accurate geometry using getBoundingClientRect ---
      const rect = element.getBoundingClientRect();
      const x = rect.left - tempRect.left;
      const y = rect.top - tempRect.top;
      const width = rect.width || 100;
      const height = rect.height || 100;

      const id = `el-${Date.now()}-${idx}`;
      const zIndex = parseInt(computed.zIndex) || (idx + 1);
      const opacity = parseFloat(computed.opacity) || 1;
      const borderRadius = parseFloat(computed.borderRadius) || 0;
      
      // Parse rotation from transform matrix
      let rotation = 0;
      if (computed.transform && computed.transform !== 'none') {
        const match = computed.transform.match(/rotate\(([^)]+)deg\)/);
        if (match && match[1]) {
          rotation = parseFloat(match[1]);
        }
      }
      
      // --- Type Detection ---

      // 1. Image (<img> tag)
      if (tagName === 'img') {
        extractedElements.push({
          id, type: 'image',
          src: (element as HTMLImageElement).src,
          x, y, width, height: height || 200,
          rotation, zIndex, opacity, borderRadius
        });
        return;
      }

      // 2. Background Image (div with background-image)
      const bgImage = computed.backgroundImage;
      if (bgImage && bgImage !== 'none' && bgImage.includes('url(')) {
        const urlMatch = bgImage.match(/url\(["']?([^"']*)["']?\)/);
        if (urlMatch && urlMatch[1]) {
          extractedElements.push({
            id, type: 'image',
            src: urlMatch[1],
            x, y, width, height,
            rotation, zIndex, opacity, borderRadius
          });
          return;
        }
      }

      // 3. Shape (Div with no text, but has bg color or border)
      const hasText = element.textContent && element.textContent.trim().length > 0;
      const bgColor = computed.backgroundColor;
      const hasBgColor = bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent';
      const borderWidth = parseFloat(computed.borderWidth);
      const hasBorder = borderWidth > 0;
      
      if (tagName === 'div' && !hasText && (hasBgColor || hasBorder)) {
        let subType = 'rectangle';
        if (computed.borderRadius === '50%' || borderRadius >= width / 2) {
          subType = 'circle';
        }

        extractedElements.push({
          id, type: 'shape', subType,
          x, y, width, height,
          rotation, zIndex, opacity,
          fillColor: bgColor || 'transparent',
          strokeColor: computed.borderColor || 'transparent',
          strokeWidth: borderWidth || 0,
          borderRadius: borderRadius || (subType === 'circle' ? 1000 : 0)
        });
        return;
      }

      // 4. Text (Fallback for everything else with content)
      const fontSize = parseFloat(computed.fontSize) || 24;
      const fontFamily = computed.fontFamily || 'Inter, sans-serif';
      const fontWeight = computed.fontWeight || 'normal';
      const textAlign = (computed.textAlign as "left" | "center" | "right") || 'left';
      const color = computed.color || '#000000';
      const lineHeight = computed.lineHeight || '1.2';
      const letterSpacing = computed.letterSpacing || 'normal';
      const clipPath = computed.clipPath && computed.clipPath !== 'none' ? computed.clipPath : undefined;

      extractedElements.push({
        id, type: 'text',
        content: element.innerHTML,
        x, y, width, height,
        rotation, zIndex, opacity,
        fontSize, fontFamily, fontWeight, textAlign, color,
        lineHeight, letterSpacing,
        clipPath
      });
    });
  } else {
    // Fallback: Process elements based on content flow
    const contentNodes = Array.from(tempContainer.querySelectorAll('h1, h2, h3, p, ul, ol, img, div'));
    
    contentNodes.forEach((node, idx) => {
      const element = node as HTMLElement;
      const tagName = element.tagName.toLowerCase();
      const computed = window.getComputedStyle(element);
      
      // Skip if already processed or empty
      if (computed.display === 'none' || computed.visibility === 'hidden') return;
      if (tagName !== 'img' && !element.textContent?.trim()) return;

      const rect = element.getBoundingClientRect();
      const x = rect.left - tempRect.left;
      const y = rect.top - tempRect.top;
      const width = rect.width || 100;
      const height = rect.height || 50;

      if (tagName === 'img') {
        extractedElements.push({
          id: `img-${Date.now()}-${idx}`,
          type: 'image',
          src: (element as HTMLImageElement).src,
          x, y,
          width: width || 600,
          height: height || 400,
          rotation: 0, zIndex: idx + 1, opacity: 1,
          borderRadius: parseFloat(computed.borderRadius) || 0
        });
      } else {
        // Text element
        const fontSize = parseFloat(computed.fontSize) || 24;
        const fontWeight = computed.fontWeight || 'normal';
        const textAlign = (computed.textAlign as "left" | "center" | "right") || 'left';
        const color = computed.color || '#000000';

        extractedElements.push({
          id: `text-${Date.now()}-${idx}`,
          type: 'text',
          content: element.innerHTML,
          x, y, width, height,
          rotation: 0, zIndex: idx + 1, opacity: 1,
          fontSize, fontWeight, textAlign, color,
          fontFamily: computed.fontFamily || 'Inter, sans-serif',
          lineHeight: computed.lineHeight || '1.2',
          letterSpacing: computed.letterSpacing || 'normal'
        });
      }
    });

    // Final fallback if no elements found
    if (extractedElements.length === 0 && tempContainer.textContent?.trim()) {
      extractedElements.push({
        id: `text-${Date.now()}-fallback`,
        type: 'text',
        content: tempContainer.innerHTML,
        x: 100, y: 100,
        width: CANVAS_WIDTH - 200,
        height: CANVAS_HEIGHT - 200,
        rotation: 0, zIndex: 1, opacity: 1,
        fontSize: 24,
        fontWeight: 'normal',
        textAlign: 'left',
        color: '#000000'
      });
    }
  }

  // 5. Cleanup: Remove temporary container
  document.body.removeChild(tempContainer);

  return { elements: extractedElements, backgroundColor, defs: defs || undefined };
};
