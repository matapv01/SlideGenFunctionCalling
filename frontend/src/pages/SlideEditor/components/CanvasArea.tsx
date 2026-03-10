import { Button } from "@/components/ui/button";
import { SlideCanvas, SlideCanvasHandle } from "@/components/SlideCanvas";
import type { Slide } from "../types";

interface CanvasAreaProps {
  currentSlide: Slide | undefined;
  zoom: number;
  canvasRef: React.RefObject<HTMLDivElement>;
  slideCanvasRef: React.RefObject<SlideCanvasHandle>;
  onDragOver: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent) => void;
  onElementSelect: (elementData: any) => void;
  onChange?: () => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
}

export const CanvasArea = ({
  currentSlide,
  zoom,
  canvasRef,
  slideCanvasRef,
  onDragOver,
  onDrop,
  onElementSelect,
  onChange,
  onZoomIn,
  onZoomOut,
}: CanvasAreaProps) => {
  return (
    <div 
      className="flex-1 bg-neutral-100 overflow-auto relative flex items-center justify-center p-20"
      onDragOver={onDragOver}
      onDrop={onDrop}
    >
      <div 
        className="relative transition-transform duration-200 ease-out origin-center"
        style={{ transform: `scale(${zoom})` }}
        ref={canvasRef}
      >
        {/* Render Slide with Shadow DOM Isolation */}
        {currentSlide && currentSlide.elements.length > 0 && (
          <SlideCanvas
            ref={slideCanvasRef}
            slideId={currentSlide.id}
            htmlContent={
              currentSlide.elements[0]?.content || 
              '<div class="slide-container"><p>Empty slide</p></div>'
            }
            backgroundColor={currentSlide.backgroundColor}
            onChange={onChange}
            onElementSelect={onElementSelect}
          />
        )}
        
        {/* Fallback if slide not loaded */}
        {(!currentSlide || currentSlide.elements.length === 0) && (
          <div className="w-[1920px] h-[1080px] bg-white shadow-2xl flex items-center justify-center text-gray-400">
            <p>Loading slide...</p>
          </div>
        )}
      </div>

      {/* Zoom Controls Overlay */}
      <div className="absolute bottom-6 right-6 flex items-center bg-white/90 backdrop-blur border rounded-md shadow-lg p-1 gap-2 z-50">
        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onZoomOut}>
          <span className="text-lg font-bold leading-none">-</span>
        </Button>
        <span className="text-xs font-mono w-12 text-center">{Math.round(zoom * 100)}%</span>
        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onZoomIn}>
          <span className="text-lg font-bold leading-none">+</span>
        </Button>
      </div>
    </div>
  );
};
