import { 
  ArrowLeft, Sidebar, MousePointer, Type, Download, Play, 
  Undo2, Redo2, Save, Settings, Maximize, Upload 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useEditorStore } from "../store/useEditorStore";
import React, { useRef } from "react";

interface ToolbarProps {
  projectName: string;
  isSidebarOpen: boolean;
  selectedElementId: string | null;
  slideCanvasRef: React.RefObject<any>;
  onNavigateBack: () => void;
  onToggleSidebar: () => void;
  onDeselectElement: () => void;
  onSetDraggedItem: (item: { type: string; subType: string }) => void;
  onSave: () => void;
  onResetZoom: () => void;
  onImport: (html: string) => void;
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
  onResetZoom,
  onImport,
}: ToolbarProps) => {
  const { undo, redo, pastStates, futureStates } = useEditorStore.temporal.getState();
  const { currentSlideId, addElement } = useEditorStore();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleAddText = (subType: 'heading' | 'paragraph') => {
    if (!currentSlideId) return;
    addElement(currentSlideId, {
      type: 'text',
      content: subType === 'heading' ? 'Heading' : 'Text block',
      x: 760, y: 440,
      width: 400, height: subType === 'heading' ? 80 : 50,
      rotation: 0, zIndex: 100, opacity: 1,
      fontSize: subType === 'heading' ? 48 : 24,
      color: '#000000',
      textAlign: 'left',
    });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result;
        if (typeof content === 'string') {
          onImport(content);
        }
      };
      reader.readAsText(file);
    }
    // Reset the input value so the same file can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="h-14 border-b bg-background flex items-center justify-between px-4 sticky top-0 z-50">
      {/* Left Section */}
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={onNavigateBack}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <span className="font-semibold text-sm max-w-[200px] truncate">{projectName}</span>
        <Separator orientation="vertical" className="h-6 mx-2" />
        <Button 
          variant={isSidebarOpen ? "secondary" : "ghost"} 
          size="icon" 
          onClick={onToggleSidebar}
          title="Toggle Sidebar"
        >
          <Sidebar className="h-5 w-5" />
        </Button>
      </div>

      {/* Center Section */}
      <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center gap-1 bg-muted/30 p-1 rounded-md">
        <Button 
          variant={!selectedElementId ? "secondary" : "ghost"} 
          size="sm" 
          onClick={onDeselectElement}
        >
          <MousePointer className="h-4 w-4 mr-2" /> Select
        </Button>
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => handleAddText('paragraph')}
          title="Add text block to slide"
        >
          <Type className="h-4 w-4 mr-2" /> Text
        </Button>
        <Button variant="ghost" size="sm">
          <Download className="h-4 w-4 mr-2" /> Export
        </Button>
        <Button variant="ghost" size="sm" className="text-blue-600 bg-blue-50/50 hover:bg-blue-100">
          <Play className="h-4 w-4 mr-2" /> Present
        </Button>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-2">
        <Button 
          variant="ghost" 
          size="icon" 
          title="Undo"
          onClick={() => undo()}
          disabled={pastStates.length === 0}
        >
          <Undo2 className="h-4 w-4" />
        </Button>
        <Button 
          variant="ghost" 
          size="icon" 
          title="Redo"
          onClick={() => redo()}
          disabled={futureStates.length === 0}
        >
          <Redo2 className="h-4 w-4" />
        </Button>
        <Separator orientation="vertical" className="h-6 mx-2" />
        <Button variant="ghost" size="icon" title="Save" onClick={onSave}>
          <Save className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" title="Properties">
          <Settings className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" onClick={onResetZoom} title="Reset Zoom">
          <Maximize className="h-4 w-4" />
        </Button>
        <input 
          type="file" 
          accept=".html" 
          style={{ display: 'none' }} 
          ref={fileInputRef} 
          onChange={handleFileChange} 
        />
        <Button variant="default" size="sm" className="ml-2" onClick={() => fileInputRef.current?.click()}>
          <Upload className="h-4 w-4 mr-2" /> Import
        </Button>
      </div>
    </div>
  );
};
