import { useCallback } from "react";
import type { Slide, SlideElement, DragItem } from "../types";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";

interface UseElementActionsParams {
  currentSlide: Slide | undefined;
  currentSlideIndex: number;
  setSlides: React.Dispatch<React.SetStateAction<Slide[]>>;
  setSelectedElementId: React.Dispatch<React.SetStateAction<string | null>>;
  slideCanvasRef: React.RefObject<SlideCanvasHandle>;
}

interface UseElementActionsReturn {
  addElement: (item: DragItem, dropX: number, dropY: number) => void;
  updateElement: (id: string, updates: Partial<SlideElement> & { _filter?: string }) => void;
  deleteElement: (id: string) => void;
  duplicateElement: (id: string) => void;
  bringForward: (id: string) => void;
  sendBackward: (id: string) => void;
}

/**
 * Hook to manage CRUD and reorder operations for elements within a slide.
 * Syncs both React state and the live Shadow DOM canvas.
 */
export const useElementActions = ({
  currentSlide,
  currentSlideIndex,
  setSlides,
  setSelectedElementId,
  slideCanvasRef,
}: UseElementActionsParams): UseElementActionsReturn => {

  const addElement = useCallback((item: DragItem, dropX: number, dropY: number) => {
    if (!currentSlide) return;

    const id = `el_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
    const x = Math.round(dropX);
    const y = Math.round(dropY);

    // ── Build the HTML fragment that will be injected into the canvas ──────
    // injectElement() will compute maxZIndex from the live canvas and apply +1
    let html = '';

    if (item.type === 'text') {
      let fontSize = 28, fontWeight = 'normal', content = 'Click to edit';
      let width = 500, height = 48, color = '#222222';
      if (item.subType === 'heading') {
        fontSize = 64; fontWeight = 'bold'; content = 'Heading'; width = 600; height = 80; color = '#111111';
      } else if (item.subType === 'subheading') {
        fontSize = 40; fontWeight = '600'; content = 'Subheading'; width = 500; height = 60; color = '#333333';
      } else if (item.subType === 'label') {
        fontSize = 20; fontWeight = '600'; content = 'Label'; width = 200; height = 32; color = '#555555';
      }
      html = `<div id="${id}" class="element" data-type="text" data-selectable="true" contenteditable="true"
        style="position:absolute;left:${x}px;top:${y}px;width:${width}px;height:${height}px;font-size:${fontSize}px;font-weight:${fontWeight};color:${color};cursor:move;user-select:none;"
        >${content}</div>`;

    } else if (item.type === 'shape') {
      let width = 200, height = 120, bg = '#e2e8f0', extra = '';
      if (item.subType === 'circle') {
        width = 150; height = 150; extra = 'border-radius:50%;';
      } else if (item.subType === 'triangle') {
        width = 150; height = 150; extra = 'clip-path:polygon(50% 0%,0% 100%,100% 100%);';
      } else if (item.subType === 'star') {
        width = 150; height = 150; extra = 'clip-path:polygon(50% 0%,61% 35%,98% 35%,68% 57%,79% 91%,50% 70%,21% 91%,32% 57%,2% 35%,39% 35%);';
      } else if (item.subType === 'diamond') {
        width = 120; height = 120; extra = 'clip-path:polygon(50% 0%,100% 50%,50% 100%,0% 50%);';
      } else if (item.subType === 'line') {
        width = 300; height = 4; bg = '#555555'; extra = 'border-radius:2px;';
      }
      html = `<div id="${id}" class="element" data-type="shape" data-selectable="true"
        style="position:absolute;left:${x}px;top:${y}px;width:${width}px;height:${height}px;background:${bg};${extra}cursor:move;"
        ></div>`;

    } else if (item.type === 'image') {
      html = `<img id="${id}" class="element" data-type="image" data-selectable="true"
        style="position:absolute;left:${x}px;top:${y}px;width:400px;height:280px;object-fit:cover;cursor:move;"
        src="/placeholder.svg" alt="Image" />`;

    } else if (item.type === 'video') {
      html = `<div id="${id}" class="element" data-type="video" data-selectable="true"
        style="position:absolute;left:${x}px;top:${y}px;width:480px;height:270px;background:#000;cursor:move;display:flex;align-items:center;justify-content:center;color:#fff;font-size:14px;"
        >Video</div>`;
    }

    if (!html) return;

    // ── Inject into live canvas (handles maxZ+1 z-index automatically) ──────
    slideCanvasRef.current?.injectElement(html);
    // canvas's selectElement → onElementSelect → handleElementSelectFromCanvas
    // will create the React state entry — just pre-select the id here
    setSelectedElementId(id);
  }, [currentSlide, slideCanvasRef, setSelectedElementId]);

  const updateElement = useCallback((id: string, updates: Partial<SlideElement> & { _filter?: string }) => {
    // Sync React state
    setSlides(prev => prev.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      return {
        ...slide,
        elements: slide.elements.map(el => el.id === id ? { ...el, ...updates } : el),
      };
    }));

    // Sync Shadow DOM canvas
    if (slideCanvasRef.current) {
      const s: Record<string, string> = {};

      // Layout
      if (updates.x !== undefined) s.left = `${updates.x}px`;
      if (updates.y !== undefined) s.top = `${updates.y}px`;
      if (updates.width !== undefined) s.width = `${updates.width}px`;
      if (updates.height !== undefined) s.height = `${updates.height}px`;
      if (updates.rotation !== undefined) s.transform = `rotate(${updates.rotation}deg)`;
      if (updates.opacity !== undefined) s.opacity = `${updates.opacity}`;
      if (updates.zIndex !== undefined) s.zIndex = `${updates.zIndex}`;

      // Typography
      if (updates.color !== undefined) s.color = updates.color;
      if (updates.fontSize !== undefined) s.fontSize = `${updates.fontSize}px`;
      if (updates.fontWeight !== undefined) s.fontWeight = updates.fontWeight;
      if (updates.fontStyle !== undefined) s.fontStyle = updates.fontStyle;
      if (updates.textDecoration !== undefined) s.textDecoration = updates.textDecoration;
      if (updates.textAlign !== undefined) s.textAlign = updates.textAlign;
      if (updates.fontFamily !== undefined) s.fontFamily = updates.fontFamily;
      if (updates.lineHeight !== undefined) s.lineHeight = updates.lineHeight;
      if (updates.letterSpacing !== undefined) s.letterSpacing = updates.letterSpacing ?? '';

      // Appearance
      if (updates.fillColor !== undefined) s.backgroundColor = updates.fillColor;
      if (updates.strokeColor !== undefined) s.borderColor = updates.strokeColor;
      if (updates.strokeWidth !== undefined) s.borderWidth = `${updates.strokeWidth}px`;
      if (updates.strokeStyle !== undefined) s.borderStyle = updates.strokeStyle;
      if (updates.borderRadius !== undefined) s.borderRadius = `${updates.borderRadius}px`;
      if (updates.shadow !== undefined) s.boxShadow = updates.shadow;

      // Padding
      if (updates.paddingTop !== undefined) s.paddingTop = `${updates.paddingTop}px`;
      if (updates.paddingRight !== undefined) s.paddingRight = `${updates.paddingRight}px`;
      if (updates.paddingBottom !== undefined) s.paddingBottom = `${updates.paddingBottom}px`;
      if (updates.paddingLeft !== undefined) s.paddingLeft = `${updates.paddingLeft}px`;

      // Content / Filter
      if (updates.content !== undefined) s.innerHTML = updates.content;
      if (updates._filter !== undefined) s.filter = updates._filter;

      slideCanvasRef.current.updateElement(s);
    }
  }, [currentSlideIndex, setSlides, slideCanvasRef]);

  const deleteElement = useCallback((id: string) => {
    // Sync Shadow DOM canvas first
    if (slideCanvasRef.current) {
      slideCanvasRef.current.deleteElement();
    }
    
    // Sync React state
    setSlides(prev => prev.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      return { ...slide, elements: slide.elements.filter(el => el.id !== id) };
    }));
    setSelectedElementId(null);
  }, [currentSlideIndex, setSlides, setSelectedElementId, slideCanvasRef]);

  const duplicateElement = useCallback((id: string) => {
    setSlides(prev => prev.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      const el = slide.elements.find(e => e.id === id);
      if (!el) return slide;
      const clone: SlideElement = { ...el, id: `element-${Date.now()}`, x: el.x + 20, y: el.y + 20 };
      return { ...slide, elements: [...slide.elements, clone] };
    }));
  }, [currentSlideIndex, setSlides]);

  const bringForward = useCallback((id: string) => {
    setSlides(prev => prev.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      return {
        ...slide,
        elements: slide.elements.map(el =>
          el.id === id ? { ...el, zIndex: (el.zIndex || 0) + 1 } : el
        ),
      };
    }));
    if (slideCanvasRef.current) {
      const current = slideCanvasRef.current.getSelectedZIndex?.() ?? 0;
      slideCanvasRef.current.updateElement({ zIndex: `${current + 1}` });
    }
  }, [currentSlideIndex, setSlides, slideCanvasRef]);

  const sendBackward = useCallback((id: string) => {
    setSlides(prev => prev.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      return {
        ...slide,
        elements: slide.elements.map(el =>
          el.id === id ? { ...el, zIndex: Math.max(0, (el.zIndex || 0) - 1) } : el
        ),
      };
    }));
    if (slideCanvasRef.current) {
      const current = slideCanvasRef.current.getSelectedZIndex?.() ?? 1;
      slideCanvasRef.current.updateElement({ zIndex: `${Math.max(0, current - 1)}` });
    }
  }, [currentSlideIndex, setSlides, slideCanvasRef]);

  return { addElement, updateElement, deleteElement, duplicateElement, bringForward, sendBackward };
};
