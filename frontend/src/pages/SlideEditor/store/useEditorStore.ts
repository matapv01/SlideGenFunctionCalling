import { create } from 'zustand';
import { temporal } from 'zundo';
import { EditorState, Slide, SlideElement } from './types';
import { v4 as uuidv4 } from 'uuid';

const createDefaultSlide = (): Slide => ({
    id: uuidv4(),
    elements: [],
    backgroundColor: '#ffffff'
});

export const useEditorStore = create<EditorState>()(
    temporal(
        (set, get) => ({
            slides: [createDefaultSlide()],
            currentSlideId: null, // Will be set on init later
            selectedElementIds: [],
            zoomLevel: 1,

            addSlide: () => {
                const newSlide = createDefaultSlide();
                set((state) => ({
                    slides: [...state.slides, newSlide],
                    currentSlideId: newSlide.id
                }));
            },

            selectSlide: (id: string) => {
                set({ currentSlideId: id, selectedElementIds: [] });
            },

            deleteSlide: (id: string) => {
                set((state) => {
                    const newSlides = state.slides.filter(s => s.id !== id);
                    if (newSlides.length === 0) {
                        newSlides.push(createDefaultSlide());
                    }
                    const nextSlideId = state.currentSlideId === id ? newSlides[0].id : state.currentSlideId;
                    return {
                        slides: newSlides,
                        currentSlideId: nextSlideId,
                        selectedElementIds: []
                    };
                });
            },

            addElement: (slideId: string, elementOpt: Omit<SlideElement, 'id'>) => {
                const newElement: SlideElement = {
                    ...elementOpt,
                    id: uuidv4(),
                };
                
                set((state) => ({
                    slides: state.slides.map(slide => 
                        slide.id === slideId 
                            ? { ...slide, elements: [...slide.elements, newElement] }
                            : slide
                    ),
                    selectedElementIds: [newElement.id]
                }));
            },

            updateElement: (slideId: string, elementId: string, updates: Partial<SlideElement>) => {
                set((state) => ({
                    slides: state.slides.map(slide => 
                        slide.id === slideId 
                            ? {
                                ...slide,
                                elements: slide.elements.map(el => 
                                    el.id === elementId ? { ...el, ...updates } : el
                                )
                            }
                            : slide
                    )
                }));
            },

            removeElement: (slideId: string, elementId: string) => {
                set((state) => ({
                    slides: state.slides.map(slide => 
                        slide.id === slideId 
                            ? { ...slide, elements: slide.elements.filter(el => el.id !== elementId) }
                            : slide
                    ),
                    selectedElementIds: state.selectedElementIds.filter(id => id !== elementId)
                }));
            },

            selectElement: (elementId: string, multi = false) => {
                set((state) => {
                    if (multi) {
                        const isSelected = state.selectedElementIds.includes(elementId);
                        return {
                            selectedElementIds: isSelected 
                                ? state.selectedElementIds.filter(id => id !== elementId)
                                : [...state.selectedElementIds, elementId]
                        };
                    }
                    return { selectedElementIds: [elementId] };
                });
            },

            clearSelection: () => {
                set({ selectedElementIds: [] });
            },

            setZoom: (zoom: number) => {
                // Limit zoom between 10% and 500%
                const clampedZoom = Math.min(Math.max(zoom, 0.1), 5);
                set({ zoomLevel: clampedZoom });
            },

            setSlides: (slides: Slide[], currentSlideId?: string) => {
                set({ 
                    slides, 
                    currentSlideId: currentSlideId || (slides.length > 0 ? slides[0].id : null),
                    selectedElementIds: [] 
                });
            }
        }),
        {
            // Zundo configuration for undo/redo
            partialize: (state) => {
                // Only track slides array for undo/redo, not selection or zoom
                const { slides } = state;
                return { slides };
            },
            limit: 100, // Keep last 100 history states
        }
    )
);
