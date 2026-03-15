import type { Slide, SlideElement } from '../types';
export type { Slide, SlideElement };

export interface EditorState {
    slides: Slide[];
    currentSlideId: string | null;
    selectedElementIds: string[];
    zoomLevel: number;
    
    // Actions
    addSlide: () => void;
    selectSlide: (id: string) => void;
    deleteSlide: (id: string) => void;
    
    addElement: (slideId: string, element: Omit<SlideElement, 'id'>) => void;
    updateElement: (slideId: string, elementId: string, updates: Partial<SlideElement>) => void;
    removeElement: (slideId: string, elementId: string) => void;
    
    selectElement: (elementId: string, multi?: boolean) => void;
    clearSelection: () => void;
    
    setZoom: (zoom: number) => void;
    setSlides: (slides: Slide[], currentSlideId?: string) => void;
}
