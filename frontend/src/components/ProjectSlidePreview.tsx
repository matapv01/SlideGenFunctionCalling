import { useEffect, useMemo, useRef, useState } from "react";
import { LazySlidePreview } from "@/components/LazySlidePreview";
import { XmlSlideCanvas } from "@/components/XmlSlideCanvas";
import { parseXmlSlide, type XmlSlideDocument } from "@/lib/xmlSlide";

const isXmlPresentationSource = (value: string) => {
  const source = value.replace(/^\uFEFF/, "").trim();
  return /^<\?xml\b/i.test(source) || /^<presentation(?:\s|>)/i.test(source);
};

export const ProjectSlidePreview = ({
  content,
  slideId,
  backgroundColor,
  backgroundImage,
  className,
}: {
  content: string;
  slideId: string;
  backgroundColor?: string;
  backgroundImage?: string;
  className?: string;
}) => {
  const frameRef = useRef<HTMLDivElement>(null);
  const [frameSize, setFrameSize] = useState({ width: 0, height: 0 });
  const xmlDocument = useMemo<XmlSlideDocument | null>(() => {
    if (!isXmlPresentationSource(content)) return null;
    try {
      return parseXmlSlide(content);
    } catch {
      return null;
    }
  }, [content]);

  useEffect(() => {
    const frame = frameRef.current;
    if (!frame) return;
    const updateSize = () => setFrameSize({ width: frame.clientWidth, height: frame.clientHeight });
    updateSize();
    const observer = new ResizeObserver(updateSize);
    observer.observe(frame);
    return () => observer.disconnect();
  }, []);

  if (!xmlDocument?.slides.length) {
    return (
      <LazySlidePreview
        slideId={slideId}
        htmlContent={content}
        backgroundColor={backgroundColor}
        backgroundImage={backgroundImage}
        className={className}
      />
    );
  }

  const scale = Math.min(
    frameSize.width / xmlDocument.width || 0,
    frameSize.height / xmlDocument.height || 0,
  );
  const safeScale = scale > 0 ? scale : 0.01;

  return (
    <div ref={frameRef} className={`overflow-hidden ${className || "relative"}`}>
      <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
        <div style={{ width: xmlDocument.width * safeScale, height: xmlDocument.height * safeScale }}>
          <div
            style={{
              width: xmlDocument.width,
              height: xmlDocument.height,
              transform: `scale(${safeScale}) translateZ(0)`,
              transformOrigin: "top left",
            }}
          >
            <XmlSlideCanvas
              slide={xmlDocument.slides[0]}
              canvasWidth={xmlDocument.width}
              canvasHeight={xmlDocument.height}
              slideWidthInches={Number(xmlDocument.presentationAttrs.slideWidthInches || 13.333)}
              slideHeightInches={Number(xmlDocument.presentationAttrs.slideHeightInches || 7.5)}
              selectedId={null}
              readOnly
              viewport="bare"
              onSelect={() => undefined}
              onChange={() => undefined}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
