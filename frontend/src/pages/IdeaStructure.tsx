import { useState, useEffect, useCallback, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Loader2,
  AlertCircle,
  RefreshCw,
  Home,
  FileText,
  Sparkles,
  Presentation,
  Plus,
  Trash2,
  Edit3,
  Save,
  ArrowLeft,
  ArrowUp,
  ArrowDown,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/AppLayout";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/contexts/LanguageContext";
import { useAuth } from "@/contexts/AuthContext";

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
  const { isAuthenticated } = useAuth();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [structure, setStructure] = useState<IdeaStructureData | null>(null);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [maxSlides, setMaxSlides] = useState<number>(-1);
  const [isDirty, setIsDirty] = useState(false);
  const [lastSavedAt, setLastSavedAt] = useState<number | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      api.getSubscriptionInfo().then((info: any) => {
        setMaxSlides(info.daily_limits?.max_docx_slides ?? -1);
      }).catch(() => { });
    }
  }, [isAuthenticated]);

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
      setIsDirty(false);
      setLastSavedAt(Date.now());
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
    if (!structure) return false;

    setSaving(true);
    try {
      const updatedData = await api.updateIdeaStructure(sessionId!, {
        title: structure.title,
        slide_chunks: structure.slide_chunks,
        enable_transition_slides: structure.enable_transition_slides,
        enable_thank_you_slide: structure.enable_thank_you_slide,
      });
      setStructure(updatedData);
      setIsDirty(false);
      setLastSavedAt(Date.now());
      toast({ title: t.profile_saved });
      return true;
    } catch (err: any) {
      const rawMsg = (err.message || "").toLowerCase();
      const isAuth = rawMsg.includes('authentication') || rawMsg.includes('unauthorized') || rawMsg.includes('not auth');
      const errMsg = isAuth ? t.error_auth_required : undefined;
      toast({ title: t.error_save_title, description: errMsg, variant: "destructive" });
      return false;
    } finally {
      setSaving(false);
    }
  }, [structure, sessionId, t.error_auth_required, t.error_save_title, t.profile_saved, toast]);

  const startGeneration = useCallback(async () => {
    if (isDirty) {
      const ok = await saveStructure();
      if (!ok) return;
    }

    setGenerating(true);
    navigate("/streaming/new", {
      state: {
        sessionId: sessionId,
        title: structure?.title,
        isFromStructure: true
      }
    });
  }, [isDirty, navigate, saveStructure, sessionId, structure?.title]);

  const updateStructure = useCallback((updater: (prev: IdeaStructureData) => IdeaStructureData) => {
    setStructure((prev) => {
      if (!prev) return prev;
      const next = updater(prev);
      setIsDirty(true);
      return next;
    });
  }, []);

  const updateSlide = useCallback((index: number, updates: Partial<SlideChunk>) => {
    updateStructure((prev) => {
      const newChunks = [...prev.slide_chunks];
      newChunks[index] = { ...newChunks[index], ...updates };
      return { ...prev, slide_chunks: newChunks };
    });
  }, [updateStructure]);

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
    updateStructure((prev) => {
      const newChunks = [...prev.slide_chunks];
      newChunks.splice(afterIndex + 1, 0, newSlide);
      return { ...prev, slide_chunks: newChunks };
    });
    setEditingIndex(afterIndex + 1);
  }, [maxSlides, structure, t, toast, updateStructure]);

  // Computed values that don't need to re-calculate on every render
  const slideCount = useMemo(() => structure?.slide_chunks.length || 0, [structure?.slide_chunks.length]);

  const removeSlide = useCallback((index: number) => {
    if (!structure || slideCount <= 1) return;
    updateStructure((prev) => {
      const newChunks = prev.slide_chunks.filter((_, i) => i !== index);
      return { ...prev, slide_chunks: newChunks };
    });
    setEditingIndex((prev) => {
      if (prev === null) return null;
      if (prev === index) return null;
      if (prev > index) return prev - 1;
      return prev;
    });
  }, [slideCount, structure, updateStructure]);

  const moveSlide = useCallback((fromIndex: number, toIndex: number) => {
    if (!structure) return;
    if (toIndex < 0 || toIndex >= structure.slide_chunks.length) return;
    updateStructure((prev) => {
      const newChunks = [...prev.slide_chunks];
      const [movedSlide] = newChunks.splice(fromIndex, 1);
      newChunks.splice(toIndex, 0, movedSlide);
      return { ...prev, slide_chunks: newChunks };
    });
  }, [structure, updateStructure]);

  const formatPreviewContent = useCallback((raw: string) => {
    const text = (raw || "")
      .replace(/\r\n?/g, "\n")
      .replace(/\u00A0/g, " ")
      .trim();
    if (!text) return "";

    // Convert inline list separators to real line breaks.
    // Supports hyphen, en dash, em dash: " - ", " – ", " — ".
    return text
      .replace(/\s+[\-–—]\s+/g, "\n- ")
      .replace(/\n{2,}/g, "\n")
      .trim();
  }, []);

  const getPreviewLines = useCallback((raw: string) => {
    return formatPreviewContent(raw)
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);
  }, [formatPreviewContent]);

  const disableActions = loading || saving || generating;

  const headerActions = (
    <>
      <button className="btn btn-sm btn-secondary" onClick={() => void saveStructure()} disabled={disableActions}>
        {saving ? <Loader2 className="mr-1.5 h-4 w-4 animate-spin" /> : <Save className="mr-1.5 h-4 w-4" />}
        {saving ? "Saving..." : "Save"}
      </button>
      <button className="btn btn-sm btn-success" onClick={() => void startGeneration()} disabled={disableActions}>
        {generating ? <Loader2 className="mr-1.5 h-4 w-4 animate-spin" /> : <Presentation className="mr-1.5 h-4 w-4" />}
        {generating ? "Starting..." : "Generate"}
      </button>
    </>
  );

  const desktopHeaderBar = (
    <div className="legacy-app-header">
      <button className="btn btn-outline-light" onClick={() => navigate("/slidegen")} disabled={disableActions}>
        <ArrowLeft className="mr-2 h-4 w-4" /> Back
      </button>
      <h2 className="header-title">
        <FileText className="mr-2 h-5 w-5" /> Idea Structure
      </h2>
      <div className="document-info">
        <FileText className="mr-2 h-4 w-4" />
        <span>{structure?.title || "Untitled"}</span>
      </div>
      <div
        className={cn("save-indicator", saving ? "saving" : isDirty ? "unsaved" : "saved")}
        title={lastSavedAt ? `Saved at ${new Date(lastSavedAt).toLocaleTimeString()}` : undefined}
      >
        {saving ? "Saving..." : isDirty ? "Unsaved changes" : "Saved"}
      </div>
      <div className="header-actions">{headerActions}</div>
    </div>
  );

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
                <button className="btn btn-sm btn-secondary" onClick={loadStructure}>
                  <RefreshCw className="mr-2 h-4 w-4" /> Retry
                </button>
                <button className="btn btn-sm btn-outline-light" onClick={() => navigate("/slidegen")}>
                  <Home className="mr-2 h-4 w-4" /> Back to Home
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout headerContent={desktopHeaderBar}>
      <div className="legacy-structure-page">
        <div className="legacy-structure-content">
          <div className="header-section header-section-mobile">
            <button className="btn btn-outline-light" onClick={() => navigate("/slidegen")} disabled={disableActions}>
              <ArrowLeft className="mr-2 h-4 w-4" /> Back
            </button>
            <h2 className="header-title">
              <FileText className="mr-2 h-5 w-5" /> Idea Structure
            </h2>
            <div className="document-info">
              <FileText className="mr-2 h-4 w-4" />
              <span>{structure.title || "Untitled"}</span>
            </div>
            <div
              className={cn("save-indicator", saving ? "saving" : isDirty ? "unsaved" : "saved")}
              title={lastSavedAt ? `Saved at ${new Date(lastSavedAt).toLocaleTimeString()}` : undefined}
            >
              {saving ? "Saving..." : isDirty ? "Unsaved changes" : "Saved"}
            </div>
            <div className="header-actions">{headerActions}</div>
          </div>

          <div className="main-content">
            <div className="editor-column">
              <div className="panel-container">
                <div className="panel-header">
                  <h5>
                    <Edit3 className="mr-2 h-4 w-4" /> Project Settings
                  </h5>
                </div>

                <div className="space-y-4">
                  <div>
                    <Label htmlFor="title">Project Title</Label>
                    <Input
                      id="title"
                      value={structure.title}
                      onChange={(e) => updateStructure((prev) => ({ ...prev, title: e.target.value }))}
                      className="mt-1"
                    />
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <Switch
                        id="transitions"
                        checked={structure.enable_transition_slides}
                        onCheckedChange={(checked) =>
                          updateStructure((prev) => ({ ...prev, enable_transition_slides: checked }))
                        }
                      />
                      <Label htmlFor="transitions" className="text-sm">Enable Transition Slides</Label>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Switch
                        id="thankyou"
                        checked={structure.enable_thank_you_slide}
                        onCheckedChange={(checked) =>
                          updateStructure((prev) => ({ ...prev, enable_thank_you_slide: checked }))
                        }
                      />
                      <Label htmlFor="thankyou" className="text-sm">Enable Thank You Slide</Label>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="preview-column">
              <div className="panel-container">
                <div className="panel-header">
                  <h5>
                    <Sparkles className="mr-2 h-4 w-4" /> Slide Structure ({slideCount}{maxSlides !== -1 ? ` / ${maxSlides}` : ""} slides)
                  </h5>
                  <div className="preview-header-actions">
                    <button className="btn btn-sm btn-secondary" onClick={() => void saveStructure()} disabled={disableActions}>
                      {saving ? <Loader2 className="mr-1.5 h-4 w-4 animate-spin" /> : <Save className="mr-1.5 h-4 w-4" />}
                      {saving ? "Saving..." : "Save"}
                    </button>
                  </div>
                </div>

                <div className="slides-container">
                  {structure.slide_chunks.map((slide, index) => (
                    <div
                      key={index}
                      className={cn(
                        "slide-thumbnail",
                        slide.slide_type === "transition" && "slide-transition",
                        slide.slide_type === "intro" && "slide-intro"
                      )}
                    >
                      <span className="slide-number">#{index + 1}</span>

                      {editingIndex === index ? (
                        <div className="space-y-3 pr-12">
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
                          <div className="slide-actions">
                            <button className="btn btn-sm btn-success" onClick={() => setEditingIndex(null)}>
                              <Save className="mr-1.5 h-4 w-4" /> Done
                            </button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <div className="slide-title">{slide.title}</div>
                          <div className="slide-content">
                            {getPreviewLines(slide.content).map((line, lineIndex) => (
                              <div key={`${index}-line-${lineIndex}`}>{line}</div>
                            ))}
                          </div>
                        </>
                      )}

                      <div className="slide-actions">
                        {editingIndex !== index && (
                          <button className="btn btn-sm btn-outline-light" onClick={() => setEditingIndex(index)}>
                            <Edit3 className="h-4 w-4" />
                          </button>
                        )}

                        <button
                          className="btn btn-sm btn-outline-light"
                          onClick={() => moveSlide(index, index - 1)}
                          disabled={index === 0 || disableActions}
                        >
                          <ArrowUp className="h-4 w-4" />
                        </button>

                        <button
                          className="btn btn-sm btn-outline-light"
                          onClick={() => moveSlide(index, index + 1)}
                          disabled={index === slideCount - 1 || disableActions}
                        >
                          <ArrowDown className="h-4 w-4" />
                        </button>

                        <button
                          className="btn btn-sm btn-outline-light"
                          onClick={() => addSlide(index)}
                          disabled={(maxSlides !== -1 && slideCount >= maxSlides) || disableActions}
                        >
                          <Plus className="h-4 w-4" />
                        </button>

                        {slideCount > 1 && (
                          <button className="btn btn-sm btn-danger" onClick={() => removeSlide(index)} disabled={disableActions}>
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default IdeaStructure;