import { useState, useEffect, useRef, useCallback } from "react";
import { api } from "@/lib/api";
import type { Slide, SlideElement } from "../types";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";

interface UseAutoSaveParams {
  currentSlide: Slide | undefined;
  setSlides: React.Dispatch<React.SetStateAction<Slide[]>>;
  slideCanvasRef: React.RefObject<SlideCanvasHandle>;
}

interface UseAutoSaveReturn {
  handleSave: () => Promise<void>;
  handleCanvasChange: () => void;
  hasUnsavedChanges: boolean;
  setHasUnsavedChanges: (value: boolean) => void;
}

// Webfix approach: canvas.innerHTML is the source of truth.
// Update elements[0].content with new HTML — no re-parsing, no new IDs, no duplicates.

/**
 * Hook tối ưu cho auto-save với debounce
 */
export const useAutoSave = ({
  currentSlide,
  setSlides,
  slideCanvasRef
}: UseAutoSaveParams): UseAutoSaveReturn => {
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current);
      }
    };
  }, []);

  /**
   * Save handler - Optimized to avoid duplicates
   */
  const handleSave = useCallback(async () => {
    if (!currentSlide) return;

    console.log('💾 [SAVE] Starting save for slide:', currentSlide.id);

    // 1. Get latest canvas HTML (webfix: currentSlide.content = canvas.innerHTML)
    let canvasHTML = '';
    if (slideCanvasRef.current) {
      try {
        canvasHTML = slideCanvasRef.current.getHTML();
      } catch (e) {
        console.error('❌ [SAVE] Failed to get HTML:', e);
        canvasHTML = currentSlide.elements[0]?.content || '';
      }
    } else {
      canvasHTML = currentSlide.elements[0]?.content || '';
    }

    const backgroundColorToSave = currentSlide.backgroundColor;
    const defsToSave = currentSlide.defs;
    const slideId = currentSlide.id;

    // Snapshot content text for the API from current (possibly stale) state — acceptable
    const titleElement = currentSlide.elements.find(
      (el) => el.type === 'text' && el.fontSize && el.fontSize > 30
    );
    const contentText = titleElement?.content || 'Slide Content';

    try {
      const designSettings = {
        elements: currentSlide.elements.map((el, idx) => idx === 0 ? { ...el, content: canvasHTML } : el),
        backgroundColor: backgroundColorToSave,
        backgroundImage: currentSlide.backgroundImage,
        defs: defsToSave,
      };

      await api.updateSlide(slideId, {
        design_settings: designSettings,
        html_content: canvasHTML,
        content_text: contentText,
      });

      console.log('✅ [AUTO-SAVE] Saved slide:', slideId);

      // 2. Sync React state — update elements[0].content using the functional updater
      // so we ALWAYS use the latest elements list (prevents erasing dynamically-added elements)
      const capturedHTML = canvasHTML;
      setSlides((prevSlides) =>
        prevSlides.map((slide) => {
          if (slide.id !== slideId) return slide;
          return {
            ...slide,
            elements: slide.elements.map((el, idx) =>
              idx === 0 ? { ...el, content: capturedHTML } : el
            ),
          };
        })
      );

      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('❌ [SAVE] Failed to save:', error);
    }
  }, [currentSlide, setSlides, slideCanvasRef]);

  /**
   * Canvas change handler - Debounced auto-save
   */
  const handleCanvasChange = useCallback(() => {
    console.log('🔄 [AUTO-SAVE] Canvas changed, scheduling save...');
    setHasUnsavedChanges(true);

    // Clear existing timer
    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current);
    }

    // Start new timer (1 second debounce)
    autoSaveTimerRef.current = setTimeout(() => {
      console.log('💾 [AUTO-SAVE] Executing auto-save...');
      handleSave();
    }, 1000);
  }, [handleSave]);

  return {
    handleSave,
    handleCanvasChange,
    hasUnsavedChanges,
    setHasUnsavedChanges,
  };
};
