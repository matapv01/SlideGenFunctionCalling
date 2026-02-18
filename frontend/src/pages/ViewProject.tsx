import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Edit, Save, ArrowLeft, Play, X, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/AppLayout";

const ViewProject = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [slides, setSlides] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editSlide, setEditSlide] = useState<any>(null);
  const [editHtml, setEditHtml] = useState("");
  const [isPresentMode, setIsPresentMode] = useState(false);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);

  useEffect(() => {
    loadSlides();
  }, [projectId]);

  // Keyboard navigation for presentation mode
  useEffect(() => {
    if (!isPresentMode) return;

    const handleKeyDown = (e: KeyboardEvent) => {
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
        case "Escape":
          setIsPresentMode(false);
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
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isPresentMode, slides.length]);

  const startPresentation = (startIndex: number = 0) => {
    setCurrentSlideIndex(startIndex);
    setIsPresentMode(true);
  };

  const loadSlides = async () => {
    try {
      const res = await api.getSlides(projectId!);
      // Map backend fields to frontend expected fields
      const mappedSlides = res.slides.map((s: any) => ({
        ...s,
        html: s.html_content,
      }));
      setSlides(mappedSlides);
    } catch (err: any) {
      toast({ title: "Failed to load slides", description: err.message, variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      // Use slide ID directly (not project-scoped)
      await api.updateSlide(editSlide.id, { html_content: editHtml });
      setSlides((prev) => prev.map((s) => (s.id === editSlide.id ? { ...s, html: editHtml, html_content: editHtml } : s)));
      setEditSlide(null);
      toast({ title: "Slide updated" });
    } catch (err: any) {
      toast({ title: "Save failed", description: err.message, variant: "destructive" });
    }
  };

  return (
    <AppLayout>
      <div className="p-4 lg:p-6">
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={() => navigate("/projects")}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <h1 className="text-2xl font-bold">View Project</h1>
          </div>
          {slides.length > 0 && (
            <Button onClick={() => startPresentation(0)}>
              <Play className="mr-2 h-4 w-4" /> Present
            </Button>
          )}
        </div>

        {loading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => <Card key={i} className="animate-pulse"><CardContent className="h-40" /></Card>)}
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {slides.map((slide, i) => (
              <Card key={slide.id || i} className="glass transition-all hover:shadow-lg cursor-pointer" onClick={() => startPresentation(i)}>
                <CardContent className="p-4">
                  <div className="aspect-video overflow-hidden rounded-lg bg-muted mb-3">
                    {slide.html ? (
                      <iframe
                        srcDoc={slide.html}
                        className="w-full h-full border-0 pointer-events-none"
                        title={`Slide ${i + 1} preview`}
                        sandbox="allow-same-origin"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center text-muted-foreground text-sm">No content</div>
                    )}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Slide {i + 1}</span>
                    <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); navigate(`/editor/${projectId}?slide=${i}`); }}>
                      <Edit className="mr-1 h-3 w-3" /> Edit
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      <Dialog open={!!editSlide} onOpenChange={() => setEditSlide(null)}>
        <DialogContent className="max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>Edit Slide HTML</DialogTitle>
            <DialogDescription>Edit the HTML content and preview your changes</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <textarea
                className="h-64 w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                value={editHtml}
                onChange={(e) => setEditHtml(e.target.value)}
              />
            </div>
            <div className="rounded-lg bg-muted overflow-hidden h-64">
              <iframe
                srcDoc={editHtml}
                className="w-full h-full border-0"
                title="Slide preview"
                sandbox="allow-same-origin"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditSlide(null)}>Cancel</Button>
            <Button onClick={handleSave}>
              <Save className="mr-2 h-4 w-4" /> Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Presentation Mode Overlay */}
      {isPresentMode && slides.length > 0 && (
        <div className="fixed inset-0 z-50 bg-black flex flex-col">
          {/* Top bar */}
          <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between p-4 bg-gradient-to-b from-black/50 to-transparent opacity-0 hover:opacity-100 transition-opacity">
            <span className="text-white text-sm">
              Slide {currentSlideIndex + 1} / {slides.length}
            </span>
            <Button variant="ghost" size="icon" className="text-white hover:bg-white/20" onClick={() => setIsPresentMode(false)}>
              <X className="h-6 w-6" />
            </Button>
          </div>

          {/* Slide content */}
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="w-full h-full max-w-7xl max-h-[80vh] bg-white rounded-lg shadow-2xl overflow-hidden">
              {slides[currentSlideIndex]?.html ? (
                <iframe
                  srcDoc={slides[currentSlideIndex].html}
                  className="w-full h-full border-0"
                  title={`Slide ${currentSlideIndex + 1}`}
                  sandbox="allow-same-origin"
                />
              ) : (
                <div className="flex h-full items-center justify-center text-gray-400">
                  No content
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
        </div>
      )}
    </AppLayout>
  );
};

export default ViewProject;
