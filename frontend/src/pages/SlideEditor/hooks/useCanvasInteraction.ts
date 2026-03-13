import { useCallback } from "react";
import type { Slide, SlideElement, DragItem } from "../types";

interface UseCanvasInteractionParams {
  currentSlide: Slide | undefined;
  currentSlideIndex: number;
  setSlides: React.Dispatch<React.SetStateAction<Slide[]>>;
  setSelectedElementId: React.Dispatch<React.SetStateAction<string | null>>;
  draggedItem: DragItem | null;
  setDraggedItem: React.Dispatch<React.SetStateAction<DragItem | null>>;
  zoom: number;
  addElement: (item: DragItem, dropX: number, dropY: number) => void;
  canvasRef: React.RefObject<HTMLDivElement>;
}

interface UseCanvasInteractionReturn {
  handleElementSelectFromCanvas: (elementData: any) => void;
  handleDrop: (e: React.DragEvent) => void;
}

/**
 * Hook để quản lý canvas interactions: selection, drag & drop
 */
export const useCanvasInteraction = ({
  currentSlide,
  currentSlideIndex,
  setSlides,
  setSelectedElementId,
  draggedItem,
  setDraggedItem,
  zoom,
  addElement,
  canvasRef
}: UseCanvasInteractionParams): UseCanvasInteractionReturn => {
  const toNumber = (value: unknown, fallback = 0): number => {
    if (typeof value === "number" && Number.isFinite(value)) return value;
    if (typeof value === "string") {
      const n = parseFloat(value);
      return Number.isFinite(n) ? n : fallback;
    }
    return fallback;
  };

  
  const handleElementSelectFromCanvas = useCallback((elementData: any) => {
    console.log('[SlideEditor] Element selected from canvas:', elementData);
    
    if (!elementData) {
      setSelectedElementId(null);
      return;
    }
    
    let matchingElement = currentSlide?.elements.find(el => el.id === elementData.id);

    // Update React state with latest data from Canvas
    if (matchingElement && elementData.style) {
      const updates: Partial<SlideElement> = {
        x: toNumber(elementData.style.left, matchingElement.x),
        y: toNumber(elementData.style.top, matchingElement.y),
        width: toNumber(elementData.style.width, matchingElement.width),
        height: toNumber(elementData.style.height, matchingElement.height),
        fontSize: toNumber(elementData.style.fontSize, matchingElement.fontSize),
        fontFamily: elementData.style.fontFamily || matchingElement.fontFamily,
        fontWeight: elementData.style.fontWeight || matchingElement.fontWeight,
        fontStyle: elementData.style.fontStyle || matchingElement.fontStyle,
        textDecoration: elementData.style.textDecoration || matchingElement.textDecoration,
        textAlign: (elementData.style.textAlign as "left" | "center" | "right") || matchingElement.textAlign,
        color: elementData.style.color || matchingElement.color,
        fillColor: elementData.style.backgroundColor || matchingElement.fillColor,
        content: elementData.content || elementData.innerHTML || matchingElement.content
      };

      setSlides(prev => prev.map((slide, i) => {
        if (i !== currentSlideIndex) return slide;
        return {
          ...slide,
          elements: slide.elements.map(el => 
            el.id === matchingElement!.id ? { ...el, ...updates } : el
          )
        };
      }));
      setSelectedElementId(matchingElement.id);
      return;
    }
    
    // Create new element if not found
    if (!matchingElement && elementData.style) {
      const elType = (elementData.dataType || 'shape') as SlideElement['type'];
      const newElement: SlideElement = {
        id: elementData.id,
        type: elType,
        content: elementData.content || elementData.innerHTML || elementData.textContent || "New Text",
        x: toNumber(elementData.style.left, 0),
        y: toNumber(elementData.style.top, 0),
        width: toNumber(elementData.style.width, 100),
        height: toNumber(elementData.style.height, 100),
        rotation: 0,
        zIndex: 1,
        opacity: 1,
        fontSize: toNumber(elementData.style.fontSize, 16),
        fontFamily: elementData.style.fontFamily || 'Inter',
        fontWeight: elementData.style.fontWeight || 'normal',
        fontStyle: elementData.style.fontStyle || 'normal',
        textDecoration: elementData.style.textDecoration || 'none',
        textAlign: elementData.style.textAlign as "left" | "center" | "right" || 'left',
        color: elementData.style.color || '#000000',
        fillColor: elementData.style.backgroundColor || 'transparent'
      };
      
      setSlides(prev => prev.map((slide, i) => {
        if (i !== currentSlideIndex) return slide;
        return { ...slide, elements: [...slide.elements, newElement] };
      }));
      matchingElement = newElement;
    }
    
    if (matchingElement) {
      setSelectedElementId(matchingElement.id);
    }
  }, [currentSlide, currentSlideIndex, setSlides, setSelectedElementId]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!draggedItem || !canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / zoom;
    const y = (e.clientY - rect.top) / zoom;

    addElement(draggedItem, x, y);
    setDraggedItem(null);
  }, [draggedItem, zoom, addElement, canvasRef, setDraggedItem]);

  return {
    handleElementSelectFromCanvas,
    handleDrop
  };
};
