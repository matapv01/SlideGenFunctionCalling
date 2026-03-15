import { useSlideEditor } from "./hooks";
import { Toolbar, EditorSidebar, PropertiesPanel, CanvasArea } from "./components";

const SlideEditor = () => {
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
    handleDrop,
    handleSave,
    importSlide,
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
        slideCanvasRef={{ current: null } as any} // temp fix so we dont change Toolbar interface deeply yet
        onNavigateBack={() => navigate(-1)}
        onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        onDeselectElement={() => setSelectedElementId(null)}
        onSetDraggedItem={setDraggedItem}
        onSave={handleSave}
        onResetZoom={() => setZoom(0.5)}
        onImport={importSlide}
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

        <CanvasArea
          currentSlide={currentSlide}
          zoom={zoom}
        />

        {/* Properties Panel */}
        <PropertiesPanel
          selectedElement={selectedElement}
          onUpdateElement={updateElement}
        />
      </div>
    </div>
  );
};

export default SlideEditor;
