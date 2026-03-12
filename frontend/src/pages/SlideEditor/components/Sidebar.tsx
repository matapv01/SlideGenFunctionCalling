import { Plus, Trash2, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import type { Slide, DragItem } from "../types";
import { TEMPLATES, ELEMENTS_CATEGORIES } from "../constants";
import { ReadOnlySlide } from "@/components/ReadOnlySlide";

interface SidebarProps {
  isOpen: boolean;
  slides: Slide[];
  currentSlideIndex: number;
  onSlideSelect: (index: number) => void;
  onAddSlide: () => void;
  onAddSlideFromTemplate: (layout: string) => void;
  onDeleteSlide: (index: number) => void;
  onDuplicateSlide: (index: number) => void;
  onSetDraggedItem: (item: DragItem) => void;
  onAddElement: (type: string, subType: string) => void;
}

// Visual CSS mockup per template layout
const TemplateMockup = ({ layout }: { layout: string }) => {
  const base = "w-full h-full flex flex-col p-2 gap-1.5 bg-background rounded";
  const bar = "bg-foreground/20 rounded-sm";
  const block = "bg-foreground/10 rounded-sm";
  if (layout === "blank") {
    return <div className={base} />;
  }
  if (layout === "title") {
    return (
      <div className={cn(base, "items-center justify-center gap-2")}>
        <div className={cn(bar, "h-2.5 w-3/4")} />
        <div className={cn(bar, "h-1.5 w-1/2 opacity-50")} />
      </div>
    );
  }
  if (layout === "content") {
    return (
      <div className={base}>
        <div className={cn(bar, "h-2 w-2/3")} />
        <div className={cn(block, "flex-1 w-full")} />
      </div>
    );
  }
  if (layout === "two-col") {
    return (
      <div className={base}>
        <div className={cn(bar, "h-2 w-1/2")} />
        <div className="flex-1 flex gap-1.5">
          <div className={cn(block, "flex-1")} />
          <div className={cn(block, "flex-1")} />
        </div>
      </div>
    );
  }
  if (layout === "image-left") {
    return (
      <div className={base}>
        <div className={cn(bar, "h-1.5 w-1/2")} />
        <div className="flex-1 flex gap-1.5">
          <div className={cn("flex-1 rounded-sm bg-primary/10")} />
          <div className="flex-1 flex flex-col gap-1">
            <div className={cn(bar, "h-1.5 w-full opacity-60")} />
            <div className={cn(bar, "h-1.5 w-3/4 opacity-40")} />
            <div className={cn(bar, "h-1.5 w-full opacity-40")} />
          </div>
        </div>
      </div>
    );
  }
  if (layout === "bullets") {
    return (
      <div className={base}>
        <div className={cn(bar, "h-2 w-2/3")} />
        <div className="flex-1 flex flex-col justify-center gap-1.5 pl-1">
          {[80, 65, 72, 58].map((w, i) => (
            <div key={i} className="flex items-center gap-1">
              <div className="w-1 h-1 rounded-full bg-foreground/30 shrink-0" />
              <div className={cn(bar, "h-1.5 opacity-50")} style={{ width: `${w}%` }} />
            </div>
          ))}
        </div>
      </div>
    );
  }
  return <div className={base} />;
};

export const EditorSidebar = ({
  isOpen,
  slides,
  currentSlideIndex,
  onSlideSelect,
  onAddSlide,
  onAddSlideFromTemplate,
  onDeleteSlide,
  onDuplicateSlide,
  onSetDraggedItem,
  onAddElement,
}: SidebarProps) => {
  return (
    <div className={cn(
      "border-r bg-background flex transition-[width] duration-300 ease-in-out overflow-hidden shrink-0",
      isOpen ? "w-56" : "w-12"
    )}>
      {/* Collapsed mini-strip */}
      <div className={cn(
        "flex flex-col items-center gap-1 py-2 transition-opacity duration-200",
        isOpen ? "w-0 overflow-hidden opacity-0 pointer-events-none" : "w-12 opacity-100"
      )}>
        {slides.map((slide, idx) => {
          const rawHtml = slide.elements[0]?.content || '';
          return (
            <button
              key={slide.id}
              onClick={() => onSlideSelect(idx)}
              className={cn(
                "w-8 h-5 rounded overflow-hidden border-2 transition-all duration-150 relative shrink-0",
                currentSlideIndex === idx
                  ? "border-primary shadow-sm shadow-primary/20"
                  : "border-transparent hover:border-border/60"
              )}
              title={`Slide ${idx + 1}`}
            >
              {rawHtml ? (
                <ReadOnlySlide
                  slideId={`mini-${slide.id}-${idx}`}
                  htmlContent={rawHtml}
                  backgroundColor={slide.backgroundColor}
                  className="absolute inset-0"
                />
              ) : (
                <div className="w-full h-full bg-muted/40 flex items-center justify-center text-[7px] text-muted-foreground font-bold">{idx + 1}</div>
              )}
            </button>
          );
        })}
        <button
          onClick={onAddSlide}
          className="w-8 h-5 mt-0.5 rounded border border-dashed border-border/50 flex items-center justify-center hover:border-border hover:bg-muted/40 transition-all"
          title="New Slide"
        >
          <Plus className="h-2.5 w-2.5 text-muted-foreground" />
        </button>
      </div>

      {/* Expanded full panel */}
      <div className={cn(
        "flex-1 flex flex-col transition-opacity duration-200 min-w-0",
        isOpen ? "opacity-100" : "opacity-0 pointer-events-none"
      )}>
        <Tabs defaultValue="slides" className="flex-1 flex flex-col h-full">
          <TabsList className="w-full justify-start rounded-none border-b h-11 p-0 bg-transparent gap-0">
            <TabsTrigger 
              value="slides" 
              className="flex-1 h-full rounded-none text-xs font-medium data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-foreground text-muted-foreground"
            >
              Slides
            </TabsTrigger>
            <TabsTrigger 
              value="templates" 
              className="flex-1 h-full rounded-none text-xs font-medium data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-foreground text-muted-foreground"
            >
              Templates
            </TabsTrigger>
            <TabsTrigger 
              value="elements" 
              className="flex-1 h-full rounded-none text-xs font-medium data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-foreground text-muted-foreground"
            >
              Elements
            </TabsTrigger>
          </TabsList>

          <TabsContent value="slides" className="flex-1 overflow-y-auto p-2 space-y-1.5 mt-0">
            <div className="grid gap-1.5">
              {slides.map((slide, idx) => {
                const rawHtml = slide.elements[0]?.content || '';
                return (
                  <div 
                    key={slide.id}
                    className={cn(
                      "group relative aspect-video rounded-lg cursor-pointer transition-all duration-150 overflow-hidden border-2",
                      currentSlideIndex === idx
                        ? "border-primary ring-2 ring-primary/20 shadow-md shadow-primary/10"
                        : "border-transparent hover:border-border/70 hover:shadow-sm"
                    )}
                    onClick={() => onSlideSelect(idx)}
                  >
                    <div className="absolute top-1.5 left-1.5 bg-black/55 backdrop-blur-sm text-white text-[9px] font-semibold px-1.5 py-0.5 rounded-md z-10 tabular-nums leading-tight">
                      {idx + 1}
                    </div>
                    {rawHtml ? (
                      <ReadOnlySlide
                        slideId={`thumb-${slide.id}-${idx}`}
                        htmlContent={rawHtml}
                        backgroundColor={slide.backgroundColor}
                        className="absolute inset-0"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-muted-foreground/20 text-2xl font-bold bg-muted/30">
                        {idx + 1}
                      </div>
                    )}
                    
                    {/* Hover Actions */}
                    <div className="absolute bottom-1 right-1 opacity-0 group-hover:opacity-100 flex gap-0.5 transition-all duration-150 bg-background/85 backdrop-blur-sm rounded-md shadow z-10 p-0.5">
                      <Button 
                        size="icon" 
                        variant="ghost" 
                        className="h-5 w-5 rounded"
                        onClick={(e) => { e.stopPropagation(); onDuplicateSlide(idx); }}
                      >
                        <Copy className="h-2.5 w-2.5" />
                      </Button>
                      <Button 
                        size="icon" 
                        variant="ghost" 
                        className="h-5 w-5 rounded text-destructive hover:text-destructive"
                        onClick={(e) => { e.stopPropagation(); onDeleteSlide(idx); }}
                      >
                        <Trash2 className="h-2.5 w-2.5" />
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
            <Button variant="ghost" className="w-full h-9 border border-dashed border-border/50 text-muted-foreground hover:text-foreground hover:border-border mt-1 rounded-lg text-xs" onClick={onAddSlide}>
              <Plus className="h-3.5 w-3.5 mr-1.5" /> New Slide
            </Button>
          </TabsContent>

          {/* Templates Tab */}
          <TabsContent value="templates" className="flex-1 overflow-y-auto mt-0">
            <div className="p-2.5">
              <p className="text-[10px] text-muted-foreground mb-2 px-0.5">Click a layout to add a new slide</p>
              <div className="grid grid-cols-2 gap-2">
                {TEMPLATES.map(tmpl => (
                  <button
                    key={tmpl.id}
                    className="flex flex-col gap-1 group cursor-pointer text-left"
                    onClick={() => onAddSlideFromTemplate(tmpl.layout)}
                    title={`Add "${tmpl.name}" slide`}
                  >
                    <div className="w-full aspect-video border-2 border-transparent group-hover:border-primary/60 rounded-md overflow-hidden transition-all duration-150 group-hover:shadow-sm bg-muted/30">
                      <TemplateMockup layout={tmpl.layout} />
                    </div>
                    <span className="text-[10px] text-muted-foreground group-hover:text-foreground font-medium text-center w-full transition-colors truncate px-0.5">
                      {tmpl.name}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </TabsContent>

          {/* Elements Tab */}
          <TabsContent value="elements" className="flex-1 overflow-y-auto mt-0">
            <div className="p-2.5 space-y-4">
              {ELEMENTS_CATEGORIES.map(cat => (
                <div key={cat.name}>
                  <h3 className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-1.5 px-0.5">{cat.name}</h3>
                  <div className="grid grid-cols-3 gap-1.5">
                    {cat.items.map(item => (
                      <button
                        key={item.id}
                        className="flex flex-col items-center justify-center gap-1 p-2 rounded-lg border border-transparent hover:border-border hover:bg-muted/50 text-muted-foreground hover:text-foreground active:scale-95 transition-all duration-100 cursor-pointer group"
                        onClick={() => onAddElement(item.type, item.subType)}
                        draggable
                        onDragStart={() => onSetDraggedItem({ type: item.type, subType: item.subType })}
                        title={`Add ${item.label}`}
                      >
                        <item.icon className="h-5 w-5" />
                        <span className="text-[9px] leading-tight text-center">{item.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

