import { useCallback } from "react";
import { api } from "@/lib/api";
import type { Slide, SlideElement } from "../types";

interface UseSlideActionsParams {
  slides: Slide[];
  setSlides: React.Dispatch<React.SetStateAction<Slide[]>>;
  currentSlideIndex: number;
  setCurrentSlideIndex: React.Dispatch<React.SetStateAction<number>>;
  projectId: string | undefined;
}

interface UseSlideActionsReturn {
  addSlide: () => Promise<void>;
  addSlideFromTemplate: (layout: string) => Promise<void>;
  deleteSlide: (index: number) => void;
  duplicateSlide: (index: number) => void;
  reorderSlides: (fromIndex: number, toIndex: number) => void;
}

function getTemplateHTML(layout: string): string {
  const el = (style: string, content: string, type = "text") =>
    `<div data-type="${type}" data-selectable="true"${type === "text" ? ' contenteditable="true"' : ''} class="element" style="${style}">${content}</div>`;

  const titleStyle = "position:absolute;left:80px;top:60px;width:1760px;height:110px;font-size:72px;font-weight:bold;color:#111111;text-align:left;cursor:move;line-height:1.3;outline:none;";
  const title = el(titleStyle, "Slide Title");

  if (layout === "blank") return "";

  if (layout === "title") {
    return (
      el("position:absolute;left:200px;top:360px;width:1520px;height:140px;font-size:90px;font-weight:bold;color:#111111;text-align:center;cursor:move;line-height:1.2;outline:none;", "Slide Title") +
      el("position:absolute;left:400px;top:520px;width:1120px;height:80px;font-size:48px;color:#666666;text-align:center;cursor:move;line-height:1.4;outline:none;", "Click to add subtitle")
    );
  }

  if (layout === "content") {
    return (
      title +
      el("position:absolute;left:80px;top:220px;width:1760px;height:760px;font-size:40px;color:#333333;text-align:left;cursor:move;line-height:1.6;outline:none;", "Click to add content here…")
    );
  }

  if (layout === "two-col") {
    return (
      title +
      el("position:absolute;left:80px;top:220px;width:860px;height:760px;font-size:36px;color:#333333;text-align:left;cursor:move;line-height:1.6;outline:none;", "Left column content…") +
      el("position:absolute;left:980px;top:220px;width:860px;height:760px;font-size:36px;color:#333333;text-align:left;cursor:move;line-height:1.6;outline:none;", "Right column content…")
    );
  }

  if (layout === "image-left") {
    return (
      title +
      el("position:absolute;left:80px;top:220px;width:800px;height:760px;background:#e8edf5;border-radius:8px;cursor:move;display:flex;align-items:center;justify-content:center;color:#9aabbd;font-size:40px;font-family:sans-serif;", "Image", "shape") +
      el("position:absolute;left:940px;top:220px;width:900px;height:760px;font-size:36px;color:#333333;text-align:left;cursor:move;line-height:1.6;outline:none;", "Click to add text here…")
    );
  }

  if (layout === "bullets") {
    return (
      title +
      el("position:absolute;left:80px;top:220px;width:1760px;height:760px;font-size:48px;color:#333333;text-align:left;cursor:move;line-height:1.8;outline:none;", "• First bullet point<br>• Second bullet point<br>• Third bullet point<br>• Fourth bullet point")
    );
  }

  return "";
}

/**
 * Hook để quản lý CRUD operations cho slides
 */
export const useSlideActions = ({
  slides,
  setSlides,
  currentSlideIndex,
  setCurrentSlideIndex,
  projectId,
}: UseSlideActionsParams): UseSlideActionsReturn => {
  
  const addSlide = useCallback(async () => {
    const tempId = `temp_${Date.now()}`;
    const newSlide: Slide = { id: tempId, elements: [], backgroundColor: "#ffffff" };
    // Optimistic update
    setSlides(prev => [...prev, newSlide]);
    setCurrentSlideIndex(slides.length);
    // Persist to server
    if (projectId) {
      try {
        const res = await api.createSlide(projectId, {
          slide_index: slides.length,
          slide_type: "custom",
          html_content: "",
          design_settings: { elements: [], backgroundColor: "#ffffff" },
        });
        // Replace temp ID with real server ID
        setSlides(prev => prev.map(s => s.id === tempId ? { ...s, id: String(res.id) } : s));
      } catch (e) {
        console.error("❌ [addSlide] Failed to persist slide:", e);
      }
    }
  }, [slides.length, setSlides, setCurrentSlideIndex, projectId]);

  const addSlideFromTemplate = useCallback(async (layout: string) => {
    const html = getTemplateHTML(layout);
    const elements: SlideElement[] = html
      ? [{
          id: Date.now().toString(),
          type: "text",
          content: html,
          x: 0, y: 0, width: 1920, height: 1080,
          rotation: 0, zIndex: 1, opacity: 1,
        }]
      : [];
    const tempId = `temp_${Date.now()}`;
    const newSlide: Slide = { id: tempId, elements, backgroundColor: "#ffffff" };
    // Optimistic update
    setSlides(prev => [...prev, newSlide]);
    setCurrentSlideIndex(slides.length);
    // Persist to server
    if (projectId) {
      try {
        const res = await api.createSlide(projectId, {
          slide_index: slides.length,
          slide_type: "custom",
          html_content: html,
          design_settings: { elements, backgroundColor: "#ffffff" },
        });
        setSlides(prev => prev.map(s => s.id === tempId ? { ...s, id: String(res.id) } : s));
      } catch (e) {
        console.error("❌ [addSlideFromTemplate] Failed to persist slide:", e);
      }
    }
  }, [slides.length, setSlides, setCurrentSlideIndex, projectId]);

  const deleteSlide = useCallback((index: number) => {
    if (slides.length <= 1) return;
    const slideId = slides[index].id;
    // Persist deletion to server (fire-and-forget)
    api.deleteSlide(slideId).catch(e => console.error("❌ [deleteSlide]", e));
    setSlides(prev => prev.filter((_, i) => i !== index));
    if (currentSlideIndex >= index && currentSlideIndex > 0) {
      setCurrentSlideIndex(prev => prev - 1);
    }
  }, [slides, currentSlideIndex, setSlides, setCurrentSlideIndex]);

  const duplicateSlide = useCallback((index: number) => {
    const slideToDup = slides[index];
    const elementsCopy = slideToDup.elements.map(el => ({ 
      ...el, 
      id: Date.now().toString() + Math.random() 
    }));
    const newSlide = { ...slideToDup, id: Date.now().toString(), elements: elementsCopy };
    setSlides(prev => {
      const newSlides = [...prev];
      newSlides.splice(index + 1, 0, newSlide);
      return newSlides;
    });
  }, [slides, setSlides]);

  const reorderSlides = useCallback((fromIndex: number, toIndex: number) => {
    if (fromIndex === toIndex) return;
    setSlides(prev => {
      const next = [...prev];
      const [moved] = next.splice(fromIndex, 1);
      next.splice(toIndex, 0, moved);
      // Persist new slide_index for each slide (fire-and-forget)
      next.forEach((slide, idx) => {
        api.updateSlide(slide.id, { slide_index: idx }).catch(() => {});
      });
      return next;
    });
    // Keep currentSlideIndex tracking the moved slide
    setCurrentSlideIndex(toIndex);
  }, [setSlides, setCurrentSlideIndex]);

  return {
    addSlide,
    addSlideFromTemplate,
    deleteSlide,
    duplicateSlide,
    reorderSlides,
  };
};
