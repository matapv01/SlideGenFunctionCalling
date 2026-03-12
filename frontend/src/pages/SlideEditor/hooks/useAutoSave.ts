import { useState, useEffect, useRef, useCallback } from "react";
import { api } from "@/lib/api";
import type { Slide } from "../types";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";

interface PendingSaveData {
  slideId: string;
  canvasHTML: string;
  elements: Slide['elements'];
  backgroundColor: string | undefined;
  backgroundImage: string | undefined;
  defs: any;
}

interface UseAutoSaveParams {
  currentSlide: Slide | undefined;
  setSlides: React.Dispatch<React.SetStateAction<Slide[]>>;
  slideCanvasRef: React.RefObject<SlideCanvasHandle>;
}

interface UseAutoSaveReturn {
  handleSave: () => Promise<void>;
  handleCanvasChange: () => void;
  flushSave: () => Promise<void>;
  hasUnsavedChanges: boolean;
  setHasUnsavedChanges: (value: boolean) => void;
}

// KEY INSIGHT: capture canvas HTML immediately on change (not when the debounce timer fires).
// This prevents the race condition where switching slides changes slideCanvasRef.current
// BEFORE the debounce timer fires, causing wrong HTML to be saved to the wrong slide.

export const useAutoSave = ({
  currentSlide,
  setSlides,
  slideCanvasRef
}: UseAutoSaveParams): UseAutoSaveReturn => {
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);
  // Pending captured data — populated immediately on canvas change, before any slide switch
  const pendingSaveRef = useRef<PendingSaveData | null>(null);

  useEffect(() => {
    return () => {
      if (autoSaveTimerRef.current) clearTimeout(autoSaveTimerRef.current);
    };
  }, []);

  /**
   * Core save executor — uses supplied data so it is immune to stale closures.
   */
  const executeSave = useCallback(async (data: PendingSaveData) => {
    const { slideId, canvasHTML, elements, backgroundColor, backgroundImage, defs } = data;

    console.log('💾 [SAVE] Saving slide:', slideId);

    const elementsToSave = elements.length > 0
      ? elements.map((el, idx) => idx === 0 ? { ...el, content: canvasHTML } : el)
      : canvasHTML
        ? [{ id: `canvas-${slideId}`, type: 'text' as const, content: canvasHTML,
             x: 0, y: 0, width: 1920, height: 1080, rotation: 0, zIndex: 1, opacity: 1 }]
        : [];

    const titleElement = elements.find(el => el.type === 'text' && el.fontSize && el.fontSize > 30);
    const contentText = titleElement?.content || 'Slide Content';

    try {
      await api.updateSlide(slideId, {
        design_settings: {
          elements: elementsToSave,
          backgroundColor,
          backgroundImage,
          defs,
        },
        html_content: canvasHTML,
        content_text: contentText,
      });

      console.log('✅ [SAVE] Saved slide:', slideId);

      setSlides(prevSlides =>
        prevSlides.map(slide => {
          if (slide.id !== slideId) return slide;
          if (slide.elements.length === 0) {
            return {
              ...slide,
              elements: canvasHTML
                ? [{ id: `canvas-${slideId}`, type: 'text' as const, content: canvasHTML,
                     x: 0, y: 0, width: 1920, height: 1080, rotation: 0, zIndex: 1, opacity: 1 }]
                : [],
            };
          }
          return {
            ...slide,
            elements: slide.elements.map((el, idx) =>
              idx === 0 ? { ...el, content: canvasHTML } : el
            ),
          };
        })
      );

      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('❌ [SAVE] Failed to save:', error);
    }
  }, [setSlides]);

  /**
   * Flush any pending save immediately (e.g. before switching slides).
   * Cancels the debounce timer and saves right now.
   */
  const flushSave = useCallback(async () => {
    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current);
      autoSaveTimerRef.current = null;
    }
    if (pendingSaveRef.current) {
      const data = pendingSaveRef.current;
      pendingSaveRef.current = null;
      await executeSave(data);
    }
  }, [executeSave]);

  /**
   * Manual save (Ctrl+S / toolbar) — captures fresh HTML from current canvas.
   */
  const handleSave = useCallback(async () => {
    if (!currentSlide) return;

    // Cancel any pending debounced save
    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current);
      autoSaveTimerRef.current = null;
    }
    pendingSaveRef.current = null;

    let canvasHTML = '';
    try {
      canvasHTML = slideCanvasRef.current?.getHTML() ?? '';
    } catch (e) {
      canvasHTML = currentSlide.elements[0]?.content || '';
    }
    if (!canvasHTML) canvasHTML = currentSlide.elements[0]?.content || '';

    await executeSave({
      slideId: currentSlide.id,
      canvasHTML,
      elements: currentSlide.elements,
      backgroundColor: currentSlide.backgroundColor,
      backgroundImage: currentSlide.backgroundImage,
      defs: currentSlide.defs,
    });
  }, [currentSlide, slideCanvasRef, executeSave]);

  /**
   * Called by SlideCanvas onChange — capture HTML immediately so the correct
   * canvas content is stored BEFORE the user can switch slides.
   * Only the API call is debounced, NOT the data capture.
   */
  const handleCanvasChange = useCallback(() => {
    if (!currentSlide) return;

    setHasUnsavedChanges(true);

    // 🔑 Capture HTML right now while the canvas is still for THIS slide
    let canvasHTML = '';
    try {
      canvasHTML = slideCanvasRef.current?.getHTML() ?? '';
    } catch (e) {
      canvasHTML = currentSlide.elements[0]?.content || '';
    }
    if (!canvasHTML) canvasHTML = currentSlide.elements[0]?.content || '';

    pendingSaveRef.current = {
      slideId: currentSlide.id,
      canvasHTML,
      elements: currentSlide.elements,
      backgroundColor: currentSlide.backgroundColor,
      backgroundImage: currentSlide.backgroundImage,
      defs: currentSlide.defs,
    };

    console.log('🔄 [AUTO-SAVE] Captured HTML for slide:', currentSlide.id, '— scheduling save...');

    // Debounce only the API call
    if (autoSaveTimerRef.current) clearTimeout(autoSaveTimerRef.current);
    autoSaveTimerRef.current = setTimeout(async () => {
      const data = pendingSaveRef.current;
      if (!data) return;
      pendingSaveRef.current = null;
      await executeSave(data);
    }, 600);
  }, [currentSlide, slideCanvasRef, executeSave]);

  return {
    handleSave,
    handleCanvasChange,
    flushSave,
    hasUnsavedChanges,
    setHasUnsavedChanges,
  };
};
