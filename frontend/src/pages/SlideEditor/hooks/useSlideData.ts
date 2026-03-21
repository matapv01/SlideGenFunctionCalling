import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { parseSlideDesignSettings, resolveSlideBackground } from "@/lib/slideBackground";
import type { Slide, SlideElement } from "../types";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "../constants";

interface UseSlideDataReturn {
  slides: Slide[];
  setSlides: React.Dispatch<React.SetStateAction<Slide[]>>;
  projectName: string;
  loading: boolean;
}

/**
 * Hook để load project và slides từ API
 */
export const useSlideData = (projectId: string | undefined): UseSlideDataReturn => {
  const { toast } = useToast();
  const [slides, setSlides] = useState<Slide[]>([
    { id: "__init__", elements: [], backgroundColor: "#ffffff" }
  ]);
  const [projectName, setProjectName] = useState("Untitled Project");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!projectId) return;

    const loadData = async () => {
      console.log('📦 [useSlideData] ========== BẮT ĐẦU LOAD DATA ==========');
      console.log('📦 [useSlideData] projectId:', projectId);
      try {
        setLoading(true);
        
        // Fetch project details
        try {
          console.log('📡 [useSlideData] Gọi api.getProject(', projectId, ')...');
          const project = await api.getProject(projectId);
          console.log('📡 [useSlideData] Project response:', JSON.stringify(project, null, 2));
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
        console.log('📡 [useSlideData] Gọi api.getSlides(', projectId, ')...');
        const slidesResponse = await api.getSlides(projectId);
        console.log('📡 [useSlideData] Slides response: total =', slidesResponse?.total, ', slides count =', slidesResponse?.slides?.length);
        
        if (slidesResponse?.slides && Array.isArray(slidesResponse.slides)) {
          const mappedSlides: Slide[] = slidesResponse.slides.map((s: any, slideIdx: number) => {
            console.log(`\n🎴 [useSlideData] --- Slide ${slideIdx + 1} (id=${s.id}) ---`);
            console.log('🎴 [useSlideData] Raw slide keys:', Object.keys(s));
            console.log('🎴 [useSlideData] slide.title:', s.title);
            console.log('🎴 [useSlideData] slide.slide_type:', s.slide_type);
            console.log('🎴 [useSlideData] slide.html_content length:', s.html_content?.length || 0);
            console.log('🎴 [useSlideData] slide.html_content (first 500 chars):', (s.html_content || '').substring(0, 500));
            console.log('🎴 [useSlideData] slide.design_settings type:', typeof s.design_settings);
            console.log('🎴 [useSlideData] slide.design_settings:', JSON.stringify(s.design_settings)?.substring(0, 500));
            
            let defs: string | undefined = undefined;

            const htmlForCanvas = s.html_content || '';
            console.log('🎨 [useSlideData] Parsing design_settings...');
            const parsedDesignSettings = parseSlideDesignSettings(s.design_settings);
            console.log('🎨 [useSlideData] Parsed design_settings:', JSON.stringify(parsedDesignSettings)?.substring(0, 500));
            
            console.log('🎨 [useSlideData] Resolving background...');
            const { backgroundColor, backgroundImage } = resolveSlideBackground(parsedDesignSettings, htmlForCanvas);
            console.log('🎨 [useSlideData] Resolved bg:', { backgroundColor, backgroundImage: backgroundImage?.substring(0, 100) });

            // Extract metadata (backgroundColor etc.) from design_settings
            if (parsedDesignSettings && typeof parsedDesignSettings === 'object') {
              if (parsedDesignSettings.defs) defs = String(parsedDesignSettings.defs);
            } else if (s.design_settings) {
              console.error("Failed to parse design_settings for slide", s.id);
            }

            // html_content is the authoritative visual source — always rendered as a
            // single full-canvas element so nothing is lost between saves.
            const elements: SlideElement[] = htmlForCanvas
              ? [{
                  id: `canvas-${s.id}`,
                  type: 'text' as const,
                  content: htmlForCanvas,
                  x: 0,
                  y: 0,
                  width: CANVAS_WIDTH,
                  height: CANVAS_HEIGHT,
                  rotation: 0,
                  zIndex: 1,
                  opacity: 1,
                }]
              : [];

            const mappedSlide = {
              id: String(s.id),
              elements,
              backgroundColor,
              backgroundImage,
              notes: s.notes,
              defs
            };
            console.log('✅ [useSlideData] Mapped slide:', {
              id: mappedSlide.id,
              elementsCount: mappedSlide.elements.length,
              firstElementContentLength: mappedSlide.elements[0]?.content?.length || 0,
              backgroundColor: mappedSlide.backgroundColor,
              backgroundImage: mappedSlide.backgroundImage?.substring(0, 80),
              hasDefs: !!mappedSlide.defs,
            });
            return mappedSlide;
          });
          
          console.log('\n📊 [useSlideData] ========== KẾT QUẢ LOAD ==========');
          console.log('📊 [useSlideData] Total slides mapped:', mappedSlides.length);
          mappedSlides.forEach((ms, i) => {
            console.log(`📊 [useSlideData] Slide ${i+1}: id=${ms.id}, bg=${ms.backgroundColor}, elements=${ms.elements.length}, contentLen=${ms.elements[0]?.content?.length || 0}`);
          });
          if (mappedSlides.length > 0) {
            setSlides(mappedSlides);
            console.log('✅ [useSlideData] setSlides() called with', mappedSlides.length, 'slides');
          } else {
            console.warn('⚠️ [useSlideData] No slides mapped, keeping default slide');
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
        console.log('📦 [useSlideData] ========== LOAD DATA XONG ==========\n');
      }
    };
    
    loadData();
  }, [projectId, toast]);

  return {
    slides,
    setSlides,
    projectName,
    loading
  };
};
