import { useRef, useEffect, useState, useCallback } from "react";
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
export const ReadOnlySlide = ({ slideId, htmlContent, backgroundColor, backgroundImage, className }: ReadOnlySlideProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(0.1);

  const updateScale = useCallback(() => {
    if (!containerRef.current) return;
    const { clientWidth: w, clientHeight: h } = containerRef.current;
    setScale(Math.min(w / CANVAS_WIDTH, h / CANVAS_HEIGHT));
  }, []);

  useEffect(() => {
    updateScale();
    const ro = new ResizeObserver(updateScale);
    if (containerRef.current) ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, [updateScale]);

  const scaledW = CANVAS_WIDTH * scale;
  const scaledH = CANVAS_HEIGHT * scale;

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
            willChange: "transform",
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
};
