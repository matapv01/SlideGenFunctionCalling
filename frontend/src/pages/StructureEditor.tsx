import { useState, useEffect, useRef } from "react";
import { useSearchParams, useNavigate, useParams } from "react-router-dom";
import {
  Check, Loader2, FileText, ArrowLeft, XCircle, Sparkles, AlertCircle,
  Bold, Italic, List, ListOrdered, Quote, Code, Heading1, Heading2, Minus
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
  DialogDescription
} from "@/components/ui/dialog";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle
} from "@/components/ui/alert-dialog";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import type { OutputFormat } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/contexts/LanguageContext";
import { useSlideGeneration } from "@/features/slidegenius/SlideGenerationContext";
import { SlidegeniusWorkspaceShell } from "@/features/slidegenius/SlidegeniusWorkspaceShell";
import ManualDemoTour from "@/features/slidegenius/ManualDemoTour";
import "@/features/slidegenius/structure-editor.css";

// ============ TYPES ============

interface IntroSlide {
  id: string;
  level: number;
  title: string;
  content: string;
  type: "title";
  children: never[];
}

interface StructureNode {
  node_id: string;
  level: number;
  title: string;
  content: string;
  children: StructureNode[];
  is_transition?: boolean;
}

interface SlidePreview {
  id: string;
  title: string;
  content: string;
  bullets: { level: number; text: string }[];
  isIntro?: boolean;
  isTransition?: boolean;
}

interface FlatEditorBlock {
  node_id: string;
  level: number;
  type: "title" | "content";
  text: string;
  is_transition: boolean;
}

interface ValidationIssue {
  message: string;
  nodeId: string;
}

// ============ HELPER TYPES ============

interface ParsedSlidePreview {
  index: number;
  title: string;
  content: string;
  bullets: Array<{ text: string; level: number }>;
}

interface ManualSlideNode {
  node_id: string;
  level: number;
  title: string;
  content: string;
  children: ManualSlideNode[];
  is_transition?: boolean;
}

const MANUAL_DEMO_MARKDOWN = `# Tạo một bài thuyết trình

Nội dung chính của slide đầu tiên.
- Ý quan trọng thứ nhất
- Ý quan trọng thứ hai

# Slide tiếp theo

Thêm nội dung cho slide thứ hai ở đây.`;

// ============ MAIN COMPONENT ============

const StructureEditor = () => {
  const [searchParams] = useSearchParams();
  const { projectId } = useParams();
  const demoMode = searchParams.get("demo") === "1";
  const sessionId = searchParams.get("session") || projectId || null;
  const navigate = useNavigate();
  const { toast } = useToast();
  const { language } = useLanguage();
  const {
    isGenerating,
    startManualSlideGeneration,
  } = useSlideGeneration();

  // State
  const [documentTitle, setDocumentTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [markdownContent, setMarkdownContent] = useState("");
  const [slidePreview, setSlidePreview] = useState<ParsedSlidePreview[]>([]);
  const [isDirty, setIsDirty] = useState(false);
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const [parseErrors, setParseErrors] = useState<string[]>([]);
  const [leftWidth, setLeftWidth] = useState(70);
  const [outputFormat, setOutputFormat] = useState<OutputFormat>("xml");

  const parsedStructureRef = useRef<any[] | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const startResizing = (mouseDownEvent: React.MouseEvent) => {
    mouseDownEvent.preventDefault();
    const handleMouseMove = (mouseMoveEvent: MouseEvent) => {
      if (containerRef.current) {
        const containerRect = containerRef.current.getBoundingClientRect();
        const newWidth = ((mouseMoveEvent.clientX - containerRect.left) / containerRect.width) * 100;
        if (newWidth > 20 && newWidth < 80) {
          setLeftWidth(newWidth);
        }
      }
    };
    const handleMouseUp = () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
  };

  // Load document and convert existing structure to markdown
  useEffect(() => {
    if (demoMode) {
      setDocumentTitle(language === "vi" ? "Bản mẫu Manual" : "Manual demo");
      setMarkdownContent("");
      setIsDirty(false);
      setLoading(false);

      let cursor = 0;
      const typingTimer = window.setInterval(() => {
        cursor += 1;
        setMarkdownContent(MANUAL_DEMO_MARKDOWN.slice(0, cursor));
        if (cursor >= MANUAL_DEMO_MARKDOWN.length) {
          window.clearInterval(typingTimer);
        }
      }, 14);

      return () => window.clearInterval(typingTimer);
    }

    if (sessionId) {
      loadDocument();
    } else {
      setLoading(false);
      toast({
        title: "Không có session ID",
        description: "Vui lòng tải lên tài liệu trước",
        variant: "destructive",
        className: "sg-manual-toast",
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, demoMode, language]);

  const loadDocument = async () => {
    try {
      const data = await api.getStructure(sessionId!);
      setDocumentTitle(data.document_title || "Untitled");
      setOutputFormat("xml");
      
      let markdown = "";
      
      // Priority 1: Use existing structure if available
      if (data.document_structure?.length) {
        markdown = convertStructureToMarkdown(data.document_structure);
      } 
      // Priority 2: Use raw document text if no structure yet
      else if (data.document_text) {
        // Keep source text unchanged; do not auto-insert headings.
        markdown = data.document_text;
      }
      
      setMarkdownContent(markdown);
      setIsDirty(false);
    } catch (err: any) {
      toast({
        title: "Lỗi tải cấu trúc",
        description: err.message,
        variant: "destructive",
        className: "sg-manual-toast",
      });
    } finally {
      setLoading(false);
    }
  };

  // Markdown formatting helpers
  const insertMarkdown = (before: string, after: string = "") => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = markdownContent.substring(start, end);
    const newText = markdownContent.substring(0, start) + before + selectedText + after + markdownContent.substring(end);

    setMarkdownContent(newText);
    setIsDirty(true);

    // Set cursor position after insertion
    setTimeout(() => {
      textarea.focus();
      const newCursorPos = start + before.length + selectedText.length;
      textarea.setSelectionRange(newCursorPos, newCursorPos);
    }, 0);
  };

  const insertAtLine = (prefix: string) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const beforeCursor = markdownContent.substring(0, start);
    const lineStart = beforeCursor.lastIndexOf('\n') + 1;

    const newText = markdownContent.substring(0, lineStart) + prefix + markdownContent.substring(lineStart);
    setMarkdownContent(newText);
    setIsDirty(true);

    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + prefix.length, start + prefix.length);
    }, 0);
  };

  // Convert structure back to markdown for editing
  const convertStructureToMarkdown = (nodes: any[], depth: number = 1): string => {
    let markdown = "";
    for (const node of nodes) {
      const heading = "#".repeat(depth);
      if (node.title) {
        markdown += `${heading} ${node.title}\n`;
      }
      if (node.content) {
        markdown += `${node.content}\n\n`;
      }
      if (node.children?.length) {
        markdown += convertStructureToMarkdown(node.children, depth + 1);
      }
    }
    return markdown;
  };

  const createManualSlide = (title: string): ManualSlideNode => ({
    node_id: `node_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    level: 1,
    title: title || "Untitled",
    content: "",
    children: [],
  });

  // Accept heading syntax without space, e.g. "#Title" -> "# Title"
  const normalizeMarkdownForParsing = (input: string): string => {
    return input
      .split("\n")
      .map((line) => line.replace(/^(#{1,6})([^#\s])/, "$1 $2"))
      .join("\n");
  };

  // Parse markdown with strict rule:
  // - only lines with leading # become slide titles
  // - other lines become content of current slide
  // - content without a slide is ignored (must start with # heading)
  const parseMarkdownToLevel1Slides = (markdown: string): ManualSlideNode[] => {
    const normalized = normalizeMarkdownForParsing(markdown).replace(/\r\n?/g, "\n");
    const lines = normalized.split("\n");
    const slides: ManualSlideNode[] = [];
    let currentSlide: ManualSlideNode | null = null;

    const appendContentLine = (line: string) => {
      // Only append content if we have a current slide (i.e., after a # heading)
      if (currentSlide) {
        currentSlide.content = currentSlide.content ? `${currentSlide.content}\n${line}` : line;
      }
      // Otherwise ignore orphaned content before first heading
    };

    for (const rawLine of lines) {
      const headingMatch = rawLine.match(/^(#{1,6})\s*(.*)$/);
      if (headingMatch) {
        const level = headingMatch[1].length;
        const headingText = headingMatch[2].trim() || "Untitled";

        if (level === 1) {
          currentSlide = createManualSlide(headingText);
          slides.push(currentSlide);
        } else {
          // Lower heading levels are not titles; keep them as content lines.
          appendContentLine(`• ${headingText}`);
        }
        continue;
      }

      appendContentLine(rawLine);
    }

    return slides.map((slide) => ({
      ...slide,
      content: slide.content
        .split("\n")
        .map((line) => line.replace(/\s+$/g, ""))
        .join("\n")
        .replace(/\n{3,}/g, "\n\n")
        .trim(),
    }));
  };

  const buildSlidePreviewFromStructure = (structure: ManualSlideNode[]): ParsedSlidePreview[] => {
    return (structure || []).map((node, idx) => {
      const lines = (node.content || "").split("\n").map((line) => line.trimEnd());

      const contentLines: string[] = [];
      const bulletsFromContent: Array<{ text: string; level: number }> = [];

      for (const line of lines) {
        const trimmedLine = line.trim();
        if (!trimmedLine) {
          continue;
        }
        if (trimmedLine.startsWith("• ")) {
          bulletsFromContent.push({ text: trimmedLine.slice(2), level: 2 });
        } else if (trimmedLine.startsWith("- ")) {
          bulletsFromContent.push({ text: trimmedLine.slice(2), level: 2 });
        } else {
          contentLines.push(trimmedLine);
        }
      }

      return {
        index: idx + 1,
        title: node.title || "Untitled",
        content: contentLines.join("\n"),
        bullets: bulletsFromContent,
      };
    });
  };

  const getSlideContentBlocks = (slide: ParsedSlidePreview) => {
    const paragraphs = (slide.content || "")
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);

    const bullets = slide.bullets
      .map((bullet) => ({
        text: bullet.text,
        level: Math.max(1, bullet.level - 1),
      }))
      .filter((bullet) => !!bullet.text);

    return { paragraphs, bullets };
  };

  // Live preview: parse markdown locally using strict heading/content rule.
  useEffect(() => {
    if (!markdownContent.trim()) {
      setSlidePreview([]);
      setParseErrors([]);
      parsedStructureRef.current = null;
      return;
    }

    const timer = setTimeout(() => {
      try {
        const level1Slides = parseMarkdownToLevel1Slides(markdownContent);
        parsedStructureRef.current = level1Slides;
        const previews = buildSlidePreviewFromStructure(level1Slides);
        setSlidePreview(previews);
        setParseErrors([]);
      } catch (err: any) {
        setParseErrors([err.message || "Failed to parse markdown"]);
        setSlidePreview([]);
        parsedStructureRef.current = null;
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [markdownContent, documentTitle]);

  const handleGoBack = () => {
    if (isDirty) {
      setCancelDialogOpen(true);
      return;
    }
    navigate(-1);
  };

  const confirmCancel = () => {
    setCancelDialogOpen(false);
    navigate(-1);
  };

  // Handle approve
  const handleApprove = async () => {
    if (!sessionId || !parsedStructureRef.current) {
      toast({ title: "Vui lòng nhập markdown trước tiên", variant: "destructive", className: "sg-manual-toast" });
      return;
    }
    if (isGenerating) {
      toast({
        title: language === "vi" ? "Đang có một deck được tạo" : "A deck is already being generated",
        description: language === "vi" ? "Bạn có thể tiếp tục chỉnh sửa, nhưng hãy chờ deck hiện tại hoàn thành." : "You can keep editing, but wait for the current deck to finish.",
        variant: "destructive",
        className: "sg-manual-toast",
      });
      return;
    }

    setSaving(true);
    try {
      await api.updateStructure(sessionId, parsedStructureRef.current, undefined, outputFormat);
      const result = await api.approveStructure(sessionId, outputFormat);
      const expectedSlides = result.slide_types?.length || slidePreview.length;
      const started = startManualSlideGeneration(sessionId, expectedSlides);

      if (!started) {
        throw new Error(language === "vi" ? "Không thể bắt đầu tạo deck lúc này." : "Unable to start deck generation right now.");
      }

      toast({
        title: language === "vi" ? "Đã bắt đầu tạo slide" : "Slide generation started",
        description: language === "vi" ? `${expectedSlides} slide đã được chuẩn bị.` : `${expectedSlides} slides are queued.`,
        className: "sg-manual-toast",
      });
      setApproveDialogOpen(false);
      navigate("/home");
    } catch (err: any) {
      toast({ title: "Lỗi", description: err.message, variant: "destructive", className: "sg-manual-toast" });
    } finally {
      setSaving(false);
    }
  };

  const handleResetMarkdown = () => {
    setMarkdownContent("");
    setSlidePreview([]);
    setParseErrors([]);
    parsedStructureRef.current = null;
    setIsDirty(false);
  };

  const headerActions = (
    <>
      <button
        className="btn btn-sm btn-danger"
        onClick={() => setCancelDialogOpen(true)}
        disabled={loading}
      >
        <XCircle className="mr-1.5 h-4 w-4" /> Cancel
      </button>
      <button
        className="btn btn-sm btn-success"
        data-tour="manual-approve"
        onClick={() => setApproveDialogOpen(true)}
        disabled={demoMode || saving || isGenerating || !parsedStructureRef.current || slidePreview.length === 0}
      >
        {saving ? <Loader2 className="mr-1.5 h-4 w-4 animate-spin" /> : <Check className="mr-1.5 h-4 w-4" />}
        {saving ? "Processing..." : "Approve & Continue"}
      </button>
    </>
  );

  const desktopHeaderBar = (
    <div className="legacy-app-header">
      <button className="btn btn-outline-light" onClick={handleGoBack} disabled={loading || saving}>
        <ArrowLeft className="mr-2 h-4 w-4" /> Back
      </button>
      <h2 className="header-title">
        <FileText className="mr-2 h-5 w-5" /> Structure Editor (Markdown)
      </h2>
      <div className="document-info">
        <FileText className="mr-2 h-4 w-4" />
        <span>{documentTitle || "Untitled document"}</span>
      </div>
      <div className={cn("save-indicator", isDirty ? "unsaved" : "saved")}>
        {isDirty ? "Unsaved changes" : "Saved"}
      </div>
      <div className="header-actions">{headerActions}</div>
    </div>
  );

  return (
    <div className="sg-manual-editor">
      <SlidegeniusWorkspaceShell activeTab="manual">
      <div className="sg-manual-editor-header">{desktopHeaderBar}</div>
      <div className="legacy-structure-page bg-background text-foreground">
        <div className="legacy-structure-content">
          <div ref={containerRef} className="flex h-full flex-col gap-4 p-4 lg:flex-row relative">
            {/* Left Panel: Markdown Editor */}
            <div className="flex flex-col gap-3" style={{ width: `${leftWidth}%` }}>
              <div className="flex items-center justify-between">
                <div className="text-sm font-semibold text-foreground" data-tour="manual-editor">Markdown Editor</div>
                <div className="text-xs text-muted-foreground">
                  {markdownContent.split('\n').length} lines • {markdownContent.split(/\s+/).filter(Boolean).length} words
                </div>
              </div>

              {/* Editor Textarea */}
              <div className="relative flex-1">
                <Textarea
                  ref={textareaRef}
                  data-tour="manual-editor"
                  value={markdownContent}
                  onChange={(e) => {
                    setMarkdownContent(e.target.value);
                    setIsDirty(true);
                  }}
                  placeholder={`# First Slide Title

Paragraph content here...
- Bullet point 1
- Bullet point 2

# Second Slide Title

More content...

Note: Each # heading creates a new slide`}
                  className="h-full min-h-[550px] resize-none rounded-lg border-2 border-border bg-card px-5 py-4 font-mono text-[15px] leading-relaxed text-foreground shadow-sm transition-colors focus:border-primary focus:ring-2 focus:ring-primary/20"
                  spellCheck={false}
                />
              </div>

              {/* Stats Footer */}
              <div className="flex items-center justify-between rounded-lg border border-border bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
                <div className="flex gap-4">
                  <span><span className="font-semibold text-foreground">{markdownContent.length}</span> characters</span>
                  <span><span className="font-semibold text-foreground">{markdownContent.split('\n').length}</span> lines</span>
                  <span><span className="font-semibold text-foreground">{markdownContent.split(/\s+/).filter(Boolean).length}</span> words</span>
                </div>
                {isDirty && (
                  <span className="flex items-center gap-1.5 text-amber-600">
                    <span className="h-1.5 w-1.5 rounded-full bg-amber-600" />
                    Unsaved changes
                  </span>
                )}
              </div>
            </div>

            {/* Resizer */}
            <div
              className="hidden lg:flex w-2 cursor-col-resize items-center justify-center hover:bg-primary/20 transition-colors shrink-0 mx-2 rounded-full"
              onMouseDown={startResizing}
            >
              <div className="h-8 w-1 rounded-full bg-border" />
            </div>

            {/* Right Panel: Live Preview */}
            <div className="flex flex-col gap-2" style={{ width: `calc(${100 - leftWidth}% - 1.5rem)` }}>
              <div className="flex items-center justify-between text-sm font-semibold" data-tour="manual-preview">
                <span>Preview</span>
                <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary">
                  {slidePreview.length} {slidePreview.length === 1 ? 'slide' : 'slides'}
                </span>
              </div>
              <div className="h-[65vh] min-h-[420px] overflow-y-auto rounded-md border border-border bg-muted/20 p-2">
                {parseErrors.length > 0 && (
                  <div className="mb-2 rounded-md border border-destructive/40 bg-destructive/10 p-2">
                    <div className="mb-1 flex items-center gap-1.5 text-xs font-semibold text-destructive">
                      <AlertCircle className="h-3.5 w-3.5" />
                      Parse Errors:
                    </div>
                    {parseErrors.map((err, idx) => (
                      <div key={idx} className="text-xs text-destructive">• {err}</div>
                    ))}
                  </div>
                )}

                {slidePreview.length === 0 && parseErrors.length === 0 ? (
                  <div className="flex h-full flex-col items-center justify-center gap-2 text-muted-foreground">
                    <FileText className="h-10 w-10 opacity-20" />
                    <div className="text-xs font-medium">No slides yet</div>
                    <div className="text-xs">Start with a <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]"># heading</code></div>
                  </div>
                ) : (
                  slidePreview.map((slide) => {
                    const { paragraphs, bullets } = getSlideContentBlocks(slide);

                    return (
                      <div key={slide.index} className="mb-2.5 rounded-md border border-border/60 bg-white p-1.5 shadow-sm hover:shadow-md transition-shadow">
                        {/* PowerPoint style slide preview */}
                        <div className="mx-auto aspect-[16/9] w-full overflow-hidden rounded-md border border-gray-200 bg-white shadow-sm flex flex-col relative group">
                          {/* Slide Number (Absolute) */}
                          <div className="absolute bottom-2 right-3 text-[9px] text-gray-400 font-medium">
                            {slide.index}
                          </div>
                          
                          {/* Title Area */}
                          <div className="flex flex-[0.25] items-end justify-center px-8 pb-1 pt-4">
                            <h2 className="text-center text-sm font-bold text-gray-800 line-clamp-2 leading-tight">
                              {slide.title}
                            </h2>
                          </div>

                          {/* Content Area */}
                          <div className="flex flex-[0.75] flex-col px-8 py-2 overflow-hidden">
                            {paragraphs.length > 0 && (
                              <div className="space-y-1">
                                {paragraphs.slice(0, 3).map((paragraph, idx) => (
                                  <p key={`${slide.index}-p-${idx}`} className="text-[10px] leading-relaxed text-gray-700 line-clamp-2">
                                    {paragraph}
                                  </p>
                                ))}
                                {paragraphs.length > 3 && (
                                  <p className="text-[9px] text-gray-400 italic">+{paragraphs.length - 3} more...</p>
                                )}
                              </div>
                            )}

                            {bullets.length > 0 && (
                              <ul className={cn("space-y-1.5", paragraphs.length > 0 ? "mt-2" : "")} style={{ listStyleType: "disc", paddingLeft: "1.2rem" }}>
                                {bullets.slice(0, 5).map((bullet, idx) => (
                                  <li
                                    key={`${slide.index}-b-${idx}`}
                                    className="text-[10px] leading-snug text-gray-700"
                                    style={{ marginLeft: `${(bullet.level - 1) * 12}px` }}
                                  >
                                    <span className="line-clamp-2">{bullet.text}</span>
                                  </li>
                                ))}
                                {bullets.length > 5 && (
                                  <li className="text-[9px] text-gray-400 italic ml-0 list-none">+{bullets.length - 5} more bullets...</li>
                                )}
                              </ul>
                            )}

                            {paragraphs.length === 0 && bullets.length === 0 && (
                              <div className="flex h-full items-center justify-center rounded border border-dashed border-gray-200 bg-gray-50/50 text-[10px] text-gray-400">
                                No content
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      {demoMode && <ManualDemoTour />}

      {/* Cancel Confirmation */}
      <AlertDialog open={cancelDialogOpen} onOpenChange={setCancelDialogOpen}>
        <AlertDialogContent className="sg-manual-dialog">
          <AlertDialogHeader>
            <AlertDialogTitle>Cancel editing?</AlertDialogTitle>
            <AlertDialogDescription className="sg-manual-dialog-description">
              Các thay đổi chưa lưu sẽ bị mất. Bạn chắc chắn muốn thoát chứ?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Tiếp tục chỉnh sửa</AlertDialogCancel>
            <AlertDialogAction onClick={confirmCancel} className="bg-secondary text-secondary-foreground">
              Thoát
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Approve Confirmation */}
      <AlertDialog open={approveDialogOpen} onOpenChange={setApproveDialogOpen}>
        <AlertDialogContent className="sg-manual-dialog">
          <AlertDialogHeader>
            <AlertDialogTitle>Duyệt cấu trúc?</AlertDialogTitle>
            <AlertDialogDescription className="sg-manual-dialog-description">
              Xác nhận cấu trúc với {slidePreview.length} slide? Hệ thống sẽ bắt đầu thiết kế slide tự động.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Hủy</AlertDialogCancel>
            <AlertDialogAction onClick={handleApprove} className="gradient-primary text-primary-foreground">
              <Check className="mr-1.5 h-3.5 w-3.5" /> Duyệt
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
      </SlidegeniusWorkspaceShell>
    </div>
  );
};

export default StructureEditor;
