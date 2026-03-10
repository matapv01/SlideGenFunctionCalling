import { useCallback } from "react";
import type { Slide, SlideElement, DragItem } from "../types";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";

interface UseElementActionsParams {
  currentSlide: Slide;
  currentSlideIndex: number;
  setSlides: React.Dispatch<React.SetStateAction<Slide[]>>;
  setSelectedElementId: React.Dispatch<React.SetStateAction<string | null>>;
  slideCanvasRef: React.RefObject<SlideCanvasHandle>;
}

interface UseElementActionsReturn {
  addElement: (item: DragItem, dropX: number, dropY: number) => void;
  updateElement: (id: string, updates: Partial<SlideElement>) => void;
  deleteElement: (id: string) => void;
  bringForward: (id: string) => void;
  sendBackward: (id: string) => void;
}

/**
 * Hook để quản lý CRUD operations cho elements trong slide
 */
export const useElementActions = ({
  currentSlide,
  currentSlideIndex,
  setSlides,
  setSelectedElementId,
  slideCanvasRef
}: UseElementActionsParams): UseElementActionsReturn => {
  
  const addElement = useCallback((item: DragItem, dropX: number, dropY: number) => {
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

  const updateElement = useCallback((id: string, updates: Partial<SlideElement>) => {
    // Update React state
    setSlides(prev => prev.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      return {
        ...slide,
        elements: slide.elements.map(el => el.id === id ? { ...el, ...updates } : el)
      };
    }));
    
    // Update Shadow DOM
    if (slideCanvasRef.current) {
      const styleUpdates: Record<string, string> = {};
      
      if (updates.x !== undefined) styleUpdates.left = `${updates.x}px`;
      if (updates.y !== undefined) styleUpdates.top = `${updates.y}px`;
      if (updates.width !== undefined) styleUpdates.width = `${updates.width}px`;
      if (updates.height !== undefined) styleUpdates.height = `${updates.height}px`;
      if (updates.color !== undefined) styleUpdates.color = updates.color;
      if (updates.fontSize !== undefined) styleUpdates.fontSize = `${updates.fontSize}px`;
      if (updates.fontWeight !== undefined) styleUpdates.fontWeight = updates.fontWeight;
      if (updates.fontStyle !== undefined) styleUpdates.fontStyle = updates.fontStyle;
      if (updates.textDecoration !== undefined) styleUpdates.textDecoration = updates.textDecoration;
      if (updates.textAlign !== undefined) styleUpdates.textAlign = updates.textAlign;
      if (updates.fillColor !== undefined) styleUpdates.backgroundColor = updates.fillColor;
      if (updates.fontFamily !== undefined) styleUpdates.fontFamily = updates.fontFamily;
      if (updates.content !== undefined) styleUpdates.innerHTML = updates.content;
      
      slideCanvasRef.current.updateElement(styleUpdates);
    }
  }, [currentSlideIndex, setSlides, slideCanvasRef]);

  const deleteElement = useCallback((id: string) => {
    setSlides(prev => prev.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      return { ...slide, elements: slide.elements.filter(el => el.id !== id) };
    }));
    setSelectedElementId(null);
  }, [currentSlideIndex, setSlides, setSelectedElementId]);

  const bringForward = useCallback((id: string) => {
    // TODO: Implement z-index increase
  }, []);

  const sendBackward = useCallback((id: string) => {
    // TODO: Implement z-index decrease
  }, []);

  return {
    addElement,
    updateElement,
    deleteElement,
    bringForward,
    sendBackward
  };
};
