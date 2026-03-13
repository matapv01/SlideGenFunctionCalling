import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { GripVertical, Plus, Check, ChevronUp, ChevronDown, Trash2, BookOpen, ArrowRightFromLine } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/AppLayout";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/contexts/LanguageContext";

interface DocumentNode {
  id: string;
  level: number;
  title: string;
  content: string;
  children: DocumentNode[];
  is_transition?: boolean;
}

const typeColors: Record<number, string> = {
  0: "border-l-4 border-l-purple-500 bg-purple-50 dark:bg-purple-950/30",
  1: "border-l-4 border-l-info bg-info/5",
  2: "border-l-4 border-l-success bg-success/5",
  3: "border-l-4 border-l-warning bg-warning/5",
};

const StructureEditor = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get("session");
  const navigate = useNavigate();
  const { toast } = useToast();
  const { t } = useLanguage();
  
  const [documentTitle, setDocumentTitle] = useState("");
  const [documentText, setDocumentText] = useState("");
  const [nodes, setNodes] = useState<DocumentNode[]>([]);
  const [introSlide, setIntroSlide] = useState<DocumentNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (sessionId) {
      loadStructure();
    } else {
      setLoading(false);
      toast({ title: t.structure_toast_no_session, description: t.structure_toast_no_session_desc, variant: "destructive" });
    }
  }, [sessionId]);

  const loadStructure = async () => {
    try {
      const data = await api.getStructure(sessionId!);
      setDocumentTitle(data.document_title || t.structure_untitled);
      setDocumentText(data.document_text || "");
      setNodes(data.document_structure?.map((n: any, i: number) => ({ ...n, id: n.id || `node-${i}` })) || []);
    } catch (err: any) {
      toast({ title: t.structure_toast_load_fail, description: err.message, variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const addNode = (level: number = 1) => {
    setNodes((prev) => [
      ...prev,
      { id: crypto.randomUUID(), level, title: "", content: "", children: [], is_transition: false },
    ]);
  };

  const addIntroSlide = () => {
    setIntroSlide({
      id: "intro",
      level: 0,
      title: "Intro",
      content: documentTitle,
      children: [],
    });
  };

  const updateNode = (id: string, updates: Partial<DocumentNode>) => {
    setNodes((prev) => prev.map((n) => (n.id === id ? { ...n, ...updates } : n)));
  };

  const removeNode = (id: string) => {
    setNodes((prev) => prev.filter((n) => n.id !== id));
  };

  const moveNode = (index: number, dir: -1 | 1) => {
    const newNodes = [...nodes];
    const target = index + dir;
    if (target < 0 || target >= newNodes.length) return;
    [newNodes[index], newNodes[target]] = [newNodes[target], newNodes[index]];
    setNodes(newNodes);
  };

  const handleApprove = async () => {
    if (!sessionId) return;
    setSaving(true);
    try {
      // Update structure first
      await api.updateStructure(sessionId, nodes, introSlide || undefined);
      // Then approve
      const result = await api.approveStructure(sessionId);
      if (result.success) {
        toast({ title: t.structure_toast_approved, description: `${result.slide_types?.length || 0} ${t.structure_toast_slides_prepared}` });
        // Navigate to streaming page with session ID
        navigate(`/streaming/manual`, { state: { sessionId, documentTitle } });
      } else {
        toast({ title: t.structure_toast_approval_fail, description: result.message, variant: "destructive" });
      }
    } catch (err: any) {
      toast({ title: t.structure_toast_approval_fail, description: err.message, variant: "destructive" });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex min-h-[60vh] items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="flex h-[calc(100vh-4rem)]">
        {/* Editor (70%) */}
        <div className="flex-[7] overflow-auto border-r border-border p-4 lg:p-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold">{t.structure_title}</h1>
              <p className="text-sm text-muted-foreground">{documentTitle}</p>
            </div>
            <div className="flex gap-2">
              {!introSlide && (
                <Button variant="outline" size="sm" onClick={addIntroSlide}>
                  <Plus className="mr-1 h-3 w-3" /> {t.structure_intro_slide}
                </Button>
              )}
              <Button variant="outline" size="sm" onClick={() => addNode(1)}>
                <Plus className="mr-1 h-3 w-3" /> {t.structure_add_section}
              </Button>
            </div>
          </div>

          {/* Intro Slide */}
          {introSlide && (
            <div className={cn("mb-4 rounded-lg p-3 transition-colors", typeColors[0])}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-xs font-semibold text-purple-600 dark:text-purple-400 mb-2">{t.structure_intro_label}</p>
                  <Input
                    value={introSlide.content}
                    onChange={(e) => setIntroSlide({ ...introSlide, content: e.target.value })}
                    placeholder={t.structure_title_ph}
                    className="border-none bg-transparent p-0 text-lg font-bold focus-visible:ring-0"
                  />
                </div>
                <button onClick={() => setIntroSlide(null)} className="text-muted-foreground hover:text-destructive">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}

          {/* Content Nodes */}
          <div className="space-y-2">
            {nodes.map((node, index) => (
              <div
                key={node.id}
                className={cn("group flex items-start gap-2 rounded-lg p-3 transition-colors", typeColors[node.level] || typeColors[3])}
                style={{ marginLeft: `${(node.level - 1) * 20}px` }}
              >
                <div className="flex flex-col items-center gap-0.5 pt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => moveNode(index, -1)} className="text-muted-foreground hover:text-foreground">
                    <ChevronUp className="h-3 w-3" />
                  </button>
                  <GripVertical className="h-4 w-4 text-muted-foreground cursor-grab" />
                  <button onClick={() => moveNode(index, 1)} className="text-muted-foreground hover:text-foreground">
                    <ChevronDown className="h-3 w-3" />
                  </button>
                </div>

                <div className="flex-1 space-y-2">
                  <Input
                    value={node.title}
                    onChange={(e) => updateNode(node.id, { title: e.target.value })}
                    placeholder={t.structure_section_title_ph}
                    className="border-none bg-transparent p-0 font-semibold focus-visible:ring-0"
                  />
                  <Textarea
                    value={node.content}
                    onChange={(e) => updateNode(node.id, { content: e.target.value })}
                    placeholder={t.structure_content_ph}
                    className="min-h-[60px] border-none bg-transparent p-0 text-sm focus-visible:ring-0 resize-none"
                  />
                  <div className="flex items-center gap-2">
                    <Select value={String(node.level)} onValueChange={(v) => updateNode(node.id, { level: Number(v) })}>
                      <SelectTrigger className="h-7 w-20 text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {[1, 2, 3, 4, 5].map((i) => (
                          <SelectItem key={i} value={String(i)}>{t.structure_level} {i}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <label className="flex items-center gap-1 text-xs text-muted-foreground">
                      <input
                        type="checkbox"
                        checked={node.is_transition || false}
                        onChange={(e) => updateNode(node.id, { is_transition: e.target.checked })}
                        className="h-3 w-3"
                      />
                      {t.structure_transition}
                    </label>
                  </div>
                </div>

                <button onClick={() => removeNode(node.id)} className="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-destructive transition-all">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>

          <Button variant="outline" className="mt-4 w-full border-dashed" onClick={() => addNode(1)}>
            <Plus className="mr-2 h-4 w-4" /> {t.structure_add_section}
          </Button>

          <div className="mt-6 flex justify-end">
            <Button className="gradient-primary text-primary-foreground" onClick={handleApprove} disabled={saving || !sessionId}>
              <Check className="mr-2 h-4 w-4" /> {saving ? t.structure_processing : t.structure_approve}
            </Button>
          </div>
        </div>

        {/* Preview (30%) */}
        <div className="hidden flex-[3] overflow-auto bg-muted/30 p-4 lg:block">
          <h2 className="mb-4 text-sm font-semibold text-muted-foreground">{t.structure_preview}</h2>
          
          {/* Source Text */}
          {documentText && (
            <div className="mb-4">
              <p className="text-xs font-semibold text-muted-foreground mb-2">{t.structure_source_text}</p>
              <div className="max-h-48 overflow-auto rounded-lg bg-card p-3 text-sm whitespace-pre-wrap">
                {documentText.slice(0, 1000)}
                {documentText.length > 1000 && "..."}
              </div>
            </div>
          )}

          {/* Structure Preview */}
          <p className="text-xs font-semibold text-muted-foreground mb-2">{t.structure_structure} ({nodes.length} {t.structure_sections})</p>
          <div className="space-y-2">
            {introSlide && (
              <div className="rounded-lg bg-purple-100 dark:bg-purple-900/30 p-3 shadow-sm">
                <h3 className="font-bold text-purple-600 dark:text-purple-400">{introSlide.content || t.structure_intro_fallback}</h3>
              </div>
            )}
            {nodes.filter((n) => n.title.trim() || n.content.trim()).map((node) => (
              <div key={node.id} className="rounded-lg bg-card p-3 shadow-sm" style={{ marginLeft: `${(node.level - 1) * 8}px` }}>
                <h4 className="font-semibold text-sm">{node.title || t.structure_untitled}</h4>
                {node.content && <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{node.content}</p>}
                {node.is_transition && <span className="text-xs text-warning">{t.structure_transition_label}</span>}
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default StructureEditor;
