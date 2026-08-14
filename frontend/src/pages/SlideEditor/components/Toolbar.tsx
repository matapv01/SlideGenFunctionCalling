import { 
  ArrowLeft, MousePointer, Type, Download, Play, ChevronDown,
  Undo2, Redo2, Trash2 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";
import { useLanguage } from "@/contexts/LanguageContext";

// Reusable tooltip wrapper
const Tip = ({
  label,
  shortcut,
  desc,
  side = "bottom",
  children,
}: {
  label: string;
  shortcut?: string;
  desc?: string;
  side?: "top" | "bottom" | "left" | "right";
  children: React.ReactNode;
}) => (
  <Tooltip delayDuration={400}>
    <TooltipTrigger asChild>{children}</TooltipTrigger>
    <TooltipContent side={side} className="max-w-[180px] text-left">
      <p className="font-semibold text-xs">
        {label}{shortcut && <span className="ml-1.5 text-[10px] opacity-60 font-normal bg-muted/40 px-1 py-0.5 rounded">{shortcut}</span>}
      </p>
      {desc && <p className="text-[11px] text-muted-foreground mt-0.5 leading-snug">{desc}</p>}
    </TooltipContent>
  </Tooltip>
);

interface ToolbarProps {
  projectName: string;
  canUndo: boolean;
  canRedo: boolean;
  selectedElementId: string | null;
  slideCanvasRef: React.RefObject<SlideCanvasHandle>;
  onNavigateBack: () => void;
  onDeselectElement: () => void;
  onAddText: () => void;
  onDeleteElement?: () => void;
  onPresentFromStart: () => void;
  onPresentFromCurrent: () => void;
  onExport: () => void;
}

export const Toolbar = ({
  projectName,
  canUndo,
  canRedo,
  selectedElementId,
  slideCanvasRef,
  onNavigateBack,
  onDeselectElement,
  onAddText,
  onDeleteElement,
  onPresentFromStart,
  onPresentFromCurrent,
  onExport,
}: ToolbarProps) => {
  const { t } = useLanguage();
  return (
    <TooltipProvider>
    <div className="h-14 border-b bg-background/95 backdrop-blur-sm flex items-center justify-between px-3 sticky top-0 z-50 shadow-sm">
      {/* Left Section */}
      <div className="flex items-center gap-1.5">
        <Tip label={t.toolbar_back} desc={t.toolbar_back_desc} side="bottom">
          <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" onClick={onNavigateBack}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Tip>
        <span className="font-semibold text-sm max-w-[180px] truncate text-foreground">{projectName}</span>
      </div>

      {/* Center Section */}
      <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center gap-0.5 bg-muted/60 border border-border/40 p-1 rounded-xl">
        <Tip label={t.toolbar_select} shortcut="V" desc={t.toolbar_select_desc} side="bottom">
          <Button 
            variant={!selectedElementId ? "secondary" : "ghost"} 
            size="sm"
            className="h-8 text-xs px-3 rounded-lg"
            onClick={onDeselectElement}
          >
            <MousePointer className="h-3.5 w-3.5 mr-1.5" /> {t.toolbar_select_button}
          </Button>
        </Tip>
        <Tip label={t.toolbar_add_text} shortcut="T" desc={t.toolbar_add_text_desc} side="bottom">
          <Button 
            variant="ghost"
            size="sm"
            className="h-8 text-xs px-3 rounded-lg"
            onClick={onAddText}
          >
            <Type className="h-3.5 w-3.5 mr-1.5" /> {t.toolbar_add_text_button}
          </Button>
        </Tip>
        <Separator orientation="vertical" className="h-5 mx-0.5 opacity-30" />
        <Tip label={t.toolbar_export} desc={t.toolbar_export_desc} side="bottom">
          <Button variant="ghost" size="sm" className="h-8 text-xs px-3 rounded-lg" onClick={onExport}>
            <Download className="h-3.5 w-3.5 mr-1.5" /> {t.toolbar_export_button}
          </Button>
        </Tip>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              size="sm"
              className="h-8 text-xs px-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 ml-0.5"
            >
              <Play className="h-3.5 w-3.5 mr-1.5" />
              {t.toolbar_present_button}
              <ChevronDown className="h-3.5 w-3.5 ml-1" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="center" className="w-52">
            <DropdownMenuItem onClick={onPresentFromStart}>
              <Play className="h-3.5 w-3.5 mr-2" /> {t.toolbar_present_from_start}
            </DropdownMenuItem>
            <DropdownMenuItem onClick={onPresentFromCurrent}>
              <Play className="h-3.5 w-3.5 mr-2" /> {t.toolbar_present_from_current}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-1">
        <Tip label={t.toolbar_undo} shortcut="Ctrl+Z" desc={t.toolbar_undo_desc} side="bottom">
          <Button 
            variant="ghost" 
            size="icon"
            disabled={!canUndo}
            className="h-8 w-8 text-muted-foreground hover:text-foreground disabled:opacity-30"
            onClick={() => {
              slideCanvasRef.current?.saveHistory?.(true);
              slideCanvasRef.current?.undo();
            }}
          >
            <Undo2 className="h-4 w-4" />
          </Button>
        </Tip>
        <Tip label={t.toolbar_redo} shortcut="Ctrl+Y" desc={t.toolbar_redo_desc} side="bottom">
          <Button 
            variant="ghost" 
            size="icon"
            disabled={!canRedo}
            className="h-8 w-8 text-muted-foreground hover:text-foreground disabled:opacity-30"
            onClick={() => {
              slideCanvasRef.current?.saveHistory?.(true);
              slideCanvasRef.current?.redo();
            }}
          >
            <Redo2 className="h-4 w-4" />
          </Button>
        </Tip>
        <Separator orientation="vertical" className="h-5 mx-1 opacity-40" />
        <Tip label={t.editor_delete} shortcut="Del" desc={t.editor_delete_desc} side="bottom">
          <Button
            variant="ghost"
            size="icon"
            disabled={!selectedElementId}
            className="h-8 w-8 text-destructive hover:text-destructive disabled:opacity-30"
            onClick={() => onDeleteElement?.()}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </Tip>

      </div>
    </div>
    </TooltipProvider>
  );
};
