import { useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { SlideCanvas, SlideCanvasHandle } from "@/components/SlideCanvas";
import { Maximize2 } from "lucide-react";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuShortcut,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
import type { Slide } from "../types";
import { useLanguage } from "@/contexts/LanguageContext";

const SLIDE_W = 1920;
const SLIDE_H = 1080;
const PAD = 48; // px on each side

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
  onZoomChange: (z: number) => void;
  autoFit: boolean;
  onResetZoom: () => void;
  onPrevSlide: () => void;
  onNextSlide: () => void;
  selectedElementId: string | null;
  onCopyElement: () => void;
  onPasteElement: () => void;
  onDuplicateElement: () => void;
  onDeleteElement: () => void;
  onBringForward: () => void;
  onSendBackward: () => void;
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
  onZoomChange,
  autoFit,
  onResetZoom,
  onPrevSlide,
  onNextSlide,
  selectedElementId,
  onCopyElement,
  onPasteElement,
  onDuplicateElement,
  onDeleteElement,
  onBringForward,
  onSendBackward,
}: CanvasAreaProps) => {
  const { t } = useLanguage();
  const hasPrev = currentSlideIndex > 0;
  const hasNext = currentSlideIndex < slides.length - 1;
  const containerRef = useRef<HTMLDivElement>(null);

  // Keyboard navigation
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      // Don't interfere when user is typing in an input/contenteditable
      const tag = (e.target as HTMLElement)?.tagName?.toLowerCase();
      if (['input', 'textarea', 'select'].includes(tag)) return;
      if ((e.target as HTMLElement)?.isContentEditable) return;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        e.preventDefault();
        onNextSlide();
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault();
        onPrevSlide();
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onPrevSlide, onNextSlide]);

  // Recalculate zoom whenever container is resized
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const recalc = () => {
      const availW = el.clientWidth  - PAD * 2;
      const availH = el.clientHeight - PAD * 2;
      if (availW <= 0 || availH <= 0) return;
      const fit = Math.min(availW / SLIDE_W, availH / SLIDE_H);
      onZoomChange(Math.floor(fit * 100) / 100);
    };
    recalc();
    const ro = new ResizeObserver(recalc);
    ro.observe(el);
    return () => ro.disconnect();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-auto relative flex items-center justify-center"
      style={{
        padding: PAD,
        backgroundColor: 'hsl(var(--muted) / 0.35)',
        backgroundImage: 'radial-gradient(circle, hsl(var(--foreground) / 0.08) 1px, transparent 1px)',
        backgroundSize: '20px 20px',
      }}
      onDragOver={onDragOver}
      onDrop={onDrop}
    >
      {/* Outer wrapper occupies the post-scale footprint so centering stays correct */}
      <ContextMenu>
        <ContextMenuTrigger asChild>
          <div style={{ width: 1920 * zoom, height: 1080 * zoom, flexShrink: 0 }}>
            <div
              ref={canvasRef}
              className="relative transition-transform duration-200 ease-out"
              style={{
                width: 1920,
                height: 1080,
                transform: `scale(${zoom})`,
                transformOrigin: 'top left',
              }}
            >
              {/* Slide shadow ring wrapper */}
              <div className="rounded shadow-2xl ring-1 ring-black/10 dark:ring-white/5 overflow-hidden" style={{ width: 1920, height: 1080 }}>
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
                  <div className="bg-white flex items-center justify-center text-gray-400" style={{ width: 1920, height: 1080 }}>
                    <p>{t.editor_loading_slide}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </ContextMenuTrigger>

        <ContextMenuContent className="w-56">
          <ContextMenuItem disabled={!selectedElementId} onClick={onCopyElement}>
            Copy
            <ContextMenuShortcut>Ctrl+C</ContextMenuShortcut>
          </ContextMenuItem>
          <ContextMenuItem onClick={onPasteElement}>
            Paste
            <ContextMenuShortcut>Ctrl+V</ContextMenuShortcut>
          </ContextMenuItem>
          <ContextMenuItem disabled={!selectedElementId} onClick={onDuplicateElement}>
            Duplicate
            <ContextMenuShortcut>Ctrl+D</ContextMenuShortcut>
          </ContextMenuItem>
          <ContextMenuSeparator />
          <ContextMenuItem disabled={!selectedElementId} onClick={onBringForward}>
            Bring Forward
            <ContextMenuShortcut>Ctrl+]</ContextMenuShortcut>
          </ContextMenuItem>
          <ContextMenuItem disabled={!selectedElementId} onClick={onSendBackward}>
            Send Backward
            <ContextMenuShortcut>Ctrl+[</ContextMenuShortcut>
          </ContextMenuItem>
          <ContextMenuSeparator />
          <ContextMenuItem disabled={!selectedElementId} className="text-destructive focus:text-destructive" onClick={onDeleteElement}>
            Delete
            <ContextMenuShortcut>Del</ContextMenuShortcut>
          </ContextMenuItem>
        </ContextMenuContent>
      </ContextMenu>

      {/* Zoom Controls Overlay */}
      <div className="absolute bottom-5 right-5 flex items-center bg-background/90 backdrop-blur-md border border-border/40 rounded-xl shadow-lg p-1 gap-1 z-50">
        <Button variant="ghost" size="icon" className="h-7 w-7 rounded-lg hover:bg-muted" onClick={onZoomOut}>
          <span className="text-base font-semibold leading-none select-none">−</span>
        </Button>
        <span className="text-xs font-mono w-11 text-center text-muted-foreground tabular-nums">{Math.round(zoom * 100)}%</span>
        <Button variant="ghost" size="icon" className="h-7 w-7 rounded-lg hover:bg-muted" onClick={onZoomIn}>
          <span className="text-base font-semibold leading-none select-none">+</span>
        </Button>
        <div className="w-px h-4 bg-border/50 mx-0.5" />
        <Button variant="ghost" size="icon" className="h-7 w-7 rounded-lg hover:bg-muted" onClick={onResetZoom} title={t.editor_reset_zoom}>
          <Maximize2 className="h-3.5 w-3.5 text-muted-foreground" />
        </Button>
      </div>
    </div>
  );
};
