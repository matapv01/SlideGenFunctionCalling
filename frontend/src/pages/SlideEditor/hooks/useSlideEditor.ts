import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import type { Slide, SlideElement, DragItem } from "../types";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "../constants";
import { parseHtmlToElements } from "../utils";
import { useEditorStore } from "../store/useEditorStore";

export const useSlideEditor = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  // Connect to Zustand
  const {
    slides,
    currentSlideId,
    selectedElementIds,
    zoomLevel: zoom,
    setSlides: _setSlides,
    selectSlide,
    addSlide: _addSlide,
    deleteSlide: _deleteSlide,
    addElement: _addElement,
    updateElement: _updateElement,
    removeElement: _deleteElement,
    selectElement,
    clearSelection,
    setZoom
  } = useEditorStore();

  const currentSlideIndex = slides.findIndex(s => s.id === currentSlideId) >= 0 
    ? slides.findIndex(s => s.id === currentSlideId) 
    : 0;
  const currentSlide = slides[currentSlideIndex];
  const selectedElementId = selectedElementIds[0] || null;
  const selectedElement = currentSlide?.elements.find(el => el.id === selectedElementId);

  // Local UI State
  const [draggedItem, setDraggedItem] = useState<DragItem | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [projectName, setProjectName] = useState("Untitled Project");
  const [loading, setLoading] = useState(true);

  // --- Load Data Effect ---
  useEffect(() => {
    if (projectId) {
      let isMounted = true;
      const loadData = async () => {
        try {
          setLoading(true);
          
          try {
            const project = await api.getProject(projectId);
            if (isMounted) setProjectName(project?.title || `Project ${projectId}`);
          } catch (e) {
            console.error("Failed to load project details", e);
          }

          const slidesResponse = await api.getSlides(projectId);
          
          if (slidesResponse?.slides && Array.isArray(slidesResponse.slides) && isMounted) {
            const mappedSlides: Slide[] = slidesResponse.slides.map((s: any) => {
              let elements: SlideElement[] = [];
              let backgroundColor = "#ffffff";
              let htmlBackground: string | undefined = undefined;

              // If backend saved pre-parsed elements in design_settings, use them
              if (s.design_settings) {
                try {
                  const ds = typeof s.design_settings === 'string' 
                    ? JSON.parse(s.design_settings) 
                    : s.design_settings;
                  
                  if (ds && typeof ds === 'object') {
                    if (Array.isArray(ds.elements) && ds.elements.length > 0) {
                      elements = ds.elements.map((el: any) => ({
                        ...el,
                        id: String(el.id || Date.now().toString() + Math.random())
                      }));
                    }
                    if (ds.backgroundColor) backgroundColor = ds.backgroundColor;
                  }
                } catch (e) {
                  // Ignore JSON parse errors
                }
              }

              // If no pre-parsed elements, parse the raw HTML into interactive elements
              if (elements.length === 0 && s.html_content) {
                try {
                  const parsed = parseHtmlToElements(s.html_content);
                  if (parsed.elements && parsed.elements.length > 0) {
                    elements = parsed.elements;
                    if (parsed.backgroundColor) backgroundColor = parsed.backgroundColor;
                  } else {
                    htmlBackground = s.html_content;
                  }
                } catch (e) {
                  console.error("Failed to parse HTML to elements", e);
                  htmlBackground = s.html_content;
                }
              }

              return {
                id: String(s.id),
                elements, // Empty array = no interactive elements yet
                htmlBackground,
                backgroundColor,
              };
            });
            
            if (mappedSlides.length > 0) {
              _setSlides(mappedSlides);
            }
          }
        } catch (error) {
          console.error("Failed to load project data", error);
        } finally {
          if (isMounted) setLoading(false);
        }
      };
      
      loadData();
      return () => { isMounted = false; };
    }
  }, [projectId]);

  // Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.key === "Delete" || e.key === "Backspace") && e.target === document.body) {
        if (selectedElementId && currentSlideId) {
          _deleteElement(currentSlideId, selectedElementId);
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedElementId, currentSlideId, _deleteElement]);

  const setCurrentSlideIndex = useCallback((index: number) => {
    if (slides[index]) selectSlide(slides[index].id);
  }, [slides, selectSlide]);

  const addSlide = useCallback(() => _addSlide(), [_addSlide]);
  const deleteSlide = useCallback((index: number) => {
    if (slides[index]) _deleteSlide(slides[index].id);
  }, [slides, _deleteSlide]);
  
  const duplicateSlide = useCallback((index: number) => {
    // Basic duplication can be handled here or moved to store
    // Leaving empty for MVP or implement simple push
  }, []);

  const addElement = useCallback((item: DragItem, dropX: number, dropY: number) => {
    if (!currentSlideId) return;
    
    const defaults: Partial<SlideElement> = {
      x: dropX, y: dropY,
      width: 200, height: 100,
      rotation: 0, zIndex: 10,
    };

    if (item.type === "text") {
      defaults.type = "text";
      defaults.content = item.subType === "heading" ? "Heading" : "Text block";
      defaults.fontSize = item.subType === "heading" ? 48 : 24;
      defaults.width = 400;
      defaults.height = item.subType === "heading" ? 60 : 40;
    } else if (item.type === "shape") {
      defaults.type = "shape";
      defaults.fillColor = "#e2e8f0";
    }

    _addElement(currentSlideId, defaults as Omit<SlideElement, 'id'>);
  }, [currentSlideId, _addElement]);

  const updateElement = useCallback((id: string, updates: Partial<SlideElement>) => {
    if (currentSlideId) _updateElement(currentSlideId, id, updates);
  }, [currentSlideId, _updateElement]);

  const handleDrop = useCallback((e: React.DragEvent, canvasRect: DOMRect) => {
    e.preventDefault();
    if (!draggedItem) return;
    const x = (e.clientX - canvasRect.left) / zoom;
    const y = (e.clientY - canvasRect.top) / zoom;
    addElement(draggedItem, x, y);
    setDraggedItem(null);
  }, [draggedItem, zoom, addElement]);

  const handleSave = useCallback(async () => {
    toast({ title: "Saved (Mock)", description: "Saved to Zustand state." });
  }, [toast]);

  const setSelectedElementId = useCallback((id: string | null) => {
    if (id) {
      selectElement(id);
    } else {
      clearSelection();
    }
  }, [selectElement, clearSelection]);
  
  const handleElementSelectFromCanvas = useCallback(() => {}, []);

  const importSlide = useCallback((htmlContent: string) => {
    try {
      const parsed = parseHtmlToElements(htmlContent);
      const newSlideId = String(Date.now().toString() + Math.random());
      
      const newSlide: Slide = {
        id: newSlideId,
        elements: parsed.elements || [],
        backgroundColor: parsed.backgroundColor || "#ffffff",
        htmlBackground: parsed.elements.length === 0 ? htmlContent : undefined
      };
      
      _setSlides([...slides, newSlide]);
      selectSlide(newSlideId);
      toast({ title: "Import Successful", description: "Slide imported from HTML." });
    } catch (e) {
      console.error("Failed to import HTML slide", e);
      toast({ title: "Import Failed", description: "Could not parse the HTML file.", variant: "destructive" });
    }
  }, [slides, _setSlides, selectSlide, toast]);

  return {
    slides, currentSlide, currentSlideIndex,
    selectedElementId, selectedElement,
    zoom, draggedItem, isSidebarOpen, projectName, loading,
    
    // Setters
    setCurrentSlideIndex, setSelectedElementId,
    setZoom, setDraggedItem, setIsSidebarOpen,
    
    // Actions
    navigate, addSlide, deleteSlide, duplicateSlide,
    addElement, updateElement, handleDrop, handleSave, handleElementSelectFromCanvas,
    importSlide,
  };
};
