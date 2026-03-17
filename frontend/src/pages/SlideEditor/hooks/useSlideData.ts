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
            let defs: string | undefined = undefined;

            const htmlForCanvas = s.html_content || '';
            const parsedDesignSettings = parseSlideDesignSettings(s.design_settings);
            const { backgroundColor, backgroundImage } = resolveSlideBackground(parsedDesignSettings, htmlForCanvas);

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
  }, [projectId, toast]);

  return {
    slides,
    setSlides,
    projectName,
    loading
  };
};
