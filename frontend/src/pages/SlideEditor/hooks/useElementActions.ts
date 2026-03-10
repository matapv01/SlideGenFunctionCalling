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
    const id = Date.now().toString();
    const maxZ = currentSlide.elements.length > 0
      ? Math.max(...currentSlide.elements.map(e => e.zIndex || 0))
      : 0;

    const defaults: Partial<SlideElement> = {
      id,
      x: dropX,
      y: dropY,
      width: 200,
      height: 100,
      rotation: 0,
      zIndex: maxZ + 1,
      opacity: 1,
      fillColor: item.type === "shape" ? "#e2e8f0" : "transparent",
      strokeColor: "transparent",
      strokeWidth: 0,
    };

    if (item.type === "text") {
      defaults.type = "text";
      defaults.content = item.subType === "heading" ? "Heading" : "Text block";
      defaults.fontSize = item.subType === "heading" ? 48 : 24;
      defaults.width = 400;
      defaults.height = item.subType === "heading" ? 60 : 40;
      defaults.color = "#000000";
    } else if (item.type === "shape") {
      defaults.type = "shape";
      if (item.subType === "circle") {
        defaults.borderRadius = 1000;
        defaults.width = 100;
        defaults.height = 100;
      }
    } else if (item.type === "image") {
      defaults.type = "image";
      defaults.src = "/placeholder.svg";
      defaults.width = 300;
      defaults.height = 200;
    }

    const newElement = { ...defaults } as SlideElement;
    setSlides(prev => prev.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      return { ...slide, elements: [...slide.elements, newElement] };
    }));
    setSelectedElementId(id);
  }, [currentSlide, currentSlideIndex, setSlides, setSelectedElementId]);

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
    setSlides(prev => prev.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      return { ...slide, elements: slide.elements.filter(el => el.id !== id) };
    }));
    setSelectedElementId(null);
  }, [currentSlideIndex, setSlides, setSelectedElementId]);

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
