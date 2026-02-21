import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft, Sidebar, MousePointer, Type, Download, Play, Undo2, Redo2,
  Save, Settings, Maximize, Upload, Plus, Trash2,
  Copy, Layers, Circle, Square, Triangle,
  Image as ImageIcon, Video, AlignLeft,
  AlignCenter, AlignRight, Bold, Italic, Underline,
  FileText
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { useToast } from "@/hooks/use-toast";
import { 
  ContextMenu, ContextMenuContent, ContextMenuItem, ContextMenuSeparator, 
  ContextMenuTrigger 
} from "@/components/ui/context-menu";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { SlideCanvas, SlideCanvasHandle } from "@/components/SlideCanvas";

// --- Helper: HTML Parsing ---
const pxToNum = (val: string | null) => val ? parseFloat(val.replace("px", "")) : 0;

const parseHtmlToElements = (html: string): { elements: SlideElement[], backgroundColor: string, defs?: string } => {
  // 1. Create a temporary hidden container to render HTML for accurate measurements
  const tempContainer = document.createElement('div');
  tempContainer.style.position = 'fixed';
  tempContainer.style.top = '-9999px';
  tempContainer.style.left = '-9999px';
  tempContainer.style.width = `${CANVAS_WIDTH}px`; // 1920px
  tempContainer.style.height = `${CANVAS_HEIGHT}px`; // 1080px
  tempContainer.style.visibility = 'hidden';
  tempContainer.innerHTML = html;
  
  document.body.appendChild(tempContainer);

  // 2. Extract background color
  let backgroundColor = "#ffffff";
  const computedBg = window.getComputedStyle(tempContainer).backgroundColor;
  if (computedBg && computedBg !== 'rgba(0, 0, 0, 0)' && computedBg !== 'transparent') {
    backgroundColor = computedBg;
  }
  
  // Check for background in child container
  const container = tempContainer.querySelector('.slide-container') as HTMLElement;
  if (container) {
    const containerBg = window.getComputedStyle(container).backgroundColor;
    if (containerBg && containerBg !== 'rgba(0, 0, 0, 0)' && containerBg !== 'transparent') {
      backgroundColor = containerBg;
    }
  }
  
  // 3. Extract SVG definitions (e.g., clipPaths)
  let defs = '';
  const svgElements = tempContainer.querySelectorAll('svg');
  svgElements.forEach(svg => {
    if (svg.querySelector('defs')) {
      defs += svg.outerHTML;
      svg.remove();
    }
  });

  const extractedElements: SlideElement[] = [];
  const tempRect = tempContainer.getBoundingClientRect();
  
  // 4. Get all child elements to convert to SlideElements
  const allElements = Array.from(tempContainer.querySelectorAll('*'));
  
  // Filter out non-visible structural elements
  const visibleElements = allElements.filter(el => {
    const element = el as HTMLElement;
    if (['SCRIPT', 'STYLE', 'LINK', 'META', 'HEAD'].includes(element.tagName)) return false;
    
    const computed = window.getComputedStyle(element);
    if (computed.display === 'none' || computed.visibility === 'hidden') return false;
    
    return true;
  });

  // Process elements with absolute positioning first
  const absoluteElements = visibleElements.filter(el => {
    const computed = window.getComputedStyle(el as HTMLElement);
    return computed.position === 'absolute' || computed.position === 'fixed';
  });

  if (absoluteElements.length > 0) {
    absoluteElements.forEach((el, idx) => {
      const element = el as HTMLElement;
      const computed = window.getComputedStyle(element);
      const tagName = element.tagName.toLowerCase();
      
      // --- Get accurate geometry using getBoundingClientRect ---
      const rect = element.getBoundingClientRect();
      const x = rect.left - tempRect.left;
      const y = rect.top - tempRect.top;
      const width = rect.width || 100;
      const height = rect.height || 100;

      const id = `el-${Date.now()}-${idx}`;
      const zIndex = parseInt(computed.zIndex) || (idx + 1);
      const opacity = parseFloat(computed.opacity) || 1;
      const borderRadius = parseFloat(computed.borderRadius) || 0;
      
      // Parse rotation from transform matrix
      let rotation = 0;
      if (computed.transform && computed.transform !== 'none') {
        const match = computed.transform.match(/rotate\(([^)]+)deg\)/);
        if (match && match[1]) {
          rotation = parseFloat(match[1]);
        }
      }
      
      // --- Type Detection ---

      // 1. Image (<img> tag)
      if (tagName === 'img') {
        extractedElements.push({
          id, type: 'image',
          src: (element as HTMLImageElement).src,
          x, y, width, height: height || 200,
          rotation, zIndex, opacity, borderRadius
        });
        return;
      }

      // 2. Background Image (div with background-image)
      const bgImage = computed.backgroundImage;
      if (bgImage && bgImage !== 'none' && bgImage.includes('url(')) {
        const urlMatch = bgImage.match(/url\(["']?([^"']*)["']?\)/);
        if (urlMatch && urlMatch[1]) {
          extractedElements.push({
            id, type: 'image',
            src: urlMatch[1],
            x, y, width, height,
            rotation, zIndex, opacity, borderRadius
          });
          return;
        }
      }

      // 3. Shape (Div with no text, but has bg color or border)
      const hasText = element.textContent && element.textContent.trim().length > 0;
      const bgColor = computed.backgroundColor;
      const hasBgColor = bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent';
      const borderWidth = parseFloat(computed.borderWidth);
      const hasBorder = borderWidth > 0;
      
      if (tagName === 'div' && !hasText && (hasBgColor || hasBorder)) {
        let subType = 'rectangle';
        if (computed.borderRadius === '50%' || borderRadius >= width / 2) {
          subType = 'circle';
        }

        extractedElements.push({
          id, type: 'shape', subType,
          x, y, width, height,
          rotation, zIndex, opacity,
          fillColor: bgColor || 'transparent',
          strokeColor: computed.borderColor || 'transparent',
          strokeWidth: borderWidth || 0,
          borderRadius: borderRadius || (subType === 'circle' ? 1000 : 0)
        });
        return;
      }

      // 4. Text (Fallback for everything else with content)
      const fontSize = parseFloat(computed.fontSize) || 24;
      const fontFamily = computed.fontFamily || 'Inter, sans-serif';
      const fontWeight = computed.fontWeight || 'normal';
      const textAlign = (computed.textAlign as any) || 'left';
      const color = computed.color || '#000000';
      const lineHeight = computed.lineHeight || '1.2';
      const letterSpacing = computed.letterSpacing || 'normal';
      const clipPath = computed.clipPath && computed.clipPath !== 'none' ? computed.clipPath : undefined;

      extractedElements.push({
        id, type: 'text',
        content: element.innerHTML,
        x, y, width, height,
        rotation, zIndex, opacity,
        fontSize, fontFamily, fontWeight, textAlign, color,
        lineHeight, letterSpacing,
        clipPath
      });
    });
  } else {
    // Fallback: Process elements based on content flow
    const contentNodes = Array.from(tempContainer.querySelectorAll('h1, h2, h3, p, ul, ol, img, div'));
    
    contentNodes.forEach((node, idx) => {
      const element = node as HTMLElement;
      const tagName = element.tagName.toLowerCase();
      const computed = window.getComputedStyle(element);
      
      // Skip if already processed or empty
      if (computed.display === 'none' || computed.visibility === 'hidden') return;
      if (tagName !== 'img' && !element.textContent?.trim()) return;

      const rect = element.getBoundingClientRect();
      const x = rect.left - tempRect.left;
      const y = rect.top - tempRect.top;
      const width = rect.width || 100;
      const height = rect.height || 50;

      if (tagName === 'img') {
        extractedElements.push({
          id: `img-${Date.now()}-${idx}`,
          type: 'image',
          src: (element as HTMLImageElement).src,
          x, y,
          width: width || 600,
          height: height || 400,
          rotation: 0, zIndex: idx + 1, opacity: 1,
          borderRadius: parseFloat(computed.borderRadius) || 0
        });
      } else {
        // Text element
        const fontSize = parseFloat(computed.fontSize) || 24;
        const fontWeight = computed.fontWeight || 'normal';
        const textAlign = (computed.textAlign as any) || 'left';
        const color = computed.color || '#000000';

        extractedElements.push({
          id: `text-${Date.now()}-${idx}`,
          type: 'text',
          content: element.innerHTML,
          x, y, width, height,
          rotation: 0, zIndex: idx + 1, opacity: 1,
          fontSize, fontWeight, textAlign, color,
          fontFamily: computed.fontFamily || 'Inter, sans-serif',
          lineHeight: computed.lineHeight || '1.2',
          letterSpacing: computed.letterSpacing || 'normal'
        });
      }
    });

    // Final fallback if no elements found
    if (extractedElements.length === 0 && tempContainer.textContent?.trim()) {
      extractedElements.push({
        id: `text-${Date.now()}-fallback`,
        type: 'text',
        content: tempContainer.innerHTML,
        x: 100, y: 100,
        width: CANVAS_WIDTH - 200,
        height: CANVAS_HEIGHT - 200,
        rotation: 0, zIndex: 1, opacity: 1,
        fontSize: 24,
        fontWeight: 'normal',
        textAlign: 'left',
        color: '#000000'
      });
    }
  }

  // 5. Cleanup: Remove temporary container
  document.body.removeChild(tempContainer);

  return { elements: extractedElements, backgroundColor, defs: defs || undefined };
};

// --- Mock Templates & Elements ---
const TEMPLATES = [
  { id: "title", name: "Title Slide", layout: "title" },
  { id: "content", name: "Title & Content", layout: "content" },
  { id: "two-col", name: "Two Columns", layout: "two-col" },
  { id: "blank", name: "Blank", layout: "blank" },
];

const ELEMENTS_CATEGORIES = [
  {
    name: "Basic Shapes",
    items: [
      { id: "rect", icon: Square, label: "Rectangle", type: "shape", subType: "rectangle" },
      { id: "circle", icon: Circle, label: "Circle", type: "shape", subType: "circle" },
      { id: "triangle", icon: Triangle, label: "Triangle", type: "shape", subType: "triangle" },
    ]
  },
  {
    name: "Media",
    items: [
      { id: "image", icon: ImageIcon, label: "Image", type: "image", subType: "" },
      { id: "video", icon: Video, label: "Video", type: "video", subType: "" },
    ]
  },
  {
    name: "Text",
    items: [
      { id: "heading", icon: Type, label: "Heading", type: "text", subType: "heading" },
      { id: "paragraph", icon: Type, label: "Paragraph", type: "text", subType: "paragraph" },
    ]
  }
];

// --- Main Component ---

const SlideEditor = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  // --- State ---
  const [slides, setSlides] = useState<Slide[]>([
    { id: "1", elements: [], backgroundColor: "#ffffff" }
  ]);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [selectedElementId, setSelectedElementId] = useState<string | null>(null);
  const [zoom, setZoom] = useState(0.5); // Start at 50% for better view
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

  // --- Effects ---
  useEffect(() => {
    // Load initial data if projectId exists
    if (projectId) {
      const loadData = async () => {
        try {
          setLoading(true);
          // Fetch project details
          let project;
          try {
             project = await api.getProject(projectId);
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
            // Map backend slides to frontend Slide interface
            const mappedSlides: Slide[] = slidesResponse.slides.map((s: any) => {
              let elements: SlideElement[] = [];
              let backgroundColor = "#ffffff";
              let backgroundImage = undefined;
              let defs: string | undefined = undefined;

              // Robustly handle design_settings
              if (s.design_settings) {
                try {
                  const ds = typeof s.design_settings === 'string' 
                    ? JSON.parse(s.design_settings) 
                    : s.design_settings;
                  
                  if (ds && typeof ds === 'object') {
                    if (Array.isArray(ds.elements)) {
                      elements = ds.elements.map((el: any) => ({
                         ...el,
                         id: String(el.id || Date.now().toString() + Math.random()) // Ensure ID is string
                      }));
                    }
                    if (ds.backgroundColor) backgroundColor = ds.backgroundColor;
                    if (ds.backgroundImage) backgroundImage = ds.backgroundImage;
                    if (ds.defs) defs = ds.defs;
                  }
                } catch (e) {
                  console.error("Failed to parse design_settings for slide", s.id, e);
                  // Fallback to empty elements if parsing fails
                }
              }

              // If no elements (or failed parse), create default from content
              if (elements.length === 0) {
                // Try to parse HTML content into elements first
                if (s.html_content) {
                  try {
                    const parsed = parseHtmlToElements(s.html_content);
                    if (parsed.elements.length > 0) {
                      elements = parsed.elements;
                      // Use parsed background if available and valid
                      if (parsed.backgroundColor) { 
                        backgroundColor = parsed.backgroundColor;
                      }
                      if (parsed.defs) {
                         defs = parsed.defs;
                      }
                    }
                  } catch (e) {
                    console.error("Failed to parse HTML content for slide", s.id, e);
                  }
                }

                // If still no elements, fallback to full-slide HTML/Text blob
                if (elements.length === 0) {
                  // Check if HTML content is available
                  const isHtml = !!s.html_content; 
                  // Prioritize HTML content if available, otherwise use text content
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
                elements: elements,
                backgroundColor,
                backgroundImage,
                notes: s.notes,
                defs // Add extracted SVG defs
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

  // Keyboard Shortcuts
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


  // --- Actions ---

  const addSlide = () => {
    const newSlide: Slide = {
      id: Date.now().toString(),
      elements: [],
      backgroundColor: "#ffffff"
    };
    setSlides([...slides, newSlide]);
    setCurrentSlideIndex(slides.length);
  };

  const deleteSlide = (index: number) => {
    if (slides.length <= 1) return;
    const newSlides = slides.filter((_, i) => i !== index);
    setSlides(newSlides);
    if (currentSlideIndex >= index && currentSlideIndex > 0) {
      setCurrentSlideIndex(currentSlideIndex - 1);
    }
  };

  const duplicateSlide = (index: number) => {
    const slideToDup = slides[index];
    // Deep copy elements
    const elementsCopy = slideToDup.elements.map(el => ({ ...el, id: Date.now().toString() + Math.random() }));
    const newSlide = { ...slideToDup, id: Date.now().toString(), elements: elementsCopy };
    const newSlides = [...slides];
    newSlides.splice(index + 1, 0, newSlide);
    setSlides(newSlides);
  };

  const addElement = (item: DragItem, dropX: number, dropY: number) => {
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
          defaults.borderRadius = 1000; // simple circle
          defaults.width = 100;
          defaults.height = 100;
      }
    } else if (item.type === "image") {
        defaults.type = "image";
        defaults.src = "/placeholder.svg"; // Placeholder
        defaults.width = 300;
        defaults.height = 200;
    }

    const newElement = { ...defaults } as SlideElement;
    
    // Add to current slide
    const updatedSlides = slides.map((slide, i) => {
        if (i !== currentSlideIndex) return slide;
        return {
            ...slide,
            elements: [...slide.elements, newElement]
        };
    });
    setSlides(updatedSlides);
    setSelectedElementId(id);
  };

  const updateElement = (id: string, updates: Partial<SlideElement>) => {
    // Update state React
    const updatedSlides = slides.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      return {
        ...slide,
        elements: slide.elements.map(el => el.id === id ? { ...el, ...updates } : el)
      };
    });
    setSlides(updatedSlides);
    
    // Update Shadow DOM thông qua SlideCanvas
    if (slideCanvasRef.current) {
      const styleUpdates: any = {};
      
      // Map SlideElement properties sang CSS properties
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
      if (updates.content !== undefined) styleUpdates.innerHTML = updates.content;
      
      slideCanvasRef.current.updateElement(styleUpdates);
    }
  };

  const deleteElement = (id: string) => {
    const updatedSlides = slides.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      return {
        ...slide,
        elements: slide.elements.filter(el => el.id !== id)
      };
    });
    setSlides(updatedSlides);
    setSelectedElementId(null);
  };

  const bringForward = (id: string) => {
    // Logic to increase z-index
  };

  const sendBackward = (id: string) => {
    // Logic to decrease z-index
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (!draggedItem || !canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const scale = zoom; // use state zoom to account for scale
    
    // Adjust x/y based on scale
    const x = (e.clientX - rect.left) / scale;
    const y = (e.clientY - rect.top) / scale;

    addElement(draggedItem, x, y);
    setDraggedItem(null);
  };

  const handleSave = async () => {
    if (!currentSlide) return;
    
    // Lấy HTML mới nhất từ Shadow DOM
    let updatedHTML = currentSlide.elements[0]?.content || '';
    if (slideCanvasRef.current) {
      try {
        updatedHTML = slideCanvasRef.current.getHTML();
      } catch (e) {
        console.error("Failed to get HTML from SlideCanvas", e);
      }
    }
    
    // Find a title if available to update content_text or title field
    const titleElement = currentSlide.elements.find(el => 
      el.type === 'text' && (el.fontSize && el.fontSize > 30) // Heuristic for title
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
        html_content: updatedHTML, // Save updated HTML
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
  };
  
  // Handler để nhận selection từ SlideCanvas
  const handleElementSelectFromCanvas = (elementData: any) => {
    console.log('[SlideEditor] Element selected from canvas:', elementData);
    
    if (!elementData) {
      setSelectedElementId(null);
      return;
    }
    
    // Tìm element trong state hiện tại
    let matchingElement = currentSlide?.elements.find(el => el.id === elementData.id);

    // --- PHẦN BỔ SUNG QUAN TRỌNG ---
    // Cập nhật State React với dữ liệu mới nhất từ Canvas (DOM)
    // Nếu không có bước này, Properties Panel sẽ luôn hiển thị dữ liệu cũ
    if (matchingElement && elementData.style) {
        const updates: Partial<SlideElement> = {
            // Map các thuộc tính style từ Canvas về State
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
            // Cập nhật cả nội dung nếu có thay đổi (ví dụ edit text trực tiếp)
            content: elementData.content || elementData.innerHTML
        };

        // Cập nhật State React (KHÔNG gọi updateElement để tránh vòng lặp vô hạn gửi lại Canvas)
        const updatedSlides = slides.map((slide, i) => {
            if (i !== currentSlideIndex) return slide;
            return {
                ...slide,
                elements: slide.elements.map(el => el.id === matchingElement!.id ? { ...el, ...updates } : el)
            };
        });
        setSlides(updatedSlides);
        setSelectedElementId(matchingElement.id);
        return; 
    }
    // --- HẾT PHẦN BỔ SUNG ---
    
    if (!matchingElement && elementData.style) {
      // Tạo SlideElement mới từ data nhận được (Giữ nguyên logic cũ của bạn)
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
        textAlign: elementData.style.textAlign as any || 'left',
        color: elementData.style.color || '#000000',
        fillColor: elementData.style.backgroundColor || 'transparent'
      };
      
      const updatedSlides = slides.map((slide, i) => {
        if (i !== currentSlideIndex) return slide;
        return {
          ...slide,
          elements: [...slide.elements, newElement]
        };
      });
      setSlides(updatedSlides);
      matchingElement = newElement;
      
      console.log('[SlideEditor] Created new element in state:', newElement);
    }
    
    if (matchingElement) {
      setSelectedElementId(matchingElement.id);
    }
  };
  
  // --- Rendering ---

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen w-screen bg-background">
        <div className="animate-pulse text-xl font-semibold text-muted-foreground">Loading project...</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-background text-foreground">
       {/* Toolbar */}
        <div className="h-14 border-b bg-background flex items-center justify-between px-4 sticky top-0 z-50">
        <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-5 w-5" />
            </Button>
            <span className="font-semibold text-sm max-w-[200px] truncate">{projectName}</span>
            <Separator orientation="vertical" className="h-6 mx-2" />
            <Button 
            variant={isSidebarOpen ? "secondary" : "ghost"} 
            size="icon" 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            title="Toggle Sidebar"
            >
            <Sidebar className="h-5 w-5" />
            </Button>
        </div>

        <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center gap-1 bg-muted/30 p-1 rounded-md">
            <Button variant={!selectedElementId ? "secondary": "ghost"} size="sm" onClick={() => setSelectedElementId(null)}>
            <MousePointer className="h-4 w-4 mr-2" /> Select
            </Button>
            <Button variant="ghost" size="sm" onClick={() => {
                setDraggedItem({ type: 'text', subType: 'paragraph' });
                // Note: ideally drag logic, but button click can add directly too
            }}>
            <Type className="h-4 w-4 mr-2" /> Text
            </Button>
            <Button variant="ghost" size="sm">
            <Download className="h-4 w-4 mr-2" /> Export
            </Button>
            <Button variant="ghost" size="sm" className="text-blue-600 bg-blue-50/50 hover:bg-blue-100">
            <Play className="h-4 w-4 mr-2" /> Present
            </Button>
        </div>

        <div className="flex items-center gap-2">
            <Button 
                variant="ghost" 
                size="icon" 
                title="Undo"
                onClick={() => slideCanvasRef.current?.undo()}
            >
                <Undo2 className="h-4 w-4" />
            </Button>
            <Button 
                variant="ghost" 
                size="icon" 
                title="Redo"
                onClick={() => slideCanvasRef.current?.redo()}
            >
                <Redo2 className="h-4 w-4" />
            </Button>
            <Separator orientation="vertical" className="h-6 mx-2" />
            <Button variant="ghost" size="icon" title="Save" onClick={handleSave}>
            <Save className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" title="Properties">
            <Settings className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => setZoom(0.5)} title="Reset Zoom">
            <Maximize className="h-4 w-4" />
            </Button>
            <Button variant="default" size="sm" className="ml-2">
            <Upload className="h-4 w-4 mr-2" /> Import
            </Button>
        </div>
        </div>

       <div className="flex flex-1 overflow-hidden">
            {/* Left Sidebar */}
            <div className={cn(
            "w-80 border-r bg-background flex flex-col transition-all duration-300",
            !isSidebarOpen && "w-0 overflow-hidden border-none"
            )}>
            <Tabs defaultValue="slides" className="flex-1 flex flex-col h-full">
                <TabsList className="w-full justify-start rounded-none border-b h-12 p-0 bg-transparent">
                <TabsTrigger value="slides" className="flex-1 h-full rounded-none data-[state=active]:bg-background data-[state=active]:border-b-2 data-[state=active]:border-primary">
                    Slides
                </TabsTrigger>
                <TabsTrigger value="templates" className="flex-1 h-full rounded-none data-[state=active]:bg-background data-[state=active]:border-b-2 data-[state=active]:border-primary">
                    Templates
                </TabsTrigger>
                <TabsTrigger value="elements" className="flex-1 h-full rounded-none data-[state=active]:bg-background data-[state=active]:border-b-2 data-[state=active]:border-primary">
                    Elements
                </TabsTrigger>
                </TabsList>

                <TabsContent value="slides" className="flex-1 overflow-y-auto p-4 space-y-4">
                <div className="grid gap-4">
                    {slides.map((slide, idx) => (
                    <div 
                        key={slide.id}
                        className={cn(
                        "group relative aspect-video bg-white border-2 rounded-lg cursor-pointer hover:border-primary/50 transition-all",
                        currentSlideIndex === idx ? "border-primary shadow-md" : "border-border"
                        )}
                        onClick={() => setCurrentSlideIndex(idx)}
                    >
                        <div className="absolute top-2 left-2 bg-black/50 text-white text-xs px-2 py-0.5 rounded-full z-10">
                        {idx + 1}
                        </div>
                        {/* Thumbnail Preview Placeholder */}
                        <div className="w-full h-full flex items-center justify-center text-muted-foreground/20 text-4xl font-bold bg-neutral-50">
                        {idx + 1}
                        </div>
                        
                        {/* Hover Actions */}
                        <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 flex gap-1 transition-opacity bg-background/80 rounded shadow z-10">
                        <Button size="icon" variant="ghost" className="h-6 w-6" onClick={(e) => { e.stopPropagation(); duplicateSlide(idx); }}>
                            <Copy className="h-3 w-3" />
                        </Button>
                        <Button size="icon" variant="ghost" className="h-6 w-6 text-destructive" onClick={(e) => { e.stopPropagation(); deleteSlide(idx); }}>
                            <Trash2 className="h-3 w-3" />
                        </Button>
                        </div>
                    </div>
                    ))}
                </div>
                <Button variant="outline" className="w-full h-12 border-dashed mt-4" onClick={addSlide}>
                    <Plus className="h-4 w-4 mr-2" /> New Slide
                </Button>
                </TabsContent>

                <TabsContent value="templates" className="flex-1 overflow-y-auto p-4">
                <div className="grid grid-cols-2 gap-4">
                    {TEMPLATES.map(tmpl => (
                    <div 
                        key={tmpl.id} 
                        className="aspect-[4/3] border rounded-md bg-muted/20 hover:bg-muted cursor-pointer flex flex-col items-center justify-center p-2 text-center select-none"
                        draggable
                        onDragStart={() => setDraggedItem({ type: "template", subType: tmpl.layout })}
                    >
                        <FileText className="h-8 w-8 mb-2 text-muted-foreground" />
                        <span className="text-xs font-medium">{tmpl.name}</span>
                    </div>
                    ))}
                </div>
                </TabsContent>

                <TabsContent value="elements" className="flex-1 overflow-y-auto p-4 space-y-6">
                {ELEMENTS_CATEGORIES.map(cat => (
                    <div key={cat.name}>
                    <h3 className="text-sm font-semibold mb-3 text-muted-foreground">{cat.name}</h3>
                    <div className="grid grid-cols-3 gap-2">
                        {cat.items.map(item => (
                        <div 
                            key={item.id}
                            className="aspect-square border rounded-md flex flex-col items-center justify-center hover:bg-secondary cursor-grab active:cursor-grabbing p-1"
                            draggable
                            onDragStart={(e) => {
                            setDraggedItem({ type: item.type, subType: item.subType });
                            }}
                        >
                            <item.icon className="h-6 w-6 mb-1 text-foreground" />
                            <span className="text-[10px] text-center leading-tight">{item.label}</span>
                        </div>
                        ))}
                    </div>
                    </div>
                ))}
                </TabsContent>
            </Tabs>
            </div>

            {/* Canvas Area - Using Shadow DOM Isolated SlideCanvas */}
            <div 
                className="flex-1 bg-neutral-100 overflow-auto relative flex items-center justify-center p-20"
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
            >
                <div 
                    className="relative transition-transform duration-200 ease-out origin-center"
                    style={{
                        transform: `scale(${zoom})`,
                    }}
                    ref={canvasRef}
                >
                    {/* Render Slide với Shadow DOM Isolation */}
                    {currentSlide && currentSlide.elements.length > 0 && (
                        <SlideCanvas
                            ref={slideCanvasRef}
                            htmlContent={
                                // Nếu có html_content từ backend, dùng ngay
                                currentSlide.elements[0]?.content || 
                                '<div class="slide-container"><p>Empty slide</p></div>'
                            }
                            onElementSelect={handleElementSelectFromCanvas}
                        />
                    )}
                    
                    {/* Fallback nếu slide chưa load */}
                    {(!currentSlide || currentSlide.elements.length === 0) && (
                        <div className="w-[1920px] h-[1080px] bg-white shadow-2xl flex items-center justify-center text-gray-400">
                            <p>Loading slide...</p>
                        </div>
                    )}
                </div>

                {/* Zoom Controls Overlay */}
                <div className="absolute bottom-6 right-6 flex items-center bg-white/90 backdrop-blur border rounded-md shadow-lg p-1 gap-2 z-50">
                    <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setZoom(Math.max(0.1, zoom - 0.1))}>
                        <span className="text-lg font-bold leading-none">-</span>
                    </Button>
                    <span className="text-xs font-mono w-12 text-center">{Math.round(zoom * 100)}%</span>
                    <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setZoom(Math.min(2, zoom + 0.1))}>
                        <span className="text-lg font-bold leading-none">+</span>
                    </Button>
                </div>
            </div>

            {/* Properties Panel */}
            {selectedElement ? (
                <div className="w-72 border-l bg-background flex flex-col h-full overflow-y-auto">
                    <div className="p-4 border-b">
                    <h3 className="font-semibold text-sm flex items-center gap-2">
                        Properties <span className="text-xs text-muted-foreground font-normal">({selectedElement.type})</span>
                    </h3>
                    </div>
                    
                    <div className="p-4 space-y-6">
                        {/* Position & Transform */}
                        <div className="space-y-4">
                        <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Position & Size</h4>
                        <div className="grid grid-cols-2 gap-2">
                            <div className="space-y-1">
                                <Label className="text-xs">X</Label>
                                <Input 
                                    type="number" 
                                    value={Math.round(selectedElement.x)} 
                                    onChange={(e) => updateElement(selectedElement.id, { x:  Number(e.target.value) })}
                                    className="h-8"
                                />
                            </div>
                            <div className="space-y-1">
                                <Label className="text-xs">Y</Label>
                                <Input 
                                    type="number" 
                                    value={Math.round(selectedElement.y)} 
                                    onChange={(e) => updateElement(selectedElement.id, { y:  Number(e.target.value) })}
                                    className="h-8" 
                                />
                            </div>
                            <div className="space-y-1">
                                <Label className="text-xs">Width</Label>
                                <Input 
                                    type="number" 
                                    value={Math.round(selectedElement.width)} 
                                    onChange={(e) => updateElement(selectedElement.id, { width:  Number(e.target.value) })} 
                                    className="h-8"
                                />
                            </div>
                            <div className="space-y-1">
                                <Label className="text-xs">Height</Label>
                                <Input 
                                    type="number" 
                                    value={Math.round(selectedElement.height)} 
                                    onChange={(e) => updateElement(selectedElement.id, { height:  Number(e.target.value) })} 
                                    className="h-8"
                                />
                            </div>
                            <div className="col-span-2 space-y-1">
                                <Label className="text-xs">Rotation ({selectedElement.rotation}°)</Label>
                                <Slider 
                                    min={0} max={360} step={1}
                                    value={[selectedElement.rotation || 0]}
                                    onValueChange={(vals) => updateElement(selectedElement.id, { rotation: vals[0] })}
                                />
                            </div>
                        </div>
                        </div>

                        <Separator />

                        {/* Appearance */}
                        <div className="space-y-4">
                        <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Appearance</h4>
                        
                        <div className="space-y-2">
                            <Label className="text-xs">Opacity</Label>
                            <Slider 
                                min={0} max={1} step={0.1}
                                value={[selectedElement.opacity ?? 1]} 
                                onValueChange={(v) => updateElement(selectedElement.id, { opacity: v[0] })}
                            />
                        </div>

                        <div className="space-y-2">
                            <Label className="text-xs">Fill Color</Label>
                            <div className="flex gap-2">
                                <Input 
                                    type="color" 
                                    value={selectedElement.fillColor || "#000000"} 
                                    onChange={(e) => updateElement(selectedElement.id, { fillColor: e.target.value })}
                                    className="w-10 h-8 p-0 border-0"
                                />
                                <Input 
                                    type="text" 
                                    value={selectedElement.fillColor || ""} 
                                    onChange={(e) => updateElement(selectedElement.id, { fillColor: e.target.value })}
                                    className="h-8 flex-1 font-mono text-xs"
                                />
                            </div>
                        </div>

                        {selectedElement.type !== 'text' && (
                            <div className="space-y-2">
                                <Label className="text-xs">Border Radius</Label>
                                <Slider 
                                    min={0} max={100} 
                                    value={[selectedElement.borderRadius || 0]} 
                                    onValueChange={(v) => updateElement(selectedElement.id, { borderRadius: v[0] })}
                                />
                            </div>
                        )}
                        </div>

                        <Separator />

                        {/* Typography (Conditional) */}
                        {selectedElement.type === 'text' && (
                            <div className="space-y-4">
                                <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Typography</h4>
                                
                                <div className="space-y-2">
                                    <Label className="text-xs">Content {selectedElement.content?.trim().startsWith('<') ? '(HTML Source)' : ''}</Label>
                                    <Textarea 
                                        value={selectedElement.content || ""} 
                                        onChange={(e) => updateElement(selectedElement.id, { content: e.target.value })}
                                        className="min-h-[200px] font-mono text-xs"
                                    />
                                </div>
                                
                                <div className="grid grid-cols-2 gap-2">
                                    <div className="space-y-1">
                                        <Label className="text-xs">Font Size</Label>
                                        <Input 
                                            type="number" 
                                            value={selectedElement.fontSize || 16} 
                                            onChange={(e) => updateElement(selectedElement.id, { fontSize: Number(e.target.value) })}
                                            className="h-8"
                                        />
                                    </div>
                                    <div className="space-y-1">
                                        <Label className="text-xs">Color</Label>
                                        <Input 
                                            type="color" 
                                            value={selectedElement.color || "#000000"} 
                                            onChange={(e) => updateElement(selectedElement.id, { color: e.target.value })}
                                            className="h-8 w-full p-0"
                                        />
                                    </div>
                                </div>

                                <div className="flex justify-between border rounded-md p-1 bg-muted/20">
                                    <Button 
                                    variant={selectedElement.textAlign === 'left' ? "secondary" : "ghost"} 
                                    size="icon" className="h-6 w-8"
                                    onClick={() => updateElement(selectedElement.id, { textAlign: 'left' })}
                                    >
                                        <AlignLeft className="h-3 w-3" />
                                    </Button>
                                    <Button 
                                    variant={selectedElement.textAlign === 'center' ? "secondary" : "ghost"} 
                                    size="icon" className="h-6 w-8"
                                    onClick={() => updateElement(selectedElement.id, { textAlign: 'center' })}
                                    >
                                        <AlignCenter className="h-3 w-3" />
                                    </Button>
                                    <Button 
                                    variant={selectedElement.textAlign === 'right' ? "secondary" : "ghost"} 
                                    size="icon" className="h-6 w-8"
                                    onClick={() => updateElement(selectedElement.id, { textAlign: 'right' })}
                                    >
                                        <AlignRight className="h-3 w-3" />
                                    </Button>
                                </div>

                                <div className="flex justify-between border rounded-md p-1 bg-muted/20">
                                    <Button 
                                    variant={selectedElement.fontWeight === 'bold' ? "secondary" : "ghost"} 
                                    size="icon" className="h-6 w-8"
                                    onClick={() => updateElement(selectedElement.id, { fontWeight: selectedElement.fontWeight === 'bold' ? 'normal' : 'bold' })}
                                    >
                                        <Bold className="h-3 w-3" />
                                    </Button>
                                    <Button 
                                    variant={selectedElement.fontStyle === 'italic' ? "secondary" : "ghost"} 
                                    size="icon" className="h-6 w-8"
                                    onClick={() => updateElement(selectedElement.id, { fontStyle: selectedElement.fontStyle === 'italic' ? 'normal' : 'italic' })}
                                    >
                                        <Italic className="h-3 w-3" />
                                    </Button>
                                    <Button 
                                    variant={selectedElement.textDecoration === 'underline' ? "secondary" : "ghost"} 
                                    size="icon" className="h-6 w-8"
                                    onClick={() => updateElement(selectedElement.id, { textDecoration: selectedElement.textDecoration === 'underline' ? 'none' : 'underline' })}
                                    >
                                        <Underline className="h-3 w-3" />
                                    </Button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            ) : (
                <div className="w-72 border-l bg-background p-6 flex flex-col items-center justify-center text-muted-foreground">
                    <MousePointer className="h-12 w-12 mb-4 opacity-20" />
                    <p className="text-sm text-center">Select an element to edit its properties</p>
                </div>
            )}
       </div>
    </div>
  );
};

export default SlideEditor;
