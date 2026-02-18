import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { CheckCircle2, Loader2, AlertCircle, RefreshCw, Home, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/AppLayout";
import { cn } from "@/lib/utils";

interface SlideThumb {
  index: number;
  html: string;
  title?: string;
}

const stages = [
  { id: "analyze", label: "Analyze Content", icon: "📊" },
  { id: "prepare", label: "Prepare Content", icon: "📝" },
  { id: "design", label: "Design Slides", icon: "🎨" },
];

const Streaming = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();

  const [currentStage, setCurrentStage] = useState(0);
  const [progress, setProgress] = useState(0);
  const [activity, setActivity] = useState("Initializing...");
  const [slides, setSlides] = useState<SlideThumb[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [completed, setCompleted] = useState(false);
  const [previewSlide, setPreviewSlide] = useState<SlideThumb | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);

  const startStreaming = () => {
    setError(null);
    setCompleted(false);
    setProgress(0);
    setCurrentStage(0);
    setSlides([]);
    setActivity("Connecting...");

    // Get filename from location state (passed from upload page)
    const filename = location.state?.filename;
    const sessionId = location.state?.sessionId;
    
    if (!filename && !sessionId) {
      setError("No file or session specified for streaming. Please upload a file first.");
      return;
    }

    // Use either manual structure stream or docx stream based on what we have
    const url = sessionId 
      ? api.manualStreamUrl(sessionId)
      : api.streamUrl(filename);

    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.addEventListener("status", (e) => {
      const data = JSON.parse(e.data);
      setActivity(data.message || data.status);
      const stageIdx = stages.findIndex((s) => s.id === data.stage);
      if (stageIdx >= 0) setCurrentStage(stageIdx);
    });

    es.addEventListener("progress", (e) => {
      const data = JSON.parse(e.data);
      setProgress(data.progress || 0);
      if (data.message) setActivity(data.message);
    });

    es.addEventListener("slide_completed", (e) => {
      const data = JSON.parse(e.data);
      // Backend sends html_path for temp files, need to fetch content via API
      const slideIndex = data.slide_index ?? data.index ?? slides.length;
      const slideTitle = data.title || `Slide ${slideIndex + 1}`;
      
      // If html is provided directly, use it; otherwise show placeholder
      const htmlContent = data.html || `<div class="p-4 text-center">
        <p class="text-lg font-semibold">${slideTitle}</p>
        <p class="text-sm text-muted-foreground">Slide ${slideIndex + 1} completed</p>
      </div>`;
      
      setSlides((prev) => [...prev, { index: slideIndex, html: htmlContent, title: slideTitle }]);
    });

    es.addEventListener("complete", (e) => {
      const data = JSON.parse(e.data);
      setCompleted(true);
      setProgress(100);
      setCurrentStage(2);
      setActivity(`Generation complete! ${data.total_slides || 0} slides created.`);
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
      setError(data.message || "An error occurred");
      es.close();
    });

    es.onerror = () => {
      if (!completed) {
        setError("Connection lost. Please try again.");
        es.close();
      }
    };
  };

  useEffect(() => {
    startStreaming();
    return () => eventSourceRef.current?.close();
  }, []);

  const finalProjectId = (window as any).__streamProjectId || projectId;

  return (
    <AppLayout>
      <div className="mx-auto max-w-4xl px-4 py-10">
        <h1 className="mb-8 text-center text-2xl font-bold">
          <span className="gradient-text">Generating Your Slides</span>
        </h1>

        {/* Stages */}
        <div className="mb-8 flex items-center justify-center gap-2">
          {stages.map((stage, i) => (
            <div key={stage.id} className="flex items-center gap-2">
              <div className={cn(
                "flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-all",
                i < currentStage ? "bg-success/20 text-success" :
                i === currentStage ? "gradient-primary text-primary-foreground" :
                "bg-muted text-muted-foreground"
              )}>
                {i < currentStage ? <CheckCircle2 className="h-4 w-4" /> :
                 i === currentStage ? <Loader2 className="h-4 w-4 animate-spin" /> :
                 <span>{stage.icon}</span>}
                <span className="hidden sm:inline">{stage.label}</span>
              </div>
              {i < stages.length - 1 && <div className="h-px w-8 bg-border" />}
            </div>
          ))}
        </div>

        {/* Progress */}
        <Card className="glass mb-8">
          <CardContent className="p-6">
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="text-muted-foreground">{activity}</span>
              <span className="font-mono font-medium">{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-3" />
          </CardContent>
        </Card>

        {/* Error */}
        {error && (
          <Card className="mb-8 border-destructive/50 bg-destructive/10">
            <CardContent className="flex items-center justify-between p-4">
              <div className="flex items-center gap-3">
                <AlertCircle className="h-5 w-5 text-destructive" />
                <p className="text-sm">{error}</p>
              </div>
              <Button variant="outline" size="sm" onClick={startStreaming}>
                <RefreshCw className="mr-2 h-4 w-4" /> Retry
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Slide thumbnails */}
        {slides.length > 0 && (
          <div>
            <h2 className="mb-4 text-lg font-semibold">Generated Slides ({slides.length})</h2>
            <div className="grid gap-4 grid-cols-2 sm:grid-cols-3 md:grid-cols-4">
              {slides.map((slide) => (
                <Card
                  key={slide.index}
                  className="glass cursor-pointer transition-all hover:shadow-lg hover:-translate-y-0.5"
                  onClick={() => setPreviewSlide(slide)}
                >
                  <CardContent className="p-3">
                    <div className="aspect-video overflow-hidden rounded bg-muted">
                      <iframe
                        srcDoc={slide.html}
                        className="w-full h-full border-0 pointer-events-none"
                        title={`Slide ${slide.index + 1} preview`}
                        sandbox="allow-same-origin"
                      />
                    </div>
                    <p className="mt-2 truncate text-xs text-muted-foreground">
                      Slide {slide.index + 1}{slide.title ? `: ${slide.title}` : ""}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Completion actions */}
        {completed && (
          <div className="mt-8 flex justify-center gap-4 animate-fade-in">
            <Button onClick={() => navigate(`/editor/${finalProjectId}`)}>
              <Edit2Icon className="mr-2 h-4 w-4" /> Open Editor
            </Button>
            <Button variant="outline" onClick={() => navigate("/")}>
              <Home className="mr-2 h-4 w-4" /> Go Home
            </Button>
          </div>
        )}
      </div>

      {/* Preview modal */}
      <Dialog open={!!previewSlide} onOpenChange={() => setPreviewSlide(null)}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Slide {previewSlide ? previewSlide.index + 1 : ""}</DialogTitle>
          </DialogHeader>
          <div className="aspect-video overflow-hidden rounded-lg bg-muted">
            {previewSlide && (
              <iframe
                srcDoc={previewSlide.html}
                className="w-full h-full border-0"
                title={`Slide ${previewSlide.index + 1}`}
                sandbox="allow-same-origin"
              />
            )}
          </div>
        </DialogContent>
      </Dialog>
    </AppLayout>
  );
};

// Small inline icon since we use Edit2 in completion
const Edit2Icon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17 3a2.83 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
    <path d="m15 5 4 4" />
  </svg>
);

export default Streaming;
