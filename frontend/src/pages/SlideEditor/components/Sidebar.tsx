import { Plus, Trash2, Copy, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import type { Slide, DragItem, ElementCategory, Template } from "../types";
import { TEMPLATES, ELEMENTS_CATEGORIES } from "../constants";

interface SidebarProps {
  isOpen: boolean;
  slides: Slide[];
  currentSlideIndex: number;
  onSlideSelect: (index: number) => void;
  onAddSlide: () => void;
  onDeleteSlide: (index: number) => void;
  onDuplicateSlide: (index: number) => void;
  onSetDraggedItem: (item: DragItem) => void;
}

export const EditorSidebar = ({
  isOpen,
  slides,
  currentSlideIndex,
  onSlideSelect,
  onAddSlide,
  onDeleteSlide,
  onDuplicateSlide,
  onSetDraggedItem,
}: SidebarProps) => {
  return (
    <div className={cn(
      "w-80 border-r bg-background flex flex-col transition-all duration-300",
      !isOpen && "w-0 overflow-hidden border-none"
    )}>
      <Tabs defaultValue="slides" className="flex-1 flex flex-col h-full">
        <TabsList className="w-full justify-start rounded-none border-b h-12 p-0 bg-transparent">
          <TabsTrigger 
            value="slides" 
            className="flex-1 h-full rounded-none data-[state=active]:bg-background data-[state=active]:border-b-2 data-[state=active]:border-primary"
          >
            Slides
          </TabsTrigger>
          <TabsTrigger 
            value="templates" 
            className="flex-1 h-full rounded-none data-[state=active]:bg-background data-[state=active]:border-b-2 data-[state=active]:border-primary"
          >
            Templates
          </TabsTrigger>
          <TabsTrigger 
            value="elements" 
            className="flex-1 h-full rounded-none data-[state=active]:bg-background data-[state=active]:border-b-2 data-[state=active]:border-primary"
          >
            Elements
          </TabsTrigger>
        </TabsList>

        {/* Slides Tab */}
        <TabsContent value="slides" className="flex-1 overflow-y-auto p-4 space-y-4">
          <div className="grid gap-4">
            {slides.map((slide, idx) => (
              <div 
                key={slide.id}
                className={cn(
                  "group relative aspect-video bg-white border-2 rounded-lg cursor-pointer hover:border-primary/50 transition-all",
                  currentSlideIndex === idx ? "border-primary shadow-md" : "border-border"
                )}
                onClick={() => onSlideSelect(idx)}
              >
                <div className="absolute top-2 left-2 bg-black/50 text-white text-xs px-2 py-0.5 rounded-full z-10">
                  {idx + 1}
                </div>
                <div className="w-full h-full flex items-center justify-center text-muted-foreground/20 text-4xl font-bold bg-neutral-50">
                  {idx + 1}
                </div>
                
                {/* Hover Actions */}
                <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 flex gap-1 transition-opacity bg-background/80 rounded shadow z-10">
                  <Button 
                    size="icon" 
                    variant="ghost" 
                    className="h-6 w-6" 
                    onClick={(e) => { e.stopPropagation(); onDuplicateSlide(idx); }}
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                  <Button 
                    size="icon" 
                    variant="ghost" 
                    className="h-6 w-6 text-destructive" 
                    onClick={(e) => { e.stopPropagation(); onDeleteSlide(idx); }}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
          <Button variant="outline" className="w-full h-12 border-dashed mt-4" onClick={onAddSlide}>
            <Plus className="h-4 w-4 mr-2" /> New Slide
          </Button>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates" className="flex-1 overflow-y-auto p-4">
          <div className="grid grid-cols-2 gap-4">
            {TEMPLATES.map(tmpl => (
              <div 
                key={tmpl.id} 
                className="aspect-[4/3] border rounded-md bg-muted/20 hover:bg-muted cursor-pointer flex flex-col items-center justify-center p-2 text-center select-none"
                draggable
                onDragStart={() => onSetDraggedItem({ type: "template", subType: tmpl.layout })}
              >
                <FileText className="h-8 w-8 mb-2 text-muted-foreground" />
                <span className="text-xs font-medium">{tmpl.name}</span>
              </div>
            ))}
          </div>
        </TabsContent>

        {/* Elements Tab */}
        <TabsContent value="elements" className="flex-1 overflow-y-auto p-4 space-y-6">
          {ELEMENTS_CATEGORIES.map(cat => (
            <div key={cat.name}>
              <h3 className="text-sm font-semibold mb-3 text-muted-foreground">{cat.name}</h3>
              <div className="grid grid-cols-3 gap-2">
                {cat.items.map(item => (
                  <div 
                    key={item.id}
                    className="aspect-square border rounded-md flex flex-col items-center justify-center hover:bg-secondary cursor-grab active:cursor-grabbing p-1"
                    draggable
                    onDragStart={() => onSetDraggedItem({ type: item.type, subType: item.subType })}
                  >
                    <item.icon className="h-6 w-6 mb-1 text-foreground" />
                    <span className="text-[10px] text-center leading-tight">{item.label}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
};
