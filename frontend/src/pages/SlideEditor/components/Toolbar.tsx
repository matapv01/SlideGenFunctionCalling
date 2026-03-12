import { 
  ArrowLeft, Sidebar, MousePointer, Type, Download, Play, 
  Undo2, Redo2, Save, Settings, Maximize, Upload 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";

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
    <TooltipProvider>
    <div className="h-14 border-b bg-background/95 backdrop-blur-sm flex items-center justify-between px-3 sticky top-0 z-50 shadow-sm">
      {/* Left Section */}
      <div className="flex items-center gap-1.5">
        <Tip label="Quay lại" desc="Trở về trang danh sách dự án" side="bottom">
          <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" onClick={onNavigateBack}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Tip>
        <span className="font-semibold text-sm max-w-[180px] truncate text-foreground">{projectName}</span>
        <Separator orientation="vertical" className="h-5 mx-1 opacity-40" />
        <Tip label="Thanh bên" desc="Hiển thị/ẩn danh sách slide và thư viện phần tử" side="bottom">
          <Button 
            variant={isSidebarOpen ? "secondary" : "ghost"} 
            size="icon"
            className="h-8 w-8"
            onClick={onToggleSidebar}
          >
            <Sidebar className="h-4 w-4" />
          </Button>
        </Tip>
      </div>

      {/* Center Section */}
      <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center gap-0.5 bg-muted/60 border border-border/40 p-1 rounded-xl">
        <Tip label="Chọn" shortcut="V" desc="Chọn, di chuyển và thay đổi kích thước phần tử" side="bottom">
          <Button 
            variant={!selectedElementId ? "secondary" : "ghost"} 
            size="sm"
            className="h-8 text-xs px-3 rounded-lg"
            onClick={onDeselectElement}
          >
            <MousePointer className="h-3.5 w-3.5 mr-1.5" /> Select
          </Button>
        </Tip>
        <Tip label="Thêm văn bản" shortcut="T" desc="Kéo vào canvas hoặc click để thêm hộp chữ" side="bottom">
          <Button 
            variant="ghost"
            size="sm"
            className="h-8 text-xs px-3 rounded-lg"
            onClick={() => onSetDraggedItem({ type: 'text', subType: 'paragraph' })}
          >
            <Type className="h-3.5 w-3.5 mr-1.5" /> Text
          </Button>
        </Tip>
        <Separator orientation="vertical" className="h-5 mx-0.5 opacity-30" />
        <Tip label="Xuất file" desc="Xuất slide thành PDF, PPTX hoặc hình ảnh" side="bottom">
          <Button variant="ghost" size="sm" className="h-8 text-xs px-3 rounded-lg" onClick={onExport}>
            <Download className="h-3.5 w-3.5 mr-1.5" /> Export
          </Button>
        </Tip>
        <Tip label="Trình chiếu" shortcut="F5" desc="Bắt đầu trình chiếu toàn màn hình từ slide đầu" side="bottom">
          <Button
            size="sm"
            className="h-8 text-xs px-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 ml-0.5"
            onClick={onPresent}
          >
            <Play className="h-3.5 w-3.5 mr-1.5" /> Present
          </Button>
        </Tip>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-1">
        <Tip label="Hoàn tác" shortcut="Ctrl+Z" desc="Quay lại thao tác vừa thực hiện" side="bottom">
          <Button 
            variant="ghost" 
            size="icon"
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
            onClick={() => slideCanvasRef.current?.undo()}
          >
            <Undo2 className="h-4 w-4" />
          </Button>
        </Tip>
        <Tip label="Làm lại" shortcut="Ctrl+Y" desc="Khôi phục thao tác đã hoàn tác" side="bottom">
          <Button 
            variant="ghost" 
            size="icon"
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
            onClick={() => slideCanvasRef.current?.redo()}
          >
            <Redo2 className="h-4 w-4" />
          </Button>
        </Tip>
        <Separator orientation="vertical" className="h-5 mx-1 opacity-40" />
        <Tip label="Lưu" shortcut="Ctrl+S" desc="Lưu toàn bộ thay đổi lên server" side="bottom">
          <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" onClick={onSave}>
            <Save className="h-4 w-4" />
          </Button>
        </Tip>
        <Tip label="Khôi phục zoom" desc="Đặt lại tỉ lệ hiển thị về 50%" side="bottom">
          <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" onClick={onResetZoom}>
            <Maximize className="h-4 w-4" />
          </Button>
        </Tip>
      </div>
    </div>
    </TooltipProvider>
  );
};
