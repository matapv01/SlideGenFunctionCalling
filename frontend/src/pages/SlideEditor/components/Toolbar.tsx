import { 
  ArrowLeft, Sidebar, MousePointer, Type, Download, Play, 
  Undo2, Redo2, Save, Settings, Maximize, Upload 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";

interface ToolbarProps {
  projectName: string;
  isSidebarOpen: boolean;
  selectedElementId: string | null;
  slideCanvasRef: React.RefObject<SlideCanvasHandle>;
  onNavigateBack: () => void;
  onToggleSidebar: () => void;
  onDeselectElement: () => void;
  onSetDraggedItem: (item: { type: string; subType: string }) => void;
  onSave: () => void;
  onPresent: () => void;
  onResetZoom: () => void;
  onExport: () => void;
}

export const Toolbar = ({
  projectName,
  isSidebarOpen,
  selectedElementId,
  slideCanvasRef,
  onNavigateBack,
  onToggleSidebar,
  onDeselectElement,
  onSetDraggedItem,
  onSave,
  onPresent,
  onResetZoom,
  onExport,
}: ToolbarProps) => {
  return (
    <div className="h-14 border-b bg-background/95 backdrop-blur-sm flex items-center justify-between px-3 sticky top-0 z-50 shadow-sm">
      {/* Left Section */}
      <div className="flex items-center gap-1.5">
        <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" onClick={onNavigateBack}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <span className="font-semibold text-sm max-w-[180px] truncate text-foreground">{projectName}</span>
        <Separator orientation="vertical" className="h-5 mx-1 opacity-40" />
        <Button 
          variant={isSidebarOpen ? "secondary" : "ghost"} 
          size="icon"
          className="h-8 w-8"
          onClick={onToggleSidebar}
          title="Toggle Sidebar"
        >
          <Sidebar className="h-4 w-4" />
        </Button>
      </div>

      {/* Center Section */}
      <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center gap-0.5 bg-muted/60 border border-border/40 p-1 rounded-xl">
        <Button 
          variant={!selectedElementId ? "secondary" : "ghost"} 
          size="sm"
          className="h-8 text-xs px-3 rounded-lg"
          onClick={onDeselectElement}
        >
          <MousePointer className="h-3.5 w-3.5 mr-1.5" /> Select
        </Button>
        <Button 
          variant="ghost"
          size="sm"
          className="h-8 text-xs px-3 rounded-lg"
          onClick={() => onSetDraggedItem({ type: 'text', subType: 'paragraph' })}
        >
          <Type className="h-3.5 w-3.5 mr-1.5" /> Text
        </Button>
        <Separator orientation="vertical" className="h-5 mx-0.5 opacity-30" />
        <Button variant="ghost" size="sm" className="h-8 text-xs px-3 rounded-lg" onClick={onExport}>
          <Download className="h-3.5 w-3.5 mr-1.5" /> Export
        </Button>
        <Button
          size="sm"
          className="h-8 text-xs px-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 ml-0.5"
          onClick={onPresent}
        >
          <Play className="h-3.5 w-3.5 mr-1.5" /> Present
        </Button>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-1">
        <Button 
          variant="ghost" 
          size="icon"
          className="h-8 w-8 text-muted-foreground hover:text-foreground"
          title="Undo (Ctrl+Z)"
          onClick={() => slideCanvasRef.current?.undo()}
        >
          <Undo2 className="h-4 w-4" />
        </Button>
        <Button 
          variant="ghost" 
          size="icon"
          className="h-8 w-8 text-muted-foreground hover:text-foreground"
          title="Redo (Ctrl+Y)"
          onClick={() => slideCanvasRef.current?.redo()}
        >
          <Redo2 className="h-4 w-4" />
        </Button>
        <Separator orientation="vertical" className="h-5 mx-1 opacity-40" />
        <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" title="Save (Ctrl+S)" onClick={onSave}>
          <Save className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" title="Reset Zoom" onClick={onResetZoom}>
          <Maximize className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};
