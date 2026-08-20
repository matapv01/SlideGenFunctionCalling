import { useEffect, useMemo, useState } from "react";
import { XmlSlideCanvas } from "@/components/XmlSlideCanvas";
import { parseXmlSlide, type XmlSlideDocument } from "@/lib/xmlSlide";

const XML_PREVIEW_EVENT = "slidegen:xml-preview";

type PreviewPayload = {
  xml: string;
  slideIndex?: number;
};

type PreviewWindow = Window & {
  __slidegenXmlPreviewAppReady?: boolean;
};

const readPayload = (event: Event): PreviewPayload | null => {
  const detail = (event as CustomEvent<PreviewPayload | string>).detail;
  if (typeof detail === "string") return { xml: detail };
  if (!detail || typeof detail.xml !== "string") return null;
  return detail;
};

const XmlRenderPreview = () => {
  const [payload, setPayload] = useState<PreviewPayload | null>(null);
  const [ready, setReady] = useState(false);
  const [viewport, setViewport] = useState(() => ({
    width: window.innerWidth,
    height: window.innerHeight,
  }));

  useEffect(() => {
    const previewWindow = window as PreviewWindow;
    const handlePreview = (event: Event) => {
      setReady(false);
      setPayload(readPayload(event));
    };

    window.addEventListener(XML_PREVIEW_EVENT, handlePreview);
    previewWindow.__slidegenXmlPreviewAppReady = true;

    return () => {
      window.removeEventListener(XML_PREVIEW_EVENT, handlePreview);
      previewWindow.__slidegenXmlPreviewAppReady = false;
    };
  }, []);

  useEffect(() => {
    const updateViewport = () => {
      setViewport({ width: window.innerWidth, height: window.innerHeight });
    };
    window.addEventListener("resize", updateViewport);
    return () => window.removeEventListener("resize", updateViewport);
  }, []);

  const parsed = useMemo<{ document: XmlSlideDocument | null; error: string }>(() => {
    if (!payload?.xml) return { document: null, error: "" };
    try {
      return { document: parseXmlSlide(payload.xml), error: "" };
    } catch (error) {
      return {
        document: null,
        error: error instanceof Error ? error.message : "Could not parse XML preview",
      };
    }
  }, [payload?.xml]);

  const slideIndex = Math.max(
    0,
    Math.min(payload?.slideIndex || 0, (parsed.document?.slides.length || 1) - 1),
  );
  const slide = parsed.document?.slides[slideIndex] || null;

  useEffect(() => {
    if (!parsed.document || !slide) return;

    let cancelled = false;
    const markReady = async () => {
      if (document.fonts?.ready) await document.fonts.ready;
      await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
      await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
      if (!cancelled) setReady(true);
    };

    void markReady();
    return () => {
      cancelled = true;
    };
  }, [parsed.document, slide]);

  const status = parsed.error ? "error" : ready && slide ? "ready" : "waiting";

  if (!parsed.document || !slide || !ready) {
    return (
      <main
        data-xml-preview-status={status}
        data-xml-preview-error={parsed.error || undefined}
        style={{ width: "100vw", height: "100vh", overflow: "hidden", background: "#fff" }}
      />
    );
  }

  const scaleX = viewport.width / Math.max(1, parsed.document.width);
  const scaleY = viewport.height / Math.max(1, parsed.document.height);

  return (
    <main
      data-xml-preview-status="ready"
      data-xml-slide-index={slideIndex}
      style={{
        position: "relative",
        width: "100vw",
        height: "100vh",
        overflow: "hidden",
        background: slide.attrs.background || "#fff",
      }}
    >
      <div
        data-xml-preview-canvas="true"
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: parsed.document.width,
          height: parsed.document.height,
          transform: `scale(${scaleX}, ${scaleY})`,
          transformOrigin: "top left",
        }}
      >
        <XmlSlideCanvas
          slide={slide}
          canvasWidth={parsed.document.width}
          canvasHeight={parsed.document.height}
          slideWidthInches={Number(parsed.document.presentationAttrs.slideWidthInches || 13.333)}
          slideHeightInches={Number(parsed.document.presentationAttrs.slideHeightInches || 7.5)}
          selectedId={null}
          readOnly
          viewport="bare"
          onSelect={() => undefined}
          onChange={() => undefined}
        />
      </div>
    </main>
  );
};

export default XmlRenderPreview;
