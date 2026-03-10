import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import type { Slide, SlideElement } from "../types";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "../constants";
import { parseHtmlToElements } from "../utils";

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
    { id: "1", elements: [], backgroundColor: "#ffffff" }
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

              // Fallback: create default element
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
  }, [projectId, toast]);

  return {
    slides,
    setSlides,
    projectName,
    loading
  };
};
