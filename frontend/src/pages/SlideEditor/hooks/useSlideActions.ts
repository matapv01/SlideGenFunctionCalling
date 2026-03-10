import { useCallback } from "react";
import type { Slide } from "../types";

interface UseSlideActionsParams {
  slides: Slide[];
  setSlides: React.Dispatch<React.SetStateAction<Slide[]>>;
  currentSlideIndex: number;
  setCurrentSlideIndex: React.Dispatch<React.SetStateAction<number>>;
}

interface UseSlideActionsReturn {
  addSlide: () => void;
  deleteSlide: (index: number) => void;
  duplicateSlide: (index: number) => void;
}

/**
 * Hook để quản lý CRUD operations cho slides
 */
export const useSlideActions = ({
  slides,
  setSlides,
  currentSlideIndex,
  setCurrentSlideIndex
}: UseSlideActionsParams): UseSlideActionsReturn => {
  
  const addSlide = useCallback(() => {
    const newSlide: Slide = {
      id: Date.now().toString(),
      elements: [],
      backgroundColor: "#ffffff"
    };
    setSlides(prev => [...prev, newSlide]);
    setCurrentSlideIndex(slides.length);
  }, [slides.length, setSlides, setCurrentSlideIndex]);

  const deleteSlide = useCallback((index: number) => {
    if (slides.length <= 1) return;
    setSlides(prev => prev.filter((_, i) => i !== index));
    if (currentSlideIndex >= index && currentSlideIndex > 0) {
      setCurrentSlideIndex(prev => prev - 1);
    }
  }, [slides.length, currentSlideIndex, setSlides, setCurrentSlideIndex]);

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

  return {
    addSlide,
    deleteSlide,
    duplicateSlide
  };
};
