import { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { CheckCircle2, Loader2, AlertCircle, RefreshCw, Home, Eye, FileText, Sparkles, PenTool, ExternalLink, Presentation, X, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/AppLayout";
import { cn } from "@/lib/utils";
import { ScaledSlidePreview } from "@/components/ScaledSlidePreview";
import { ReadOnlySlide } from "@/components/ReadOnlySlide";
import { useLanguage } from "@/contexts/LanguageContext";

interface SlideThumb {
  index: number;
  html: string;
  title?: string;
}

const Streaming = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const { t } = useLanguage();

  const stages = [
    { id: "analyze", label: t.streaming_stage_analyze, icon: FileText },
    { id: "prepare", label: t.streaming_stage_prepare, icon: Sparkles },
    { id: "design", label: t.streaming_stage_design, icon: PenTool },
  ];

  const [currentStage, setCurrentStage] = useState(0);
  const [progress, setProgress] = useState(0);
  const [activity, setActivity] = useState(t.streaming_initializing);
  const [slides, setSlides] = useState<SlideThumb[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [completed, setCompleted] = useState(false);
  const [previewSlide, setPreviewSlide] = useState<SlideThumb | null>(null);
  const [isPresentMode, setIsPresentMode] = useState(false);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [ideaSessionId, setIdeaSessionId] = useState<string | null>(null);
  const [isPreparingIdea, setIsPreparingIdea] = useState(false);
  const [totalSlides, setTotalSlides] = useState<number | string>('...');
  
  const updateStage = (newStage: number) => {
    setCurrentStage(prev => Math.max(prev, newStage));
  };

  const eventSourceRef = useRef<EventSource | null>(null);
  
  const translateBackendMessage = (msg: string | undefined): string => {
    if (!msg) return "";
    const lowerMsg = msg.toLowerCase();
    
    // Process "Completed X/Y slides" pattern
    const slideMatch = lowerMsg.match(/completed (\d+)\/(\d+) slides/);
    if (slideMatch) {
      const total = slideMatch[2];
      setTotalSlides(total);
      return `${t.streaming_slide_completed} ${slideMatch[1]}/${total} ${t.streaming_slides_unit}`;
    }

    if (lowerMsg.includes("analyzing content")) return t.streaming_msg_analyzing;
    if (lowerMsg.includes("processing document structure")) return t.streaming_msg_processing_struct;
    if (lowerMsg.includes("generating document structure")) return t.streaming_msg_generating_struct;
    if (lowerMsg.includes("booting system")) return t.streaming_msg_booting;
    if (lowerMsg.includes("initializing infrastructure")) return t.streaming_msg_initializing_infra;
    if (lowerMsg.includes("starting slide generation")) return t.streaming_msg_starting_generation;
    if (lowerMsg.includes("generating slides")) return t.streaming_msg_generating_slides;
    if (lowerMsg.includes("no slides were created")) return t.streaming_msg_no_slides;
    if (lowerMsg.includes("system ready")) return t.streaming_msg_ready;
    return msg;
  };

  const startStreaming = () => {
    setError(null);
    setCompleted(false);
    setProgress(0);
    setCurrentStage(0);
    setSlides([]);
    setActivity(t.streaming_connecting);

    // Get parameters from location state
    const filename = location.state?.filename;
    const sessionId = location.state?.sessionId || ideaSessionId;
    
    if (!filename && !sessionId) {
      setError(t.streaming_err_no_file);
      return;
    }

    // Determine which stream URL to use
    let url: string;
    if (ideaSessionId) {
      // Idea workflow
      url = api.ideaStreamUrl(ideaSessionId);
    } else if (sessionId) {
      // Manual structure workflow
      url = api.manualStreamUrl(sessionId);
    } else {
      // DOCX workflow
      url = api.streamUrl(filename);
    }

    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.addEventListener("status", (e) => {
      const data = JSON.parse(e.data);
      const translatedMsg = translateBackendMessage(data.message);
      setActivity(translatedMsg || data.description || data.status);
      
      // Map backend messages to frontend stage
      // Stage 0 = Analyze Content, Stage 1 = Prepare Content, Stage 2 = Design Slides
      const message = (data.message || '').toLowerCase();
      const title = (data.title || '').toLowerCase();
      
      // STRICT Stage mapping logic
      // Priority 1: Check Step number (most reliable)
      if (data.step !== undefined) {
        if (data.step === 1 || data.step === 2) {
          updateStage(0);
        } else if (data.step === 3) {
          // Inside Step 3 (Planner/Generator), only move to Stage 1 after planning confirms design phase
          if (title.includes('design slides') || title.includes('creating') || title.includes('generation')) {
            updateStage(1);
          } else {
            updateStage(0); // STAY IN STAGE 0 (Analyze) during all analysis & planning
          }
        }
      } 
      // Priority 2: Title keywords (only if step is missing or for specific markers)
      else if (title.includes('design slides') || title.includes('creating')) {
        updateStage(1);
      } else if (title.includes('prepare')) {
        updateStage(0);
      } else if (title.includes('analyze') || title.includes('starting')) {
        updateStage(0);
      } 
      // Priority 3: Fallback to stage field
      else {
        const stageIdx = stages.findIndex((s) => s.id === data.stage);
        if (stageIdx >= 0) updateStage(stageIdx);
      }
    });
    
    es.addEventListener("progress", (e) => {
      const data = JSON.parse(e.data);
      setProgress(data.progress || data.percentage || 0);
      if (data.message) setActivity(translateBackendMessage(data.message));
      
      // When we receive progress events about slide completion, we're in Design stage
      const message = (data.message || '').toLowerCase();
      if (message.includes('completed') && message.includes('/')) {
        updateStage(2); // Design Slides - actively creating slides
      }
    });

    es.addEventListener("slide_completed", async (e) => {
      const data = JSON.parse(e.data);
      const slideIndex = data.slide_index ?? data.index ?? slides.length;
      const slideTitle = data.title || `Slide ${slideIndex + 1}`;
      
      let htmlContent = data.html;
      
      // If html_path is provided, fetch the actual HTML content from the temp file
      if (!htmlContent && data.html_path) {
        try {
          const response = await fetch(api.getTempFileUrl(data.html_path));
          if (response.ok) {
            htmlContent = await response.text();
          }
        } catch (err) {
          console.error("Failed to fetch slide HTML:", err);
        }
      }
      
      // Fallback placeholder if fetch fails
      if (!htmlContent) {
        htmlContent = `<div class="p-4 text-center">
          <p class="text-lg font-semibold">${slideTitle}</p>
          <p class="text-sm text-muted-foreground">Slide ${slideIndex + 1} completed</p>
        </div>`;
      }
      
      setSlides((prev) => [...prev, { index: slideIndex, html: htmlContent, title: slideTitle }]);
    });

    es.addEventListener("complete", (e) => {
      const data = JSON.parse(e.data);
      const total = data.total_slides || slides.length;
      setCompleted(true);
      setProgress(100);
      setCurrentStage(stages.length);
      setTotalSlides(total);
      setActivity(`${t.streaming_done} ${total} ${t.streaming_slides_unit}`);
      es.close();
      // Store project_id for navigation
      if (data.project_id) {
        (window as any).__streamProjectId = data.project_id;
      }
      // Also store temp_dir for cleanup if needed
      if (data.temp_dir) {
        (window as any).__streamTempDir = data.temp_dir;
      }
    });

    es.addEventListener("error_event", (e) => {
      const data = JSON.parse(e.data);
      setError(data.message || t.streaming_err_generic);
      es.close();
    });

    es.onerror = () => {
      if (!completed) {
        // Redirect to slidegen page when connection lost
        navigate("/slidegen", { replace: true });
      }
    };
  };

  // Handle idea workflow - prepare structure first
  useEffect(() => {
    const title = location.state?.title;
    const description = location.state?.description;
    const enableTransitions = location.state?.enableTransitions ?? true;
    const enableThankYou = location.state?.enableThankYou ?? true;
    const contentLength = location.state?.contentLength || "standard";

    // Check if this is an idea workflow
    if (title && description) {
      setIsPreparingIdea(true);
      setActivity(t.streaming_preparing_activity);
      
      api.generateIdeaStructure({
        title: title,
        prompt: description,
        content_length: contentLength,
        enable_transition_slides: enableTransitions,
        enable_thank_you_slide: enableThankYou,
      })
        .then((response) => {
          setIdeaSessionId(response.session_id);
          setIsPreparingIdea(false);
          toast({ title: t.streaming_toast_ready, description: t.streaming_toast_starting });
        })
        .catch((err) => {
          setError(err.message || t.streaming_err_prepare);
          setIsPreparingIdea(false);
          toast({ title: t.streaming_toast_failed, description: err.message, variant: "destructive" });
        });
      return;
    }
  }, []);

  // Start streaming when we have the necessary data
  useEffect(() => {
    const filename = location.state?.filename;
    const sessionId = location.state?.sessionId;
    const title = location.state?.title;
    
    // No state means user navigated back - redirect to slidegen
    if (!filename && !sessionId && !title && !ideaSessionId) {
      navigate("/slidegen", { replace: true });
      return;
    }
    
    // For idea workflow, wait until we have the session ID
    if (title && !ideaSessionId) {
      return; // Still preparing
    }
    
    // Start streaming for all workflows
    if (filename || sessionId || ideaSessionId) {
      startStreaming();
    }
    
    return () => eventSourceRef.current?.close();
  }, [ideaSessionId]);

  // Centralized keyboard navigation for Presentation and Preview modes
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (isPresentMode) {
          exitPresentation();
        } else if (previewSlide) {
          setPreviewSlide(null);
        }
        return;
      }

      if (isPresentMode) {
        switch (e.key) {
          case "ArrowRight":
          case " ":
            e.preventDefault();
            setCurrentSlideIndex((prev) => Math.min(prev + 1, slides.length - 1));
            break;
          case "ArrowLeft":
            e.preventDefault();
            setCurrentSlideIndex((prev) => Math.max(prev - 1, 0));
            break;
          case "Home":
            e.preventDefault();
            setCurrentSlideIndex(0);
            break;
          case "End":
            e.preventDefault();
            setCurrentSlideIndex(slides.length - 1);
            break;
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isPresentMode, previewSlide, slides.length]);

  // Listen for fullscreen exit
  useEffect(() => {
    const handleFullscreenChange = () => {
      if (!document.fullscreenElement && isPresentMode) {
        setIsPresentMode(false);
      }
    };
    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => document.removeEventListener("fullscreenchange", handleFullscreenChange);
  }, [isPresentMode]);

  const finalProjectId = (window as any).__streamProjectId || projectId;

  const startPresentation = async (startIndex: number = 0) => {
    setCurrentSlideIndex(startIndex);
    setIsPresentMode(true);
    // Request fullscreen
    try {
      await document.documentElement.requestFullscreen();
    } catch (err) {
      // Fullscreen not supported or denied
    }
  };

  const exitPresentation = async () => {
    setIsPresentMode(false);
    // Exit fullscreen if active
    if (document.fullscreenElement) {
      try {
        await document.exitFullscreen();
      } catch (err) {
        // Ignore errors
      }
    }
  };

  // Get status label for stage
  const getStageStatus = (stageIndex: number) => {
    if (stageIndex < currentStage) return t.streaming_stage_completed_label;
    if (stageIndex === currentStage) return t.streaming_stage_processing;
    return t.streaming_stage_pending;
  };

  return (
    <AppLayout>
      {/* Animated background */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-violet-500/10 via-transparent to-transparent rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-emerald-500/10 via-transparent to-transparent rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      <div className="mx-auto max-w-4xl px-4 py-10">
        {/* Header with animated sparkles */}
        <div className="mb-10 text-center relative">
          <div className="inline-flex items-center gap-2 mb-2">
            <Sparkles className="h-8 w-8 text-violet-500 animate-pulse" />
            <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
              SlideGen AI
            </h1>
          </div>
          <p className="text-muted-foreground animate-fade-in">
          {completed ? t.streaming_completed : isPreparingIdea ? t.streaming_preparing : t.streaming_creating}
          </p>
        </div>

        {/* Animated Stage Indicators */}
        <div className="mb-10 flex items-center justify-center gap-4 sm:gap-8">
          {stages.map((stage, i) => {
            const Icon = stage.icon;
            const isCompleted = i < currentStage;
            const isActive = i === currentStage;
            const isPending = i > currentStage;
            
            return (
              <div key={stage.id} className="flex items-center gap-4">
                {/* Stage Circle */}
                <div className="flex flex-col items-center gap-2">
                  <div className="relative">
                    {/* Animated ring for active state */}
                    {isActive && (
                      <>
                        <div className="absolute inset-0 rounded-full bg-emerald-400/30 animate-ping" />
                        <div className="absolute -inset-1 rounded-full bg-gradient-to-r from-emerald-400 to-teal-400 opacity-50 blur-sm animate-pulse" />
                      </>
                    )}
                    
                    {/* Completed glow */}
                    {isCompleted && (
                      <div className="absolute -inset-1 rounded-full bg-emerald-400/40 blur-md" />
                    )}
                    
                    {/* Circle */}
                    <div className={cn(
                      "relative w-16 h-16 sm:w-20 sm:h-20 rounded-full flex items-center justify-center transition-all duration-500 shadow-lg",
                      isCompleted && "bg-gradient-to-br from-emerald-400 to-teal-500 text-white scale-100",
                      isActive && "bg-gradient-to-br from-emerald-400 to-teal-500 text-white scale-110",
                      isPending && "bg-muted/50 text-muted-foreground border-2 border-dashed border-muted-foreground/30"
                    )}>
                      {isCompleted ? (
                        <CheckCircle2 className="h-8 w-8 sm:h-10 sm:w-10 drop-shadow-md animate-scale-in" />
                      ) : isActive ? (
                        <div className="relative">
                          <Icon className="h-8 w-8 sm:h-10 sm:w-10 drop-shadow-md animate-bounce" />
                        </div>
                      ) : (
                        <Icon className="h-6 w-6 sm:h-8 sm:w-8 opacity-50" />
                      )}
                    </div>
                  </div>
                  
                  {/* Stage Label */}
                  <div className="text-center">
                    <p className={cn(
                      "text-xs sm:text-sm font-medium transition-colors",
                      isCompleted && "text-emerald-600 dark:text-emerald-400",
                      isActive && "text-emerald-600 dark:text-emerald-400",
                      isPending && "text-muted-foreground"
                    )}>
                      {stage.label}
                    </p>
                    <p className={cn(
                      "text-xs transition-colors",
                      isCompleted && "text-emerald-500",
                      isActive && "text-emerald-500 animate-pulse",
                      isPending && "text-muted-foreground/60"
                    )}>
                      {getStageStatus(i)}
                    </p>
                  </div>
                </div>
                
                {/* Connector Line */}
                {i < stages.length - 1 && (
                  <div className="relative w-12 sm:w-20 h-1 -mt-8">
                    <div className="absolute inset-0 bg-muted rounded-full" />
                    <div 
                      className={cn(
                        "absolute inset-y-0 left-0 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-full transition-all duration-700",
                        isCompleted ? "w-full" : isActive ? "w-1/2 animate-pulse" : "w-0"
                      )} 
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Progress Card with Glass Effect */}
        <Card className="mb-8 overflow-hidden bg-gradient-to-r from-white/80 to-white/60 dark:from-gray-900/80 dark:to-gray-900/60 backdrop-blur-xl border border-white/20 shadow-xl">
          <CardContent className="p-6">
            {/* Progress Bar */}
            <div className="relative mb-4">
              <div className="h-4 bg-muted/50 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 rounded-full transition-all duration-500 relative"
                  style={{ width: `${progress}%` }}
                >
                  {/* Shimmer effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
                </div>
              </div>
              <span className="absolute right-0 -top-6 text-sm font-mono font-bold text-emerald-600 dark:text-emerald-400">
                {Math.round(progress)}%
              </span>
            </div>

            {/* Status Message */}
            {completed ? (
              <div className="flex items-center gap-3 p-4 bg-emerald-50 dark:bg-emerald-950/30 rounded-lg border border-emerald-200 dark:border-emerald-800">
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center animate-bounce">
                  <span className="text-xl">🎉</span>
                </div>
                <div>
                  <p className="font-semibold text-emerald-700 dark:text-emerald-300">{t.streaming_done}</p>
                  <p className="text-sm text-emerald-600/80 dark:text-emerald-400/80">
                    {t.streaming_slides_created} {slides.length} {t.streaming_slides_unit}
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3 text-muted-foreground">
                <Loader2 className="h-5 w-5 animate-spin text-emerald-500" />
                <span className="text-sm">{activity}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Error */}
        {error && (
          <Card className="mb-8 border-destructive/50 bg-destructive/10 animate-shake">
            <CardContent className="flex items-center justify-between p-4">
              <div className="flex items-center gap-3">
                <AlertCircle className="h-5 w-5 text-destructive animate-pulse" />
                <p className="text-sm">{error}</p>
              </div>
              <Button variant="outline" size="sm" onClick={startStreaming} className="hover:bg-destructive/20">
                <RefreshCw className="mr-2 h-4 w-4" /> {t.streaming_retry}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Slide thumbnails */}
        {slides.length > 0 && (
          <div className="animate-fade-in">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                <FileText className="h-4 w-4 text-white" />
              </div>
              <h2 className="text-lg font-semibold">
                {t.streaming_slides_header} {slides.length}/{totalSlides}
              </h2>
            </div>
            
            <div className="grid gap-4 grid-cols-2 sm:grid-cols-3 md:grid-cols-4">
              {slides.map((slide, index) => (
                <Card
                  key={slide.index}
                  className="group cursor-pointer overflow-hidden bg-white dark:bg-gray-900 transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 hover:scale-[1.02] animate-slide-up"
                  style={{ animationDelay: `${index * 100}ms` }}
                  onClick={() => setPreviewSlide(slide)}
                >
                  {/* Colored header bar */}
                  <div className={cn(
                    "h-1.5",
                    index % 3 === 0 && "bg-gradient-to-r from-orange-400 to-amber-500",
                    index % 3 === 1 && "bg-gradient-to-r from-violet-500 to-purple-600",
                    index % 3 === 2 && "bg-gradient-to-r from-emerald-400 to-teal-500"
                  )} />
                  
                  <CardContent className="p-3">
                    {/* Slide label */}
                    <div className={cn(
                      "inline-block px-2 py-0.5 rounded text-xs font-semibold mb-2",
                      index % 3 === 0 && "bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-300",
                      index % 3 === 1 && "bg-violet-100 text-violet-700 dark:bg-violet-950 dark:text-violet-300",
                      index % 3 === 2 && "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
                    )}>
                      {t.streaming_slide_n} {slide.index + 1}
                    </div>
                    
                    {/* Thumbnail */}
                    <div className="aspect-video overflow-hidden rounded-lg bg-gradient-to-br from-muted/50 to-muted border relative">
                      <ScaledSlidePreview
                        html={slide.html}
                        title={`Slide ${slide.index + 1} preview`}
                        className="absolute inset-0"
                      />
                      
                      {/* Hover overlay */}
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100 z-10">
                        <Eye className="h-8 w-8 text-white drop-shadow-lg" />
                      </div>
                    </div>
                    
                    {/* Status badge */}
                    <div className="mt-2 flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      <span className="text-xs font-medium">{t.streaming_slide_completed}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Completion actions */}
        {completed && (
          <div className="mt-10 flex flex-col sm:flex-row justify-center gap-4 animate-fade-in">
            <Button 
              size="lg"
              onClick={() => navigate(`/editor/${finalProjectId}`)}
              className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all hover:scale-105"
            >
              <ExternalLink className="mr-2 h-4 w-4" /> {t.streaming_go_editor}
            </Button>
            <Button 
              size="lg"
              onClick={() => startPresentation(0)}
              className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white shadow-lg hover:shadow-xl transition-all hover:scale-105"
            >
              <Presentation className="mr-2 h-4 w-4" /> {t.streaming_present}
            </Button>
            <Button 
              size="lg"
              onClick={() => navigate("/slidegen")}
              className="border-2 border-violet-500 !text-violet-700 dark:!text-violet-300 bg-white dark:bg-gray-900 hover:bg-white dark:hover:bg-violet-950/50 hover:border-violet-500 transition-all hover:scale-105 shadow-md font-medium hover:!text-violet-700 dark:hover:!text-violet-300"
            >
              <Home className="mr-2 h-4 w-4" /> {t.streaming_back}
            </Button>
          </div>
        )}
      </div>

      {/* Preview modal */}
      <Dialog open={!!previewSlide} onOpenChange={() => setPreviewSlide(null)}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                <Eye className="h-4 w-4 text-white" />
              </div>
              {t.streaming_slide_n} {previewSlide ? previewSlide.index + 1 : ""}
              {previewSlide?.title && <span className="text-muted-foreground font-normal">- {previewSlide.title}</span>}
            </DialogTitle>
          </DialogHeader>
          <div className="aspect-video overflow-hidden rounded-xl bg-gradient-to-br from-muted/50 to-muted border-2 shadow-inner relative">
            {previewSlide && (
              <ScaledSlidePreview
                html={previewSlide.html}
                title={`Slide ${previewSlide.index + 1}`}
                className="absolute inset-0"
              />
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Custom CSS for animations */}
      <style>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        @keyframes scale-in {
          0% { transform: scale(0); opacity: 0; }
          100% { transform: scale(1); opacity: 1; }
        }
        
        @keyframes slide-up {
          0% { transform: translateY(20px); opacity: 0; }
          100% { transform: translateY(0); opacity: 1; }
        }
        
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }
        
        @keyframes fade-in {
          0% { opacity: 0; }
          100% { opacity: 1; }
        }
        
        .animate-shimmer {
          animation: shimmer 2s infinite;
        }
        
        .animate-scale-in {
          animation: scale-in 0.3s ease-out;
        }
        
        .animate-slide-up {
          animation: slide-up 0.5s ease-out forwards;
          opacity: 0;
        }
        
        .animate-shake {
          animation: shake 0.5s ease-in-out;
        }
        
        .animate-fade-in {
          animation: fade-in 0.5s ease-out;
        }
      `}</style>

      {/* Presentation Mode Overlay */}
      {isPresentMode && slides.length > 0 && createPortal(
        <div className="fixed inset-0 z-50 bg-black flex flex-col">
          {/* Top bar */}
          <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between p-4 bg-gradient-to-b from-black/50 to-transparent opacity-0 hover:opacity-100 transition-opacity">
            <span className="text-white text-sm">
              {t.streaming_slide_n} {currentSlideIndex + 1} / {slides.length}
            </span>
            <Button variant="ghost" size="icon" className="text-white hover:bg-white/20" onClick={() => exitPresentation()}>
              <X className="h-6 w-6" />
            </Button>
          </div>

          {/* Slide content - Full screen with maintained aspect ratio */}
          <div className="flex-1 flex items-center justify-center bg-black">
            <div className="w-full h-full relative">
              {slides[currentSlideIndex]?.html ? (
                <ReadOnlySlide
                  slideId={`present-${currentSlideIndex}`}
                  htmlContent={slides[currentSlideIndex].html}
                  className="w-full h-full"
                />
              ) : (
                <div className="flex h-full items-center justify-center text-gray-400">
                  {t.streaming_no_content}
                </div>
              )}
            </div>
          </div>

          {/* Navigation buttons */}
          <div className="absolute left-4 top-1/2 -translate-y-1/2">
            <Button
              variant="ghost"
              size="icon"
              className="h-12 w-12 text-white hover:bg-white/20 disabled:opacity-30"
              disabled={currentSlideIndex === 0}
              onClick={() => setCurrentSlideIndex((prev) => prev - 1)}
            >
              <ChevronLeft className="h-8 w-8" />
            </Button>
          </div>
          <div className="absolute right-4 top-1/2 -translate-y-1/2">
            <Button
              variant="ghost"
              size="icon"
              className="h-12 w-12 text-white hover:bg-white/20 disabled:opacity-30"
              disabled={currentSlideIndex === slides.length - 1}
              onClick={() => setCurrentSlideIndex((prev) => prev + 1)}
            >
              <ChevronRight className="h-8 w-8" />
            </Button>
          </div>

          {/* Bottom progress bar */}
          <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/50 to-transparent opacity-0 hover:opacity-100 transition-opacity">
            <div className="flex justify-center gap-2">
              {slides.map((_, i) => (
                <button
                  key={i}
                  className={`h-2 rounded-full transition-all ${
                    i === currentSlideIndex ? "w-8 bg-white" : "w-2 bg-white/50 hover:bg-white/80"
                  }`}
                  onClick={() => setCurrentSlideIndex(i)}
                />
              ))}
            </div>
            <p className="text-center text-white/60 text-xs mt-2">
              Use ← → or Space to navigate, ESC to exit
            </p>
          </div>
        </div>,
        document.body
      )}
    </AppLayout>
  );
};

export default Streaming;
