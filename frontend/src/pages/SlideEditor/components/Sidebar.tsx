import { useState, useRef } from "react";
import { Plus, Trash2, Copy, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import type { Slide, DragItem } from "../types";
import { TEMPLATES, ELEMENTS_CATEGORIES } from "../constants";
import { ReadOnlySlide } from "@/components/ReadOnlySlide";
import { useLanguage } from "@/contexts/LanguageContext";

interface SidebarProps {
  isOpen: boolean;
  slides: Slide[];
  currentSlideIndex: number;
  onSlideSelect: (index: number) => void;
  onAddSlide: () => void;
  onAddSlideFromTemplate: (layout: string) => void;
  onDeleteSlide: (index: number) => void;
  onDuplicateSlide: (index: number) => void;
  onReorderSlides: (fromIndex: number, toIndex: number) => void;
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
  onReorderSlides,
  onSetDraggedItem,
  onAddElement,
}: SidebarProps) => {
  const { t, language } = useLanguage();
  const [elementQuery, setElementQuery] = useState("");

  const tmplLabel: Record<string, string> = {
    blank: t.editor_tmpl_blank,
    title: t.editor_tmpl_title,
    content: t.editor_tmpl_content,
    "two-col": t.editor_tmpl_two_col,
    "img-left": t.editor_tmpl_img_text,
    bullets: t.editor_tmpl_bullets,
  };

  const catLabel: Record<string, string> = {
    Text: t.editor_cat_text,
    Shapes: t.editor_cat_shapes,
    Icons: language === "vi" ? "Biểu tượng" : "Icons",
    Media: t.editor_cat_media,
  };

  const elLabel: Record<string, string> = {
    heading: t.editor_el_title,
    subheading: t.editor_el_subtitle,
    paragraph: t.editor_el_body,
    label: t.editor_el_label,
    rect: t.editor_el_rect,
    circle: t.editor_el_circle,
    triangle: t.editor_el_triangle,
    star: t.editor_el_star,
    diamond: t.editor_el_diamond,
    line: t.editor_el_line,
    equation: 'Equation',
    image: t.editor_el_image,
    video: t.editor_el_video,
  };

  const normalizedElementQuery = elementQuery.trim().toLocaleLowerCase(language);
  const filteredCategories = ELEMENTS_CATEGORIES.map(cat => ({
    ...cat,
    items: cat.items.filter(item => {
      if (!normalizedElementQuery) return true;
      const label = elLabel[item.id] || item.label;
      return `${label} ${catLabel[cat.name] || cat.name}`
        .toLocaleLowerCase(language)
        .includes(normalizedElementQuery);
    }),
  })).filter(cat => cat.items.length > 0);

  // Drag-reorder state
  const dragIndexRef = useRef<number | null>(null);
  const [dropTarget, setDropTarget] = useState<{ index: number; position: 'before' | 'after' } | null>(null);

  const handleSlideDragStart = (e: React.DragEvent, index: number) => {
    dragIndexRef.current = index;
    e.dataTransfer.effectAllowed = 'move';
    // Prevent element-drag from sidebar interfering
    e.dataTransfer.setData('slide-reorder', String(index));
  };

  const handleSlideDragOver = (e: React.DragEvent, index: number) => {
    if (!e.dataTransfer.types.includes('slide-reorder')) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const midY = rect.top + rect.height / 2;
    setDropTarget({ index, position: e.clientY < midY ? 'before' : 'after' });
  };

  const handleSlideDrop = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (dragIndexRef.current === null) return;
    const from = dragIndexRef.current;
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const midY = rect.top + rect.height / 2;
    let to = e.clientY < midY ? index : index + 1;
    // Adjust for removal of source item
    if (from < to) to -= 1;
    dragIndexRef.current = null;
    setDropTarget(null);
    onReorderSlides(from, to);
  };

  const handleSlideDragEnd = () => {
    dragIndexRef.current = null;
    setDropTarget(null);
  };

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
              title={`${t.editor_slide_n} ${idx + 1}`}
            >
              {rawHtml ? (
                <ReadOnlySlide
                  slideId={`mini-${slide.id}-${idx}`}
                  htmlContent={rawHtml}
                  backgroundColor={slide.backgroundColor}
                  backgroundImage={slide.backgroundImage}
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
          title={t.editor_new_slide}
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
              {t.editor_tab_slides}
            </TabsTrigger>
            <TabsTrigger 
              value="templates" 
              className="flex-1 h-full rounded-none text-xs font-medium data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-foreground text-muted-foreground"
            >
              {t.editor_tab_templates}
            </TabsTrigger>
            <TabsTrigger 
              value="elements" 
              className="flex-1 h-full rounded-none text-xs font-medium data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-foreground text-muted-foreground"
            >
              {t.editor_tab_elements}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="slides" className="flex-1 overflow-y-auto p-2 space-y-0 mt-0 [&::-webkit-scrollbar]:hidden" style={{ scrollbarWidth: 'none' }}>
            <div className="grid gap-0">
              {slides.map((slide, idx) => {
                const rawHtml = slide.elements[0]?.content || '';
                const isDragging = dragIndexRef.current === idx;
                const isDropBefore = dropTarget?.index === idx && dropTarget.position === 'before';
                const isDropAfter  = dropTarget?.index === idx && dropTarget.position === 'after';
                return (
                  <div key={slide.id} className="relative">
                    {/* Drop indicator — before */}
                    {isDropBefore && (
                      <div className="h-0.5 rounded-full bg-primary mx-1 mb-1 shadow-[0_0_6px_2px] shadow-primary/50" />
                    )}
                    <div
                      draggable
                      onDragStart={(e) => handleSlideDragStart(e, idx)}
                      onDragOver={(e) => handleSlideDragOver(e, idx)}
                      onDrop={(e) => handleSlideDrop(e, idx)}
                      onDragEnd={handleSlideDragEnd}
                      className={cn(
                        "group relative aspect-video rounded-lg cursor-grab active:cursor-grabbing transition-all duration-150 overflow-hidden border-2 mb-1.5",
                        isDragging && "opacity-40 scale-95",
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
                        backgroundImage={slide.backgroundImage}
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
                    {/* Drop indicator — after */}
                    {isDropAfter && (
                      <div className="h-0.5 rounded-full bg-primary mx-1 mt-0.5 mb-1 shadow-[0_0_6px_2px] shadow-primary/50" />
                    )}
                  </div>
                );
              })}
            </div>
            <Button variant="ghost" className="w-full h-9 border border-dashed border-border/50 text-muted-foreground hover:text-foreground hover:border-border mt-1 rounded-lg text-xs" onClick={onAddSlide}>
              <Plus className="h-3.5 w-3.5 mr-1.5" /> {t.editor_new_slide}
            </Button>
          </TabsContent>

          {/* Templates Tab */}
          <TabsContent value="templates" className="flex-1 overflow-y-auto mt-0 [&::-webkit-scrollbar]:hidden" style={{ scrollbarWidth: 'none' }}>
            <div className="p-2.5">
              <p className="text-[10px] text-muted-foreground mb-2 px-0.5">{t.editor_template_hint}</p>
              <div className="grid grid-cols-2 gap-2">
                {TEMPLATES.map(tmpl => (
                  <button
                    key={tmpl.id}
                    className="flex flex-col gap-1 group cursor-pointer text-left"
                    onClick={() => onAddSlideFromTemplate(tmpl.layout)}
                    title={`${t.editor_add_slide_prefix}: ${tmplLabel[tmpl.id] || tmpl.name}`}
                  >
                    <div className="w-full aspect-video border-2 border-transparent group-hover:border-primary/60 rounded-md overflow-hidden transition-all duration-150 group-hover:shadow-sm bg-muted/30">
                      <TemplateMockup layout={tmpl.layout} />
                    </div>
                    <span className="text-[10px] text-muted-foreground group-hover:text-foreground font-medium text-center w-full transition-colors truncate px-0.5">
                      {tmplLabel[tmpl.id] || tmpl.name}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </TabsContent>

          {/* Elements Tab */}
          <TabsContent value="elements" className="flex-1 overflow-y-auto mt-0 [&::-webkit-scrollbar]:hidden" style={{ scrollbarWidth: 'none' }}>
            <div className="sticky top-0 z-10 bg-background px-2.5 pt-2.5 pb-1.5">
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
                <Input
                  value={elementQuery}
                  onChange={(event) => setElementQuery(event.target.value)}
                  placeholder={language === "vi" ? "Tìm phần tử..." : "Search elements..."}
                  className="h-8 pl-8 text-xs"
                />
              </div>
            </div>
            <div className="px-2.5 pb-3">
              {filteredCategories.length > 0 ? (
                <Accordion
                  type="multiple"
                  defaultValue={ELEMENTS_CATEGORIES.map(cat => cat.name)}
                  className="space-y-1"
                >
                  {filteredCategories.map(cat => (
                    <AccordionItem key={cat.name} value={cat.name} className="rounded-lg border px-2">
                      <AccordionTrigger className="py-2 hover:no-underline">
                        <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                          {catLabel[cat.name] || cat.name}
                        </span>
                      </AccordionTrigger>
                      <AccordionContent className="pb-2">
                        <div className="grid grid-cols-3 gap-1.5">
                          {cat.items.map(item => (
                            <button
                              key={item.id}
                              className="flex min-h-16 flex-col items-center justify-center gap-1 rounded-lg border border-transparent p-2 text-muted-foreground transition-all duration-100 hover:border-border hover:bg-muted/50 hover:text-foreground active:scale-95 cursor-pointer group"
                              onClick={() => onAddElement(item.type, item.subType)}
                              draggable
                              onDragStart={() => onSetDraggedItem({ type: item.type, subType: item.subType })}
                              title={`${t.editor_add_el_prefix} ${elLabel[item.id] || item.label}`}
                            >
                              <item.icon className="h-5 w-5" />
                              <span className="text-[9px] leading-tight text-center">{elLabel[item.id] || item.label}</span>
                            </button>
                          ))}
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              ) : (
                <div className="py-10 text-center text-xs text-muted-foreground">
                  {language === "vi" ? "Không tìm thấy phần tử phù hợp" : "No matching elements"}
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

