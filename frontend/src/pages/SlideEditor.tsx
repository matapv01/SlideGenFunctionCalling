import { useState, useEffect, useCallback, useRef } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import {
  Plus, Copy, Trash2, ChevronLeft, ChevronRight, ZoomIn, ZoomOut,
  Undo2, Redo2, Save, Download, FileText, Upload, Play, Type,
  Image, Square, Minus, MousePointer, RotateCw, Layers, Move,
  AlignLeft, AlignCenter, AlignRight, Bold, Italic, Underline,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useNavigate } from "react-router-dom";
import { ScaledSlidePreview } from "@/components/ScaledSlidePreview";

interface SlideElement {
  id: string;
  type: "text" | "image" | "shape" | "icon" | "connector";
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  zIndex: number;
  content?: string;
  src?: string;
  style?: Record<string, any>;
  connectorType?: "straight" | "curved" | "elbow";
}

interface Slide {
  id: string;
  elements: SlideElement[];
  html?: string;
}

const SlideEditor = () => {
  const { projectId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const canvasRef = useRef<HTMLDivElement>(null);

  const [slides, setSlides] = useState<Slide[]>([{ id: "1", elements: [], html: "" }]);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [selectedElement, setSelectedElement] = useState<string | null>(null);
  const [zoom, setZoom] = useState(100);
  const [undoStack, setUndoStack] = useState<Slide[][]>([]);
  const [redoStack, setRedoStack] = useState<Slide[][]>([]);
  const [autoSaved, setAutoSaved] = useState(true);
  const [leftTab, setLeftTab] = useState("slides");
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  useEffect(() => {
    if (projectId) loadSlides();
  }, [projectId]);

  // Auto-save
  useEffect(() => {
    setAutoSaved(false);
    const timer = setTimeout(() => {
      saveSlides();
    }, 3000);
    return () => clearTimeout(timer);
  }, [slides]);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === "z") { e.preventDefault(); undo(); }
        if (e.key === "y") { e.preventDefault(); redo(); }
      }
      if (e.key === "Delete" && selectedElement) {
        deleteElement(selectedElement);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [selectedElement, undoStack]);

  const loadSlides = async () => {
    try {
      const res = await api.getSlides(projectId!);
      if (res.slides.length) {
        setSlides(res.slides.map((s: any, i: number) => ({
          id: s.id || String(i),
          elements: s.design_settings?.elements || [],
          html: s.html_content
        })));
        // Set initial slide from query param
        const slideParam = searchParams.get('slide');
        if (slideParam) {
          const slideIndex = parseInt(slideParam, 10);
          if (!isNaN(slideIndex) && slideIndex >= 0 && slideIndex < res.slides.length) {
            setCurrentSlide(slideIndex);
          }
        }
      }
    } catch { /* use defaults */ }
  };

  const saveSlides = async () => {
    if (!projectId) return;
    try {
      for (const slide of slides) {
        await api.updateSlide(slide.id, {
          html_content: slide.html,
          design_settings: { elements: slide.elements }
        });
      }
      setAutoSaved(true);
    } catch { /* silent */ }
  };

  const pushUndo = () => {
    setUndoStack((prev) => [...prev.slice(-20), JSON.parse(JSON.stringify(slides))]);
    setRedoStack([]);
  };

  const undo = () => {
    if (undoStack.length === 0) return;
    setRedoStack((prev) => [...prev, JSON.parse(JSON.stringify(slides))]);
    setSlides(undoStack[undoStack.length - 1]);
    setUndoStack((prev) => prev.slice(0, -1));
  };

  const redo = () => {
    if (redoStack.length === 0) return;
    setUndoStack((prev) => [...prev, JSON.parse(JSON.stringify(slides))]);
    setSlides(redoStack[redoStack.length - 1]);
    setRedoStack((prev) => prev.slice(0, -1));
  };

  const addSlide = () => {
    pushUndo();
    setSlides((prev) => [...prev, { id: crypto.randomUUID(), elements: [] }]);
    setCurrentSlide(slides.length);
  };

  const duplicateSlide = () => {
    pushUndo();
    const dupe = JSON.parse(JSON.stringify(slides[currentSlide]));
    dupe.id = crypto.randomUUID();
    setSlides((prev) => [...prev.slice(0, currentSlide + 1), dupe, ...prev.slice(currentSlide + 1)]);
    setCurrentSlide(currentSlide + 1);
  };

  const deleteSlide = (index: number) => {
    if (slides.length <= 1) return;
    pushUndo();
    setSlides((prev) => prev.filter((_, i) => i !== index));
    if (currentSlide >= slides.length - 1) setCurrentSlide(Math.max(0, slides.length - 2));
  };

  const addElement = (type: SlideElement["type"]) => {
    pushUndo();
    const el: SlideElement = {
      id: crypto.randomUUID(),
      type,
      x: 100,
      y: 100,
      width: type === "text" ? 300 : 150,
      height: type === "text" ? 60 : 150,
      rotation: 0,
      zIndex: (slides[currentSlide]?.elements.length || 0) + 1,
      content: type === "text" ? "Double-click to edit" : undefined,
    };
    setSlides((prev) =>
      prev.map((s, i) => (i === currentSlide ? { ...s, elements: [...s.elements, el] } : s))
    );
    setSelectedElement(el.id);
  };

  const deleteElement = (id: string) => {
    pushUndo();
    setSlides((prev) =>
      prev.map((s, i) => (i === currentSlide ? { ...s, elements: s.elements.filter((e) => e.id !== id) } : s))
    );
    setSelectedElement(null);
  };

  const updateElement = (id: string, updates: Partial<SlideElement>) => {
    setSlides((prev) =>
      prev.map((s, i) =>
        i === currentSlide
          ? { ...s, elements: s.elements.map((e) => (e.id === id ? { ...e, ...updates } : e)) }
          : s
      )
    );
  };

  const currentSlideData = slides[currentSlide];
  const selected = currentSlideData?.elements.find((e) => e.id === selectedElement);

  const handleCanvasMouseDown = (e: React.MouseEvent, elementId?: string) => {
    if (elementId) {
      setSelectedElement(elementId);
      setIsDragging(true);
      setDragStart({ x: e.clientX, y: e.clientY });
      pushUndo();
    } else {
      setSelectedElement(null);
    }
  };

  const handleCanvasMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !selectedElement) return;
    const dx = e.clientX - dragStart.x;
    const dy = e.clientY - dragStart.y;
    setDragStart({ x: e.clientX, y: e.clientY });
    updateElement(selectedElement, {
      x: (selected?.x || 0) + dx / (zoom / 100),
      y: (selected?.y || 0) + dy / (zoom / 100),
    });
  };

  const handleCanvasMouseUp = () => {
    setIsDragging(false);
  };

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Toolbar */}
      <div className="flex h-12 items-center justify-between border-b border-border bg-card px-4">
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => navigate(-1)}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Separator orientation="vertical" className="mx-1 h-6" />
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={undo} title="Undo (Ctrl+Z)">
            <Undo2 className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={redo} title="Redo (Ctrl+Y)">
            <Redo2 className="h-4 w-4" />
          </Button>
          <Separator orientation="vertical" className="mx-1 h-6" />
          <Button variant="ghost" size="sm" className="h-8 text-xs" onClick={() => addElement("text")}>
            <Type className="mr-1 h-3 w-3" /> Text
          </Button>
          <Button variant="ghost" size="sm" className="h-8 text-xs" onClick={() => addElement("image")}>
            <Image className="mr-1 h-3 w-3" /> Image
          </Button>
          <Button variant="ghost" size="sm" className="h-8 text-xs" onClick={() => addElement("shape")}>
            <Square className="mr-1 h-3 w-3" /> Shape
          </Button>
          <Button variant="ghost" size="sm" className="h-8 text-xs" onClick={() => addElement("connector")}>
            <Minus className="mr-1 h-3 w-3" /> Line
          </Button>
        </div>
        <div className="flex items-center gap-2">
          <span className={cn("text-xs", autoSaved ? "text-success" : "text-warning")}>
            {autoSaved ? "✓ Saved" : "● Saving..."}
          </span>
          <Separator orientation="vertical" className="mx-1 h-6" />
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => navigate(`/present/${projectId}`)}>
            <Play className="h-4 w-4" />
          </Button>
          {/* Export PDF and Download removed - use capture service */}
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Left sidebar */}
        <div className="w-56 flex-shrink-0 overflow-auto border-r border-border bg-card">
          <Tabs value={leftTab} onValueChange={setLeftTab}>
            <TabsList className="w-full rounded-none border-b bg-transparent">
              <TabsTrigger value="slides" className="flex-1 text-xs">Slides</TabsTrigger>
              <TabsTrigger value="elements" className="flex-1 text-xs">Elements</TabsTrigger>
            </TabsList>
            <TabsContent value="slides" className="p-2 space-y-2">
              {slides.map((slide, i) => (
                <div
                  key={slide.id}
                  onClick={() => setCurrentSlide(i)}
                  className={cn(
                    "group relative cursor-pointer rounded-lg border p-1 transition-all",
                    i === currentSlide ? "border-primary ring-2 ring-primary/20" : "border-border hover:border-primary/50"
                  )}
                >
                  <div className="aspect-video rounded bg-muted flex items-center justify-center text-xs text-muted-foreground">
                    {slide.elements.length} elements
                  </div>
                  <p className="mt-1 text-center text-[10px] text-muted-foreground">Slide {i + 1}</p>
                  {slides.length > 1 && (
                    <button
                      onClick={(e) => { e.stopPropagation(); deleteSlide(i); }}
                      className="absolute -right-1 -top-1 hidden h-5 w-5 items-center justify-center rounded-full bg-destructive text-destructive-foreground group-hover:flex"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  )}
                </div>
              ))}
              <div className="flex gap-1">
                <Button variant="outline" size="sm" className="flex-1 text-xs" onClick={addSlide}>
                  <Plus className="mr-1 h-3 w-3" /> Add
                </Button>
                <Button variant="outline" size="sm" className="flex-1 text-xs" onClick={duplicateSlide}>
                  <Copy className="mr-1 h-3 w-3" /> Copy
                </Button>
              </div>
            </TabsContent>
            <TabsContent value="elements" className="p-2 space-y-2">
              {["text", "image", "shape", "icon", "connector"].map((type) => (
                <Button key={type} variant="outline" className="w-full justify-start text-xs capitalize" onClick={() => addElement(type as SlideElement["type"])}>
                  {type === "text" && <Type className="mr-2 h-3 w-3" />}
                  {type === "image" && <Image className="mr-2 h-3 w-3" />}
                  {type === "shape" && <Square className="mr-2 h-3 w-3" />}
                  {type === "connector" && <Minus className="mr-2 h-3 w-3" />}
                  {type}
                </Button>
              ))}
            </TabsContent>
          </Tabs>
        </div>

        {/* Canvas */}
        <div
          className="flex-1 overflow-auto bg-muted/30 p-8"
          style={{
            backgroundImage: "radial-gradient(circle, hsl(var(--border)) 1px, transparent 1px)",
            backgroundSize: "20px 20px",
          }}
        >
          <div className="mb-4 flex items-center justify-center gap-2">
            <Button variant="outline" size="icon" className="h-7 w-7" onClick={() => setZoom((z) => Math.max(25, z - 25))}>
              <ZoomOut className="h-3 w-3" />
            </Button>
            <span className="text-xs font-mono w-12 text-center">{zoom}%</span>
            <Button variant="outline" size="icon" className="h-7 w-7" onClick={() => setZoom((z) => Math.min(200, z + 25))}>
              <ZoomIn className="h-3 w-3" />
            </Button>
          </div>

          <div
            ref={canvasRef}
            className="relative mx-auto bg-card shadow-2xl rounded-lg overflow-hidden"
            style={{
              width: `${960 * (zoom / 100)}px`,
              height: `${540 * (zoom / 100)}px`,
            }}
            onMouseDown={(e) => handleCanvasMouseDown(e)}
            onMouseMove={handleCanvasMouseMove}
            onMouseUp={handleCanvasMouseUp}
          >
            {/* Render HTML if present */}
            {currentSlideData?.html && (
              <ScaledSlidePreview
                html={currentSlideData.html}
                title="Slide preview"
                className="absolute inset-0"
              />
            )}

            {/* Render elements */}
            {currentSlideData?.elements.map((el) => (
              <div
                key={el.id}
                className={cn(
                  "absolute cursor-move select-none",
                  selectedElement === el.id && "ring-2 ring-primary"
                )}
                style={{
                  left: `${el.x * (zoom / 100)}px`,
                  top: `${el.y * (zoom / 100)}px`,
                  width: `${el.width * (zoom / 100)}px`,
                  height: `${el.height * (zoom / 100)}px`,
                  transform: `rotate(${el.rotation}deg)`,
                  zIndex: el.zIndex,
                }}
                onMouseDown={(e) => { e.stopPropagation(); handleCanvasMouseDown(e, el.id); }}
              >
                {el.type === "text" && (
                  <div className="h-full w-full p-2 text-sm" contentEditable suppressContentEditableWarning>
                    {el.content}
                  </div>
                )}
                {el.type === "shape" && (
                  <div className="h-full w-full rounded bg-primary/20 border border-primary/40" />
                )}
                {el.type === "image" && (
                  <div className="flex h-full w-full items-center justify-center rounded bg-muted border border-dashed border-border">
                    <Image className="h-6 w-6 text-muted-foreground" />
                  </div>
                )}
                {el.type === "connector" && (
                  <svg className="h-full w-full" viewBox="0 0 100 100">
                    <line x1="0" y1="50" x2="100" y2="50" stroke="hsl(var(--foreground))" strokeWidth="2" />
                  </svg>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Right properties panel */}
        <div className="w-60 flex-shrink-0 overflow-auto border-l border-border bg-card p-3">
          <h3 className="mb-3 text-sm font-semibold">Properties</h3>
          {selected ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <Label className="text-xs">X</Label>
                  <Input type="number" className="h-8 text-xs" value={Math.round(selected.x)} onChange={(e) => updateElement(selected.id, { x: Number(e.target.value) })} />
                </div>
                <div>
                  <Label className="text-xs">Y</Label>
                  <Input type="number" className="h-8 text-xs" value={Math.round(selected.y)} onChange={(e) => updateElement(selected.id, { y: Number(e.target.value) })} />
                </div>
                <div>
                  <Label className="text-xs">W</Label>
                  <Input type="number" className="h-8 text-xs" value={Math.round(selected.width)} onChange={(e) => updateElement(selected.id, { width: Number(e.target.value) })} />
                </div>
                <div>
                  <Label className="text-xs">H</Label>
                  <Input type="number" className="h-8 text-xs" value={Math.round(selected.height)} onChange={(e) => updateElement(selected.id, { height: Number(e.target.value) })} />
                </div>
              </div>
              <div>
                <Label className="text-xs">Rotation</Label>
                <Input type="number" className="h-8 text-xs" value={selected.rotation} onChange={(e) => updateElement(selected.id, { rotation: Number(e.target.value) })} />
              </div>
              <div>
                <Label className="text-xs">Z-Index</Label>
                <Input type="number" className="h-8 text-xs" value={selected.zIndex} onChange={(e) => updateElement(selected.id, { zIndex: Number(e.target.value) })} />
              </div>
              <Separator />
              <div className="flex gap-1">
                <Button variant="outline" size="icon" className="h-7 w-7">
                  <AlignLeft className="h-3 w-3" />
                </Button>
                <Button variant="outline" size="icon" className="h-7 w-7">
                  <AlignCenter className="h-3 w-3" />
                </Button>
                <Button variant="outline" size="icon" className="h-7 w-7">
                  <AlignRight className="h-3 w-3" />
                </Button>
              </div>
              {selected.type === "text" && (
                <div className="flex gap-1">
                  <Button variant="outline" size="icon" className="h-7 w-7">
                    <Bold className="h-3 w-3" />
                  </Button>
                  <Button variant="outline" size="icon" className="h-7 w-7">
                    <Italic className="h-3 w-3" />
                  </Button>
                  <Button variant="outline" size="icon" className="h-7 w-7">
                    <Underline className="h-3 w-3" />
                  </Button>
                </div>
              )}
              <Button variant="destructive" size="sm" className="w-full" onClick={() => deleteElement(selected.id)}>
                <Trash2 className="mr-2 h-3 w-3" /> Delete
              </Button>
            </div>
          ) : (
            <p className="text-xs text-muted-foreground">Select an element to edit its properties</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default SlideEditor;
