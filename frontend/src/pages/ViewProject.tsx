import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Edit, Save, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/AppLayout";

const ViewProject = () => {
  const { projectId } = useParams();
  const { toast } = useToast();
  const [slides, setSlides] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editSlide, setEditSlide] = useState<any>(null);
  const [editHtml, setEditHtml] = useState("");

  useEffect(() => {
    loadSlides();
  }, [projectId]);

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
        <h1 className="mb-6 text-2xl font-bold">View Project</h1>

        {loading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => <Card key={i} className="animate-pulse"><CardContent className="h-40" /></Card>)}
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {slides.map((slide, i) => (
              <Card key={slide.id || i} className="glass transition-all hover:shadow-lg">
                <CardContent className="p-4">
                  <div className="aspect-video overflow-hidden rounded-lg bg-muted mb-3">
                    {slide.html ? (
                      <div className="h-full w-full scale-[0.25] origin-top-left" style={{ width: "400%" }}>
                        <div dangerouslySetInnerHTML={{ __html: slide.html }} />
                      </div>
                    ) : (
                      <div className="flex h-full items-center justify-center text-muted-foreground text-sm">No content</div>
                    )}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Slide {i + 1}</span>
                    <Button variant="ghost" size="sm" onClick={() => { setEditSlide(slide); setEditHtml(slide.html || ""); }}>
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
            <div className="rounded-lg bg-muted p-4 overflow-auto h-64">
              <div dangerouslySetInnerHTML={{ __html: editHtml }} />
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
    </AppLayout>
  );
};

export default ViewProject;
