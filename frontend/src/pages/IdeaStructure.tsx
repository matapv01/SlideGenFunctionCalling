import { useState, useEffect, useCallback, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { CheckCircle2, Loader2, AlertCircle, RefreshCw, Home, Eye, FileText, Sparkles, PenTool, ExternalLink, Presentation, X, ChevronLeft, ChevronRight, Plus, Trash2, Edit3, Save, Move } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/AppLayout";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/contexts/LanguageContext";

interface SlideChunk {
  title: string;
  content: string;
  slide_type?: string;
}

interface IdeaStructureData {
  session_id: string;
  title: string;
  slide_chunks: SlideChunk[];
  enable_transition_slides: boolean;
  enable_thank_you_slide: boolean;
  metadata?: any;
}

const IdeaStructure = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { t } = useLanguage();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [structure, setStructure] = useState<IdeaStructureData | null>(null);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [maxSlides, setMaxSlides] = useState<number>(-1);

  useEffect(() => {
    api.getSubscriptionInfo().then((info: any) => {
      setMaxSlides(info.daily_limits?.max_docx_slides ?? -1);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!sessionId) {
      navigate("/slidegen", { replace: true });
      return;
    }
    loadStructure();
  }, [sessionId]);

  const loadStructure = async () => {
    setLoading(true);
    try {
      const data = await api.getIdeaStructure(sessionId!);
      setStructure(data);
      setError(null);
    } catch (err: any) {
      const rawMsg = (err.message || "").toLowerCase();
      const isAuth = rawMsg.includes('authentication') || rawMsg.includes('unauthorized') || rawMsg.includes('not auth');
      const errorMessage = isAuth ? t.error_auth_required : t.error_load_title;
      setError(errorMessage);
      toast({ title: t.error_load_title, variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const saveStructure = useCallback(async () => {
    if (!structure) return;

    setSaving(true);
    try {
      const updatedData = await api.updateIdeaStructure(sessionId!, {
        title: structure.title,
        slide_chunks: structure.slide_chunks,
        enable_transition_slides: structure.enable_transition_slides,
        enable_thank_you_slide: structure.enable_thank_you_slide,
      });
      setStructure(updatedData);
      toast({ title: t.profile_saved });
    } catch (err: any) {
      const rawMsg = (err.message || "").toLowerCase();
      const isAuth = rawMsg.includes('authentication') || rawMsg.includes('unauthorized') || rawMsg.includes('not auth');
      const errMsg = isAuth ? t.error_auth_required : undefined;
      toast({ title: t.error_save_title, description: errMsg, variant: "destructive" });
    } finally {
      setSaving(false);
    }
  }, [structure, sessionId, toast]);

  const startGeneration = useCallback(() => {
    setGenerating(true);
    navigate("/streaming/new", {
      state: {
        sessionId: sessionId,
        title: structure?.title,
        isFromStructure: true
      }
    });
  }, [sessionId, structure?.title, navigate]);

  const updateSlide = useCallback((index: number, updates: Partial<SlideChunk>) => {
    if (!structure) return;
    const newChunks = [...structure.slide_chunks];
    newChunks[index] = { ...newChunks[index], ...updates };
    setStructure({ ...structure, slide_chunks: newChunks });
  }, [structure]);

  const addSlide = useCallback((afterIndex: number) => {
    if (!structure) return;
    const currentCount = structure.slide_chunks.length;
    if (maxSlides !== -1 && currentCount >= maxSlides) {
      toast({ title: t.plan_slide_limit_title, description: t.plan_slide_limit_desc, variant: "destructive" });
      return;
    }
    const newSlide: SlideChunk = {
      title: "New Slide",
      content: "Enter slide content here...",
      slide_type: "content"
    };
    const newChunks = [...structure.slide_chunks];
    newChunks.splice(afterIndex + 1, 0, newSlide);
    setStructure({ ...structure, slide_chunks: newChunks });
  }, [structure, maxSlides, toast, t]);

  // Computed values that don't need to re-calculate on every render
  const slideCount = useMemo(() => structure?.slide_chunks.length || 0, [structure?.slide_chunks.length]);

  const removeSlide = useCallback((index: number) => {
    if (!structure || slideCount <= 1) return;
    const newChunks = structure.slide_chunks.filter((_, i) => i !== index);
    setStructure({ ...structure, slide_chunks: newChunks });
  }, [structure, slideCount]);

  const moveSlide = useCallback((fromIndex: number, toIndex: number) => {
    if (!structure) return;
    const newChunks = [...structure.slide_chunks];
    const [movedSlide] = newChunks.splice(fromIndex, 1);
    newChunks.splice(toIndex, 0, movedSlide);
    setStructure({ ...structure, slide_chunks: newChunks });
  }, [structure]);

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Loading structure...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (error || !structure) {
    return (
      <AppLayout>
        <div className="max-w-2xl mx-auto p-6">
          <Card className="border-destructive/50 bg-destructive/10">
            <CardContent className="flex items-center justify-between p-4">
              <div className="flex items-center gap-3">
                <AlertCircle className="h-5 w-5 text-destructive" />
                <p className="text-sm">{error || "Structure not found"}</p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={loadStructure}>
                  <RefreshCw className="mr-2 h-4 w-4" /> Retry
                </Button>
                <Button variant="outline" size="sm" onClick={() => navigate("/slidegen")}>
                  <Home className="mr-2 h-4 w-4" /> Back to Home
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="mx-auto max-w-6xl px-4 py-10">
        {/* Header */}
        <div className="mb-10 text-center">
          <div className="inline-flex items-center gap-2 mb-2">
            <FileText className="h-8 w-8 text-violet-500" />
            <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
              Structure Preview
            </h1>
          </div>
          <p className="text-muted-foreground">
            Review and edit your slide structure before generation
          </p>
        </div>

        {/* Title and Settings */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Edit3 className="h-5 w-5" />
              Project Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="title">Project Title</Label>
              <Input
                id="title"
                value={structure.title}
                onChange={(e) => setStructure({ ...structure, title: e.target.value })}
                className="mt-1"
              />
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex items-center space-x-2">
                <Switch
                  id="transitions"
                  checked={structure.enable_transition_slides}
                  onCheckedChange={(checked) => setStructure({ ...structure, enable_transition_slides: checked })}
                />
                <Label htmlFor="transitions" className="text-sm">Enable Transition Slides</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="thankyou"
                  checked={structure.enable_thank_you_slide}
                  onCheckedChange={(checked) => setStructure({ ...structure, enable_thank_you_slide: checked })}
                />
                <Label htmlFor="thankyou" className="text-sm">Enable Thank You Slide</Label>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Slide Structure */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5" />
                Slide Structure ({slideCount}{maxSlides !== -1 ? ` / ${maxSlides}` : ""} slides)
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={saveStructure} disabled={saving}>
                  {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                  {saving ? "Saving..." : "Save"}
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {structure.slide_chunks.map((slide, index) => (
                <Card key={index} className="relative group">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white text-sm font-semibold">
                        {index + 1}
                      </div>

                      <div className="flex-1 space-y-3">
                        {editingIndex === index ? (
                          <div className="space-y-3">
                            <Input
                              value={slide.title}
                              onChange={(e) => updateSlide(index, { title: e.target.value })}
                              placeholder="Slide title..."
                              className="font-semibold"
                            />
                            <Textarea
                              value={slide.content}
                              onChange={(e) => updateSlide(index, { content: e.target.value })}
                              placeholder="Slide content..."
                              rows={4}
                            />
                            <div className="flex gap-2">
                              <Button size="sm" onClick={() => setEditingIndex(null)}>
                                <Save className="h-4 w-4 mr-1" />
                                Done
                              </Button>
                            </div>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <h4 className="font-semibold text-lg">{slide.title}</h4>
                            <p className="text-sm text-muted-foreground line-clamp-3">{slide.content}</p>
                          </div>
                        )}
                      </div>

                      <div className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="flex gap-1">
                          {editingIndex !== index && (
                            <Button variant="ghost" size="icon" onClick={() => setEditingIndex(index)}>
                              <Edit3 className="h-4 w-4" />
                            </Button>
                          )}
                          <Button variant="ghost" size="icon" onClick={() => addSlide(index)} disabled={maxSlides !== -1 && slideCount >= maxSlides}>
                            <Plus className="h-4 w-4" />
                          </Button>
                          {slideCount > 1 && (
                            <Button variant="ghost" size="icon" onClick={() => removeSlide(index)}>
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Button
            size="lg"
            onClick={startGeneration}
            disabled={generating}
            className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white shadow-lg hover:shadow-xl transition-all hover:scale-105"
          >
            {generating ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Presentation className="mr-2 h-4 w-4" />
            )}
            {generating ? "Starting Generation..." : "Generate Slides"}
          </Button>

          <Button
            size="lg"
            variant="outline"
            onClick={() => navigate("/slidegen")}
            className="border-2 border-violet-500 text-violet-700 dark:text-violet-300 bg-white dark:bg-gray-900 hover:bg-violet-50 dark:hover:bg-violet-950/50 transition-all hover:scale-105"
          >
            <Home className="mr-2 h-4 w-4" />
            Back to Home
          </Button>
        </div>
      </div>
    </AppLayout>
  );
};

export default IdeaStructure;