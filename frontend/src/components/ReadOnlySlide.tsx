import { memo, useRef, useLayoutEffect, useState, useCallback } from "react";
import { SlideCanvas } from "./SlideCanvas";
import { cn } from "@/lib/utils";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "@/pages/SlideEditor/constants";

interface ReadOnlySlideProps {
  slideId: string;
  htmlContent: string;
  backgroundColor?: string;
  backgroundImage?: string;
  className?: string;
}

/**
 * Renders a slide using the exact same Shadow DOM + processHTML pipeline as the editor,
 * but without any editing functionality. Scales to fit the container.
 */
export const ReadOnlySlide = memo(({ slideId, htmlContent, backgroundColor, backgroundImage, className }: ReadOnlySlideProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(0.1);
  const frameRef = useRef<number | null>(null);
  const lastScaleRef = useRef<number>(0.1);

  const updateScale = useCallback(() => {
    if (!containerRef.current) return;
    const { clientWidth: w, clientHeight: h } = containerRef.current;
    const next = Math.min(w / CANVAS_WIDTH, h / CANVAS_HEIGHT);
    // Round to 2 decimals to avoid noisy sub-pixel rerenders and flicker.
    const rounded = Math.max(0.01, Math.round(next * 100) / 100);
    if (Math.abs(rounded - lastScaleRef.current) < 0.01) return;
    lastScaleRef.current = rounded;
    setScale(rounded);
  }, []);

  // Measure before the browser paints the thumbnail. Starting at a fake scale
  // and correcting it in useEffect makes every card visibly jump when it
  // enters the scroll viewport.
  useLayoutEffect(() => {
    const scheduleScaleUpdate = () => {
      if (frameRef.current !== null) cancelAnimationFrame(frameRef.current);
      frameRef.current = requestAnimationFrame(() => {
        frameRef.current = null;
        updateScale();
      });
    };

    scheduleScaleUpdate();
    const ro = new ResizeObserver(scheduleScaleUpdate);
    if (containerRef.current) ro.observe(containerRef.current);
    return () => {
      ro.disconnect();
      if (frameRef.current !== null) {
        cancelAnimationFrame(frameRef.current);
        frameRef.current = null;
      }
    };
  }, [updateScale]);

  const scaledW = Math.round(CANVAS_WIDTH * scale);
  const scaledH = Math.round(CANVAS_HEIGHT * scale);

  return (
    <div ref={containerRef} className={cn("relative overflow-hidden", className)}>
      <div className="absolute inset-0 flex items-center justify-center">
        <div style={{ width: scaledW, height: scaledH, overflow: "hidden", position: "relative" }}>
          <div style={{
            width: CANVAS_WIDTH,
            height: CANVAS_HEIGHT,
            transform: `scale(${scale}) translateZ(0)`,
            transformOrigin: "top left",
            position: "absolute",
            top: 0,
            left: 0,
            backfaceVisibility: "hidden",
          }}>
            <SlideCanvas
              slideId={slideId}
              htmlContent={htmlContent}
              backgroundColor={backgroundColor}
              backgroundImage={backgroundImage}
              readOnly
            />
          </div>
        </div>
      </div>
    </div>
  );
});
