import { useState } from "react";
import { useParams } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useSlideEditor } from "./hooks";
import { Toolbar, EditorSidebar, PropertiesPanel, CanvasArea, ExportModal } from "./components";
import { useLanguage } from "@/contexts/LanguageContext";

const MIN_ZOOM = 0.1;
const MAX_ZOOM = 2;
const ZOOM_STEP = 0.01; // 1%

const clampAndRoundZoom = (value: number) => {
  const clamped = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, value));
  return Math.round(clamped * 100) / 100;
};

type SidebarLayout = "both-open" | "left-open" | "right-open" | "both-closed";

const SlideEditor = () => {
  const { projectId } = useParams();
  const { t } = useLanguage();
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [isPropsPanelOpen, setIsPropsPanelOpen] = useState(true);
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);
  
  const {
    // State
    slides,
    currentSlide,
    currentSlideIndex,
    selectedElementId,
    selectedElement,
    zoom,
    isSidebarOpen,
    projectName,
    loading,
    
    // Refs
    canvasRef,
    slideCanvasRef,
    
    // Setters
    setCurrentSlideIndex,
    setSelectedElementId,
    setZoom,
    setDraggedItem,
    setIsSidebarOpen,
    
    // Actions
    navigate,
    addSlide,
    addSlideFromTemplate,
    addElement,
    deleteSlide,
    duplicateSlide,
    reorderSlides,
    updateElement,
    deleteElement,
    duplicateElement,
    bringForward,
    sendBackward,
    handleDrop,
    handleSave,
    handleElementSelectFromCanvas,
    handleCanvasChange: _handleCanvasChange,
    selectSlide,
  } = useSlideEditor();

  const handleCanvasChange = () => {
    _handleCanvasChange();
    setCanUndo(slideCanvasRef.current?.canUndo() ?? false);
    setCanRedo(slideCanvasRef.current?.canRedo() ?? false);
  };

  const sidebarLayout: SidebarLayout = isSidebarOpen
    ? (isPropsPanelOpen ? "both-open" : "left-open")
    : (isPropsPanelOpen ? "right-open" : "both-closed");


  // --- Loading State ---
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen w-screen bg-background">
        <div className="animate-pulse text-xl font-semibold text-muted-foreground">{t.editor_loading}</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-background text-foreground">
      {/* Toolbar */}
      <Toolbar
        projectName={projectName}
        canUndo={canUndo}
        canRedo={canRedo}
        selectedElementId={selectedElementId}
        slideCanvasRef={slideCanvasRef}
        onNavigateBack={() => navigate(-1)}
        onDeselectElement={() => setSelectedElementId(null)}
        onSetDraggedItem={setDraggedItem}
        onDeleteElement={selectedElementId ? () => deleteElement(selectedElementId) : undefined}
        onPresentFromStart={() => navigate(`/present/${projectId}?slide=0`)}
        onPresentFromCurrent={() => navigate(`/present/${projectId}?slide=${currentSlideIndex}`)}
        onExport={() => setIsExportModalOpen(true)}
      />


      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar with edge arrow toggle */}
        <div className="relative flex shrink-0">
          <EditorSidebar
            isOpen={isSidebarOpen}
            slides={slides}
            currentSlideIndex={currentSlideIndex}
            onSlideSelect={selectSlide}
            onAddSlide={addSlide}
            onAddSlideFromTemplate={addSlideFromTemplate}
            onDeleteSlide={deleteSlide}
            onDuplicateSlide={duplicateSlide}
            onReorderSlides={reorderSlides}
            onSetDraggedItem={setDraggedItem}
            onAddElement={(type, subType) => addElement({ type, subType }, 760, 440)}
          />
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-full z-20 h-10 w-4 flex items-center justify-center bg-background border border-l-0 border-border rounded-r-md shadow-sm hover:bg-muted transition-colors"
          >
            {isSidebarOpen ? <ChevronLeft className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
          </button>
        </div>

        {/* Canvas Area */}
        <CanvasArea
          currentSlide={currentSlide}
          slides={slides}
          currentSlideIndex={currentSlideIndex}
          zoom={zoom}
          canvasRef={canvasRef}
          slideCanvasRef={slideCanvasRef}
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          onElementSelect={(data) => { handleElementSelectFromCanvas(data); if (data) setIsPropsPanelOpen(true); }}
          onChange={handleCanvasChange}
          onZoomIn={() => setZoom((prev) => clampAndRoundZoom(prev + ZOOM_STEP))}
          onZoomOut={() => setZoom((prev) => clampAndRoundZoom(prev - ZOOM_STEP))}
          onZoomChange={setZoom}
          sidebarLayout={sidebarLayout}
          onResetZoom={() => setZoom(0.6)}
          onPrevSlide={() => currentSlideIndex > 0 && selectSlide(currentSlideIndex - 1)}
          onNextSlide={() => currentSlideIndex < slides.length - 1 && selectSlide(currentSlideIndex + 1)}
          selectedElementId={selectedElementId}
          onCopyElement={() => {
            if (!selectedElementId) return;
            slideCanvasRef.current?.copySelectedElement(selectedElementId);
          }}
          onPasteElement={() => {
            slideCanvasRef.current?.pasteElement();
          }}
          onDuplicateElement={() => {
            if (!selectedElementId) return;
            duplicateElement(selectedElementId);
          }}
          onDeleteElement={() => {
            if (!selectedElementId) return;
            deleteElement(selectedElementId);
          }}
          onBringForward={() => {
            if (!selectedElementId) return;
            bringForward(selectedElementId);
          }}
          onSendBackward={() => {
            if (!selectedElementId) return;
            sendBackward(selectedElementId);
          }}
        />

        {/* Properties Panel with edge arrow toggle */}
        <div className="relative flex shrink-0">
          <button
            onClick={() => setIsPropsPanelOpen(p => !p)}
            className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-full z-20 h-10 w-4 flex items-center justify-center bg-background border border-r-0 border-border rounded-l-md shadow-sm hover:bg-muted transition-colors"
          >
            {isPropsPanelOpen ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
          </button>
          <div className={`transition-[width] duration-300 ease-in-out overflow-hidden ${isPropsPanelOpen ? 'w-72' : 'w-0'}`}>
            <PropertiesPanel
              selectedElement={selectedElement}
              onUpdateElement={updateElement}
              slideCanvasRef={slideCanvasRef}
              onDeleteElement={selectedElementId ? () => deleteElement(selectedElementId) : undefined}
              onDuplicateElement={selectedElementId ? () => duplicateElement(selectedElementId) : undefined}
              onBringForward={selectedElementId ? () => bringForward(selectedElementId) : undefined}
              onSendBackward={selectedElementId ? () => sendBackward(selectedElementId) : undefined}
            />
          </div>
        </div>
      </div>
      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        slides={slides}
        currentSlideIndex={currentSlideIndex}
        slideCanvasRef={slideCanvasRef}
        projectName={projectName}
      />
    </div>
  );
};

export default SlideEditor;
