import { Button } from "@/components/ui/button";
import { SlideCanvas, SlideCanvasHandle } from "@/components/SlideCanvas";
import { ChevronLeft, ChevronRight } from "lucide-react";
import type { Slide } from "../types";

interface CanvasAreaProps {
  currentSlide: Slide | undefined;
  slides: Slide[];
  currentSlideIndex: number;
  zoom: number;
  canvasRef: React.RefObject<HTMLDivElement>;
  slideCanvasRef: React.RefObject<SlideCanvasHandle>;
  onDragOver: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent) => void;
  onElementSelect: (elementData: any) => void;
  onChange?: () => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onPrevSlide: () => void;
  onNextSlide: () => void;
}

export const CanvasArea = ({
  currentSlide,
  slides,
  currentSlideIndex,
  zoom,
  canvasRef,
  slideCanvasRef,
  onDragOver,
  onDrop,
  onElementSelect,
  onChange,
  onZoomIn,
  onZoomOut,
  onPrevSlide,
  onNextSlide,
}: CanvasAreaProps) => {
  const hasPrev = currentSlideIndex > 0;
  const hasNext = currentSlideIndex < slides.length - 1;

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

      {/* Prev / Next slide navigation */}
      <button
        onClick={onPrevSlide}
        disabled={!hasPrev}
        className="absolute left-3 top-1/2 -translate-y-1/2 z-50 opacity-30 hover:opacity-80 transition-opacity disabled:opacity-0 disabled:cursor-not-allowed"
        title="Previous slide"
      >
        <div className="bg-background/70 backdrop-blur-sm border border-border/30 rounded-xl shadow p-2">
          <ChevronLeft className="h-5 w-5 text-foreground" />
        </div>
      </button>

      <button
        onClick={onNextSlide}
        disabled={!hasNext}
        className="absolute right-3 top-1/2 -translate-y-1/2 z-50 opacity-30 hover:opacity-80 transition-opacity disabled:opacity-0 disabled:cursor-not-allowed"
        title="Next slide"
      >
        <div className="bg-background/70 backdrop-blur-sm border border-border/30 rounded-xl shadow p-2">
          <ChevronRight className="h-5 w-5 text-foreground" />
        </div>
      </button>

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
