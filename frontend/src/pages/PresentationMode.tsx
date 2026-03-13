import { useState, useEffect, useCallback, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ChevronLeft, ChevronRight, X, Maximize } from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { ReadOnlySlide } from "@/components/ReadOnlySlide";
import { useLanguage } from "@/contexts/LanguageContext";

const PresentationMode = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [slides, setSlides] = useState<any[]>([]);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);
  const hideTimer = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    loadSlides();
  }, [projectId]);

  const loadSlides = async () => {
    try {
      const data = await api.getSlides(projectId!);
      const mapped = (data?.slides ?? []).map((s: any) => {
        let backgroundColor = '#ffffff';
        let backgroundImage: string | undefined;
        if (s.design_settings) {
          try {
            const ds = typeof s.design_settings === 'string' ? JSON.parse(s.design_settings) : s.design_settings;
            if (ds?.backgroundColor) backgroundColor = ds.backgroundColor;
            if (ds?.backgroundImage) backgroundImage = ds.backgroundImage;
          } catch { /* ignore */ }
        }
        return { ...s, backgroundColor, backgroundImage, html: s.html_content || '' };
      });
      setSlides(mapped);
    } catch { /* fallback */ }
  };

  const next = useCallback(() => setCurrentSlide((c) => Math.min(c + 1, slides.length - 1)), [slides.length]);
  const prev = useCallback(() => setCurrentSlide((c) => Math.max(c - 1, 0)), []);

  const enterFullscreen = async () => {
    try {
      await containerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } catch { /* ignore */ }
  };

  const exitPresentation = () => {
    if (document.fullscreenElement) document.exitFullscreen();
    navigate(-1);
  };

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === " ") { e.preventDefault(); next(); }
      if (e.key === "ArrowLeft") { e.preventDefault(); prev(); }
      if (e.key === "Escape") exitPresentation();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [next, prev]);

  useEffect(() => {
    const handleFullscreenChange = () => {
      if (!document.fullscreenElement) setIsFullscreen(false);
    };
    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => document.removeEventListener("fullscreenchange", handleFullscreenChange);
  }, []);

  // Hide cursor after inactivity
  const handleMouseMove = () => {
    setShowControls(true);
    if (hideTimer.current) clearTimeout(hideTimer.current);
    hideTimer.current = setTimeout(() => setShowControls(false), 3000);
  };

  useEffect(() => {
    enterFullscreen();
  }, []);

  const currentSlideData = slides[currentSlide];
  const html = currentSlideData?.html || '';

  return (
    <div
      ref={containerRef}
      className="relative flex h-screen w-screen items-center justify-center bg-background"
      onMouseMove={handleMouseMove}
      style={{ cursor: showControls ? "default" : "none" }}
    >
      {/* Slide content */}
      <div className="relative h-full w-full flex items-center justify-center">
        {html ? (
          <ReadOnlySlide
            slideId={`present-${currentSlide}`}
            htmlContent={html}
            backgroundColor={currentSlideData?.backgroundColor}
            className="w-full h-full"
          />
        ) : (
          <div className="text-center text-muted-foreground">
            <p className="text-2xl font-bold">{t.present_slide} {currentSlide + 1}</p>
            <p className="text-sm">{t.present_no_content}</p>
          </div>
        )}
      </div>

      {/* Click zones */}
      <div className="absolute inset-y-0 left-0 w-1/4 cursor-pointer" onClick={prev} />
      <div className="absolute inset-y-0 right-0 w-1/4 cursor-pointer" onClick={next} />

      {/* Side navigation arrows */}
      {currentSlide > 0 && (
        <button
          onClick={prev}
          className={cn(
            "absolute left-4 top-1/2 -translate-y-1/2 z-20 flex items-center justify-center rounded-full bg-black/30 hover:bg-black/50 backdrop-blur-sm transition-all duration-200 w-12 h-12",
            showControls ? "opacity-80" : "opacity-0"
          )}
        >
          <ChevronLeft className="h-7 w-7 text-white" />
        </button>
      )}
      {currentSlide < slides.length - 1 && (
        <button
          onClick={next}
          className={cn(
            "absolute right-4 top-1/2 -translate-y-1/2 z-20 flex items-center justify-center rounded-full bg-black/30 hover:bg-black/50 backdrop-blur-sm transition-all duration-200 w-12 h-12",
            showControls ? "opacity-80" : "opacity-0"
          )}
        >
          <ChevronRight className="h-7 w-7 text-white" />
        </button>
      )}

      {/* Controls overlay */}
      <div className={cn(
        "absolute inset-x-0 bottom-0 transition-opacity duration-300",
        showControls ? "opacity-100" : "opacity-0"
      )}>
        {/* Slide counter */}
        <div className="absolute right-4 top-[-2rem] rounded-full bg-card/80 px-3 py-1 text-xs font-mono backdrop-blur">
          {currentSlide + 1} / {slides.length || 1}
        </div>

        {/* Timeline scrubber */}
        <div className="flex items-center gap-1 bg-card/80 p-2 backdrop-blur">
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={prev}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <div className="flex flex-1 gap-1 overflow-auto">
            {slides.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentSlide(i)}
                className={cn(
                  "h-2 flex-1 rounded-full transition-all",
                  i === currentSlide ? "gradient-primary" : "bg-muted hover:bg-muted-foreground/30"
                )}
              />
            ))}
          </div>
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={next}>
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={exitPresentation}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Fullscreen button */}
      {!isFullscreen && showControls && (
        <Button variant="outline" size="icon" className="absolute right-4 top-4" onClick={enterFullscreen}>
          <Maximize className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
};

export default PresentationMode;
