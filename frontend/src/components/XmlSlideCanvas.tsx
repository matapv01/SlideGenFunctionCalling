import { Fragment, useEffect, useLayoutEffect, useRef, useState } from "react";
import type { CSSProperties, PointerEvent as ReactPointerEvent } from "react";
import type { XmlSlideElement, XmlSlidePage } from "@/lib/xmlSlide";
import { XML_GROUP_ATTR } from "@/lib/xmlGrouping";
import {
  replaceXmlTextContent,
  type XmlTextFormat,
  type XmlTextSelection,
} from "@/lib/xmlTextFormatting";
import "mathlive";

interface XmlSlideCanvasProps {
  slide: XmlSlidePage;
  canvasWidth: number;
  canvasHeight: number;
  slideWidthInches?: number;
  slideHeightInches?: number;
  selectedId: string | null;
  selectedIds?: string[];
  zoom?: number;
  readOnly?: boolean;
  viewport?: "standalone" | "bare";
  onSelect: (id: string | null, additive?: boolean) => void;
  onChange: (id: string, update: Partial<Pick<XmlSlideElement, "text" | "attrs" | "children">>) => void;
  onFormatText?: (id: string, selection: XmlTextSelection, format: XmlTextFormat) => void;
  onTextSelectionChange?: (id: string | null, selection: XmlTextSelection | null) => void;
  onCommit?: () => void;
}

interface MathFieldPreviewProps {
  latex: string;
  fontSize: number;
  color: string;
}

function remoteImageProxyUrl(source: string): string | null {
  if (!/^https?:\/\//i.test(source)) return null;
  return `/api/v1/image-serve/remote-proxy?url=${encodeURIComponent(source)}`;
}

const MathFieldPreview = ({ latex, fontSize, color }: MathFieldPreviewProps) => {
  const hostRef = useRef<HTMLSpanElement>(null);

  useLayoutEffect(() => {
    if (!hostRef.current || !customElements.get("math-span")) return;

    // `math-field` is an editable control. XML formulas are static slide
    // content, so use MathLive's read-only custom element instead. Loading
    // MathLive statically and using a layout effect prevents the preview/PDF
    // capture from running before the formula has been materialized.
    const mathSpan = document.createElement("math-span");
    mathSpan.setAttribute("aria-label", latex);
    mathSpan.style.display = "inline-flex";
    mathSpan.style.verticalAlign = "middle";
    mathSpan.style.color = color;
    mathSpan.style.fontSize = `${fontSize}px`;
    mathSpan.textContent = latex;
    hostRef.current.replaceChildren(mathSpan);
  }, [color, fontSize, latex]);

  return (
    <span
      ref={hostRef}
      style={{
        display: "inline-block",
        verticalAlign: "middle",
        color,
        fontSize,
      }}
    >
      {latex}
    </span>
  );
};

interface MathFieldEditorProps extends MathFieldPreviewProps {
  onChange: (latex: string) => void;
}

const MathFieldEditor = ({ latex, fontSize, color, onChange }: MathFieldEditorProps) => {
  const hostRef = useRef<HTMLSpanElement>(null);
  const onChangeRef = useRef(onChange);

  useEffect(() => {
    onChangeRef.current = onChange;
  }, [onChange]);

  useLayoutEffect(() => {
    if (!hostRef.current || !customElements.get("math-field")) return;

    const mathField = document.createElement("math-field") as HTMLElement & {
      value?: string;
    };
    mathField.setAttribute("aria-label", "LaTeX formula");
    mathField.style.display = "inline-block";
    mathField.style.verticalAlign = "middle";
    mathField.style.color = color;
    mathField.style.fontSize = `${fontSize}px`;
    mathField.style.minWidth = "120px";
    mathField.style.background = "transparent";
    mathField.style.border = "1px solid rgba(148, 163, 184, 0.65)";
    mathField.style.borderRadius = "4px";
    mathField.style.padding = "4px 8px";

    const handleInput = () => {
      onChangeRef.current(String(mathField.value ?? mathField.textContent ?? ""));
    };
    mathField.addEventListener("input", handleInput);
    hostRef.current.replaceChildren(mathField);
    mathField.value = latex;

    return () => mathField.removeEventListener("input", handleInput);
  }, []);

  useEffect(() => {
    const mathField = hostRef.current?.querySelector("math-field") as (HTMLElement & { value?: string }) | null;
    if (mathField && mathField.value !== latex) mathField.value = latex;
  }, [latex]);

  useEffect(() => {
    const mathField = hostRef.current?.querySelector("math-field") as HTMLElement | null;
    if (!mathField) return;
    mathField.style.color = color;
    mathField.style.fontSize = `${fontSize}px`;
  }, [color, fontSize]);

  return <span ref={hostRef} style={{ display: "inline-block", verticalAlign: "middle" }} />;
};

interface DragState {
  id: string;
  mode: "move" | "resize";
  handle?: "tl" | "tr" | "bl" | "br";
  startClientX: number;
  startClientY: number;
  startX: number;
  startY: number;
  startWidth: number;
  startHeight: number;
  startPoints?: string;
  members?: Array<{
    id: string;
    startX: number;
    startY: number;
    startPoints?: string;
    startAttrs: Record<string, string>;
  }>;
}

interface AlignmentGuide {
  type: "vertical" | "horizontal";
  position: number;
}

interface TextSelectionState extends XmlTextSelection {
  elementId: string;
  left: number;
  top: number;
}

const numberAttr = (element: XmlSlideElement, name: string, fallback = 0) => {
  const value = Number(element.attrs[name]);
  return Number.isFinite(value) ? value : fallback;
};

interface CanvasMetrics {
  canvasWidth: number;
  canvasHeight: number;
  slideWidthInches: number;
  slideHeightInches: number;
}

const createMetrics = (
  canvasWidth: number,
  canvasHeight: number,
  slideWidthInches = 13.333,
  slideHeightInches = 7.5,
): CanvasMetrics => ({
  canvasWidth,
  canvasHeight,
  slideWidthInches,
  slideHeightInches,
});

const ptToCanvasX = (pointSize: number, metrics: CanvasMetrics) =>
  pointSize * (metrics.canvasWidth / metrics.slideWidthInches) / 72;

const ptToCanvasY = (pointSize: number, metrics: CanvasMetrics) =>
  pointSize * (metrics.canvasHeight / metrics.slideHeightInches) / 72;

const toBool = (value: string | undefined, fallback = false) => {
  if (value === undefined) return fallback;
  return ["true", "1", "yes", "on"].includes(value.trim().toLowerCase());
};

// Keep text measurement and DOM rendering on the exact same fallback stack.
// The XML tool measures with a Linux fallback when Arial is unavailable, while
// the browser may otherwise resolve `font-family: Arial` differently.
const textFontFamily = (requested?: string) => {
  const primary = (requested || "Arial").trim().replace(/["']/g, "") || "Arial";
  return `"${primary}", "Arial", "Segoe UI", "Noto Sans", "DejaVu Sans", sans-serif`;
};

const textFont = (element: XmlSlideElement, fontSizePt: number, metrics: CanvasMetrics) => {
  const weight = toBool(element.attrs.bold) ? "bold " : "";
  const italic = toBool(element.attrs.italic) ? "italic " : "";
  const font = textFontFamily(element.attrs.font || element.attrs.font_family);
  return `${italic}${weight}${ptToCanvasY(fontSizePt, metrics)}px ${font}`;
};

const normalizedMixedText = (value: string) => value
  .replace(/\r\n/g, "\n")
  .replace(/\n[ \t]+/g, "\n");

const richRunStyle = (
  run: XmlSlideElement,
  textbox: XmlSlideElement,
  metrics: CanvasMetrics,
): CSSProperties => {
  return {
    color: run.attrs.color || textbox.attrs.color || "#111827",
    fontFamily: textFontFamily(
      run.attrs.font || textbox.attrs.font || textbox.attrs.font_family,
    ),
    fontSize: `${ptToCanvasY(
      numberAttr(run, "size", numberAttr(textbox, "size", 24)),
      metrics,
    )}px`,
    fontWeight: toBool(run.attrs.bold, toBool(textbox.attrs.bold))
      ? 700
      : run.attrs.font_weight || textbox.attrs.font_weight || "normal",
    fontStyle: toBool(run.attrs.italic, toBool(textbox.attrs.italic))
      ? "italic"
      : "normal",
    textDecoration: toBool(run.attrs.underline)
      ? "underline"
      : toBool(run.attrs.strike)
        ? "line-through"
        : "none",
    backgroundColor: run.attrs.highlight || run.attrs.background || "transparent",
  };
};

let measureContext: CanvasRenderingContext2D | null = null;

const getMeasureContext = () => {
  if (typeof document === "undefined") return null;
  if (!measureContext) {
    measureContext = document.createElement("canvas").getContext("2d");
  }
  return measureContext;
};

const measureText = (text: string, font: string) => {
  const context = getMeasureContext();
  if (!context) return text.length * 8;
  context.font = font;
  return context.measureText(text).width;
};

const lineHeight = (font: string, spacing: number, fallbackPx: number) => {
  const context = getMeasureContext();
  if (!context) return fallbackPx * spacing;
  context.font = font;
  // `Mg` does not include Vietnamese upper/lower diacritics. Measure a glyph
  // sample containing the tallest accents so the fixed line box is large
  // enough for words such as `Tiếng`, `Hồi`, `Ảnh`, and `Sản`.
  const metrics = context.measureText("MgÁẮẰẶỀỂỄỎỐỒỔỖỘƠỨỪỰĐạặệỉịỏốồổỗộơứừựỷỹ");
  const ascent = metrics.actualBoundingBoxAscent || fallbackPx * 0.8;
  const descent = metrics.actualBoundingBoxDescent || fallbackPx * 0.2;
  // Vietnamese tone marks can extend above the Latin capital ascent. Reserve
  // a small amount of extra line box space so they are not clipped in a
  // fixed-height XML textbox.
  return (ascent + descent + fallbackPx * 0.12) * spacing;
};

// XML generators and browser font metrics can differ by a few percent. Give
// every textbox a small shared horizontal allowance so a word that fits in
// the generated layout is not wrapped one word too early in the editor.
const TEXTBOX_WIDTH_GROWTH = 0.10;

const wrapParagraph = (paragraph: string, font: string, maxWidth: number) => {
  const words = paragraph.split(/\s+/).filter(Boolean);
  if (!words.length) return [""];
  const lines: string[] = [];
  let current = "";

  for (const word of words) {
    const pieces: string[] = [];
    if (measureText(word, font) > maxWidth) {
      let piece = "";
      for (const character of word) {
        const candidate = piece + character;
        if (piece && measureText(candidate, font) > maxWidth) {
          pieces.push(piece);
          piece = character;
        } else {
          piece = candidate;
        }
      }
      if (piece) pieces.push(piece);
    } else {
      pieces.push(word);
    }

    for (const piece of pieces) {
      const candidate = current ? `${current} ${piece}` : piece;
      if (!current || measureText(candidate, font) <= maxWidth) {
        current = candidate;
      } else {
        lines.push(current);
        current = piece;
      }
    }
  }
  if (current) lines.push(current);
  return lines.length ? lines : [""];
};

const textLayout = (element: XmlSlideElement, metrics: CanvasMetrics) => {
  const sourceX = numberAttr(element, "x");
  const sourceY = numberAttr(element, "y");
  const sourceWidth = numberAttr(element, "width", 300);
  const sourceHeight = numberAttr(element, "height", 100);
  const widthGrowth = sourceWidth * TEXTBOX_WIDTH_GROWTH;
  const heightGrowth = sourceHeight * 0.08;
  const x = Math.max(0, sourceX - widthGrowth / 2);
  const y = Math.max(0, sourceY - heightGrowth / 2);
  const width = Math.min(metrics.canvasWidth - x, sourceWidth + widthGrowth);
  const height = Math.min(metrics.canvasHeight - y, sourceHeight + heightGrowth);
  const initialSize = numberAttr(element, "size", 24);
  const minSize = numberAttr(element, "min_font_size", 10);
  const spacing = numberAttr(element, "line_spacing", 1);
  const safetyRatio = numberAttr(element, "safety_ratio", 0.97);
  const singleLine = toBool(element.attrs.single_line);
  const reflowOnResize = toBool(element.attrs.reflow_on_resize);
  const overflow = (element.attrs.overflow || "shrink").toLowerCase();
  const maxLines = element.attrs.max_lines ? Number(element.attrs.max_lines) : (singleLine ? 1 : undefined);
  const marginLeft = ptToCanvasX(numberAttr(element, "margin_left"), metrics);
  const marginRight = ptToCanvasX(numberAttr(element, "margin_right"), metrics);
  const marginTop = ptToCanvasY(numberAttr(element, "margin_top"), metrics);
  const marginBottom = ptToCanvasY(numberAttr(element, "margin_bottom"), metrics);
  const availableWidth = Math.max(1, width - marginLeft - marginRight);
  const availableHeight = Math.max(1, height - marginTop - marginBottom);
  const targetWidth = Math.max(1, availableWidth * safetyRatio);
  const targetHeight = Math.max(1, availableHeight * safetyRatio);

  let finalSize = initialSize;
  let lines: string[] = [];
  let requiredHeight = 0;
  while (finalSize >= minSize) {
    const font = textFont(element, finalSize, metrics);
    lines = singleLine
      ? [element.text.replace(/\s+/g, " ").trim()]
      : element.text.split(/\r?\n/).flatMap((paragraph) => wrapParagraph(paragraph.trim(), font, targetWidth));
    const heightForLines = lineHeight(font, spacing, ptToCanvasY(finalSize, metrics)) * lines.length;
    const widthOk = lines.every((line) => measureText(line, font) <= targetWidth);
    const heightOk = heightForLines <= targetHeight;
    const linesOk = maxLines === undefined || lines.length <= maxLines;
    requiredHeight = heightForLines;
    if ((widthOk && heightOk && linesOk) || overflow !== "shrink") break;
    finalSize = Math.round((finalSize - 0.5) * 100) / 100;
  }

  const finalHeight = overflow === "resize"
    ? Math.max(height, requiredHeight + marginTop + marginBottom)
    : height;
  return {
    x,
    y,
    width,
    height: finalHeight,
    fontSize: finalSize,
    lines,
    lineHeight: lineHeight(textFont(element, finalSize, metrics), spacing, ptToCanvasY(finalSize, metrics)),
    marginLeft,
    marginRight,
    marginTop,
    marginBottom,
    availableHeight,
    verticalAlign: (element.attrs.vertical_align || "top").toLowerCase(),
    reflowOnResize,
    singleLine,
    overflow,
  };
};

const polygonBounds = (points: string) => {
  const parsed = points
    .trim()
    .split(/\s+/)
    .map((point) => point.split(",").map(Number))
    .filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));
  if (!parsed.length) return { x: 0, y: 0, width: 100, height: 100, parsed: [] as number[][] };
  const xs = parsed.map(([x]) => x);
  const ys = parsed.map(([, y]) => y);
  return {
    x: Math.min(...xs),
    y: Math.min(...ys),
    width: Math.max(1, Math.max(...xs) - Math.min(...xs)),
    height: Math.max(1, Math.max(...ys) - Math.min(...ys)),
    parsed,
  };
};

const movePoints = (points: string, dx: number, dy: number) =>
  points
    .trim()
    .split(/\s+/)
    .map((point) => {
      const [x, y] = point.split(",").map(Number);
      return `${(x + dx).toFixed(2)},${(y + dy).toFixed(2)}`;
    })
    .join(" ");

const decodeXmlEntities = (value: string) => {
  if (!value.includes("&lt;") && !value.includes("&quot;") && !value.includes("&amp;")) {
    return value;
  }
  if (typeof document === "undefined") return value;
  const textarea = document.createElement("textarea");
  textarea.innerHTML = value;
  return textarea.value;
};

const normalizeInlineSvg = (value: string) => {
  const decoded = decodeXmlEntities(value).trim();
  if (!decoded.match(/^<svg\b/i)) return decoded;

  return decoded.replace(
    /^<svg\b/i,
    '<svg style="display:block;width:100%;height:100%;overflow:visible;" preserveAspectRatio="none"',
  );
};

const elementFrame = (element: XmlSlideElement, metrics: CanvasMetrics) => {
  const tag = element.tag.toLowerCase();
  if (tag === "textbox" || tag === "text") return textLayout(element, metrics);
  if (tag === "polygon") {
    const bounds = polygonBounds(element.attrs.points || "");
    return bounds;
  }
  if (tag === "line") {
    const x1 = numberAttr(element, "x1");
    const y1 = numberAttr(element, "y1");
    const x2 = numberAttr(element, "x2", x1 + 100);
    const y2 = numberAttr(element, "y2", y1);
    return { x: Math.min(x1, x2), y: Math.min(y1, y2), width: Math.max(1, Math.abs(x2 - x1)), height: Math.max(1, Math.abs(y2 - y1)) };
  }
  if (tag === "svg") {
    return {
      x: numberAttr(element, "x"),
      y: numberAttr(element, "y"),
      width: numberAttr(element, "width", numberAttr(element, "pixel_width", 100)),
      height: numberAttr(element, "height", numberAttr(element, "pixel_height", 100)),
    };
  }
  return {
    x: numberAttr(element, "x"),
    y: numberAttr(element, "y"),
    width: numberAttr(element, "width", element.tag.toLowerCase() === "textbox" ? 300 : 100),
    height: numberAttr(element, "height", element.tag.toLowerCase() === "textbox" ? 80 : 100),
  };
};

const elementStyle = (element: XmlSlideElement, selected: boolean, baseZIndex: number, metrics: CanvasMetrics): CSSProperties => {
  const tag = element.tag.toLowerCase();
  const frame = elementFrame(element, metrics);
  const transforms: string[] = [];
  const style: CSSProperties = {
    position: "absolute",
    left: frame.x,
    top: frame.y,
    width: frame.width,
    height: frame.height,
    // Selection must not change the visual layer order. A selected object can
    // stay behind overlapping objects while it is moved, matching Canva.
    zIndex: baseZIndex,
    boxSizing: "border-box",
    outline: selected ? "2px solid #2563eb" : "none",
    cursor: "move",
    userSelect: tag === "textbox" ? "text" : "none",
  };

  if (tag === "polygon") {
    style.background = "transparent";
  } else if (tag === "textbox" || tag === "text") {
    const layout = textLayout(element, metrics);
    style.color = element.attrs.color || "#111827";
    style.fontFamily = textFontFamily(element.attrs.font || element.attrs.font_family);
    style.fontSize = `${ptToCanvasY(layout.fontSize, metrics)}px`;
    style.fontWeight = element.attrs.bold === "true" ? 700 : element.attrs.font_weight || "normal";
    style.fontStyle = element.attrs.italic === "true" ? "italic" : "normal";
    style.textAlign = (element.attrs.align || "left") as CSSProperties["textAlign"];
    style.textDecoration = element.attrs.underline === "true" ? "underline" : element.attrs.strike === "true" ? "line-through" : "none";
    style.lineHeight = `${layout.lineHeight}px`;
    style.padding = 0;
    style.display = "block";
    style.whiteSpace = "nowrap";
    // Do not clip the glyph box: clipping removes Vietnamese accents before
    // the text itself reaches the edge of the textbox.
    style.overflow = "visible";
    const textFill = element.attrs.fill ?? element.attrs.background;
    if (textFill && textFill !== "none") style.background = textFill;
    if (element.attrs.line_color && element.attrs.line_color !== "none") {
      style.border = `${ptToCanvasY(numberAttr(element, "line_width", 1), metrics)}px solid ${element.attrs.line_color}`;
    }
    if (element.attrs.radius) style.borderRadius = `${element.attrs.radius}px`;
    if (element.attrs.gradient_start && element.attrs.gradient_end) {
      style.backgroundImage = `linear-gradient(90deg, ${element.attrs.gradient_start}, ${element.attrs.gradient_end})`;
      style.backgroundClip = "text";
      style.webkitBackgroundClip = "text";
      style.color = "transparent";
    }
  } else if (tag === "rect" || tag === "rectangle" || tag === "shape") {
    const fill = element.attrs.fill ?? element.attrs.background ?? "#cbd5e1";
    style.background = fill === "none" ? "transparent" : fill;
    const shapeType = element.attrs.type?.toLowerCase() || "rectangle";
    if (["circle", "ellipse", "oval"].includes(shapeType)) style.borderRadius = "50%";
    if (shapeType === "rounded_rectangle") style.borderRadius = Math.min(frame.width, frame.height) * 0.18;
    const clipPaths: Record<string, string> = {
      triangle: "polygon(50% 0%, 0% 100%, 100% 100%)",
      diamond: "polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)",
      hexagon: "polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)",
      chevron: "polygon(0% 0%, 75% 0%, 100% 50%, 75% 100%, 0% 100%, 25% 50%)",
      right_arrow: "polygon(0% 20%, 65% 20%, 65% 0%, 100% 50%, 65% 100%, 65% 80%, 0% 80%)",
    };
    if (clipPaths[shapeType]) style.clipPath = clipPaths[shapeType];
    if (element.attrs.radius) style.borderRadius = `${element.attrs.radius}px`;
    if (element.attrs.line_color && element.attrs.line_color !== "none") {
      style.border = `${ptToCanvasY(numberAttr(element, "line_width", 1), metrics)}px solid ${element.attrs.line_color}`;
    }
  } else if (tag === "image") {
    const imageFill = element.attrs.fill ?? element.attrs.background;
    if (imageFill && imageFill !== "none") style.background = imageFill;
    if (element.attrs.line_color && element.attrs.line_color !== "none") {
      style.border = `${ptToCanvasY(numberAttr(element, "line_width", 1), metrics)}px solid ${element.attrs.line_color}`;
    }
    if (element.attrs.radius) style.borderRadius = `${element.attrs.radius}px`;
  } else if (tag === "line") {
    const lineStyle = element.attrs.dash === "dashed" ? "dashed" : element.attrs.dash === "dotted" ? "dotted" : "solid";
    style.borderTop = `${ptToCanvasY(numberAttr(element, "width", 1), metrics)}px ${lineStyle} ${element.attrs.stroke || element.attrs.color || "#111"}`;
    style.height = 0;
    const angle = Math.atan2(numberAttr(element, "y2") - numberAttr(element, "y1"), numberAttr(element, "x2") - numberAttr(element, "x1")) * 180 / Math.PI;
    style.transformOrigin = "left center";
    transforms.push(`rotate(${angle}deg)`);
  } else if (["piechart", "barchart", "linechart"].includes(tag)) {
    style.border = "1px dashed #64748b";
    style.background = "rgba(148, 163, 184, 0.18)";
    style.color = element.attrs.color || "#334155";
    style.padding = 12;
    style.fontSize = 14;
  }

  if (element.attrs.opacity !== undefined) style.opacity = Number(element.attrs.opacity);
  if (element.attrs.rotation !== undefined && tag !== "line") transforms.push(`rotate(${numberAttr(element, "rotation")}deg)`);
  if (transforms.length) style.transform = transforms.join(" ");

  return style;
};

export const XmlSlideCanvas = ({
  slide,
  canvasWidth,
  canvasHeight,
  slideWidthInches,
  slideHeightInches,
  selectedId,
  selectedIds = [],
  zoom = 0.7,
  readOnly = false,
  viewport = "standalone",
  onSelect,
  onChange,
  onFormatText,
  onTextSelectionChange,
  onCommit,
}: XmlSlideCanvasProps) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [textSelection, setTextSelection] = useState<TextSelectionState | null>(null);
  const [alignmentGuides, setAlignmentGuides] = useState<AlignmentGuide[]>([]);
  const canvasRef = useRef<HTMLDivElement>(null);
  const dragRef = useRef<DragState | null>(null);
  const dragFrameRef = useRef<number | null>(null);
  const pendingPointerRef = useRef<{ clientX: number; clientY: number } | null>(null);
  const metrics = createMetrics(canvasWidth, canvasHeight, slideWidthInches, slideHeightInches);

  const textOffsetAt = (root: Node, container: Node, offset: number) => {
    try {
      const range = document.createRange();
      range.selectNodeContents(root);
      range.setEnd(container, offset);
      return range.toString().length;
    } catch {
      return 0;
    }
  };

  const handleTextSelection = (root: HTMLElement, elementId: string) => {
    if (readOnly || editingId !== elementId || !onFormatText) return;
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0 || selection.isCollapsed) {
      setTextSelection(null);
      onTextSelectionChange?.(null, null);
      return;
    }
    const range = selection.getRangeAt(0);
    if (!root.contains(range.startContainer) || !root.contains(range.endContainer)) return;
    const start = textOffsetAt(root, range.startContainer, range.startOffset);
    const end = textOffsetAt(root, range.endContainer, range.endOffset);
    if (start === end) {
      setTextSelection(null);
      onTextSelectionChange?.(null, null);
      return;
    }
    const canvas = canvasRef.current;
    if (!canvas) return;
    const canvasRect = canvas.getBoundingClientRect();
    const scaleX = canvasRect.width / canvasWidth || 1;
    const scaleY = canvasRect.height / canvasHeight || 1;
    const selectionRect = range.getBoundingClientRect();
    const left = (selectionRect.left + selectionRect.width / 2 - canvasRect.left) / scaleX;
    const rawTop = (selectionRect.top - canvasRect.top) / scaleY;
    const top = rawTop > 54
      ? rawTop - 50
      : (selectionRect.bottom - canvasRect.top) / scaleY + 10;
    const nextSelection = {
      elementId,
      start: Math.min(start, end),
      end: Math.max(start, end),
      text: root.innerText,
      left: Math.max(12, Math.min(canvasWidth - 12, left)),
      top: Math.max(8, Math.min(canvasHeight - 46, top)),
    };
    setTextSelection(nextSelection);
    onTextSelectionChange?.(elementId, {
      start: nextSelection.start,
      end: nextSelection.end,
      text: nextSelection.text,
    });
  };

  const clearTextSelection = () => {
    setTextSelection(null);
    onTextSelectionChange?.(null, null);
  };

  const handlePointerDown = (event: ReactPointerEvent<HTMLDivElement>, element: XmlSlideElement) => {
    if (readOnly) return;
    if (event.button !== 0) return;
    if (editingId === element.id) {
      event.stopPropagation();
      return;
    }
    event.stopPropagation();
    setEditingId(null);
    clearTextSelection();
    setAlignmentGuides([]);
    const additive = event.shiftKey || event.ctrlKey || event.metaKey;
    if (additive) {
      onSelect(element.id, true);
      return;
    }
    const frame = elementFrame(element, metrics);
    const groupId = element.attrs[XML_GROUP_ATTR];
    const groupedIds = groupId
      ? slide.elements.filter((item) => item.attrs[XML_GROUP_ATTR] === groupId).map((item) => item.id)
      : [element.id];
    const dragIds = selectedIds.includes(element.id) && selectedIds.length > 1
      ? selectedIds
      : groupedIds;
    const members = dragIds.flatMap((id) => {
      const member = slide.elements.find((item) => item.id === id);
      if (!member) return [];
      const memberFrame = elementFrame(member, metrics);
      return [{
        id,
        startX: memberFrame.x,
        startY: memberFrame.y,
        startPoints: member.attrs.points,
        startAttrs: { ...member.attrs },
      }];
    });
    dragRef.current = {
      id: element.id,
      mode: "move",
      startClientX: event.clientX,
      startClientY: event.clientY,
      startX: frame.x,
      startY: frame.y,
      startWidth: frame.width,
      startHeight: frame.height,
      startPoints: element.attrs.points,
      members,
    };
    onSelect(element.id, false);
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const handleResizePointerDown = (
    event: ReactPointerEvent<HTMLSpanElement>,
    element: XmlSlideElement,
    handle: DragState["handle"],
  ) => {
    if (readOnly) return;
    event.preventDefault();
    event.stopPropagation();
    setEditingId(null);
    setAlignmentGuides([]);
    const frame = elementFrame(element, metrics);
    dragRef.current = {
      id: element.id,
      mode: "resize",
      handle,
      startClientX: event.clientX,
      startClientY: event.clientY,
      startX: frame.x,
      startY: frame.y,
      startWidth: frame.width,
      startHeight: frame.height,
      startPoints: element.attrs.points,
    };
    onSelect(element.id);
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const snapFrame = (element: XmlSlideElement, x: number, y: number, ignoredIds: string[] = []) => {
    const frame = elementFrame(element, metrics);
    const threshold = Math.max(6, 8 / Math.max(zoom, 0.1));
    const draggedX = [x, x + frame.width / 2, x + frame.width];
    const draggedY = [y, y + frame.height / 2, y + frame.height];
    const xCandidates: Array<{ distance: number; value: number; position: number; priority: number }> = [];
    const yCandidates: Array<{ distance: number; value: number; position: number; priority: number }> = [];

    const addTarget = (left: number, top: number, width: number, height: number, priority: number) => {
      const targetX = [left, left + width / 2, left + width];
      const targetY = [top, top + height / 2, top + height];
      draggedX.forEach((dragAnchor, dragIndex) => {
        targetX.forEach((targetAnchor) => {
          xCandidates.push({
            distance: Math.abs(dragAnchor - targetAnchor),
            value: targetAnchor - [0, frame.width / 2, frame.width][dragIndex],
            position: targetAnchor,
            priority,
          });
        });
      });
      draggedY.forEach((dragAnchor, dragIndex) => {
        targetY.forEach((targetAnchor) => {
          yCandidates.push({
            distance: Math.abs(dragAnchor - targetAnchor),
            value: targetAnchor - [0, frame.height / 2, frame.height][dragIndex],
            position: targetAnchor,
            priority,
          });
        });
      });
    };

    // Slide edges and center are alignment targets just like in PowerPoint.
    addTarget(0, 0, canvasWidth, canvasHeight, 1);
    slide.elements.forEach((other) => {
      if (other.id === element.id || ignoredIds.includes(other.id)) return;
      const otherFrame = elementFrame(other, metrics);
      if (otherFrame.width > 0 && otherFrame.height > 0) {
        // Prefer object-to-object alignment when two candidates are equally close.
        addTarget(otherFrame.x, otherFrame.y, otherFrame.width, otherFrame.height, 2);
      }
    });

    const best = <T extends { distance: number; priority: number }>(candidates: T[]) => candidates
      .filter((candidate) => candidate.distance <= threshold)
      .sort((a, b) => a.distance - b.distance || b.priority - a.priority)[0];
    const bestX = best(xCandidates);
    const bestY = best(yCandidates);
    const guides: AlignmentGuide[] = [];
    if (bestX) {
      x = bestX.value;
      guides.push({ type: "vertical", position: bestX.position });
    }
    if (bestY) {
      y = bestY.value;
      guides.push({ type: "horizontal", position: bestY.position });
    }
    return { x, y, guides };
  };

  const applyDrag = (clientX: number, clientY: number) => {
    const drag = dragRef.current;
    if (readOnly) return;
    if (!drag) return;
    const dx = (clientX - drag.startClientX) / zoom;
    const dy = (clientY - drag.startClientY) / zoom;
    const element = slide.elements.find((item) => item.id === drag.id);
    if (!element) return;

    if (drag.mode === "resize") {
      setAlignmentGuides([]);
      const minSize = 20;
      let left = drag.startX;
      let top = drag.startY;
      let width = drag.startWidth;
      let height = drag.startHeight;
      if (drag.handle?.includes("r")) width = Math.max(minSize, drag.startWidth + dx);
      if (drag.handle?.includes("l")) {
        width = Math.max(minSize, drag.startWidth - dx);
        left = drag.startX + drag.startWidth - width;
      }
      if (drag.handle?.includes("b")) height = Math.max(minSize, drag.startHeight + dy);
      if (drag.handle?.includes("t")) {
        height = Math.max(minSize, drag.startHeight - dy);
        top = drag.startY + drag.startHeight - height;
      }

      if (element.tag.toLowerCase() === "textbox" || element.tag.toLowerCase() === "text") {
        const sourceWidth = Math.max(1, width / (1 + TEXTBOX_WIDTH_GROWTH));
        const sourceHeight = Math.max(1, height / 1.08);
        onChange(drag.id, {
          attrs: {
            x: String(Math.round(left + sourceWidth * (TEXTBOX_WIDTH_GROWTH / 2))),
            y: String(Math.round(top + sourceHeight * 0.04)),
            width: String(Math.round(sourceWidth)),
            height: String(Math.round(sourceHeight)),
          },
        });
      } else if (element.tag.toLowerCase() === "polygon" && drag.startPoints) {
        const old = polygonBounds(drag.startPoints);
        const scaleX = width / old.width;
        const scaleY = height / old.height;
        const points = old.parsed.map(([pointX, pointY]) => `${(left + (pointX - old.x) * scaleX).toFixed(2)},${(top + (pointY - old.y) * scaleY).toFixed(2)}`).join(" ");
        onChange(drag.id, { attrs: { points } });
      } else {
        onChange(drag.id, {
          attrs: { x: String(Math.round(left)), y: String(Math.round(top)), width: String(Math.round(width)), height: String(Math.round(height)) },
        });
      }
      return;
    }

    const members = drag.members?.length
      ? drag.members
      : [{
        id: drag.id,
        startX: drag.startX,
        startY: drag.startY,
        startPoints: drag.startPoints,
        startAttrs: { ...element.attrs },
      }];
    const snapped = snapFrame(element, drag.startX + dx, drag.startY + dy, members.map((member) => member.id));
    setAlignmentGuides(snapped.guides);
    const finalDx = snapped.x - drag.startX;
    const finalDy = snapped.y - drag.startY;
    members.forEach((member) => {
      const memberElement = slide.elements.find((item) => item.id === member.id);
      if (!memberElement) return;
      const nextX = member.startX + finalDx;
      const nextY = member.startY + finalDy;
      const tag = memberElement.tag.toLowerCase();
      if (tag === "polygon" && member.startPoints) {
        onChange(member.id, {
          attrs: { points: movePoints(member.startPoints, finalDx, finalDy) },
        });
      } else if (tag === "line") {
        onChange(member.id, {
          attrs: {
            x1: String(Math.round(Number(member.startAttrs.x1 || 0) + finalDx)),
            y1: String(Math.round(Number(member.startAttrs.y1 || 0) + finalDy)),
            x2: String(Math.round(Number(member.startAttrs.x2 || 0) + finalDx)),
            y2: String(Math.round(Number(member.startAttrs.y2 || 0) + finalDy)),
          },
        });
      } else if (tag === "textbox" || tag === "text") {
        const sourceWidth = numberAttr(memberElement, "width", 300);
        const sourceHeight = numberAttr(memberElement, "height", 100);
        onChange(member.id, {
          attrs: {
            x: String(Math.round(nextX + sourceWidth * (TEXTBOX_WIDTH_GROWTH / 2))),
            y: String(Math.round(nextY + sourceHeight * 0.04)),
          },
        });
      } else {
        onChange(member.id, {
          attrs: { x: String(Math.round(nextX)), y: String(Math.round(nextY)) },
        });
      }
    });
  };

  const handlePointerMove = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (readOnly || !dragRef.current) return;
    pendingPointerRef.current = { clientX: event.clientX, clientY: event.clientY };
    if (dragFrameRef.current !== null) return;

    dragFrameRef.current = window.requestAnimationFrame(() => {
      dragFrameRef.current = null;
      const pending = pendingPointerRef.current;
      pendingPointerRef.current = null;
      if (pending) applyDrag(pending.clientX, pending.clientY);
    });
  };

  const stopDragging = () => {
    if (pendingPointerRef.current) {
      const pending = pendingPointerRef.current;
      pendingPointerRef.current = null;
      applyDrag(pending.clientX, pending.clientY);
    }
    if (dragFrameRef.current !== null) {
      window.cancelAnimationFrame(dragFrameRef.current);
      dragFrameRef.current = null;
    }
    if (dragRef.current) onCommit?.();
    dragRef.current = null;
    setAlignmentGuides([]);
  };

  const renderElement = (element: XmlSlideElement, elementIndex: number) => {
    const tag = element.tag.toLowerCase();
    const selected = selectedIds.length > 0
      ? selectedIds.includes(element.id)
      : selectedId === element.id;
    const primarySelected = selectedId === element.id;
    const hasMathFields = element.children.some(
      (child) => child.tag.toLowerCase() === "math-field",
    );
    const style = elementStyle(element, selected, elementIndex + 1, metrics);
    const common = {
      key: element.id,
      style,
      onPointerDown: (event: ReactPointerEvent<HTMLDivElement>) => handlePointerDown(event, element),
      onDoubleClick: () => !readOnly && tag === "textbox" && setEditingId(element.id),
    };

    const resizeHandles = primarySelected && !readOnly ? (["tl", "tr", "bl", "br"] as const).map((handle) => (
      <span
        key={handle}
        className="absolute z-[1001] h-2.5 w-2.5 rounded-sm border border-blue-700 bg-white shadow"
        style={{
          left: handle.includes("l") ? -5 : undefined,
          right: handle.includes("r") ? -5 : undefined,
          top: handle.includes("t") ? -5 : undefined,
          bottom: handle.includes("b") ? -5 : undefined,
          cursor: `${handle.includes("t") ? "n" : "s"}${handle.includes("l") ? "w" : "e"}-resize`,
        }}
        onPointerDown={(event) => handleResizePointerDown(event, element, handle)}
      />
    )) : null;

    if (tag === "image") {
      const source = element.attrs.src || "";
      const proxySource = remoteImageProxyUrl(source);
      return (
        <div {...common} className="overflow-hidden bg-slate-200">
          <img
            key={source}
            src={source}
            alt={element.attrs.alt || "Slide element"}
            className="h-full w-full"
            style={{ display: "block", objectFit: (element.attrs.fit || "cover") as CSSProperties["objectFit"] }}
            draggable={false}
            onLoad={(event) => {
              event.currentTarget.style.visibility = "visible";
            }}
            onError={(event) => {
              const image = event.currentTarget;
              if (proxySource && image.dataset.proxyAttempted !== "true") {
                image.dataset.proxyAttempted = "true";
                image.src = proxySource;
                return;
              }
              // Keep the slide layout intact when both the original and proxy
              // source are unavailable instead of showing a broken-image icon.
              image.style.visibility = "hidden";
            }}
          />
          {resizeHandles}
        </div>
      );
    }

    if (tag === "polygon") {
      const bounds = polygonBounds(element.attrs.points || "");
      const points = bounds.parsed
        .map(([x, y]) => `${x - bounds.x},${y - bounds.y}`)
        .join(" ");
      const fill = element.attrs.fill || "none";
      const stroke = element.attrs.line_color && element.attrs.line_color !== "none" ? element.attrs.line_color : "none";
      const strokeWidth = stroke === "none" ? 0 : ptToCanvasY(numberAttr(element, "line_width", 1), metrics);

      return (
        <div {...common}>
          <svg width="100%" height="100%" viewBox={`0 0 ${bounds.width} ${bounds.height}`} preserveAspectRatio="none">
            <polygon points={points} fill={fill} stroke={stroke} strokeWidth={strokeWidth} vectorEffect="non-scaling-stroke" />
          </svg>
          {resizeHandles}
        </div>
      );
    }

    if (tag === "textbox" || tag === "text") {
      const layout = textLayout(element, metrics);
      const isEditing = !readOnly && editingId === element.id;
      const richRuns = element.children.filter(
        (child) => child.tag.toLowerCase() === "run",
      );
      const mathFields = element.children.filter(
        (child) => child.tag.toLowerCase() === "math-field",
      );
      const hasRichRuns = richRuns.length > 0;
      const textContentHeight = layout.lineHeight * layout.lines.length;
      const verticalOffset = layout.verticalAlign === "bottom"
        ? Math.max(0, layout.availableHeight - textContentHeight)
        : layout.verticalAlign === "middle" || layout.verticalAlign === "center"
          ? Math.max(0, (layout.availableHeight - textContentHeight) / 2)
          : 0;
      return (
        <div
          {...common}
          contentEditable={isEditing && !hasMathFields}
          suppressContentEditableWarning
          onMouseUp={(event) => handleTextSelection(event.currentTarget, element.id)}
          onKeyUp={(event) => handleTextSelection(event.currentTarget, element.id)}
          onBlur={(event) => {
            if (!hasMathFields) {
              const relatedTarget = event.relatedTarget as HTMLElement | null;
              if (relatedTarget?.closest("[data-text-format-toolbar],[data-text-format-panel]")) return;
              const nextText = event.currentTarget.innerText;
              const next = hasRichRuns
                ? replaceXmlTextContent({ ...element, text: nextText }, nextText)
                : [];
              onChange(element.id, hasRichRuns
                ? { text: nextText, children: next }
                : { text: nextText });
              setEditingId(null);
              clearTextSelection();
              onCommit?.();
            }
          }}
          className="rounded-sm"
        >
          <div
            style={{
              position: "absolute",
              left: layout.marginLeft,
              top: layout.marginTop + verticalOffset,
              width: Math.max(1, layout.width - layout.marginLeft - layout.marginRight),
               minHeight: textContentHeight,
               lineHeight: `${layout.lineHeight}px`,
               textAlign: (element.attrs.align || "left") as CSSProperties["textAlign"],
               whiteSpace: layout.singleLine
                 ? "nowrap"
                 : hasRichRuns
                   ? "pre-wrap"
                   : layout.reflowOnResize
                     ? "pre-line"
                     : "nowrap",
               overflowWrap: layout.singleLine ? "normal" : "break-word",
             }}
           >
             {isEditing && hasMathFields
               ? mathFields.map((field, index) => (
                 <MathFieldEditor
                   key={`${element.id}-math-editor-${index}`}
                   latex={field.attrs.value || field.text}
                   fontSize={ptToCanvasY(layout.fontSize, metrics)}
                   color={element.attrs.color || "#111827"}
                   onChange={(latex) => {
                     const children = element.children.map((child, childIndex) => {
                       if (childIndex !== element.children.indexOf(field)) return child;
                       const attrs = { ...child.attrs };
                       delete attrs.value;
                       return { ...child, attrs, text: latex };
                     });
                     onChange(element.id, { children });
                   }}
                 />
               ))
               : isEditing && !hasRichRuns
                 ? element.text
               : mathFields.length > 0
                 ? (
                   <span style={{ display: "inline", whiteSpace: "pre-wrap" }}>
                     {normalizedMixedText(element.leadingText ?? element.text)}
                     {element.children.map((child, childIndex) => (
                       <Fragment key={`${element.id}-math-segment-${childIndex}`}>
                         {child.tag.toLowerCase() === "math-field" && (
                           <MathFieldPreview
                             latex={child.attrs.value || child.text}
                             fontSize={ptToCanvasY(layout.fontSize, metrics)}
                             color={element.attrs.color || "#111827"}
                           />
                         )}
                         {child.tail && <span>{normalizedMixedText(child.tail)}</span>}
                       </Fragment>
                     ))}
                   </span>
                 )
               : hasRichRuns
                 ? richRuns.map((run, index) => (
                   <span
                     key={`${element.id}-run-${index}`}
                     style={richRunStyle(run, element, metrics)}
                   >
                     {run.text}
                   </span>
                 ))
               : layout.reflowOnResize && !layout.singleLine
                 ? element.text
                  .split(/\r?\n/)
                  .map((paragraph) => paragraph.replace(/\s+/g, " ").trim())
                  .join("\n")
                : layout.lines.map((line, index) => (
                  <span
                    key={`${element.id}-line-${index}`}
                    style={{ display: "block", height: layout.lineHeight, lineHeight: `${layout.lineHeight}px` }}
                  >
                    {line || "\u00a0"}
                  </span>
                ))}
          </div>
          {resizeHandles}
        </div>
      );
    }

    // Several XML generators store an inline SVG string as the text of an
    // <svg> node. Keep that vector decoration visible while the surrounding
    // XML elements remain selectable and editable.
    if (tag === "svg" || decodeXmlEntities(element.text).trimStart().startsWith("<svg")) {
      const svgMarkup = normalizeInlineSvg(element.text);
      return (
        <div
          {...common}
          style={{ ...style, overflow: "hidden" }}
        >
          <div
            style={{ width: "100%", height: "100%", overflow: "hidden" }}
            dangerouslySetInnerHTML={{ __html: svgMarkup }}
          />
          {resizeHandles}
        </div>
      );
    }

    if (["piechart", "barchart", "linechart"].includes(tag)) {
      return (
        <div {...common} className="flex flex-col justify-center gap-2 rounded text-center">
          <strong>{element.attrs.title || element.tag}</strong>
          <span className="text-xs text-slate-500">Chart preview · {element.children.length} series</span>
        </div>
      );
    }

    return <div {...common} aria-label={element.tag}>{resizeHandles}</div>;
  };

  const applySelectedTextFormat = (format: XmlTextFormat) => {
    if (!textSelection || !onFormatText) return;
    onFormatText(textSelection.elementId, {
      start: textSelection.start,
      end: textSelection.end,
      text: textSelection.text,
    }, format);
  };

  const textFormatToolbar = textSelection && editingId === textSelection.elementId && !readOnly && onFormatText ? (
    <div
      data-text-format-toolbar
      className="absolute z-[3000] flex items-center gap-1 rounded-2xl border border-slate-700/80 bg-slate-950/95 p-2 text-white shadow-2xl backdrop-blur-xl"
      style={{
        left: textSelection.left,
        top: textSelection.top,
        transform: "translateX(-50%)",
      }}
      onPointerDown={(event) => event.stopPropagation()}
    >
      <button
        type="button"
        title="Bold"
        aria-label="Bold selected text"
        className="flex h-10 w-10 items-center justify-center rounded-xl text-white/75 transition-colors hover:bg-white/15 hover:text-white"
        onMouseDown={(event) => event.preventDefault()}
        onClick={() => applySelectedTextFormat({ bold: "toggle" })}
      >
        <span className="text-base font-black leading-none">B</span>
      </button>
      <button
        type="button"
        title="Italic"
        aria-label="Italic selected text"
        className="flex h-10 w-10 items-center justify-center rounded-xl text-white/75 transition-colors hover:bg-white/15 hover:text-white"
        onMouseDown={(event) => event.preventDefault()}
        onClick={() => applySelectedTextFormat({ italic: "toggle" })}
      >
        <span className="text-base font-serif italic leading-none">I</span>
      </button>
      <button
        type="button"
        title="Underline"
        aria-label="Underline selected text"
        className="flex h-10 w-10 items-center justify-center rounded-xl text-white/75 transition-colors hover:bg-white/15 hover:text-white"
        onMouseDown={(event) => event.preventDefault()}
        onClick={() => applySelectedTextFormat({ underline: "toggle" })}
      >
        <span className="text-base font-serif underline leading-none">U</span>
      </button>
      <span className="mx-1 h-7 w-px bg-white/15" />
      <label title="Text color" className="flex h-10 w-10 cursor-pointer items-center justify-center rounded-xl text-white/75 transition-colors hover:bg-white/15 hover:text-white">
        <span className="relative flex h-7 w-7 items-center justify-center">
          <span className="absolute bottom-0.5 h-1 w-6 rounded-full bg-red-400" />
          <span className="text-sm font-bold">A</span>
          <input
            type="color"
            aria-label="Text color"
            defaultValue="#ef4444"
            className="absolute inset-0 cursor-pointer opacity-0"
            onChange={(event) => applySelectedTextFormat({ color: event.target.value })}
          />
        </span>
      </label>
      <label title="Highlight color" className="flex h-10 w-10 cursor-pointer items-center justify-center rounded-xl text-white/75 transition-colors hover:bg-white/15 hover:text-white">
        <span className="relative flex h-7 w-7 items-center justify-center">
          <span className="rounded-sm bg-yellow-200 px-1 text-xs font-bold leading-5 text-slate-900">H</span>
          <input
            type="color"
            aria-label="Highlight color"
            defaultValue="#fef08a"
            className="absolute inset-0 cursor-pointer opacity-0"
            onChange={(event) => applySelectedTextFormat({ highlight: event.target.value })}
          />
        </span>
      </label>
    </div>
  ) : null;

  const slideCanvas = (
    <div
      ref={canvasRef}
      className="relative overflow-hidden bg-white"
      style={{ width: canvasWidth, height: canvasHeight }}
      onPointerMove={handlePointerMove}
      onPointerUp={stopDragging}
      onPointerCancel={stopDragging}
      onPointerDown={() => {
        if (!readOnly) {
          setEditingId(null);
          clearTextSelection();
          onSelect(null, false);
        }
      }}
      onClick={(event) => {
        // A read-only canvas is also used inside a clickable slide thumbnail.
        // Let that thumbnail receive the click; the editor canvas still keeps
        // its event isolated so clicking its background clears the selection.
        if (!readOnly) event.stopPropagation();
      }}
    >
      <div className="absolute inset-0" style={{ background: slide.attrs.background || "#fff" }}>
        {slide.elements.map(renderElement)}
        {alignmentGuides.map((guide) => (
          <div
            key={`${guide.type}-${Math.round(guide.position)}`}
            aria-hidden="true"
            style={{
              position: "absolute",
              zIndex: 2000,
              pointerEvents: "none",
              background: "#ff3d82",
              boxShadow: "0 0 6px rgba(255, 61, 130, 0.75)",
              ...(guide.type === "vertical"
                ? { left: guide.position, top: 0, width: 2, height: canvasHeight }
                : { top: guide.position, left: 0, height: 2, width: canvasWidth }),
            }}
          />
        ))}
      </div>
      {textFormatToolbar}
    </div>
  );

  if (viewport === "bare") {
    return slideCanvas;
  }

  return (
    <div className="flex h-full w-full items-start justify-center overflow-auto bg-slate-100 p-8">
      <div style={{ width: canvasWidth * zoom, height: canvasHeight * zoom, flex: "0 0 auto" }}>
        <div
          className="relative origin-top-left overflow-hidden bg-white shadow-xl"
          style={{ width: canvasWidth, height: canvasHeight, transform: `scale(${zoom})` }}
        >
          {slideCanvas}
        </div>
      </div>
    </div>
  );
};
