import { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import type { Slide, SlideElement, DragItem } from "../types";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "../constants";
import { parseHtmlToElements } from "../utils";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";

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
                try {
                  const ds = typeof s.design_settings === 'string' 
                    ? JSON.parse(s.design_settings) 
                    : s.design_settings;
                  
                  if (ds && typeof ds === 'object') {
                    if (Array.isArray(ds.elements)) {
                      elements = ds.elements.map((el: any) => ({
                        ...el,
                        id: String(el.id || Date.now().toString() + Math.random())
                      }));
                    }
                    if (ds.backgroundColor) backgroundColor = ds.backgroundColor;
                    if (ds.backgroundImage) backgroundImage = ds.backgroundImage;
                    if (ds.defs) defs = ds.defs;
                  }
                } catch (e) {
                  console.error("Failed to parse design_settings for slide", s.id, e);
                }
              }

              // If no elements, create from HTML content
              if (elements.length === 0) {
                if (s.html_content) {
                  try {
                    const parsed = parseHtmlToElements(s.html_content);
                    if (parsed.elements.length > 0) {
                      elements = parsed.elements;
                      if (parsed.backgroundColor) backgroundColor = parsed.backgroundColor;
                      if (parsed.defs) defs = parsed.defs;
                    }
                  } catch (e) {
                    console.error("Failed to parse HTML content for slide", s.id, e);
                  }
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

  // --- Keyboard Shortcuts ---
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Delete" || e.key === "Backspace") {
        if (selectedElementId) {
          deleteElement(selectedElementId);
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedElementId]);

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
  }, [currentSlideIndex]);

  const deleteElement = useCallback((id: string) => {
    setSlides(prev => prev.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      return { ...slide, elements: slide.elements.filter(el => el.id !== id) };
    }));
    setSelectedElementId(null);
  }, [currentSlideIndex]);

  const bringForward = useCallback((id: string) => {
    // TODO: Implement z-index increase
  }, []);

  const sendBackward = useCallback((id: string) => {
    // TODO: Implement z-index decrease
  }, []);

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

  // --- Save Handler ---
  const handleSave = useCallback(async () => {
    if (!currentSlide) return;
    
    let updatedHTML = currentSlide.elements[0]?.content || '';
    if (slideCanvasRef.current) {
      try {
        updatedHTML = slideCanvasRef.current.getHTML();
      } catch (e) {
        console.error("Failed to get HTML from SlideCanvas", e);
      }
    }
    
    const titleElement = currentSlide.elements.find(el => 
      el.type === 'text' && (el.fontSize && el.fontSize > 30)
    );
    const contentText = titleElement?.content || "Slide Content";

    try {
      const designSettings = {
        elements: currentSlide.elements,
        backgroundColor: currentSlide.backgroundColor,
        backgroundImage: currentSlide.backgroundImage,
        defs: currentSlide.defs,
      };

      await api.updateSlide(currentSlide.id, {
        design_settings: JSON.stringify(designSettings),
        html_content: updatedHTML,
        content_text: contentText,
      });
      
      toast({
        title: "Saved",
        description: "Slide changes saved successfully."
      });
    } catch (error) {
      console.error("Failed to save slide", error);
      toast({
        title: "Error",
        description: "Failed to save slide changes.",
        variant: "destructive"
      });
    }
  }, [currentSlide, toast]);

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
    bringForward,
    sendBackward,
    handleDrop,
    handleSave,
    handleElementSelectFromCanvas,
  };
};
