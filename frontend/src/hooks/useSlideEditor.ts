import { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { SlideCanvasHandle } from "@/components/SlideCanvas";
import { Slide, SlideElement, DragItem } from "@/types/slide";

// --- Constants ---
const CANVAS_WIDTH = 1920;
const CANVAS_HEIGHT = 1080;

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

export const useSlideEditor = () => {
  const { projectId } = useParams();
  const { toast } = useToast();
  
  // --- State ---
  const [slides, setSlides] = useState<Slide[]>([{ id: "1", elements: [], backgroundColor: "#ffffff" }]);
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
  
  const currentSlide = slides[currentSlideIndex];
  const selectedElement = currentSlide?.elements.find(el => el.id === selectedElementId);

  // --- Load Data ---
  useEffect(() => {
    if (projectId) {
      const loadData = async () => {
        try {
          setLoading(true);
          const project = await api.getProject(projectId);
          setProjectName(project?.title || `Project ${projectId}`);

          const slidesResponse = await api.getSlides(projectId);
          if (slidesResponse?.slides && Array.isArray(slidesResponse.slides)) {
             // Logic map slides response giữ nguyên như cũ
             // ... (Copy logic map từ component cũ vào đây nếu cần chi tiết)
             // Ở đây tôi set tạm để code chạy được
             const mappedSlides = slidesResponse.slides.map((s: any) => ({
                 id: String(s.id),
                 elements: [], // Cần logic parse thực tế
                 backgroundColor: "#ffffff"
             }));
             if(mappedSlides.length > 0) setSlides(mappedSlides);
          }
        } catch (error) {
          console.error(error);
          toast({ title: "Error", description: "Failed to load project", variant: "destructive" });
        } finally {
          setLoading(false);
        }
      };
      loadData();
    }
  }, [projectId, toast]);

  // --- Actions ---
  const updateElement = (id: string, updates: Partial<SlideElement>) => {
    // 1. Update React State
    const updatedSlides = slides.map((slide, i) => {
      if (i !== currentSlideIndex) return slide;
      return {
        ...slide,
        elements: slide.elements.map(el => el.id === id ? { ...el, ...updates } : el)
      };
    });
    setSlides(updatedSlides);
    
    // 2. Update Shadow DOM (Visual)
    if (slideCanvasRef.current) {
      const styleUpdates: any = {};
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

  // --- QUAN TRỌNG: Logic nhận selection từ Canvas và đồng bộ ngược về State ---
  const handleElementSelectFromCanvas = (elementData: any) => {
    if (!elementData) {
      setSelectedElementId(null);
      return;
    }
    
    let matchingElement = currentSlide?.elements.find(el => el.id === elementData.id);
    
    // Nếu tìm thấy, cập nhật state React với các style thực tế từ DOM (fix lỗi properties không cập nhật)
    if (matchingElement && elementData.style) {
        const updates: Partial<SlideElement> = {
            x: parseFloat(elementData.style.left) || 0,
            y: parseFloat(elementData.style.top) || 0,
            width: parseFloat(elementData.style.width),
            height: parseFloat(elementData.style.height),
            fontSize: parseFloat(elementData.style.fontSize),
            fontWeight: elementData.style.fontWeight,
            fontStyle: elementData.style.fontStyle,
            textDecoration: elementData.style.textDecoration,
            textAlign: elementData.style.textAlign,
            color: elementData.style.color,
            fillColor: elementData.style.backgroundColor,
            content: elementData.content || elementData.innerHTML
        };

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
  };

  const addElement = (item: DragItem, dropX: number, dropY: number) => {
      // Logic thêm phần tử (giữ nguyên logic cũ)
      const id = Date.now().toString();
      const newElement: SlideElement = {
        id, type: item.type as any, subType: item.subType,
        x: dropX, y: dropY, width: 200, height: 100, rotation: 0, zIndex: 1, opacity: 1,
        content: item.type === 'text' ? (item.subType === 'heading' ? 'Heading' : 'Text') : '',
        fillColor: item.type === 'shape' ? '#e2e8f0' : 'transparent',
        fontSize: 24, color: '#000000'
      };
      
      const updatedSlides = slides.map((slide, i) => {
        if (i !== currentSlideIndex) return slide;
        return { ...slide, elements: [...slide.elements, newElement] };
      });
      setSlides(updatedSlides);
      setSelectedElementId(id);
  };

  const deleteElement = (id: string) => {
      const updatedSlides = slides.map((slide, i) => {
        if (i !== currentSlideIndex) return slide;
        return { ...slide, elements: slide.elements.filter(el => el.id !== id) };
      });
      setSlides(updatedSlides);
      setSelectedElementId(null);
  };

  const addSlide = () => {
    const newSlide: Slide = { id: Date.now().toString(), elements: [], backgroundColor: "#ffffff" };
    setSlides([...slides, newSlide]);
    setCurrentSlideIndex(slides.length);
  };
  
  const deleteSlide = (index: number) => {
    if (slides.length <= 1) return;
    const newSlides = slides.filter((_, i) => i !== index);
    setSlides(newSlides);
    if (currentSlideIndex >= index && currentSlideIndex > 0) setCurrentSlideIndex(currentSlideIndex - 1);
  };

  const duplicateSlide = (index: number) => {
     // Logic duplicate...
  };

  const handleSave = async () => {
      // Logic save...
  };

  return {
    state: { slides, currentSlideIndex, currentSlide, selectedElementId, selectedElement, zoom, draggedItem, isSidebarOpen, projectName, loading },
    refs: { canvasRef, slideCanvasRef },
    actions: {
      setSlides, setCurrentSlideIndex, setSelectedElementId, setZoom, setDraggedItem, setIsSidebarOpen,
      addSlide, deleteSlide, duplicateSlide, addElement, updateElement, deleteElement, handleSave, handleElementSelectFromCanvas
    }
  };
};