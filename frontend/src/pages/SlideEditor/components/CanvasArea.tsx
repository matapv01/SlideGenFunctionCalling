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
      className="flex-1 overflow-auto relative flex items-center justify-center p-20"
      style={{
        backgroundColor: 'hsl(var(--muted) / 0.35)',
        backgroundImage: 'radial-gradient(circle, hsl(var(--foreground) / 0.08) 1px, transparent 1px)',
        backgroundSize: '20px 20px',
      }}
      onDragOver={onDragOver}
      onDrop={onDrop}
    >
      <div 
        className="relative transition-transform duration-200 ease-out origin-center"
        style={{ transform: `scale(${zoom})` }}
        ref={canvasRef}
      >
        {/* Slide shadow ring wrapper */}
        <div className="rounded shadow-2xl ring-1 ring-black/10 dark:ring-white/5 overflow-hidden">
          {currentSlide ? (
            <SlideCanvas
              ref={slideCanvasRef}
              slideId={currentSlide.id}
              htmlContent={currentSlide.elements[0]?.content || ''}
              backgroundColor={currentSlide.backgroundColor}
              onChange={onChange}
              onElementSelect={onElementSelect}
              zoom={zoom}
            />
          ) : (
            <div className="w-[1920px] h-[1080px] bg-white flex items-center justify-center text-gray-400">
              <p>Loading slide...</p>
            </div>
          )}
        </div>
      </div>

      {/* Zoom Controls Overlay */}
      <div className="absolute bottom-5 right-5 flex items-center bg-background/90 backdrop-blur-md border border-border/40 rounded-xl shadow-lg p-1 gap-1 z-50">
        <Button variant="ghost" size="icon" className="h-7 w-7 rounded-lg hover:bg-muted" onClick={onZoomOut}>
          <span className="text-base font-semibold leading-none select-none">−</span>
        </Button>
        <span className="text-xs font-mono w-11 text-center text-muted-foreground tabular-nums">{Math.round(zoom * 100)}%</span>
        <Button variant="ghost" size="icon" className="h-7 w-7 rounded-lg hover:bg-muted" onClick={onZoomIn}>
          <span className="text-base font-semibold leading-none select-none">+</span>
        </Button>
      </div>
    </div>
  );
};
