import { useState } from "react";
import { useParams } from "react-router-dom";
import { useSlideEditor } from "./hooks";
import { Toolbar, EditorSidebar, PropertiesPanel, CanvasArea, ExportModal } from "./components";

const SlideEditor = () => {
  const { projectId } = useParams();
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
    handleCanvasChange,
    selectSlide,
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
        onPresent={() => navigate(`/present/${projectId}`)}
        onResetZoom={() => setZoom(0.5)}
        onExport={() => setIsExportModalOpen(true)}
      />


      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
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
          onElementSelect={handleElementSelectFromCanvas}
          onChange={handleCanvasChange}
          onZoomIn={() => setZoom(Math.min(2, zoom + 0.1))}
          onZoomOut={() => setZoom(Math.max(0.1, zoom - 0.1))}
          onPrevSlide={() => currentSlideIndex > 0 && selectSlide(currentSlideIndex - 1)}
          onNextSlide={() => currentSlideIndex < slides.length - 1 && selectSlide(currentSlideIndex + 1)}
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
