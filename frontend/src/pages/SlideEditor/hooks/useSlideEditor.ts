import { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import type { Slide, SlideElement, DragItem } from "../types";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "../constants";
import { parseHtmlToElements } from "../utils";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";
import { useAutoSave } from "./useAutoSave";

// Debounce utility
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

export const useSlideEditor = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  // --- State ---
  const [slides, setSlides] = useState<Slide[]>([
    { id: "1", elements: [], backgroundColor: "#ffffff" }
  ]);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [selectedElementId, setSelectedElementId] = useState<string | null>(null);
  const [zoom, setZoom] = useState(0.5);
  const [draggedItem, setDraggedItem] = useState<DragItem | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [projectName, setProjectName] = useState("Untitled Project");
  const [loading, setLoading] = useState(true);
  
  // Refs
  const canvasRef = useRef<HTMLDivElement>(null);
  const slideCanvasRef = useRef<SlideCanvasHandle>(null);
  
  // --- Computed ---
  const currentSlide = slides[currentSlideIndex];
  const selectedElement = currentSlide?.elements.find(el => el.id === selectedElementId);

  // Debug: Log when currentSlide.backgroundColor changes
  useEffect(() => {
    if (currentSlide) {
      console.log('🔵 [currentSlide] backgroundColor:', currentSlide.backgroundColor);
    }
  }, [currentSlide?.backgroundColor]);

  // --- Load Data Effect ---
  useEffect(() => {
    if (projectId) {
      const loadData = async () => {
        try {
          setLoading(true);
          
          // Fetch project details
          try {
            const project = await api.getProject(projectId);
            setProjectName(project?.title || `Project ${projectId}`);
          } catch (e) {
            console.error("Failed to load project details", e);
            toast({
              title: "Warning",
              description: "Failed to load project details. Slides might still load.",
              variant: "default",
            });
          }

          // Fetch slides
          const slidesResponse = await api.getSlides(projectId);
          
          if (slidesResponse?.slides && Array.isArray(slidesResponse.slides)) {
            const mappedSlides: Slide[] = slidesResponse.slides.map((s: any) => {
              let elements: SlideElement[] = [];
              let backgroundColor = "#ffffff";
              let backgroundImage = undefined;
              let defs: string | undefined = undefined;

              // Handle design_settings
              if (s.design_settings) {
                console.log('🔍 [Load] Raw design_settings:', s.design_settings);
                try {
                  const ds = typeof s.design_settings === 'string' 
                    ? JSON.parse(s.design_settings) 
                    : s.design_settings;
                  
                  console.log('🔍 [Load] Parsed design_settings:', ds);
                  
                  if (ds && typeof ds === 'object') {
                    if (Array.isArray(ds.elements)) {
                      elements = ds.elements.map((el: any) => ({
                        ...el,
                        id: String(el.id || Date.now().toString() + Math.random())
                      }));
                      console.log('✅ [Load] Loaded elements from design_settings:', elements.length);
                    }
                    if (ds.backgroundColor) {
                      backgroundColor = ds.backgroundColor;
                      console.log(`🎨 [Load] Slide ${s.id} backgroundColor from design_settings:`, backgroundColor);
                    } else {
                      console.warn(`⚠️ [Load] Slide ${s.id} has NO backgroundColor in design_settings`);
                    }
                    if (ds.backgroundImage) backgroundImage = ds.backgroundImage;
                    if (ds.defs) defs = ds.defs;
                  }
                } catch (e) {
                  console.error("Failed to parse design_settings for slide", s.id, e);
                }
              }

              // If no elements, create from HTML content
              if (elements.length === 0) {
                console.log('⚠️ [Load] No elements in design_settings, parsing HTML...');
                if (s.html_content) {
                  console.log('🔍 [Load] HTML content preview:', s.html_content.substring(0, 500));
                  try {
                    const parsed = parseHtmlToElements(s.html_content);
                    if (parsed.elements.length > 0) {
                      elements = parsed.elements;
                      console.log('✅ [Load] Parsed elements from HTML:', elements.length);
                      // DON'T override backgroundColor from design_settings with parsed value
                      // Background is stored separately (Legacy pattern)
                      // Only use parsed background if we don't have one from design_settings
                      console.log('🔍 [Load] Before override check - backgroundColor:', backgroundColor);
                      console.log('🔍 [Load] Parsed backgroundColor from HTML:', parsed.backgroundColor);
                      if (!backgroundColor || backgroundColor === "#ffffff") {
                        if (parsed.backgroundColor) {
                          console.log('⚠️ [Load] Overriding backgroundColor with parsed value:', parsed.backgroundColor);
                          backgroundColor = parsed.backgroundColor;
                        }
                      } else {
                        console.log('✅ [Load] Keeping backgroundColor from design_settings (not using parsed)');
                      }
                      if (parsed.defs) defs = parsed.defs;
                    }
                  } catch (e) {
                    console.error("Failed to parse HTML content for slide", s.id, e);
                  }
                } else {
                  console.log('⚠️ [Load] No HTML content to parse');
                }

                // Fallback
                if (elements.length === 0) {
                  const isHtml = !!s.html_content;
                  const content = s.html_content || s.content_text || "New Slide";
                    
                  elements.push({
                    id: `text-${s.id}`,
                    type: "text",
                    content: content,
                    x: isHtml ? 0 : 100,
                    y: isHtml ? 0 : 100,
                    width: isHtml ? CANVAS_WIDTH : 800,
                    height: isHtml ? CANVAS_HEIGHT : 400,
                    rotation: 0,
                    zIndex: 1,
                    opacity: 1,
                    fontSize: 32,
                    textAlign: "left",
                    color: "#000000"
                  });
                }
              }

              console.log(`✅ [Load] Final slide ${s.id} backgroundColor:`, backgroundColor);
              
              return {
                id: String(s.id),
                elements,
                backgroundColor,
                backgroundImage,
                notes: s.notes,
                defs
              };
            });
            
            if (mappedSlides.length > 0) {
              setSlides(mappedSlides);
            }
          }
        } catch (error) {
           console.error("Failed to load project data", error);
          toast({
            title: "Error",
            description: "Failed to load slides. Please try again.",
            variant: "destructive",
          });
        } finally {
          setLoading(false);
        }
      };
      
      loadData();
    }
  }, [projectId, toast]);

  // --- Auto-save (real-time, 1s debounce) ---
  const { handleSave, handleCanvasChange, hasUnsavedChanges } = useAutoSave({
    currentSlide,
    setSlides,
    slideCanvasRef,
  });

  // --- Slide Actions ---
  const addSlide = useCallback(() => {
    const newSlide: Slide = {
      id: Date.now().toString(),
      elements: [],
      backgroundColor: "#ffffff"
    };
    setSlides(prev => [...prev, newSlide]);
    setCurrentSlideIndex(slides.length);
  }, [slides.length]);

  const deleteSlide = useCallback((index: number) => {
    if (slides.length <= 1) return;
    setSlides(prev => prev.filter((_, i) => i !== index));
    if (currentSlideIndex >= index && currentSlideIndex > 0) {
      setCurrentSlideIndex(prev => prev - 1);
    }
  }, [slides.length, currentSlideIndex]);

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
  }, [slides]);

  // --- Element Actions ---
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
  }, [currentSlide, currentSlideIndex]);

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
      if (updates.rotation !== undefined) styleUpdates.transform = `rotate(${updates.rotation}deg)`;
      if (updates.opacity !== undefined) styleUpdates.opacity = `${updates.opacity}`;
      if (updates.zIndex !== undefined) styleUpdates.zIndex = `${updates.zIndex}`;
      
      if (updates.color !== undefined) styleUpdates.color = updates.color;
      if (updates.fontSize !== undefined) styleUpdates.fontSize = `${updates.fontSize}px`;
      if (updates.fontWeight !== undefined) styleUpdates.fontWeight = updates.fontWeight;
      if (updates.fontStyle !== undefined) styleUpdates.fontStyle = updates.fontStyle;
      if (updates.textDecoration !== undefined) styleUpdates.textDecoration = updates.textDecoration;
      if (updates.textAlign !== undefined) styleUpdates.textAlign = updates.textAlign;
      if (updates.fontFamily !== undefined) styleUpdates.fontFamily = updates.fontFamily;
      if (updates.lineHeight !== undefined) styleUpdates.lineHeight = updates.lineHeight;
      if (updates.letterSpacing !== undefined) styleUpdates.letterSpacing = updates.letterSpacing ?? '';
      
      if (updates.fillColor !== undefined) styleUpdates.backgroundColor = updates.fillColor;
      if (updates.strokeColor !== undefined) styleUpdates.borderColor = updates.strokeColor;
      if (updates.strokeWidth !== undefined) styleUpdates.borderWidth = `${updates.strokeWidth}px`;
      if (updates.strokeStyle !== undefined) styleUpdates.borderStyle = updates.strokeStyle;
      if (updates.borderRadius !== undefined) styleUpdates.borderRadius = `${updates.borderRadius}px`;
      if (updates.shadow !== undefined) styleUpdates.boxShadow = updates.shadow;
      
      if (updates.paddingTop !== undefined) styleUpdates.paddingTop = `${updates.paddingTop}px`;
      if (updates.paddingRight !== undefined) styleUpdates.paddingRight = `${updates.paddingRight}px`;
      if (updates.paddingBottom !== undefined) styleUpdates.paddingBottom = `${updates.paddingBottom}px`;
      if (updates.paddingLeft !== undefined) styleUpdates.paddingLeft = `${updates.paddingLeft}px`;
      
      if (updates.content !== undefined) styleUpdates.innerHTML = updates.content;
      
      // Build CSS filter string when any filter value changes
      if (updates.blur !== undefined || updates.brightness !== undefined || updates.saturation !== undefined) {
        // These will be merged into state, read from the element state
        // The filter string is built in PropertiesPanel and NOT passed here
        // So we handle it via the _filter key if present
      }
      if ((updates as any)._filter !== undefined) {
        styleUpdates.filter = (updates as any)._filter;
      }
      
      slideCanvasRef.current.updateElement(styleUpdates);
    }
  }, [currentSlideIndex]);

  const deleteElement = useCallback((id: string) => {
    setSlides(prev => prev.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      return { ...slide, elements: slide.elements.filter(el => el.id !== id) };
    }));
    setSelectedElementId(null);
  }, [currentSlideIndex]);

  const duplicateElement = useCallback((id: string) => {
    setSlides(prev => prev.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      const el = slide.elements.find(e => e.id === id);
      if (!el) return slide;
      const clone: SlideElement = {
        ...el,
        id: `element-${Date.now()}`,
        x: el.x + 20,
        y: el.y + 20,
      };
      return { ...slide, elements: [...slide.elements, clone] };
    }));
  }, [currentSlideIndex]);

  const bringForward = useCallback((id: string) => {
    setSlides(prev => prev.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      return {
        ...slide,
        elements: slide.elements.map(el =>
          el.id === id ? { ...el, zIndex: (el.zIndex || 0) + 1 } : el
        )
      };
    }));
    if (slideCanvasRef.current) {
      const current = slideCanvasRef.current.getSelectedZIndex?.() ?? 0;
      slideCanvasRef.current.updateElement({ zIndex: `${current + 1}` });
    }
  }, [currentSlideIndex]);

  const sendBackward = useCallback((id: string) => {
    setSlides(prev => prev.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      return {
        ...slide,
        elements: slide.elements.map(el =>
          el.id === id ? { ...el, zIndex: Math.max(0, (el.zIndex || 0) - 1) } : el
        )
      };
    }));
    if (slideCanvasRef.current) {
      const current = slideCanvasRef.current.getSelectedZIndex?.() ?? 1;
      slideCanvasRef.current.updateElement({ zIndex: `${Math.max(0, current - 1)}` });
    }
  }, [currentSlideIndex]);

  // --- Drop Handler ---
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!draggedItem || !canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / zoom;
    const y = (e.clientY - rect.top) / zoom;

    addElement(draggedItem, x, y);
    setDraggedItem(null);
  }, [draggedItem, zoom, addElement]);

  // --- Keyboard Shortcuts ---
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Delete/Backspace
      if (e.key === "Delete" || e.key === "Backspace") {
        if (selectedElementId && document.activeElement?.getAttribute('contenteditable') !== 'true') {
          deleteElement(selectedElementId);
        }
      }
      
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedElementId]);

  // --- Canvas Selection Handler ---
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
        x: elementData.style.left,
        y: elementData.style.top,
        width: elementData.style.width,
        height: elementData.style.height,
        fontSize: elementData.style.fontSize,
        fontFamily: elementData.style.fontFamily,
        fontWeight: elementData.style.fontWeight,
        fontStyle: elementData.style.fontStyle,
        textDecoration: elementData.style.textDecoration,
        textAlign: elementData.style.textAlign,
        color: elementData.style.color,
        fillColor: elementData.style.backgroundColor,
        content: elementData.content || elementData.innerHTML
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
      const newElement: SlideElement = {
        id: elementData.id,
        type: 'text',
        content: elementData.content || elementData.innerHTML || elementData.textContent || "New Text",
        x: parseFloat(elementData.style.left) || 0,
        y: parseFloat(elementData.style.top) || 0,
        width: parseFloat(elementData.style.width) || 100,
        height: parseFloat(elementData.style.height) || 100,
        rotation: 0,
        zIndex: 1,
        opacity: 1,
        fontSize: parseFloat(elementData.style.fontSize) || 16,
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
  }, [currentSlide, currentSlideIndex]);

  return {
    // State
    slides,
    currentSlide,
    currentSlideIndex,
    selectedElementId,
    selectedElement,
    zoom,
    draggedItem,
    isSidebarOpen,
    projectName,
    loading,
    
    // Refs
    canvasRef,
    slideCanvasRef,
    
    // Setters
    setCurrentSlideIndex,
    setSelectedElementId,
    setZoom,
    setDraggedItem,
    setIsSidebarOpen,
    
    // Actions
    navigate,
    addSlide,
    deleteSlide,
    duplicateSlide,
    addElement,
    updateElement,
    deleteElement,
    duplicateElement,
    bringForward,
    sendBackward,
    handleDrop,
    handleSave,
    handleElementSelectFromCanvas,
    handleCanvasChange,
  };
};
