import { useState } from "react";
import { useSlideEditor } from "./hooks";
import { Toolbar, EditorSidebar, PropertiesPanel, CanvasArea, ExportModal } from "./components";

const SlideEditor = () => {
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  
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
    deleteSlide,
    duplicateSlide,
    updateElement,
    deleteElement,
    duplicateElement,
    bringForward,
    sendBackward,
    handleDrop,
    handleSave,
    handleElementSelectFromCanvas,
    handleCanvasChange,
  } = useSlideEditor();


  // --- Loading State ---
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen w-screen bg-background">
        <div className="animate-pulse text-xl font-semibold text-muted-foreground">Loading project...</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-background text-foreground">
      {/* Toolbar */}
      <Toolbar
        projectName={projectName}
        isSidebarOpen={isSidebarOpen}
        selectedElementId={selectedElementId}
        slideCanvasRef={slideCanvasRef}
        onNavigateBack={() => navigate(-1)}
        onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        onDeselectElement={() => setSelectedElementId(null)}
        onSetDraggedItem={setDraggedItem}
        onSave={handleSave}
        onResetZoom={() => setZoom(0.5)}
        onExport={() => setIsExportModalOpen(true)}
      />


      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <EditorSidebar
          isOpen={isSidebarOpen}
          slides={slides}
          currentSlideIndex={currentSlideIndex}
          onSlideSelect={setCurrentSlideIndex}
          onAddSlide={addSlide}
          onDeleteSlide={deleteSlide}
          onDuplicateSlide={duplicateSlide}
          onSetDraggedItem={setDraggedItem}
        />

        {/* Canvas Area */}
        <CanvasArea
          currentSlide={currentSlide}
          zoom={zoom}
          canvasRef={canvasRef}
          slideCanvasRef={slideCanvasRef}
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          onElementSelect={handleElementSelectFromCanvas}
          onChange={handleCanvasChange}
          onZoomIn={() => setZoom(Math.min(2, zoom + 0.1))}
          onZoomOut={() => setZoom(Math.max(0.1, zoom - 0.1))}
        />

        {/* Properties Panel */}
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
