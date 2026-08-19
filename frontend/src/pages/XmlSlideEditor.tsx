import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  BarChart3,
  BringToFront,
  Circle,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  Copy,
  Download,
  Diamond,
  Hexagon,
  Group as GroupIcon,
  Image,
  LayoutDashboard,
  Layers,
  Loader2,
  Maximize2,
  Minimize2,
  MousePointer,
  PaintBucket,
  Pause,
  Play,
  Plus,
  Redo2,
  RotateCcw,
  RotateCw,
  SendToBack,
  Shapes,
  Sparkles,
  StickyNote,
  Square,
  Timer,
  Triangle,
  Quote,
  List,
  Trash2,
  Type,
  Upload,
  Undo2,
  Ungroup,
  X,
} from "lucide-react";
import type { CSSProperties } from "react";
import { Button } from "@/components/ui/button";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuShortcut,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { XmlSlideCanvas } from "@/components/XmlSlideCanvas";
import {
  XML_GROUP_ATTR,
  cloneXmlElements,
  getXmlSelection,
  groupXmlElements,
  moveXmlSelectionLayer,
  ungroupXmlElements,
} from "@/lib/xmlGrouping";
import {
  applyXmlTextFormatting,
  type XmlTextFormat,
  type XmlTextSelection,
} from "@/lib/xmlTextFormatting";
import {
  defaultXmlSlide,
  parseXmlSlide,
  serializeXmlSlide,
  updateXmlElement,
  type XmlSlideDocument,
  type XmlSlideElement,
} from "@/lib/xmlSlide";
import {
  XML_TRANSITION_DIRECTIONS,
  XML_TRANSITION_OPTIONS,
  readXmlTransition,
  transitionAnimationName,
  transitionNeedsDirection,
  transitionOutgoingAnimationName,
} from "@/lib/xmlTransitions";

const MIN_ZOOM = 0.1;
const MAX_ZOOM = 2;
const ZOOM_STEP = 0.01;
const PAD = 48;
const TEXT_FONT_OPTIONS = [
  "Arial",
  "Helvetica",
  "Times New Roman",
  "Verdana",
  "Tahoma",
  "Trebuchet MS",
  "Courier New",
  "Inter",
  "Roboto",
  "Open Sans",
  "Poppins",
  "Montserrat",
  "Lato",
  "Nunito",
  "Be Vietnam Pro",
];

type SidebarLayout = "both-open" | "left-open" | "right-open" | "both-closed";
type XmlSaveStatus = "idle" | "saving" | "saved" | "error";
type AddElementKind =
  | "textbox" | "quote" | "bullets"
  | "shape" | "rounded" | "ellipse" | "triangle" | "diamond" | "hexagon" | "arrow" | "chevron"
  | "image" | "line" | "polygon" | "bar-chart";

const initialDocument = parseXmlSlide(defaultXmlSlide);

const PLAYWRIGHT_CAPTURE_WIDTH = 1920;
const PLAYWRIGHT_CAPTURE_HEIGHT = 1080;
const CAPTURE_STYLE_PROPERTIES = [
  "box-sizing",
  "position",
  "top",
  "right",
  "bottom",
  "left",
  "width",
  "height",
  "min-width",
  "min-height",
  "max-width",
  "max-height",
  "display",
  "flex",
  "flex-direction",
  "flex-grow",
  "flex-shrink",
  "justify-content",
  "align-items",
  "gap",
  "overflow",
  "overflow-x",
  "overflow-y",
  "background",
  "background-color",
  "background-image",
  "background-size",
  "background-position",
  "color",
  "font-family",
  "font-size",
  "font-weight",
  "font-style",
  "line-height",
  "letter-spacing",
  "text-align",
  "text-decoration",
  "white-space",
  "word-break",
  "overflow-wrap",
  "padding",
  "border",
  "border-radius",
  "box-shadow",
  "object-fit",
  "object-position",
  "opacity",
  "transform",
  "transform-origin",
  "z-index",
  "clip-path",
  "visibility",
  "vertical-align",
  "user-select",
];

const inlineCaptureStyles = (source: Element, target: Element) => {
  const computed = window.getComputedStyle(source);
  const computedStyles = CAPTURE_STYLE_PROPERTIES
    .map((property) => {
      const value = computed.getPropertyValue(property);
      return value ? `${property}:${value};` : "";
    })
    .join("");
  const existingStyles = target.getAttribute("style") || "";
  target.setAttribute("style", `${existingStyles}${computedStyles}`);

  Array.from(source.children).forEach((sourceChild, index) => {
    const targetChild = target.children[index];
    if (targetChild) inlineCaptureStyles(sourceChild, targetChild);
  });
};

const waitForCaptureImages = async (root: Element) => {
  const images = Array.from(root.querySelectorAll<HTMLImageElement>("img"));
  await Promise.all(images.map((image) => {
    if (image.complete) return Promise.resolve();
    return new Promise<void>((resolve) => {
      const finish = () => resolve();
      image.addEventListener("load", finish, { once: true });
      image.addEventListener("error", finish, { once: true });
      window.setTimeout(finish, 3000);
    });
  }));
};

const createPlaywrightSlideHtml = (canvas: HTMLElement, width: number, height: number) => {
  const clone = canvas.cloneNode(true) as HTMLElement;
  inlineCaptureStyles(canvas, clone);

  clone.querySelectorAll(".resize-handle, .drag-handle, .connector-control-point, .smart-guide, .distance-indicator")
    .forEach((element) => element.remove());
  clone.querySelectorAll("[contenteditable]").forEach((element) => element.removeAttribute("contenteditable"));

  // MathLive renders formulas inside a shadow root. Replace the custom element
  // with its readable LaTeX text so the server-side Playwright page can render
  // the formula even though it does not load the editor bundle.
  clone.querySelectorAll<HTMLElement>("math-span").forEach((mathElement) => {
    const replacement = document.createElement("span");
    replacement.setAttribute("style", mathElement.getAttribute("style") || "");
    replacement.textContent = mathElement.getAttribute("aria-label") || mathElement.textContent || "";
    mathElement.replaceWith(replacement);
  });

  // The editor uses a relative API URL for the image proxy. The Playwright
  // page has no frontend origin, so resolve relative image URLs to the API host.
  const apiOrigin = new URL(api.downloadCaptureUrl("capture"), window.location.origin).origin;
  clone.querySelectorAll<HTMLImageElement>("img").forEach((image) => {
    const source = image.getAttribute("src");
    if (source?.startsWith("/")) image.setAttribute("src", `${apiOrigin}${source}`);
  });

  const scaleX = PLAYWRIGHT_CAPTURE_WIDTH / Math.max(1, width);
  const scaleY = PLAYWRIGHT_CAPTURE_HEIGHT / Math.max(1, height);
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { box-sizing: border-box; }
    html, body {
      margin: 0;
      padding: 0;
      width: ${PLAYWRIGHT_CAPTURE_WIDTH}px;
      height: ${PLAYWRIGHT_CAPTURE_HEIGHT}px;
      overflow: hidden;
      background: #fff;
    }
    .playwright-capture-viewport {
      position: relative;
      width: ${PLAYWRIGHT_CAPTURE_WIDTH}px;
      height: ${PLAYWRIGHT_CAPTURE_HEIGHT}px;
      overflow: hidden;
    }
    .playwright-capture-slide {
      width: ${width}px;
      height: ${height}px;
      transform: scale(${scaleX}, ${scaleY});
      transform-origin: top left;
    }
  </style>
</head>
<body>
  <div class="playwright-capture-viewport">
    <div class="playwright-capture-slide">
      ${clone.outerHTML}
    </div>
  </div>
</body>
</html>`;
};

const clampZoom = (value: number) => Math.round(Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, value)) * 100) / 100;
const formatPresentTime = (totalSeconds: number) => {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
};
const toNumber = (value: string | undefined, fallback = 0) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const Tip = ({
  label,
  shortcut,
  side = "bottom",
  children,
}: {
  label: string;
  shortcut?: string;
  side?: "top" | "bottom" | "left" | "right";
  children: React.ReactNode;
}) => (
  <Tooltip delayDuration={350}>
    <TooltipTrigger asChild>{children}</TooltipTrigger>
    <TooltipContent side={side} className="max-w-[180px] text-left">
      <p className="text-xs font-semibold">
        {label}
        {shortcut && <span className="ml-1.5 rounded bg-muted/40 px-1 py-0.5 text-[10px] font-normal opacity-60">{shortcut}</span>}
      </p>
    </TooltipContent>
  </Tooltip>
);

const elementLabel = (element: XmlSlideElement) => {
  const tag = element.tag.toLowerCase();
  if (tag === "textbox" || tag === "text") return element.text.trim().slice(0, 32) || "Text";
  if (tag === "image") return "Image";
  if (tag === "line") return "Line";
  if (tag === "polygon") return "Polygon";
  return element.attrs.type || element.tag;
};

const makeElement = (kind: AddElementKind): XmlSlideElement => {
  const id = `xml-element-${Date.now()}-${Math.round(Math.random() * 1000)}`;
  const common = { id, text: "", children: [] };

  if (kind === "textbox" || kind === "quote" || kind === "bullets") {
    const isQuote = kind === "quote";
    const isBullets = kind === "bullets";
    return {
      ...common,
      tag: "textbox",
      text: isQuote ? "Add a quote" : isBullets ? "• First point\n• Second point\n• Third point" : "Click to edit",
      attrs: {
        x: "160",
        y: "150",
        width: isQuote ? "850" : isBullets ? "650" : "520",
        height: isQuote ? "180" : isBullets ? "220" : "130",
        font: "Arial",
        size: isQuote ? "42" : isBullets ? "30" : "32",
        color: "#111827",
        align: "left",
        vertical_align: "top",
        overflow: "shrink",
        reflow_on_resize: "true",
        ...(isQuote ? { italic: "true", font_weight: "500" } : {}),
      },
    };
  }

  if (kind === "image") {
    return {
      ...common,
      tag: "image",
      attrs: {
        x: "220",
        y: "220",
        width: "480",
        height: "300",
        src: "/placeholder.svg",
      },
    };
  }

  if (kind === "line") {
    return {
      ...common,
      tag: "line",
      attrs: {
        x1: "180",
        y1: "220",
        x2: "680",
        y2: "220",
        color: "#334155",
        width: "2",
      },
    };
  }

  if (kind === "polygon") {
    return {
      ...common,
      tag: "polygon",
      attrs: {
        points: "280,180 520,180 600,360 220,360",
        fill: "#94A3B8",
        line_color: "none",
      },
    };
  }

  if (kind === "bar-chart") {
    return {
      ...common,
      tag: "barchart",
      attrs: {
        x: "260",
        y: "230",
        width: "620",
        height: "360",
        title: "Chart title",
        color: "#3B82F6",
      },
    };
  }

  const shapeTypes: Partial<Record<AddElementKind, string>> = {
    rounded: "rounded_rectangle",
    ellipse: "ellipse",
    triangle: "triangle",
    diamond: "diamond",
    hexagon: "hexagon",
    arrow: "right_arrow",
    chevron: "chevron",
  };
  const shapeType = shapeTypes[kind];

  if (shapeType) {
    return {
      ...common,
      tag: "shape",
      attrs: {
        x: "220",
        y: "220",
        width: kind === "ellipse" ? "240" : "280",
        height: kind === "ellipse" ? "180" : "150",
        type: shapeType,
        fill: kind === "arrow" || kind === "chevron" ? "#60A5FA" : "#CBD5E1",
        line_color: "none",
      },
    };
  }

  return {
    ...common,
    tag: "shape",
    attrs: {
      x: "220",
      y: "220",
      width: "280",
      height: "150",
      type: "rectangle",
      fill: "#CBD5E1",
      line_color: "none",
    },
  };
};

const blankSlide = () => ({
  id: `xml-slide-${Date.now()}`,
  attrs: { background: "#FFFFFF" },
  elements: [],
});

const titleTemplateSlide = () => ({
  id: `xml-slide-${Date.now()}`,
  attrs: { background: "#FFFFFF" },
  elements: [
    {
      ...makeElement("textbox"),
      text: "Presentation Title",
      attrs: {
        x: "250",
        y: "310",
        width: "1100",
        height: "140",
        font: "Arial",
        size: "58",
        color: "#111827",
        align: "center",
        vertical_align: "middle",
        overflow: "shrink",
        reflow_on_resize: "true",
      },
    },
    {
      ...makeElement("textbox"),
      text: "Subtitle or short supporting statement",
      attrs: {
        x: "360",
        y: "470",
        width: "880",
        height: "70",
        font: "Arial",
        size: "24",
        color: "#64748B",
        align: "center",
        vertical_align: "middle",
        overflow: "shrink",
        reflow_on_resize: "true",
      },
    },
  ],
});

const contentTemplateSlide = () => ({
  id: `xml-slide-${Date.now()}`,
  attrs: { background: "#FFFFFF" },
  elements: [
    {
      ...makeElement("textbox"),
      text: "Section Heading",
      attrs: { x: "120", y: "90", width: "880", height: "90", font: "Arial", size: "42", color: "#0F172A", align: "left", vertical_align: "middle", overflow: "shrink" },
    },
    {
      ...makeElement("textbox"),
      text: "Add your key message here. Use concise content so the slide preview remains close to PowerPoint.",
      attrs: { x: "120", y: "230", width: "620", height: "310", font: "Arial", size: "25", color: "#334155", align: "left", vertical_align: "top", overflow: "shrink", reflow_on_resize: "true", line_spacing: "1.12" },
    },
    {
      ...makeElement("shape"),
      attrs: { x: "860", y: "230", width: "560", height: "330", type: "rounded_rectangle", fill: "#E2E8F0", line_color: "none" },
    },
  ],
});

const updateSlideAt = (document: XmlSlideDocument, slideIndex: number, patch: Partial<XmlSlideDocument["slides"][number]>) => ({
  ...document,
  slides: document.slides.map((slide, index) => (index === slideIndex ? { ...slide, ...patch } : slide)),
});

const prefixXmlElementIds = (element: XmlSlideElement, prefix: string): XmlSlideElement => ({
  ...element,
  id: `${prefix}-${element.id}`,
  children: element.children.map((child) => prefixXmlElementIds(child, prefix)),
});

const buildDocumentFromXmlSources = (sources: string[]): XmlSlideDocument => {
  const docs = sources.map((source) => parseXmlSlide(source));
  const first = docs[0];

  return {
    presentationAttrs: first.presentationAttrs,
    width: first.width,
    height: first.height,
    slides: docs.flatMap((doc, docIndex) =>
      doc.slides.map((slide, slideIndex) => {
        const prefix = `project-${docIndex}-${slideIndex}`;
        return {
          ...slide,
          id: `${prefix}-${slide.id}`,
          elements: slide.elements.map((element) => prefixXmlElementIds(element, prefix)),
        };
      }),
    ),
  };
};

const isXmlPresentationSource = (value: unknown): value is string => {
  if (typeof value !== "string") return false;
  const source = value.replace(/^\uFEFF/, "").trim();
  return /^<\?xml\b/i.test(source) || /^<presentation(?:\s|>)/i.test(source);
};

const XmlSlideThumbnail = memo(({
  slide,
  canvasWidth,
  canvasHeight,
  slideWidthInches,
  slideHeightInches,
  slideIndex,
  active,
  onClick,
}: {
  slide: XmlSlideDocument["slides"][number];
  canvasWidth: number;
  canvasHeight: number;
  slideWidthInches: number;
  slideHeightInches: number;
  slideIndex: number;
  active: boolean;
  onClick: () => void;
}) => {
  const frameRef = useRef<HTMLDivElement>(null);
  const [frameWidth, setFrameWidth] = useState(0);
  const safeFrameWidth = frameWidth || 1;
  const scale = safeFrameWidth / canvasWidth;

  useEffect(() => {
    const frame = frameRef.current;
    if (!frame) return;

    const updateWidth = () => setFrameWidth(frame.clientWidth);
    updateWidth();

    const observer = new ResizeObserver(updateWidth);
    observer.observe(frame);

    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={frameRef}
      onClick={onClick}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onClick();
        }
      }}
      role="button"
      tabIndex={0}
      aria-label={`Select slide ${slideIndex + 1}`}
      className={cn(
        "group relative w-full cursor-pointer overflow-hidden rounded-lg border-2 bg-muted/30 text-left transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/60",
        active ? "border-primary shadow-md shadow-primary/10 ring-2 ring-primary/20" : "border-transparent hover:border-border/70",
      )}
      style={{ aspectRatio: `${canvasWidth} / ${canvasHeight}` }}
    >
      <div className="absolute inset-0 overflow-hidden">
        <div style={{ width: canvasWidth, height: canvasHeight, transform: `scale(${scale})`, transformOrigin: "top left" }}>
          <XmlSlideCanvas
            slide={slide}
            canvasWidth={canvasWidth}
            canvasHeight={canvasHeight}
            slideWidthInches={slideWidthInches}
            slideHeightInches={slideHeightInches}
            selectedId={null}
            readOnly
            viewport="bare"
            onSelect={() => undefined}
            onChange={() => undefined}
          />
        </div>
      </div>
    </div>
  );
});

XmlSlideThumbnail.displayName = "XmlSlideThumbnail";

const XmlSlideEditor = () => {
  const [searchParams] = useSearchParams();
  const projectId = searchParams.get("project");
  const slideParam = searchParams.get("slide");
  const [xmlDocument, setXmlDocument] = useState<XmlSlideDocument>(initialDocument);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const selectedId = selectedIds[0] || null;
  const setSelectedId = (id: string | null) => setSelectedIds(id ? [id] : []);
  const [activeSlideIndex, setActiveSlideIndex] = useState(0);
  const [parseError, setParseError] = useState("");
  const [importMessage, setImportMessage] = useState("");
  const [zoom, setZoom] = useState(0.6);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isPropsPanelOpen, setIsPropsPanelOpen] = useState(true);
  const [isPresenting, setIsPresenting] = useState(false);
  const [isPresentFullscreen, setIsPresentFullscreen] = useState(false);
  const [isPresentControlsVisible, setIsPresentControlsVisible] = useState(true);
  const [isPresentNotesVisible, setIsPresentNotesVisible] = useState(false);
  const [isPresenterView, setIsPresenterView] = useState(false);
  const [isPresentTimerRunning, setIsPresentTimerRunning] = useState(false);
  const [presentElapsedSeconds, setPresentElapsedSeconds] = useState(0);
  const [presentTransition, setPresentTransition] = useState<{
    from: number;
    to: number;
    nonce: number;
  } | null>(null);
  const [presentViewport, setPresentViewport] = useState(() => ({
    width: typeof window === "undefined" ? 1440 : window.innerWidth,
    height: typeof window === "undefined" ? 900 : window.innerHeight,
  }));
  const [isExportingPptx, setIsExportingPptx] = useState(false);
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [saveStatus, setSaveStatus] = useState<XmlSaveStatus>("idle");
  const [historyVersion, setHistoryVersion] = useState(0);
  const [activeTextSelection, setActiveTextSelection] = useState<{
    elementId: string;
    selection: XmlTextSelection;
  } | null>(null);

  const documentRef = useRef(initialDocument);
  const historyRef = useRef<{ items: XmlSlideDocument[]; index: number }>({ items: [initialDocument], index: 0 });
  const clipboardRef = useRef<XmlSlideElement[] | null>(null);
  const canvasShellRef = useRef<HTMLDivElement>(null);
  const presentShellRef = useRef<HTMLDivElement>(null);
  const presentHideTimerRef = useRef<number | null>(null);
  const presentTransitionTimerRef = useRef<number | null>(null);
  const presentAdvanceTimerRef = useRef<number | null>(null);
  const dragSlideIndexRef = useRef<number | null>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const pendingImageElementRef = useRef<string | null>(null);
  const databaseSlideIdsRef = useRef<Map<string, string>>(new Map());
  const documentLoadedRef = useRef(false);
  const lastSavedXmlRef = useRef("");
  const saveTimerRef = useRef<number | null>(null);
  const saveInFlightRef = useRef<Promise<void> | null>(null);

  const selected = useMemo(
    () => xmlDocument.slides[activeSlideIndex]?.elements.find((element) => element.id === selectedId) || null,
    [xmlDocument.slides, activeSlideIndex, selectedId],
  );
  const selectedElements = useMemo(
    () => xmlDocument.slides[activeSlideIndex]?.elements.filter((element) => selectedIds.includes(element.id)) || [],
    [xmlDocument.slides, activeSlideIndex, selectedIds],
  );
  const selectionGroupId = selectedElements.length > 0
    ? selectedElements[0].attrs[XML_GROUP_ATTR] || null
    : null;
  const canUngroup = Boolean(
    selectionGroupId
    && selectedElements.every((element) => element.attrs[XML_GROUP_ATTR] === selectionGroupId),
  );
  const selectedMathFields = selected
    ? selected.children
      .map((child, index) => ({ child, index }))
      .filter(({ child }) => child.tag.toLowerCase() === "math-field")
    : [];
  const selectedTextRange = activeTextSelection && selected && activeTextSelection.elementId === selected.id
    ? activeTextSelection.selection
    : null;
  const selectedTextSnippet = selectedTextRange
    ? (selectedTextRange.text ?? selected?.text ?? "").slice(selectedTextRange.start, selectedTextRange.end)
    : "";

  const canUndo = historyRef.current.index > 0;
  const canRedo = historyRef.current.index < historyRef.current.items.length - 1;
  const sidebarLayout: SidebarLayout = isSidebarOpen
    ? isPropsPanelOpen ? "both-open" : "left-open"
    : isPropsPanelOpen ? "right-open" : "both-closed";

  const applyDocument = (next: XmlSlideDocument, recordHistory = false) => {
    documentRef.current = next;
    setXmlDocument(next);
    if (recordHistory) {
      const history = historyRef.current;
      history.items = [...history.items.slice(0, history.index + 1), next].slice(-60);
      history.index = history.items.length - 1;
      setHistoryVersion((version) => version + 1);
    }
  };

  const resetDocument = (next: XmlSlideDocument) => {
    documentRef.current = next;
    setXmlDocument(next);
    historyRef.current = { items: [next], index: 0 };
    setHistoryVersion((version) => version + 1);
    setActiveSlideIndex(0);
    setSelectedId(null);
  };

  const saveXmlDocument = useCallback(async (documentToSave: XmlSlideDocument) => {
    if (!projectId || documentToSave.slides.length === 0) return;

    const serializedDocument = serializeXmlSlide(documentToSave);
    if (serializedDocument === lastSavedXmlRef.current) {
      if (saveInFlightRef.current) await saveInFlightRef.current;
      return;
    }

    const previousSave = saveInFlightRef.current;
    const saveTask = (previousSave ? previousSave.catch(() => undefined) : Promise.resolve()).then(async () => {
      // A queued save may contain the same document as the save before it.
      if (serializedDocument === lastSavedXmlRef.current) return;

      setSaveStatus("saving");
      const previousSlideIds = new Map(databaseSlideIdsRef.current);
      const persistedSlideIds = new Map<string, string>();

      try {
        await Promise.all(documentToSave.slides.map(async (slide, index) => {
          const singleSlideXml = serializeXmlSlide({
            ...documentToSave,
            slides: [slide],
          });
          const slideData = {
            slide_index: index,
            html_content: singleSlideXml,
            design_settings: { format: "xml" },
          };
          const existingId = previousSlideIds.get(slide.id);

          if (existingId) {
            await api.updateSlide(existingId, slideData);
            persistedSlideIds.set(slide.id, existingId);
            return;
          }

          const created = await api.createSlide(projectId, {
            ...slideData,
            slide_type: index === 0 ? "intro" : "content",
            title: `Slide ${index + 1}`,
          });
          const createdId = created.id ?? created.project_id;
          if (createdId === undefined || createdId === null) {
            throw new Error("The server did not return the new slide id");
          }
          persistedSlideIds.set(slide.id, String(createdId));
        }));

        const idsToKeep = new Set(persistedSlideIds.values());
        const staleIds = [...new Set(previousSlideIds.values())].filter((id) => !idsToKeep.has(id));
        await Promise.all(staleIds.map((slideId) => api.deleteSlide(slideId)));

        databaseSlideIdsRef.current = persistedSlideIds;
        await api.updateProject(projectId, { slide_count: documentToSave.slides.length });
        lastSavedXmlRef.current = serializedDocument;
        setSaveStatus("saved");
      } catch (error) {
        setSaveStatus("error");
        console.error("Failed to save XML presentation", error);
        throw error;
      }
    });

    saveInFlightRef.current = saveTask;
    try {
      await saveTask;
    } finally {
      if (saveInFlightRef.current === saveTask) saveInFlightRef.current = null;
    }
  }, [projectId]);

  useEffect(() => {
    if (!projectId) return;

    documentLoadedRef.current = false;
    if (saveTimerRef.current !== null) {
      window.clearTimeout(saveTimerRef.current);
      saveTimerRef.current = null;
    }

    let cancelled = false;
    api.getSlides(projectId)
      .then((response) => {
        // XML projects are persisted in the legacy html_content column. Only
        // accept a real <presentation> document here; otherwise the old HTML
        // editor payload can be mistaken for an XML slide and render as a
        // large image/HTML snapshot.
        const xmlSources = (response.slides as Array<Record<string, unknown>> || [])
          .flatMap((slide) => {
            const source = [slide.xmlContent, slide.xml_content, slide.html_content, slide.content]
              .find(isXmlPresentationSource);
            if (!isXmlPresentationSource(source) || slide.id === undefined || slide.id === null) return [];
            return [{ id: String(slide.id), source }];
          });

        if (!xmlSources.length) {
          throw new Error("Project has no slides");
        }

        const next = buildDocumentFromXmlSources(xmlSources.map(({ source }) => source));
        if (cancelled) return;
        const databaseSlideIds = new Map<string, string>();
        let flattenedSlideIndex = 0;
        xmlSources.forEach(({ id, source }) => {
          const sourceDocument = parseXmlSlide(source);
          sourceDocument.slides.forEach(() => {
            const loadedSlide = next.slides[flattenedSlideIndex];
            if (loadedSlide && !databaseSlideIds.has(loadedSlide.id)) {
              databaseSlideIds.set(loadedSlide.id, id);
            }
            flattenedSlideIndex += 1;
          });
        });
        databaseSlideIdsRef.current = databaseSlideIds;
        lastSavedXmlRef.current = serializeXmlSlide(next);
        documentLoadedRef.current = true;
        setSaveStatus("saved");
        resetDocument(next);
        const requestedSlide = Number(slideParam);
        if (Number.isInteger(requestedSlide) && requestedSlide >= 0 && requestedSlide < next.slides.length) {
          setActiveSlideIndex(requestedSlide);
        }
        setParseError("");
        setImportMessage(`Loaded ${next.slides.length} slide(s) from project.`);
      })
      .catch((error) => {
        if (cancelled) return;
        setParseError(error instanceof Error ? error.message : "Could not load project");
      });

    return () => {
      cancelled = true;
    };
  }, [projectId, slideParam]);

  useEffect(() => {
    if (!projectId || !documentLoadedRef.current || xmlDocument.slides.length === 0) return;

    const serializedDocument = serializeXmlSlide(xmlDocument);
    if (serializedDocument === lastSavedXmlRef.current) return;

    if (saveTimerRef.current !== null) window.clearTimeout(saveTimerRef.current);
    saveTimerRef.current = window.setTimeout(() => {
      saveTimerRef.current = null;
      void saveXmlDocument(xmlDocument).catch(() => undefined);
    }, 2000);

    return () => {
      if (saveTimerRef.current !== null) {
        window.clearTimeout(saveTimerRef.current);
        saveTimerRef.current = null;
      }
    };
  }, [projectId, saveXmlDocument, xmlDocument]);

  const flushXmlSave = useCallback(async () => {
    if (saveTimerRef.current !== null) {
      window.clearTimeout(saveTimerRef.current);
      saveTimerRef.current = null;
    }
    if (documentLoadedRef.current) await saveXmlDocument(documentRef.current);
    if (saveInFlightRef.current) await saveInFlightRef.current;
  }, [saveXmlDocument]);

  const handleExitEditor = async () => {
    try {
      await flushXmlSave();
      window.history.back();
    } catch {
      window.alert("Could not save the latest changes. Please try again.");
    }
  };

  const updateElement = (id: string, update: Parameters<typeof updateXmlElement>[2], recordHistory = false) => {
    applyDocument(updateXmlElement(documentRef.current, id, update, activeSlideIndex), recordHistory);
  };

  const updateMathField = (elementId: string, childIndex: number, latex: string, recordHistory = true) => {
    const element = documentRef.current.slides[activeSlideIndex]?.elements.find((item) => item.id === elementId);
    if (!element) return;
    const children = element.children.map((child, index) => {
      if (index !== childIndex || child.tag.toLowerCase() !== "math-field") return child;
      const attrs = { ...child.attrs };
      delete attrs.value;
      return { ...child, attrs, text: latex };
    });
    updateElement(elementId, { children }, recordHistory);
  };

  const updateAttr = (name: string, value: string, recordHistory = true) => {
    if (selected) updateElement(selected.id, { attrs: { [name]: value } }, recordHistory);
  };

  const formatTextSelection = (elementId: string, selection: XmlTextSelection, format: XmlTextFormat) => {
    const element = documentRef.current.slides[activeSlideIndex]?.elements.find((item) => item.id === elementId);
    if (!element) return;
    const source = selection.text === undefined ? element : { ...element, text: selection.text };
    const children = applyXmlTextFormatting(source, selection, format);
    if (children.length === 0) return;
    updateElement(elementId, { text: source.text, children }, true);
  };

  const formatSelectedTextFromPanel = (format: XmlTextFormat) => {
    if (!selected || !selectedTextRange) return;
    formatTextSelection(selected.id, selectedTextRange, format);
  };

  const updateSlideBackground = (value: string) => {
    const currentSlide = documentRef.current.slides[activeSlideIndex];
    applyDocument(updateSlideAt(documentRef.current, activeSlideIndex, { attrs: { ...currentSlide.attrs, background: value } }), true);
  };

  const updateSlideNotes = (value: string) => {
    const currentSlide = documentRef.current.slides[activeSlideIndex];
    if (!currentSlide) return;
    const attrs = { ...currentSlide.attrs };
    if (value) attrs.speaker_notes = value;
    else delete attrs.speaker_notes;
    applyDocument(updateSlideAt(documentRef.current, activeSlideIndex, { attrs }), true);
  };

  const updateSlideTransition = (update: Record<string, string>) => {
    const currentSlide = documentRef.current.slides[activeSlideIndex];
    if (!currentSlide) return;
    applyDocument(
      updateSlideAt(documentRef.current, activeSlideIndex, {
        attrs: { ...currentSlide.attrs, ...update },
      }),
      true,
    );
  };

  const undo = () => {
    const history = historyRef.current;
    if (history.index <= 0) return;
    history.index -= 1;
    const next = history.items[history.index];
    documentRef.current = next;
    setXmlDocument(next);
    setSelectedId(null);
    setHistoryVersion((version) => version + 1);
  };

  const redo = () => {
    const history = historyRef.current;
    if (history.index >= history.items.length - 1) return;
    history.index += 1;
    const next = history.items[history.index];
    documentRef.current = next;
    setXmlDocument(next);
    setSelectedId(null);
    setHistoryVersion((version) => version + 1);
  };

  const updateSlideElements = (elements: XmlSlideElement[], recordHistory = true) => {
    applyDocument(updateSlideAt(documentRef.current, activeSlideIndex, { elements }), recordHistory);
  };

  const addElement = (kind: AddElementKind) => {
    const element = makeElement(kind);
    updateSlideElements([...documentRef.current.slides[activeSlideIndex].elements, element]);
    setSelectedId(element.id);
    if (kind === "image") {
      pendingImageElementRef.current = element.id;
      // Let React commit the new selection before opening the native picker.
      window.setTimeout(() => imageInputRef.current?.click(), 0);
    }
  };

  const openImagePicker = (elementId: string) => {
    pendingImageElementRef.current = elementId;
    imageInputRef.current?.click();
  };

  const handleImageFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";

    const elementId = pendingImageElementRef.current;
    pendingImageElementRef.current = null;
    if (!file || !elementId || !file.type.startsWith("image/")) return;

    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result !== "string" || !reader.result.startsWith("data:image/")) return;
      updateElement(elementId, {
        attrs: {
          src: reader.result,
          alt: file.name,
        },
      }, true);
    };
    reader.onerror = () => {
      setImportMessage("Could not read the selected image.");
    };
    reader.readAsDataURL(file);
  };

  const addSlide = (template: "blank" | "title" | "content" = "blank") => {
    const slide = template === "title" ? titleTemplateSlide() : template === "content" ? contentTemplateSlide() : blankSlide();
    const next = { ...documentRef.current, slides: [...documentRef.current.slides, slide] };
    applyDocument(next, true);
    setActiveSlideIndex(next.slides.length - 1);
    setSelectedId(null);
  };

  const deleteSlide = (index: number) => {
    if (documentRef.current.slides.length <= 1) return;
    const slides = documentRef.current.slides.filter((_, slideIndex) => slideIndex !== index);
    applyDocument({ ...documentRef.current, slides }, true);
    setActiveSlideIndex((current) => Math.max(0, Math.min(current, slides.length - 1)));
    setSelectedId(null);
  };

  const duplicateSlide = (index: number) => {
    const clone = JSON.parse(JSON.stringify(documentRef.current.slides[index])) as XmlSlideDocument["slides"][number];
    clone.id = `xml-slide-${Date.now()}`;
    clone.elements = clone.elements.map((element, elementIndex) => ({ ...element, id: `${element.id}-copy-${Date.now()}-${elementIndex}` }));
    const slides = [...documentRef.current.slides];
    slides.splice(index + 1, 0, clone);
    applyDocument({ ...documentRef.current, slides }, true);
    setActiveSlideIndex(index + 1);
    setSelectedId(null);
  };

  const reorderSlides = (fromIndex: number, toIndex: number) => {
    if (fromIndex === toIndex || toIndex < 0 || toIndex >= documentRef.current.slides.length) return;
    const slides = [...documentRef.current.slides];
    const [moved] = slides.splice(fromIndex, 1);
    slides.splice(toIndex, 0, moved);
    applyDocument({ ...documentRef.current, slides }, true);
    setActiveSlideIndex(toIndex);
    setSelectedId(null);
  };

  const handleCanvasSelect = (id: string | null, additive = false) => {
    const elements = documentRef.current.slides[activeSlideIndex]?.elements || [];
    setSelectedIds((current) => getXmlSelection(elements, current, id, additive));
    setActiveTextSelection(null);
  };

  const handleTextSelectionChange = (elementId: string | null, selection: XmlTextSelection | null) => {
    setActiveTextSelection(elementId && selection ? { elementId, selection } : null);
  };

  const deleteSelected = () => {
    if (selectedIds.length === 0) return;
    const selectedSet = new Set(selectedIds);
    updateSlideElements(documentRef.current.slides[activeSlideIndex].elements.filter((element) => !selectedSet.has(element.id)));
    setSelectedId(null);
  };

  const duplicateSelected = () => {
    if (selectedElements.length === 0) return;
    const clones = cloneXmlElements(selectedElements);
    updateSlideElements([...documentRef.current.slides[activeSlideIndex].elements, ...clones]);
    setSelectedIds(clones.map((clone) => clone.id));
  };

  const moveLayer = (direction: "up" | "down") => {
    if (selectedIds.length === 0) return;
    updateSlideElements(moveXmlSelectionLayer(
      documentRef.current.slides[activeSlideIndex].elements,
      selectedIds,
      direction,
    ));
  };

  const groupSelected = () => {
    if (selectedIds.length < 2) return;
    updateSlideElements(groupXmlElements(
      documentRef.current.slides[activeSlideIndex].elements,
      selectedIds,
    ));
  };

  const ungroupSelected = () => {
    if (!canUngroup) return;
    updateSlideElements(ungroupXmlElements(
      documentRef.current.slides[activeSlideIndex].elements,
      selectedIds,
    ));
  };

  const copySelected = () => {
    if (selectedElements.length === 0) return;
    clipboardRef.current = JSON.parse(JSON.stringify(selectedElements)) as XmlSlideElement[];
  };

  const pasteSelected = () => {
    if (!clipboardRef.current) return;
    const clones = cloneXmlElements(clipboardRef.current);
    updateSlideElements([...documentRef.current.slides[activeSlideIndex].elements, ...clones]);
    setSelectedIds(clones.map((clone) => clone.id));
  };

  const downloadPowerPoint = async () => {
    if (isExportingPptx) return;

    setIsExportingPptx(true);
    try {
      const result = await api.exportXmlToPptx(
        serializeXmlSlide(documentRef.current),
        "presentation",
      );

      if (!result.success || !result.filename) {
        throw new Error(result.error || result.message || "PowerPoint export failed");
      }

      const anchor = window.document.createElement("a");
      anchor.href = api.downloadCaptureUrl(result.filename);
      anchor.download = result.filename;
      anchor.click();
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "PowerPoint export failed");
    } finally {
      setIsExportingPptx(false);
    }
  };

  const exportPdf = () => {
    if (isExportingPptx || isExportingPdf) return;
    setIsExportingPdf(true);
  };

  const isExporting = isExportingPptx || isExportingPdf;

  useEffect(() => {
    if (!isExportingPdf) return;

    let cancelled = false;
    const timer = window.setTimeout(async () => {
      try {
        const pages = Array.from(
          document.querySelectorAll<HTMLElement>("[data-xml-export-page]"),
        );
        if (pages.length !== xmlDocument.slides.length) {
          throw new Error("Could not prepare all slides for PDF export");
        }

        await Promise.all(pages.map((page) => waitForCaptureImages(page)));
        const slides = pages.map((page, index) => {
          const canvas = page.querySelector<HTMLElement>("[data-xml-slide-canvas]");
          if (!canvas) throw new Error(`Could not render slide ${index + 1} for PDF export`);
          return {
            html_content: createPlaywrightSlideHtml(canvas, xmlDocument.width, xmlDocument.height),
            slide_name: `slide_${index + 1}`,
          };
        });

        const result = await api.exportSlidesPdf(slides);
        const filename = result.filename || result.download_url?.split("/").pop();
        if (!result.success || !filename) {
          throw new Error(result.error || result.message || "PDF export failed");
        }

        const anchor = window.document.createElement("a");
        anchor.href = api.downloadCaptureUrl(filename);
        anchor.download = filename;
        anchor.click();
      } catch (error) {
        if (!cancelled) {
          window.alert(error instanceof Error ? error.message : "PDF export failed");
        }
      } finally {
        if (!cancelled) setIsExportingPdf(false);
      }
    }, 100);

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [isExportingPdf, xmlDocument.height, xmlDocument.slides.length, xmlDocument.width]);

  const fitZoom = () => {
    const el = canvasShellRef.current;
    if (!el) return;
    const availW = el.clientWidth - PAD * 2;
    const availH = el.clientHeight - PAD * 2;
    const fit = Math.min(availW / xmlDocument.width, availH / xmlDocument.height);
    if (Number.isFinite(fit)) setZoom(clampZoom(Math.floor(fit * 100) / 100));
  };

  const navigatePresent = useCallback((toIndex: number) => {
    const fromIndex = activeSlideIndex;
    const slides = documentRef.current.slides;
    if (toIndex < 0 || toIndex >= slides.length || toIndex === fromIndex || presentTransition) return;

    if (presentAdvanceTimerRef.current !== null) {
      window.clearTimeout(presentAdvanceTimerRef.current);
      presentAdvanceTimerRef.current = null;
    }
    if (presentTransitionTimerRef.current !== null) {
      window.clearTimeout(presentTransitionTimerRef.current);
      presentTransitionTimerRef.current = null;
    }

    const config = readXmlTransition(slides[toIndex]?.attrs || {});
    setActiveSlideIndex(toIndex);
    if (config.type === "none" || config.type === "cut") {
      setPresentTransition(null);
      return;
    }

    const nonce = Date.now();
    setPresentTransition({ from: fromIndex, to: toIndex, nonce });
    presentTransitionTimerRef.current = window.setTimeout(() => {
      setPresentTransition(null);
      presentTransitionTimerRef.current = null;
    }, config.duration + 80);
  }, [activeSlideIndex, presentTransition]);

  const presentNext = useCallback(() => {
    navigatePresent(Math.min(documentRef.current.slides.length - 1, activeSlideIndex + 1));
  }, [activeSlideIndex, navigatePresent]);

  const presentPrevious = useCallback(() => {
    navigatePresent(Math.max(0, activeSlideIndex - 1));
  }, [activeSlideIndex, navigatePresent]);

  const startPresent = async () => {
    setIsPresentControlsVisible(true);
    setIsPresentNotesVisible(false);
    setIsPresenterView(false);
    setPresentElapsedSeconds(0);
    setIsPresentTimerRunning(true);
    setIsPresenting(true);
    try {
      if (!document.fullscreenElement && document.documentElement.requestFullscreen) {
        await document.documentElement.requestFullscreen();
        setIsPresentFullscreen(Boolean(document.fullscreenElement));
      }
    } catch {
      // Fullscreen can be denied by the browser; the full-window overlay still works.
    }
  };

  const closePresent = () => {
    setIsPresenting(false);
    setIsPresentFullscreen(false);
    setIsPresentNotesVisible(false);
    setIsPresenterView(false);
    setIsPresentTimerRunning(false);
    if (presentHideTimerRef.current !== null) {
      window.clearTimeout(presentHideTimerRef.current);
      presentHideTimerRef.current = null;
    }
    if (presentTransitionTimerRef.current !== null) {
      window.clearTimeout(presentTransitionTimerRef.current);
      presentTransitionTimerRef.current = null;
    }
    if (presentAdvanceTimerRef.current !== null) {
      window.clearTimeout(presentAdvanceTimerRef.current);
      presentAdvanceTimerRef.current = null;
    }
    setPresentTransition(null);
    if (document.fullscreenElement) {
      document.exitFullscreen().catch(() => undefined);
    }
  };

  const togglePresentFullscreen = async () => {
    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen();
      } else {
        await (presentShellRef.current || document.documentElement).requestFullscreen?.();
      }
    } catch {
      // Fullscreen can be denied by the browser; the in-app presentation still works.
    }
  };

  const revealPresentControls = () => {
    setIsPresentControlsVisible(true);
    if (presentHideTimerRef.current !== null) window.clearTimeout(presentHideTimerRef.current);
    presentHideTimerRef.current = window.setTimeout(() => {
      setIsPresentControlsVisible(false);
      presentHideTimerRef.current = null;
    }, 3200);
  };

  useEffect(() => {
    if (!isPresenting) return;
    const updateViewport = () => setPresentViewport({ width: window.innerWidth, height: window.innerHeight });
    const handleFullscreenChange = () => {
      setIsPresentFullscreen(Boolean(document.fullscreenElement));
      updateViewport();
    };
    updateViewport();
    revealPresentControls();
    window.addEventListener("resize", updateViewport);
    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => {
      window.removeEventListener("resize", updateViewport);
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
      if (presentHideTimerRef.current !== null) {
        window.clearTimeout(presentHideTimerRef.current);
        presentHideTimerRef.current = null;
      }
      if (presentTransitionTimerRef.current !== null) {
        window.clearTimeout(presentTransitionTimerRef.current);
        presentTransitionTimerRef.current = null;
      }
      if (presentAdvanceTimerRef.current !== null) {
        window.clearTimeout(presentAdvanceTimerRef.current);
        presentAdvanceTimerRef.current = null;
      }
      setPresentTransition(null);
    };
  }, [isPresenting]);

  useEffect(() => {
    if (!isPresenting || !isPresentTimerRunning) return;
    const timer = window.setInterval(() => {
      setPresentElapsedSeconds((seconds) => seconds + 1);
    }, 1000);
    return () => window.clearInterval(timer);
  }, [isPresenting, isPresentTimerRunning]);

  useEffect(() => {
    if (!isPresenting) return;
    if (presentAdvanceTimerRef.current !== null) {
      window.clearTimeout(presentAdvanceTimerRef.current);
      presentAdvanceTimerRef.current = null;
    }
    const currentSlide = documentRef.current.slides[activeSlideIndex];
    const config = readXmlTransition(currentSlide?.attrs || {});
    if (!currentSlide || (config.advance !== "after" && config.advance !== "both") || activeSlideIndex >= documentRef.current.slides.length - 1) {
      return;
    }
    const waitMs = config.delay + (presentTransition ? config.duration : 0);
    presentAdvanceTimerRef.current = window.setTimeout(() => {
      presentAdvanceTimerRef.current = null;
      presentNext();
    }, waitMs);
    return () => {
      if (presentAdvanceTimerRef.current !== null) {
        window.clearTimeout(presentAdvanceTimerRef.current);
        presentAdvanceTimerRef.current = null;
      }
    };
  }, [isPresenting, activeSlideIndex, presentNext, presentTransition, xmlDocument.slides]);

  useEffect(() => {
    const timer = window.setTimeout(fitZoom, 320);
    return () => window.clearTimeout(timer);
  }, [sidebarLayout, activeSlideIndex, xmlDocument.width, xmlDocument.height]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const typing = !!target && (target.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName));
      if (isPresenting) {
        if (event.key === "Escape") {
          event.preventDefault();
          closePresent();
        } else if (event.key.toLowerCase() === "p") {
          event.preventDefault();
          setIsPresenterView((visible) => !visible);
          setIsPresentNotesVisible(false);
          revealPresentControls();
        } else if (event.key.toLowerCase() === "n" && !isPresenterView) {
          event.preventDefault();
          setIsPresentNotesVisible((visible) => !visible);
          revealPresentControls();
        } else if (event.key.toLowerCase() === "t") {
          event.preventDefault();
          setIsPresentTimerRunning((running) => !running);
          revealPresentControls();
        } else if (event.key === "ArrowRight" || event.key === "PageDown" || event.key === " " || event.key === "Enter") {
          event.preventDefault();
          presentNext();
        } else if (event.key === "ArrowLeft" || event.key === "PageUp") {
          event.preventDefault();
          presentPrevious();
        } else if (event.key === "Home") {
          event.preventDefault();
          navigatePresent(0);
        } else if (event.key === "End") {
          event.preventDefault();
          navigatePresent(documentRef.current.slides.length - 1);
        }
        return;
      }
      if (!typing && event.key === "ArrowDown") {
        setActiveSlideIndex((index) => Math.min(documentRef.current.slides.length - 1, index + 1));
        setSelectedId(null);
        return;
      }
      if (!typing && event.key === "ArrowUp") {
        setActiveSlideIndex((index) => Math.max(0, index - 1));
        setSelectedId(null);
        return;
      }
      if (!typing && event.key === "Delete" && selectedIds.length > 0) {
        event.preventDefault();
        deleteSelected();
        return;
      }
      const modifier = event.ctrlKey || event.metaKey;
      if (!modifier || typing) return;
      const key = event.key.toLowerCase();
      if (key === "z" && !event.shiftKey) {
        event.preventDefault();
        undo();
      } else if (key === "y" || (key === "z" && event.shiftKey)) {
        event.preventDefault();
        redo();
      } else if (key === "d" && selectedElements.length > 0) {
        event.preventDefault();
        duplicateSelected();
      } else if (key === "c" && selectedElements.length > 0) {
        event.preventDefault();
        copySelected();
      } else if (key === "v" && clipboardRef.current) {
        event.preventDefault();
        pasteSelected();
      } else if (key === "g") {
        event.preventDefault();
        if (event.shiftKey) ungroupSelected();
        else groupSelected();
      } else if (event.key === "]" && selectedIds.length > 0) {
        event.preventDefault();
        moveLayer("up");
      } else if (event.key === "[" && selectedIds.length > 0) {
        event.preventDefault();
        moveLayer("down");
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  });

  const activeSlide = xmlDocument.slides[activeSlideIndex];
  const resolvedActiveSlide = activeSlide || xmlDocument.slides[0];
  const activeTransition = readXmlTransition(resolvedActiveSlide?.attrs || {});
  const activeSlideNotes = resolvedActiveSlide?.attrs.speaker_notes || "";
  useEffect(() => {
    if (xmlDocument.slides.length === 0) {
      if (activeSlideIndex !== 0) setActiveSlideIndex(0);
      return;
    }
    if (activeSlideIndex >= xmlDocument.slides.length) {
      setActiveSlideIndex(xmlDocument.slides.length - 1);
    }
  }, [activeSlideIndex, xmlDocument.slides.length]);

  const canvasFootprint: CSSProperties = {
    width: xmlDocument.width * zoom,
    height: xmlDocument.height * zoom,
    flexShrink: 0,
    transition: "width 140ms cubic-bezier(0.22, 1, 0.36, 1), height 140ms cubic-bezier(0.22, 1, 0.36, 1)",
  };

  if (!resolvedActiveSlide) {
    return (
      <TooltipProvider>
        <div className="flex h-screen w-screen items-center justify-center bg-background p-6 text-center text-muted-foreground">
          <div>
            <p className="text-sm font-semibold">No slides available</p>
            <p className="mt-1 text-xs">The presentation does not contain a valid slide.</p>
          </div>
        </div>
      </TooltipProvider>
    );
  }

  return (
    <TooltipProvider>
      <input
        ref={imageInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleImageFileChange}
        aria-label="Import image"
      />
      <style>{`
        .xml-pdf-print-deck {
          position: fixed;
          top: 0;
          left: -100000px;
          display: block;
          opacity: 0;
          pointer-events: none;
          width: ${PLAYWRIGHT_CAPTURE_WIDTH}px;
        }
        .xml-editor-shell select {
          color: hsl(var(--foreground));
          background-color: transparent;
        }
        .xml-editor-shell select option {
          color: hsl(var(--popover-foreground));
          background-color: hsl(var(--popover));
        }
        .dark .xml-editor-shell select { color-scheme: dark; }
        @keyframes xml-present-fade { from { opacity: 0; } to { opacity: 1; } }
        @keyframes xml-present-push-l { from { transform: translateX(-100%); } to { transform: translateX(0); } }
        @keyframes xml-present-push-r { from { transform: translateX(100%); } to { transform: translateX(0); } }
        @keyframes xml-present-push-u { from { transform: translateY(-100%); } to { transform: translateY(0); } }
        @keyframes xml-present-push-d { from { transform: translateY(100%); } to { transform: translateY(0); } }
        @keyframes xml-present-out-push-l { from { transform: translateX(0); } to { transform: translateX(100%); } }
        @keyframes xml-present-out-push-r { from { transform: translateX(0); } to { transform: translateX(-100%); } }
        @keyframes xml-present-out-push-u { from { transform: translateY(0); } to { transform: translateY(100%); } }
        @keyframes xml-present-out-push-d { from { transform: translateY(0); } to { transform: translateY(-100%); } }
        @keyframes xml-present-out-uncover-l { from { transform: translateX(0); } to { transform: translateX(-100%); } }
        @keyframes xml-present-out-uncover-r { from { transform: translateX(0); } to { transform: translateX(100%); } }
        @keyframes xml-present-out-uncover-u { from { transform: translateY(0); } to { transform: translateY(-100%); } }
        @keyframes xml-present-out-uncover-d { from { transform: translateY(0); } to { transform: translateY(100%); } }
        @keyframes xml-present-wipe-l { from { clip-path: inset(0 100% 0 0); } to { clip-path: inset(0); } }
        @keyframes xml-present-wipe-r { from { clip-path: inset(0 0 0 100%); } to { clip-path: inset(0); } }
        @keyframes xml-present-wipe-u { from { clip-path: inset(100% 0 0 0); } to { clip-path: inset(0); } }
        @keyframes xml-present-wipe-d { from { clip-path: inset(0 0 100% 0); } to { clip-path: inset(0); } }
        @keyframes xml-present-split-horizontal { from { clip-path: inset(0 50% 0 50%); } to { clip-path: inset(0); } }
        @keyframes xml-present-split-vertical { from { clip-path: inset(50% 0 50% 0); } to { clip-path: inset(0); } }
        @keyframes xml-present-zoom-in { from { opacity: 0; transform: scale(0.65); } to { opacity: 1; transform: scale(1); } }
        @keyframes xml-present-zoom-out { from { opacity: 0; transform: scale(1.35); } to { opacity: 1; transform: scale(1); } }
        @keyframes xml-present-circle { from { clip-path: circle(0% at 50% 50%); } to { clip-path: circle(75% at 50% 50%); } }
        @keyframes xml-present-diamond { from { clip-path: polygon(50% 50%, 50% 50%, 50% 50%, 50% 50%); } to { clip-path: polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%); } }
        @keyframes xml-present-plus { from { clip-path: polygon(45% 45%, 55% 45%, 55% 45%, 55% 55%, 55% 55%, 45% 55%, 45% 55%, 45% 45%); } to { clip-path: polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%); } }
        @media (prefers-reduced-motion: reduce) {
          .xml-present-transition { animation-duration: 1ms !important; }
        }
        @media print {
          @page { size: 13.333in 7.5in; margin: 0; }
          html, body {
            margin: 0 !important;
            background: #fff !important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
          }
          .xml-editor-shell { display: none !important; }
          .xml-export-loading { display: none !important; }
          .xml-pdf-print-deck {
            position: static;
            left: auto;
            opacity: 1;
            display: block !important;
            width: 100%;
          }
          .xml-pdf-print-page {
            position: relative;
            width: 13.333in;
            height: 7.5in;
            overflow: hidden;
            page-break-after: always;
          }
          .xml-pdf-print-page:last-child { page-break-after: auto; }
        }
      `}</style>
      <div className="xml-editor-shell flex h-screen w-screen flex-col overflow-hidden bg-background text-foreground">
        <div className="sticky top-0 z-50 flex h-14 items-center justify-between border-b bg-background/95 px-3 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-1.5">
            <Tip label="Back">
              <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" onClick={() => void handleExitEditor()}>
                <ArrowLeft className="h-4 w-4" />
              </Button>
            </Tip>
          <div className="flex min-w-0 items-center gap-2">
            <span className="max-w-[180px] truncate text-sm font-semibold text-foreground">Slide Editor</span>
            {saveStatus !== "idle" && (
              <span className={cn(
                "hidden text-[10px] sm:inline",
                saveStatus === "saving" && "text-muted-foreground",
                saveStatus === "saved" && "text-emerald-600",
                saveStatus === "error" && "text-destructive",
              )}>
                {saveStatus === "saving" ? "Saving…" : saveStatus === "saved" ? "Saved" : "Save failed"}
              </span>
            )}
          </div>
          </div>

          <div className="absolute left-1/2 flex -translate-x-1/2 items-center gap-0.5 rounded-xl border border-border/40 bg-muted/60 p-1">
            <Tip label="Select" shortcut="V">
              <Button variant={!selectedId ? "secondary" : "ghost"} size="sm" className="h-8 rounded-lg px-3 text-xs" onClick={() => setSelectedId(null)}>
                <MousePointer className="mr-1.5 h-3.5 w-3.5" /> Select
              </Button>
            </Tip>
            <Tip label="Add text" shortcut="T">
              <Button variant="ghost" size="sm" className="h-8 rounded-lg px-3 text-xs" onClick={() => addElement("textbox")}>
                <Type className="mr-1.5 h-3.5 w-3.5" /> Text
              </Button>
            </Tip>
            <Tip label="Add shape">
              <Button variant="ghost" size="sm" className="h-8 rounded-lg px-3 text-xs" onClick={() => addElement("shape")}>
                <Square className="mr-1.5 h-3.5 w-3.5" /> Shape
              </Button>
            </Tip>
            {selectedIds.length > 1 && (
              <Tip label={canUngroup ? "Ungroup" : "Group"} shortcut={canUngroup ? "Ctrl+Shift+G" : "Ctrl+G"}>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 rounded-lg px-3 text-xs"
                  onClick={canUngroup ? ungroupSelected : groupSelected}
                >
                  {canUngroup
                    ? <Ungroup className="mr-1.5 h-3.5 w-3.5" />
                    : <GroupIcon className="mr-1.5 h-3.5 w-3.5" />}
                  {canUngroup ? "Ungroup" : "Group"}
                </Button>
              </Tip>
            )}
            <Separator orientation="vertical" className="mx-0.5 h-5 opacity-30" />
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="secondary"
                  size="sm"
                  className="h-8 rounded-lg px-3 text-xs"
                  disabled={isExporting}
                  aria-busy={isExporting}
                >
                  {isExporting ? (
                    <Loader2 aria-hidden="true" className="mr-1.5 h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Download className="mr-1.5 h-3.5 w-3.5" />
                  )}
                  {isExportingPptx ? "Exporting…" : isExportingPdf ? "Preparing PDF…" : "Export"}
                  {!isExporting && <ChevronDown className="ml-1 h-3.5 w-3.5 opacity-70" />}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="center" className="w-52">
                <DropdownMenuItem onClick={downloadPowerPoint} disabled={isExportingPptx}>
                  <Download className="mr-2 h-4 w-4" />
                  {isExportingPptx ? "Exporting…" : "PowerPoint (.pptx)"}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={exportPdf}>
                  <Download className="mr-2 h-4 w-4" />
                  PDF / Save as PDF
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <Button size="sm" className="ml-0.5 h-8 rounded-lg px-3 text-xs" onClick={startPresent}>
              <Play className="mr-1.5 h-3.5 w-3.5" /> Present
            </Button>
          </div>

          <div className="flex items-center gap-1">
            <Tip label="Undo" shortcut="Ctrl+Z">
              <Button variant="ghost" size="icon" disabled={!canUndo} className="h-8 w-8 text-muted-foreground hover:text-foreground disabled:opacity-30" onClick={undo}>
                <Undo2 className="h-4 w-4" />
              </Button>
            </Tip>
            <Tip label="Redo" shortcut="Ctrl+Y">
              <Button variant="ghost" size="icon" disabled={!canRedo} className="h-8 w-8 text-muted-foreground hover:text-foreground disabled:opacity-30" onClick={redo}>
                <Redo2 className="h-4 w-4" />
              </Button>
            </Tip>
            <Separator orientation="vertical" className="mx-1 h-5 opacity-40" />
            <Tip label="Delete" shortcut="Del">
              <Button variant="ghost" size="icon" disabled={selectedIds.length === 0} className="h-8 w-8 text-destructive hover:text-destructive disabled:opacity-30" onClick={deleteSelected}>
                <Trash2 className="h-4 w-4" />
              </Button>
            </Tip>
          </div>
        </div>

        <div className="flex flex-1 overflow-hidden">
          <div className="relative flex shrink-0">
            <div className={cn("flex shrink-0 overflow-hidden border-r bg-background transition-[width] duration-300 ease-in-out", isSidebarOpen ? "w-56" : "w-12")}>
              <div className={cn("flex flex-col items-center gap-1 py-2 transition-opacity duration-200", isSidebarOpen ? "w-0 overflow-hidden opacity-0 pointer-events-none" : "w-12 opacity-100")}>
                {xmlDocument.slides.map((_, index) => (
                  <button
                    key={xmlDocument.slides[index].id}
                    onClick={() => {
                      setActiveSlideIndex(index);
                      setSelectedId(null);
                    }}
                    className={cn("relative h-5 w-8 shrink-0 overflow-hidden rounded border-2", activeSlideIndex === index ? "border-primary" : "border-transparent hover:border-border")}
                    title={`Slide ${index + 1}`}
                  >
                    <span className="text-[7px] font-bold text-muted-foreground">{index + 1}</span>
                  </button>
                ))}
                <button onClick={() => addSlide()} className="mt-0.5 flex h-5 w-8 items-center justify-center rounded border border-dashed border-border/50 hover:bg-muted/40">
                  <Plus className="h-2.5 w-2.5 text-muted-foreground" />
                </button>
              </div>

              <div className={cn("flex min-w-0 flex-1 flex-col transition-opacity duration-200", isSidebarOpen ? "opacity-100" : "opacity-0 pointer-events-none")}>
                <Tabs defaultValue="slides" className="flex h-full flex-1 flex-col">
                  <TabsList className="h-11 w-full justify-start gap-0 rounded-none border-b bg-transparent p-0">
                    <TabsTrigger value="slides" className="h-full flex-1 rounded-none text-xs data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:bg-transparent">
                      Slides
                    </TabsTrigger>
                    <TabsTrigger value="elements" className="h-full flex-1 rounded-none text-xs data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:bg-transparent">
                      Elements
                    </TabsTrigger>
                  </TabsList>
                  {(parseError || importMessage) && (
                    <div className={cn(
                      "border-b p-2 text-[11px]",
                      parseError
                        ? "border-red-900 bg-red-950/60 text-red-200"
                        : "border-emerald-900 bg-emerald-950/60 text-emerald-200",
                    )}>
                      {parseError || importMessage}
                    </div>
                  )}

                  <TabsContent value="slides" className="mt-0 flex-1 space-y-0 overflow-y-auto p-2 [&::-webkit-scrollbar]:hidden" style={{ scrollbarWidth: "none" }}>
                    {xmlDocument.slides.map((_, index) => (
                      <div
                        key={xmlDocument.slides[index].id}
                        className="group mb-2 flex gap-2"
                        draggable
                        onDragStart={() => {
                          dragSlideIndexRef.current = index;
                        }}
                        onDragOver={(event) => event.preventDefault()}
                        onDrop={() => {
                          if (dragSlideIndexRef.current !== null) reorderSlides(dragSlideIndexRef.current, index);
                          dragSlideIndexRef.current = null;
                        }}
                      >
                        <button
                          className={cn(
                            "mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-bold tabular-nums transition-colors",
                            activeSlideIndex === index ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground group-hover:bg-muted/80",
                          )}
                          onClick={() => {
                            setActiveSlideIndex(index);
                            setSelectedId(null);
                          }}
                        >
                          {index + 1}
                        </button>
                        <div className="flex min-w-0 flex-1 items-start gap-1">
                          <div className="relative min-w-0 flex-1">
                            <XmlSlideThumbnail
                              slide={xmlDocument.slides[index]}
                              canvasWidth={xmlDocument.width}
                              canvasHeight={xmlDocument.height}
                              slideWidthInches={Number(xmlDocument.presentationAttrs.slideWidthInches || 13.333)}
                              slideHeightInches={Number(xmlDocument.presentationAttrs.slideHeightInches || 7.5)}
                              slideIndex={index}
                              active={activeSlideIndex === index}
                              onClick={() => {
                                setActiveSlideIndex(index);
                                setSelectedId(null);
                              }}
                            />
                          </div>
                          <div className="flex w-6 shrink-0 flex-col gap-0.5 opacity-0 transition-opacity group-hover:opacity-100">
                            <Button
                              size="icon"
                              variant="ghost"
                              className="h-6 w-6 rounded"
                              onClick={(event) => {
                                event.stopPropagation();
                                duplicateSlide(index);
                              }}
                            >
                              <Copy className="h-2.5 w-2.5" />
                            </Button>
                            <Button
                              size="icon"
                              variant="ghost"
                              className="h-6 w-6 rounded text-destructive hover:text-destructive"
                              onClick={(event) => {
                                event.stopPropagation();
                                deleteSlide(index);
                              }}
                            >
                              <Trash2 className="h-2.5 w-2.5" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                    <Button variant="ghost" className="mt-1 h-9 w-full rounded-lg border border-dashed border-border/50 text-xs text-muted-foreground hover:border-border hover:text-foreground" onClick={() => addSlide()}>
                      <Plus className="mr-1.5 h-3.5 w-3.5" /> New slide
                    </Button>
                  </TabsContent>

                  <TabsContent value="elements" className="mt-0 flex-1 overflow-y-auto p-2.5 [&::-webkit-scrollbar]:hidden" style={{ scrollbarWidth: "none" }}>
                    <p className="mb-2 px-0.5 text-[10px] text-muted-foreground">Add elements to the current slide.</p>
                    <div className="grid grid-cols-3 gap-1.5">
                      {[
                        { kind: "textbox" as const, label: "Text", icon: Type },
                        { kind: "quote" as const, label: "Quote", icon: Quote },
                        { kind: "bullets" as const, label: "Bullets", icon: List },
                        { kind: "shape" as const, label: "Rectangle", icon: Square },
                        { kind: "rounded" as const, label: "Rounded", icon: Square },
                        { kind: "ellipse" as const, label: "Ellipse", icon: Circle },
                        { kind: "triangle" as const, label: "Triangle", icon: Triangle },
                        { kind: "diamond" as const, label: "Diamond", icon: Diamond },
                        { kind: "hexagon" as const, label: "Hexagon", icon: Hexagon },
                        { kind: "arrow" as const, label: "Arrow", icon: ArrowRight },
                        { kind: "chevron" as const, label: "Chevron", icon: ArrowRight },
                        { kind: "image" as const, label: "Image", icon: Image },
                        { kind: "line" as const, label: "Line", icon: Square },
                        { kind: "polygon" as const, label: "Polygon", icon: Layers },
                        { kind: "bar-chart" as const, label: "Bar chart", icon: BarChart3 },
                      ].map((item) => (
                        <button
                          key={item.kind}
                          className="flex flex-col items-center justify-center gap-1 rounded-lg border border-transparent p-2 text-muted-foreground transition-all hover:border-border hover:bg-muted/50 hover:text-foreground"
                          onClick={() => addElement(item.kind)}
                        >
                          <item.icon className="h-5 w-5" />
                          <span className="text-[9px] leading-tight">{item.label}</span>
                        </button>
                      ))}
                    </div>
                    <Separator className="my-4" />
                    <p className="mb-2 px-0.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Templates</p>
                    <div className="grid grid-cols-2 gap-2">
                      {[
                        { id: "blank", label: "Blank" },
                        { id: "title", label: "Title" },
                        { id: "content", label: "Content" },
                      ].map((template) => (
                        <button key={template.id} className="group text-left" onClick={() => addSlide(template.id as "blank" | "title" | "content")}>
                          <div className="aspect-video rounded-md border-2 border-transparent bg-muted/30 p-2 transition-all group-hover:border-primary/60">
                            <div className="h-full rounded bg-background">
                              {template.id === "title" && <div className="flex h-full flex-col items-center justify-center gap-2"><div className="h-2 w-3/4 rounded bg-foreground/20" /><div className="h-1.5 w-1/2 rounded bg-foreground/10" /></div>}
                              {template.id === "content" && <div className="flex h-full flex-col gap-1.5 p-2"><div className="h-2 w-2/3 rounded bg-foreground/20" /><div className="flex-1 rounded bg-foreground/10" /></div>}
                            </div>
                          </div>
                          <span className="block w-full truncate px-0.5 text-center text-[10px] text-muted-foreground group-hover:text-foreground">{template.label}</span>
                        </button>
                      ))}
                    </div>
                  </TabsContent>
                </Tabs>
              </div>
            </div>
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="absolute right-0 top-1/2 z-20 flex h-10 w-4 -translate-y-1/2 translate-x-full items-center justify-center rounded-r-md border border-l-0 bg-background shadow-sm transition-colors hover:bg-muted"
            >
              {isSidebarOpen ? <ChevronLeft className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
            </button>
          </div>

          <div
            ref={canvasShellRef}
            className="relative flex flex-1 items-center justify-center overflow-auto"
            style={{
              padding: PAD,
              backgroundColor: "hsl(var(--muted) / 0.35)",
              backgroundImage: "radial-gradient(circle, hsl(var(--foreground) / 0.08) 1px, transparent 1px)",
              backgroundSize: "20px 20px",
            }}
          >
            <ContextMenu>
              <ContextMenuTrigger asChild>
                <div style={canvasFootprint}>
                  <div
                    className="relative"
                    style={{
                      width: xmlDocument.width,
                      height: xmlDocument.height,
                      transform: `translateZ(0) scale(${zoom})`,
                      transformOrigin: "top left",
                      transition: "transform 140ms cubic-bezier(0.22, 1, 0.36, 1)",
                    }}
                  >
                    <div className="overflow-hidden rounded shadow-2xl ring-1 ring-black/10 dark:ring-white/5" style={{ width: xmlDocument.width, height: xmlDocument.height }}>
                      <XmlSlideCanvas
                        slide={resolvedActiveSlide}
                        canvasWidth={xmlDocument.width}
                        canvasHeight={xmlDocument.height}
                        slideWidthInches={Number(xmlDocument.presentationAttrs.slideWidthInches || 13.333)}
                        slideHeightInches={Number(xmlDocument.presentationAttrs.slideHeightInches || 7.5)}
                        selectedId={selectedId}
                        selectedIds={selectedIds}
                        viewport="bare"
                        onSelect={handleCanvasSelect}
                        onChange={updateElement}
                        onFormatText={formatTextSelection}
                        onTextSelectionChange={handleTextSelectionChange}
                        onCommit={() => applyDocument(documentRef.current, true)}
                      />
                    </div>
                  </div>
                </div>
              </ContextMenuTrigger>
              <ContextMenuContent className="w-56">
                <ContextMenuItem disabled={selectedElements.length === 0} onClick={copySelected}>
                  Copy <ContextMenuShortcut>Ctrl+C</ContextMenuShortcut>
                </ContextMenuItem>
                <ContextMenuItem onClick={pasteSelected}>
                  Paste <ContextMenuShortcut>Ctrl+V</ContextMenuShortcut>
                </ContextMenuItem>
                <ContextMenuItem disabled={selectedElements.length === 0} onClick={duplicateSelected}>
                  Duplicate <ContextMenuShortcut>Ctrl+D</ContextMenuShortcut>
                </ContextMenuItem>
                <ContextMenuSeparator />
                {canUngroup ? (
                  <ContextMenuItem onClick={ungroupSelected}>
                    Ungroup <ContextMenuShortcut>Ctrl+Shift+G</ContextMenuShortcut>
                  </ContextMenuItem>
                ) : (
                  <ContextMenuItem disabled={selectedIds.length < 2} onClick={groupSelected}>
                    Group <ContextMenuShortcut>Ctrl+G</ContextMenuShortcut>
                  </ContextMenuItem>
                )}
                <ContextMenuSeparator />
                <ContextMenuItem disabled={selectedElements.length === 0} onClick={() => moveLayer("up")}>
                  Bring Forward <ContextMenuShortcut>Ctrl+]</ContextMenuShortcut>
                </ContextMenuItem>
                <ContextMenuItem disabled={selectedElements.length === 0} onClick={() => moveLayer("down")}>
                  Send Backward <ContextMenuShortcut>Ctrl+[</ContextMenuShortcut>
                </ContextMenuItem>
                <ContextMenuSeparator />
                <ContextMenuItem disabled={selectedElements.length === 0} className="text-destructive focus:text-destructive" onClick={deleteSelected}>
                  Delete <ContextMenuShortcut>Del</ContextMenuShortcut>
                </ContextMenuItem>
              </ContextMenuContent>
            </ContextMenu>

            <div className="absolute bottom-5 right-5 z-50 flex items-center gap-1 rounded-xl border border-border/40 bg-background/90 p-1 shadow-lg backdrop-blur-md">
              <Button variant="ghost" size="icon" className="h-7 w-7 rounded-lg" onClick={() => setZoom((value) => clampZoom(value - ZOOM_STEP))}>
                <span className="select-none text-base font-semibold leading-none">-</span>
              </Button>
              <span className="w-11 text-center font-mono text-xs tabular-nums text-muted-foreground">{Math.round(zoom * 100)}%</span>
              <Button variant="ghost" size="icon" className="h-7 w-7 rounded-lg" onClick={() => setZoom((value) => clampZoom(value + ZOOM_STEP))}>
                <span className="select-none text-base font-semibold leading-none">+</span>
              </Button>
              <div className="mx-0.5 h-4 w-px bg-border/50" />
              <Button variant="ghost" size="icon" className="h-7 w-7 rounded-lg" onClick={fitZoom}>
                <Maximize2 className="h-3.5 w-3.5 text-muted-foreground" />
              </Button>
            </div>
          </div>

          <div className="relative flex shrink-0">
            <button
              onClick={() => setIsPropsPanelOpen((value) => !value)}
              className="absolute left-0 top-1/2 z-20 flex h-10 w-4 -translate-x-full -translate-y-1/2 items-center justify-center rounded-l-md border border-r-0 bg-background shadow-sm transition-colors hover:bg-muted"
            >
              {isPropsPanelOpen ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
            </button>
            <div className={cn("overflow-hidden transition-[width] duration-300 ease-in-out", isPropsPanelOpen ? "w-72" : "w-0")}>
              <aside className="flex h-full w-72 flex-col overflow-y-auto border-l bg-background [&::-webkit-scrollbar]:hidden" style={{ scrollbarWidth: "none" }}>
                {selectedIds.length > 1 ? (
                  <div className="flex h-full flex-col">
                    <div className="flex items-center justify-between border-b px-3 py-2.5">
                      <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
                        {selectedIds.length} elements selected
                      </span>
                      <div className="flex items-center gap-0.5">
                        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={duplicateSelected}>
                          <Copy className="h-3.5 w-3.5" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive hover:text-destructive" onClick={deleteSelected}>
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                    <div className="space-y-4 p-3">
                      <div className="rounded-xl border bg-muted/30 p-3">
                        <div className="mb-3 flex items-center gap-2">
                          {canUngroup ? <Ungroup className="h-4 w-4 text-primary" /> : <GroupIcon className="h-4 w-4 text-primary" />}
                          <div>
                            <p className="text-xs font-semibold">{canUngroup ? "Grouped elements" : "Multiple selection"}</p>
                            <p className="text-[10px] text-muted-foreground">
                              {canUngroup ? "Move and duplicate these elements together." : "Group them to keep their layout together."}
                            </p>
                          </div>
                        </div>
                        <Button className="h-8 w-full text-xs" onClick={canUngroup ? ungroupSelected : groupSelected}>
                          {canUngroup ? <Ungroup className="mr-1.5 h-3.5 w-3.5" /> : <GroupIcon className="mr-1.5 h-3.5 w-3.5" />}
                          {canUngroup ? "Ungroup" : "Group"}
                          <span className="ml-auto text-[10px] opacity-70">{canUngroup ? "Ctrl+Shift+G" : "Ctrl+G"}</span>
                        </Button>
                      </div>
                      <div>
                        <PanelLabel icon={Layers} label="Layer" />
                        <div className="grid grid-cols-2 gap-1.5">
                          <Button variant="outline" size="sm" className="h-8 text-xs" onClick={() => moveLayer("down")}>
                            <SendToBack className="mr-1.5 h-3.5 w-3.5" /> Backward
                          </Button>
                          <Button variant="outline" size="sm" className="h-8 text-xs" onClick={() => moveLayer("up")}>
                            <BringToFront className="mr-1.5 h-3.5 w-3.5" /> Forward
                          </Button>
                        </div>
                      </div>
                      <p className="text-[10px] leading-relaxed text-muted-foreground">
                        Hold Shift or Ctrl while clicking to add or remove elements from the selection.
                      </p>
                    </div>
                  </div>
                ) : !selected ? (
                  <div className="flex h-full flex-col overflow-y-auto p-3 [&::-webkit-scrollbar]:hidden" style={{ scrollbarWidth: "none" }}>
                    <div className="mb-3 rounded-xl border border-amber-500/25 bg-amber-500/5 p-3">
                      <PanelLabel icon={StickyNote} label="Speaker notes" />
                      <p className="mb-2 text-[10px] leading-relaxed text-muted-foreground">
                        Notes are only visible to you in Present mode and are not placed on the slide.
                      </p>
                      <Textarea
                        value={activeSlideNotes}
                        onChange={(event) => updateSlideNotes(event.target.value)}
                        placeholder="Add talking points for this slide…"
                        aria-label={`Speaker notes for slide ${activeSlideIndex + 1}`}
                        className="min-h-[128px] resize-y bg-background/70 text-xs leading-relaxed"
                      />
                      <div className="mt-1.5 flex items-center justify-between text-[10px] text-muted-foreground/70">
                        <span>Saved with this slide</span>
                        <span className="tabular-nums">{activeSlideNotes.length} characters</span>
                      </div>
                    </div>
                    <div className="rounded-xl border border-primary/20 bg-primary/5 p-3">
                      <PanelLabel icon={Sparkles} label="Slide transition" />
                      <p className="mb-2 text-[10px] leading-relaxed text-muted-foreground">
                        Applied when this slide appears in Present mode and in PowerPoint export.
                      </p>
                      <label className="mb-1.5 flex h-9 items-center gap-2 rounded-md border border-border/50 bg-background/70 px-2">
                        <span className="w-16 shrink-0 text-[10px] font-bold text-muted-foreground">Effect</span>
                        <select
                          value={activeTransition.type}
                          onChange={(event) => updateSlideTransition({
                            transition: event.target.value,
                            ...(event.target.value === "zoom"
                              ? { transition_direction: "in" }
                              : (["in", "out"].includes(activeTransition.direction) ? { transition_direction: "l" } : {})),
                          })}
                          className="min-w-0 flex-1 bg-transparent text-xs outline-none"
                        >
                          {XML_TRANSITION_OPTIONS.map((option) => (
                            <option key={option.value} value={option.value}>{option.label}</option>
                          ))}
                        </select>
                      </label>
                      {transitionNeedsDirection(activeTransition.type) && (
                        <label className="mb-1.5 flex h-9 items-center gap-2 rounded-md border border-border/50 bg-background/70 px-2">
                          <span className="w-16 shrink-0 text-[10px] font-bold text-muted-foreground">Direction</span>
                          <select
                            value={activeTransition.direction}
                            onChange={(event) => updateSlideTransition({ transition_direction: event.target.value })}
                            className="min-w-0 flex-1 bg-transparent text-xs outline-none"
                          >
                            {XML_TRANSITION_DIRECTIONS.filter((direction) => (activeTransition.type === "zoom"
                              ? ["in", "out"].includes(direction.value)
                              : ["l", "r", "u", "d"].includes(direction.value))).map((direction) => (
                              <option key={direction.value} value={direction.value}>{direction.label}</option>
                            ))}
                          </select>
                        </label>
                      )}
                      <div className="mb-2 rounded-md border border-border/50 bg-background/50 px-2 py-2">
                        <div className="mb-1 flex items-center justify-between text-[10px] text-muted-foreground">
                          <span className="flex items-center gap-1.5 font-bold"><Timer className="h-3 w-3" /> Duration</span>
                          <span className="tabular-nums">{activeTransition.duration} ms</span>
                        </div>
                        <Slider
                          min={120}
                          max={3000}
                          step={20}
                          value={[activeTransition.duration]}
                          onValueChange={(value) => updateSlideTransition({ transition_duration: String(value[0]) })}
                        />
                      </div>
                      <label className="mb-1.5 flex h-9 items-center gap-2 rounded-md border border-border/50 bg-background/70 px-2">
                        <span className="w-16 shrink-0 text-[10px] font-bold text-muted-foreground">Advance</span>
                        <select
                          value={activeTransition.advance}
                          onChange={(event) => updateSlideTransition({ transition_advance: event.target.value })}
                          className="min-w-0 flex-1 bg-transparent text-xs outline-none"
                        >
                          <option value="click">On click</option>
                          <option value="after">After delay</option>
                          <option value="both">Click or delay</option>
                        </select>
                      </label>
                      {(activeTransition.advance === "after" || activeTransition.advance === "both") && (
                        <IconField
                          label="Wait"
                          type="number"
                          min={500}
                          max={60000}
                          step={100}
                          value={String(activeTransition.delay)}
                          onChange={(value) => updateSlideTransition({ transition_delay: value })}
                        />
                      )}
                    </div>
                    <div className="mt-3 rounded-xl border bg-muted/20 p-3">
                      <PanelLabel icon={PaintBucket} label="Slide background" />
                      <Input type="color" value={resolvedActiveSlide.attrs.background || "#ffffff"} onChange={(event) => updateSlideBackground(event.target.value)} className="h-9 w-full p-1" />
                    </div>
                    <div className="mt-auto flex flex-col items-center justify-center gap-3 px-3 py-8 text-muted-foreground">
                      <div className="flex items-center justify-center rounded-2xl bg-muted/60 p-4">
                        <MousePointer className="h-6 w-6 opacity-30" />
                      </div>
                      <p className="text-center text-xs leading-relaxed text-muted-foreground/70">Select an element to edit its position, content, appearance, and layer order.</p>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex items-center justify-between border-b px-3 py-2.5">
                      <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">{elementLabel(selected)}</span>
                      <div className="flex items-center gap-0.5">
                        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => moveLayer("down")}>
                          <SendToBack className="h-3.5 w-3.5" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => moveLayer("up")}>
                          <BringToFront className="h-3.5 w-3.5" />
                        </Button>
                        <Separator orientation="vertical" className="mx-0.5 h-4" />
                        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={duplicateSelected}>
                          <Copy className="h-3.5 w-3.5" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive hover:text-destructive" onClick={deleteSelected}>
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>

                    <div className="space-y-4 overflow-y-auto p-3 [&::-webkit-scrollbar]:hidden" style={{ scrollbarWidth: "none" }}>
                      <div>
                        <PanelLabel icon={MousePointer} label="Transform" />
                        {selected.tag.toLowerCase() === "line" ? (
                          <div className="grid grid-cols-2 gap-1.5">
                            {["x1", "y1", "x2", "y2"].map((name) => (
                              <IconField key={name} label={name.toUpperCase()} type="number" value={selected.attrs[name] || ""} onChange={(value) => updateAttr(name, value)} />
                            ))}
                          </div>
                        ) : selected.tag.toLowerCase() === "polygon" ? (
                          <textarea value={selected.attrs.points || ""} onChange={(event) => updateAttr("points", event.target.value)} className="min-h-20 w-full rounded-md border bg-muted/30 p-2 font-mono text-xs outline-none" />
                        ) : (
                          <div className="grid grid-cols-2 gap-1.5">
                            {["x", "y", "width", "height"].map((name) => (
                              <IconField key={name} label={name.toUpperCase()[0]} type="number" value={selected.attrs[name] || ""} onChange={(value) => updateAttr(name, value)} />
                            ))}
                          </div>
                        )}
                        <div className="mt-2">
                          <SliderRow icon={RotateCw} value={toNumber(selected.attrs.rotation, 0)} min={-180} max={180} step={1} suffix="deg" onChange={(value) => updateAttr("rotation", String(value))} />
                        </div>
                        <div className="mt-1.5">
                          <IconField label="Rot" type="number" min={-180} max={180} value={selected.attrs.rotation || "0"} onChange={(value) => updateAttr("rotation", value)} />
                        </div>
                      </div>

                      <Separator />

                      {(selected.tag.toLowerCase() === "textbox" || selected.tag.toLowerCase() === "text") && (
                        <>
                          <div>
                            <PanelLabel icon={Type} label="Typography" />
                            {selectedTextRange && selectedTextSnippet && (
                              <div data-text-format-panel className="mb-2 rounded-xl border border-primary/30 bg-primary/5 p-2.5">
                                <div className="mb-2 flex items-center justify-between gap-2">
                                  <span className="text-[10px] font-bold uppercase tracking-wider text-primary">Selected text</span>
                                  <span className="max-w-[130px] truncate text-[10px] text-muted-foreground">“{selectedTextSnippet}”</span>
                                </div>
                                <div className="grid grid-cols-3 gap-1.5">
                                  <button
                                    type="button"
                                    className="flex h-10 items-center justify-center rounded-lg border bg-background text-base font-black transition-colors hover:bg-muted"
                                    title="Bold selected text"
                                    onMouseDown={(event) => event.preventDefault()}
                                    onClick={() => formatSelectedTextFromPanel({ bold: "toggle" })}
                                  >
                                    B
                                  </button>
                                  <button
                                    type="button"
                                    className="flex h-10 items-center justify-center rounded-lg border bg-background text-base font-serif italic transition-colors hover:bg-muted"
                                    title="Italic selected text"
                                    onMouseDown={(event) => event.preventDefault()}
                                    onClick={() => formatSelectedTextFromPanel({ italic: "toggle" })}
                                  >
                                    I
                                  </button>
                                  <button
                                    type="button"
                                    className="flex h-10 items-center justify-center rounded-lg border bg-background text-base font-serif underline transition-colors hover:bg-muted"
                                    title="Underline selected text"
                                    onMouseDown={(event) => event.preventDefault()}
                                    onClick={() => formatSelectedTextFromPanel({ underline: "toggle" })}
                                  >
                                    U
                                  </button>
                                  <label className="col-span-3 flex h-9 cursor-pointer items-center gap-2 rounded-lg border bg-background px-2 text-xs hover:bg-muted">
                                    <span className="font-semibold text-muted-foreground">Text color</span>
                                    <input
                                      type="color"
                                      aria-label="Selected text color"
                                      defaultValue="#ef4444"
                                      className="ml-auto h-6 w-10 cursor-pointer rounded border-0 bg-transparent p-0"
                                      onChange={(event) => formatSelectedTextFromPanel({ color: event.target.value })}
                                    />
                                  </label>
                                  <label className="col-span-3 flex h-9 cursor-pointer items-center gap-2 rounded-lg border bg-background px-2 text-xs hover:bg-muted">
                                    <span className="font-semibold text-muted-foreground">Highlight</span>
                                    <input
                                      type="color"
                                      aria-label="Selected text highlight"
                                      defaultValue="#fef08a"
                                      className="ml-auto h-6 w-10 cursor-pointer rounded border-0 bg-transparent p-0"
                                      onChange={(event) => formatSelectedTextFromPanel({ highlight: event.target.value })}
                                    />
                                  </label>
                                </div>
                                <p className="mt-2 text-[10px] leading-relaxed text-muted-foreground">Only the selected characters will change.</p>
                              </div>
                            )}
                            <textarea value={selected.text} onChange={(event) => updateElement(selected.id, { text: event.target.value }, true)} className="mb-2 min-h-24 w-full rounded-md border bg-muted/30 p-2 text-xs outline-none" />
                            {selectedMathFields.length > 0 && (
                              <div className="mb-2 space-y-1.5 rounded-md border border-primary/30 bg-primary/5 p-2">
                                <div className="text-[10px] font-bold uppercase tracking-wide text-primary">LaTeX formula</div>
                                {selectedMathFields.map(({ child, index }, formulaIndex) => (
                                  <textarea
                                    key={`${selected.id}-formula-${index}`}
                                    value={child.attrs.value || child.text}
                                    onChange={(event) => updateMathField(selected.id, index, event.target.value)}
                                    className="min-h-16 w-full rounded-md border bg-background p-2 font-mono text-xs outline-none"
                                    placeholder={formulaIndex === 0 ? "\\frac{a}{b}" : "LaTeX"}
                                  />
                                ))}
                                <p className="text-[10px] text-muted-foreground">Double-click công thức trên slide để sửa trực tiếp.</p>
                              </div>
                            )}
                            <div className="grid grid-cols-2 gap-1.5">
                              <label className="flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                                <span className="w-8 shrink-0 text-[10px] font-bold text-muted-foreground">Font</span>
                                <select
                                  value={TEXT_FONT_OPTIONS.includes(selected.attrs.font || "") ? selected.attrs.font : "Arial"}
                                  onChange={(event) => updateAttr("font", event.target.value)}
                                  className="min-w-0 flex-1 bg-transparent text-xs outline-none"
                                >
                                  {TEXT_FONT_OPTIONS.map((font) => <option key={font} value={font} style={{ fontFamily: font }}>{font}</option>)}
                                </select>
                              </label>
                              <IconField label="Size" type="number" value={selected.attrs.size || ""} onChange={(value) => updateAttr("size", value)} />
                              <IconField label="Color" type="color" value={selected.attrs.color || "#111827"} onChange={(value) => updateAttr("color", value)} />
                              <label className="flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                                <span className="w-8 shrink-0 text-[10px] font-bold text-muted-foreground">Align</span>
                                <select value={selected.attrs.align || "left"} onChange={(event) => updateAttr("align", event.target.value)} className="min-w-0 flex-1 bg-transparent text-xs outline-none">
                                  <option value="left">Left</option>
                                  <option value="center">Center</option>
                                  <option value="right">Right</option>
                                  <option value="justify">Justify</option>
                                </select>
                              </label>
                            </div>
                            <div className="mt-1.5 flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                              <span className="w-8 shrink-0 text-[10px] font-bold text-muted-foreground">Style</span>
                              <div className="flex h-6 flex-1 overflow-hidden rounded border border-border/50 bg-background/40">
                                <button
                                  type="button"
                                  className={cn("flex-1 text-xs font-bold transition-colors", selected.attrs.bold === "true" ? "bg-primary/20 text-primary" : "text-muted-foreground hover:bg-muted")}
                                  onClick={() => updateAttr("bold", String(selected.attrs.bold !== "true"))}
                                  title="Bold"
                                >
                                  B
                                </button>
                                <div className="w-px bg-border/50" />
                                <button
                                  type="button"
                                  className={cn("flex-1 text-xs italic transition-colors", selected.attrs.italic === "true" ? "bg-primary/20 text-primary" : "text-muted-foreground hover:bg-muted")}
                                  onClick={() => updateAttr("italic", String(selected.attrs.italic !== "true"))}
                                  title="Italic"
                                >
                                  I
                                </button>
                              </div>
                            </div>
                            <div className="mt-1.5 grid grid-cols-2 gap-1.5">
                              <IconField label="Line" type="number" step={0.1} value={selected.attrs.line_spacing || "1"} onChange={(value) => updateAttr("line_spacing", value)} />
                              <IconField label="Indent" type="number" value={selected.attrs.margin_left || "0"} onChange={(value) => updateAttr("margin_left", value)} />
                            </div>
                            <label className="mt-1.5 flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                              <span className="w-8 shrink-0 text-[10px] font-bold text-muted-foreground">Weight</span>
                              <select
                                value={selected.attrs.font_weight || (selected.attrs.bold === "true" ? "700" : "400")}
                                onChange={(event) => updateElement(selected.id, { attrs: { font_weight: event.target.value, bold: String(Number(event.target.value) >= 700) } }, true)}
                                className="min-w-0 flex-1 bg-transparent text-xs outline-none"
                              >
                                <option value="300">Light</option>
                                <option value="400">Regular</option>
                                <option value="500">Medium</option>
                                <option value="600">Semibold</option>
                                <option value="700">Bold</option>
                                <option value="900">Black</option>
                              </select>
                            </label>
                            <div className="mt-1.5 grid grid-cols-2 gap-1.5">
                              <label className="flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                                <span className="text-[10px] font-bold text-muted-foreground">V</span>
                                <select value={selected.attrs.vertical_align || "top"} onChange={(event) => updateAttr("vertical_align", event.target.value)} className="min-w-0 flex-1 bg-transparent text-xs outline-none">
                                  <option value="top">Top</option>
                                  <option value="middle">Middle</option>
                                  <option value="bottom">Bottom</option>
                                </select>
                              </label>
                              <label className="flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                                <span className="text-[10px] font-bold text-muted-foreground">O</span>
                                <select value={selected.attrs.overflow || "shrink"} onChange={(event) => updateAttr("overflow", event.target.value)} className="min-w-0 flex-1 bg-transparent text-xs outline-none">
                                  <option value="shrink">Shrink text</option>
                                  <option value="resize">Resize box</option>
                                  <option value="clip">Clip</option>
                                </select>
                              </label>
                            </div>
                          </div>
                          <Separator />
                        </>
                      )}

                      {selected.tag.toLowerCase() === "image" && (
                        <>
                          <div>
                            <PanelLabel icon={Image} label="Media" />
                            <Input value={selected.attrs.src || ""} onChange={(event) => updateAttr("src", event.target.value)} className="h-8 text-xs" />
                            <Button
                              type="button"
                              variant="outline"
                              className="mt-1.5 h-8 w-full text-xs"
                              onClick={() => openImagePicker(selected.id)}
                            >
                              <Upload className="mr-1.5 h-3.5 w-3.5" />
                              Import image from device
                            </Button>
                            <div className="mt-1.5 grid grid-cols-2 gap-1.5">
                              <IconField label="Alt" value={selected.attrs.alt || ""} onChange={(value) => updateAttr("alt", value)} />
                              <label className="flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                                <span className="text-[10px] font-bold text-muted-foreground">Fit</span>
                                <select value={selected.attrs.fit || "cover"} onChange={(event) => updateAttr("fit", event.target.value)} className="min-w-0 flex-1 bg-transparent text-xs outline-none">
                                  <option value="cover">Cover</option>
                                  <option value="contain">Contain</option>
                                  <option value="fill">Stretch</option>
                                </select>
                              </label>
                            </div>
                          </div>
                          <Separator />
                        </>
                      )}

                      {(["shape", "rect", "rectangle"].includes(selected.tag.toLowerCase())) && (
                        <>
                          <div>
                            <PanelLabel icon={Shapes} label="Shape" />
                            <div className="grid grid-cols-2 gap-1.5">
                              <label className="col-span-2 flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                                <span className="text-[10px] font-bold text-muted-foreground">Type</span>
                                <select value={selected.attrs.type || "rectangle"} onChange={(event) => updateAttr("type", event.target.value)} className="min-w-0 flex-1 bg-transparent text-xs outline-none">
                                  <option value="rectangle">Rectangle</option>
                                  <option value="rounded_rectangle">Rounded rectangle</option>
                                  <option value="ellipse">Ellipse</option>
                                  <option value="triangle">Triangle</option>
                                  <option value="diamond">Diamond</option>
                                  <option value="hexagon">Hexagon</option>
                                  <option value="right_arrow">Arrow</option>
                                  <option value="chevron">Chevron</option>
                                </select>
                              </label>
                              <IconField label="Radius" type="number" value={selected.attrs.radius || "0"} onChange={(value) => updateAttr("radius", value)} />
                              <IconField label="Stroke" type="number" value={selected.attrs.line_width || "1"} onChange={(value) => updateAttr("line_width", value)} />
                            </div>
                          </div>
                          <Separator />
                        </>
                      )}

                      {selected.tag.toLowerCase() === "line" && (
                        <>
                          <div>
                            <PanelLabel icon={Shapes} label="Line" />
                            <div className="grid grid-cols-2 gap-1.5">
                              <IconField label="Width" type="number" value={selected.attrs.width || "2"} onChange={(value) => updateAttr("width", value)} />
                              <IconField label="Color" type="color" value={selected.attrs.color || "#111827"} onChange={(value) => updateAttr("color", value)} />
                              <label className="col-span-2 flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                                <span className="text-[10px] font-bold text-muted-foreground">Style</span>
                                <select value={selected.attrs.dash || "solid"} onChange={(event) => updateAttr("dash", event.target.value)} className="min-w-0 flex-1 bg-transparent text-xs outline-none">
                                  <option value="solid">Solid</option>
                                  <option value="dashed">Dashed</option>
                                  <option value="dotted">Dotted</option>
                                </select>
                              </label>
                            </div>
                          </div>
                          <Separator />
                        </>
                      )}

                      {["barchart", "piechart", "linechart"].includes(selected.tag.toLowerCase()) && (
                        <>
                          <div>
                            <PanelLabel icon={BarChart3} label="Chart" />
                            <div className="grid grid-cols-2 gap-1.5">
                              <IconField label="Title" value={selected.attrs.title || ""} onChange={(value) => updateAttr("title", value)} />
                              <IconField label="Color" type="color" value={selected.attrs.color || "#3b82f6"} onChange={(value) => updateAttr("color", value)} />
                            </div>
                          </div>
                          <Separator />
                        </>
                      )}

                      <div>
                        <PanelLabel icon={PaintBucket} label="Appearance" />
                        <div className="grid grid-cols-2 gap-1.5">
                          <IconField label="Fill" type="color" value={(selected.attrs.fill && selected.attrs.fill !== "none" ? selected.attrs.fill : "#ffffff")} onChange={(value) => updateAttr("fill", value)} />
                          <IconField label="Stroke" type="color" value={(selected.attrs.line_color && selected.attrs.line_color !== "none" ? selected.attrs.line_color : selected.attrs.color || "#000000")} onChange={(value) => selected.tag.toLowerCase() === "line" ? updateAttr("color", value) : updateAttr("line_color", value)} />
                          <IconField
                            label="Line"
                            value={selected.tag.toLowerCase() === "line" ? selected.attrs.width || "" : selected.attrs.line_width || ""}
                            onChange={(value) => selected.tag.toLowerCase() === "line" ? updateAttr("width", value) : updateAttr("line_width", value)}
                          />
                          <IconField label="Opacity" type="number" step={0.1} min={0} max={1} value={selected.attrs.opacity ?? "1"} onChange={(value) => updateAttr("opacity", value)} />
                        </div>
                        <div className="mt-2">
                          <label className="mb-1 block text-[10px] text-muted-foreground">Slide background</label>
                          <Input type="color" value={resolvedActiveSlide.attrs.background || "#ffffff"} onChange={(event) => updateSlideBackground(event.target.value)} className="h-8 p-1" />
                        </div>
                      </div>

                      <Separator />

                      <div>
                        <PanelLabel icon={Layers} label="Layer" />
                        <div className="flex items-center gap-1.5">
                          <Button variant="outline" size="icon" className="h-8 w-8" onClick={() => moveLayer("down")}>
                            <ChevronDown className="h-4 w-4" />
                          </Button>
                          <div className="flex-1 rounded-md border bg-muted/30 px-2 py-1.5 text-center text-xs text-muted-foreground">
                            {resolvedActiveSlide.elements.findIndex((element) => element.id === selected.id) + 1} / {resolvedActiveSlide.elements.length}
                          </div>
                          <Button variant="outline" size="icon" className="h-8 w-8" onClick={() => moveLayer("up")}>
                            <ChevronUp className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </aside>
            </div>
          </div>
        </div>

        {isPresenting && (() => {
          const presentScale = Math.max(
            0.1,
            Math.min(
              presentViewport.width / xmlDocument.width,
              presentViewport.height / xmlDocument.height,
            ),
          );
          const presentSlideWidth = xmlDocument.width * presentScale;
          const presentSlideHeight = xmlDocument.height * presentScale;
          const slideCount = xmlDocument.slides.length;
          const progress = slideCount > 1 ? (activeSlideIndex / (slideCount - 1)) * 100 : 100;
          const outgoingSlide = presentTransition ? xmlDocument.slides[presentTransition.from] : null;
          const incomingTransition = presentTransition
            ? readXmlTransition(xmlDocument.slides[presentTransition.to]?.attrs || {})
            : null;
          const incomingAnimationName = incomingTransition
            ? transitionAnimationName(incomingTransition.type, incomingTransition.direction)
            : "none";
          const outgoingAnimationName = incomingTransition
            ? transitionOutgoingAnimationName(incomingTransition.type, incomingTransition.direction)
            : "none";
          const incomingAnimationStyle: CSSProperties = incomingTransition && incomingAnimationName !== "none"
            ? {
              animationName: incomingAnimationName,
              animationDuration: `${incomingTransition.duration}ms`,
              animationTimingFunction: "cubic-bezier(0.22, 1, 0.36, 1)",
              animationFillMode: "both",
              willChange: "transform, opacity, clip-path",
            }
            : {};
          const outgoingAnimationStyle: CSSProperties = incomingTransition && outgoingAnimationName !== "none"
            ? {
              animationName: outgoingAnimationName,
              animationDuration: `${incomingTransition.duration}ms`,
              animationTimingFunction: "cubic-bezier(0.22, 1, 0.36, 1)",
              animationFillMode: "both",
              willChange: "transform, opacity, clip-path",
            }
            : {};
          const outgoingZIndex = incomingTransition?.type === "uncover" ? 2 : 1;
          const incomingZIndex = incomingTransition?.type === "uncover" ? 1 : 2;

          const renderPresentSlide = (slide: XmlSlideDocument["slides"][number], key: string, style: CSSProperties = {}, animated = false) => (
            <div
              key={key}
              className="absolute left-0 top-0"
              style={{
                width: xmlDocument.width,
                height: xmlDocument.height,
                transform: `scale(${presentScale})`,
                transformOrigin: "top left",
                zIndex: style.zIndex,
              }}
            >
              <div
                className={cn("h-full w-full", animated && "xml-present-transition")}
                style={{ ...style, zIndex: undefined }}
              >
                <XmlSlideCanvas
                  slide={slide}
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
          );
          const presenterScale = Math.max(
            0.1,
            Math.min(
              (presentViewport.width * 0.62) / xmlDocument.width,
              (presentViewport.height * 0.7) / xmlDocument.height,
            ),
          );
          const presenterSlideWidth = xmlDocument.width * presenterScale;
          const presenterSlideHeight = xmlDocument.height * presenterScale;
          const presenterPreviewScale = Math.min(250 / xmlDocument.width, 160 / xmlDocument.height);
          const nextSlide = xmlDocument.slides[activeSlideIndex + 1];
          const renderPresenterCanvas = (slide: XmlSlideDocument["slides"][number], scale: number) => (
            <div
              style={{
                width: xmlDocument.width,
                height: xmlDocument.height,
                transform: `scale(${scale})`,
                transformOrigin: "top left",
              }}
            >
              <XmlSlideCanvas
                slide={slide}
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
          );

          return (
            <div
              ref={presentShellRef}
              className={cn(
                "fixed inset-0 z-[100] overflow-hidden bg-[#080b12] text-white",
                isPresentControlsVisible ? "cursor-default" : "cursor-none",
              )}
              onMouseMove={revealPresentControls}
              onMouseLeave={() => setIsPresentControlsVisible(false)}
              role="dialog"
              aria-label="Presentation mode"
            >
              <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_42%,rgba(55,65,81,0.32),transparent_58%)]" />
              <div className="pointer-events-none absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-black/60 to-transparent" />

              <div className={cn(
                "pointer-events-none absolute inset-x-0 top-0 z-30 flex items-center justify-between bg-gradient-to-b from-black/75 via-black/25 to-transparent px-6 py-5 transition-all duration-300",
                isPresentControlsVisible ? "translate-y-0 opacity-100" : "-translate-y-full opacity-0",
              )}>
                <div className="flex items-center gap-3">
                  <div>
                    <p className="text-sm font-semibold tracking-wide drop-shadow">{isPresenterView ? "Presenter View" : "Presentation"}</p>
                    <p className="text-[11px] text-white/60">Slide {activeSlideIndex + 1} of {slideCount}</p>
                  </div>
                </div>
                <div className="pointer-events-auto flex items-center gap-1.5">
                  <div className="flex h-9 items-center gap-1.5 rounded-lg bg-white/10 px-2.5 text-xs text-white/80" title="Presentation timer">
                    <Timer className="h-3.5 w-3.5 text-white/60" />
                    <span className="min-w-[42px] font-mono tabular-nums">{formatPresentTime(presentElapsedSeconds)}</span>
                    <button
                      type="button"
                      onClick={() => setIsPresentTimerRunning((running) => !running)}
                      className="rounded p-0.5 text-white/60 transition-colors hover:bg-white/10 hover:text-white"
                      aria-label={isPresentTimerRunning ? "Pause timer" : "Resume timer"}
                      title={isPresentTimerRunning ? "Pause timer" : "Resume timer"}
                    >
                      {isPresentTimerRunning ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
                    </button>
                    <button
                      type="button"
                      onClick={() => setPresentElapsedSeconds(0)}
                      className="rounded p-0.5 text-white/60 transition-colors hover:bg-white/10 hover:text-white"
                      aria-label="Reset timer"
                      title="Reset timer"
                    >
                      <RotateCcw className="h-3.5 w-3.5" />
                    </button>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setIsPresenterView((visible) => !visible);
                      setIsPresentNotesVisible(false);
                    }}
                    className={cn(
                      "flex h-9 items-center gap-2 rounded-lg px-3 text-xs transition-colors",
                      isPresenterView ? "bg-primary/25 text-white" : "text-white/70 hover:bg-white/10 hover:text-white",
                    )}
                    aria-pressed={isPresenterView}
                    title="Toggle Presenter View"
                  >
                    <LayoutDashboard className="h-4 w-4" />
                    <span className="hidden sm:inline">Presenter</span>
                  </button>
                  {!isPresenterView && (
                    <button
                      type="button"
                      onClick={() => setIsPresentNotesVisible((visible) => !visible)}
                      className={cn(
                        "flex h-9 items-center gap-2 rounded-lg px-3 text-xs transition-colors",
                        isPresentNotesVisible ? "bg-amber-400/20 text-amber-100" : "text-white/70 hover:bg-white/10 hover:text-white",
                      )}
                      aria-pressed={isPresentNotesVisible}
                      title="Show speaker notes"
                    >
                      <StickyNote className="h-4 w-4" />
                      <span className="hidden sm:inline">Notes</span>
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={togglePresentFullscreen}
                    className="flex h-9 items-center gap-2 rounded-lg px-3 text-xs text-white/70 transition-colors hover:bg-white/10 hover:text-white"
                    title={isPresentFullscreen ? "Exit fullscreen" : "Fullscreen"}
                  >
                    {isPresentFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                    <span className="hidden sm:inline">{isPresentFullscreen ? "Exit fullscreen" : "Fullscreen"}</span>
                  </button>
                  <button
                    type="button"
                    onClick={closePresent}
                    className="flex h-9 items-center gap-2 rounded-lg bg-white/10 px-3 text-xs font-medium text-white transition-colors hover:bg-white/20"
                  >
                    <X className="h-4 w-4" />
                    <span>Exit</span>
                  </button>
                </div>
              </div>

              {isPresentNotesVisible && !isPresenterView && (
                <aside
                  className="pointer-events-auto absolute right-5 top-20 z-40 flex w-[min(360px,calc(100vw-2.5rem))] flex-col overflow-hidden rounded-2xl border border-amber-200/20 bg-[#111722]/95 text-white shadow-2xl backdrop-blur-xl"
                  role="region"
                  aria-label={`Speaker notes for slide ${activeSlideIndex + 1}`}
                >
                  <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
                    <div className="flex items-center gap-2">
                      <StickyNote className="h-4 w-4 text-amber-200" />
                      <div>
                        <p className="text-xs font-semibold">Speaker notes</p>
                        <p className="text-[10px] text-white/45">Slide {activeSlideIndex + 1} of {slideCount}</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => setIsPresentNotesVisible(false)}
                      className="rounded-md p-1 text-white/45 transition-colors hover:bg-white/10 hover:text-white"
                      aria-label="Hide speaker notes"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="max-h-[min(70vh,520px)] overflow-y-auto whitespace-pre-wrap px-4 py-4 text-sm leading-relaxed text-white/85">
                    {activeSlideNotes || <span className="italic text-white/40">No notes for this slide.</span>}
                  </div>
                </aside>
              )}

              {isPresenterView ? (
                <main className="absolute inset-x-5 bottom-20 top-20 z-10 flex min-h-0 items-stretch justify-center">
                  <div className="grid h-full w-full min-h-0 grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(280px,360px)]">
                    <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-2xl border border-white/10 bg-[#111722]/85 shadow-2xl backdrop-blur-xl">
                      <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
                        <div>
                          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-white/80">Current slide</p>
                          <p className="mt-0.5 text-[10px] text-white/45">Slide {activeSlideIndex + 1} of {slideCount}</p>
                        </div>
                        <span className="rounded-md bg-white/10 px-2 py-1 font-mono text-xs tabular-nums text-white/70">
                          {formatPresentTime(presentElapsedSeconds)}
                        </span>
                      </div>
                      <div className="flex min-h-0 flex-1 items-center justify-center overflow-hidden p-4 sm:p-6">
                        <div
                          className="overflow-hidden rounded-[3px] bg-white shadow-[0_25px_80px_rgba(0,0,0,0.55),0_0_0_1px_rgba(255,255,255,0.12)]"
                          style={{ width: presenterSlideWidth, height: presenterSlideHeight }}
                        >
                          {renderPresenterCanvas(resolvedActiveSlide, presenterScale)}
                        </div>
                      </div>
                    </section>

                    <aside className="flex min-h-0 min-w-0 flex-col gap-4 overflow-y-auto pr-1">
                      <section className="flex min-h-[220px] flex-1 flex-col overflow-hidden rounded-2xl border border-amber-200/20 bg-[#111722]/95 shadow-2xl backdrop-blur-xl">
                        <div className="flex items-center gap-2 border-b border-white/10 px-4 py-3">
                          <StickyNote className="h-4 w-4 text-amber-200" />
                          <div>
                            <p className="text-xs font-semibold">Speaker notes</p>
                            <p className="text-[10px] text-white/45">Only visible in Presenter View</p>
                          </div>
                        </div>
                        <div className="flex-1 overflow-y-auto whitespace-pre-wrap px-4 py-4 text-sm leading-relaxed text-white/85">
                          {activeSlideNotes || <span className="italic text-white/40">No notes for this slide.</span>}
                        </div>
                      </section>

                      <section className="shrink-0 rounded-2xl border border-white/10 bg-[#111722]/85 p-3 shadow-2xl backdrop-blur-xl">
                        <div className="mb-2 flex items-center justify-between">
                          <div>
                            <p className="text-xs font-semibold text-white/80">Next slide</p>
                            <p className="text-[10px] text-white/45">
                              {nextSlide ? `Slide ${activeSlideIndex + 2}` : "End of presentation"}
                            </p>
                          </div>
                          {nextSlide && <ChevronRight className="h-4 w-4 text-white/35" />}
                        </div>
                        {nextSlide ? (
                          <button
                            type="button"
                            onClick={presentNext}
                            className="block w-full overflow-hidden rounded-lg bg-white text-left shadow-lg transition-transform hover:scale-[1.01]"
                            aria-label={`Go to slide ${activeSlideIndex + 2}`}
                          >
                            <div
                              className="relative overflow-hidden"
                              style={{
                                width: xmlDocument.width * presenterPreviewScale,
                                height: xmlDocument.height * presenterPreviewScale,
                                maxWidth: "100%",
                                aspectRatio: `${xmlDocument.width} / ${xmlDocument.height}`,
                              }}
                            >
                              {renderPresenterCanvas(nextSlide, presenterPreviewScale)}
                            </div>
                          </button>
                        ) : (
                          <div className="flex aspect-video items-center justify-center rounded-lg border border-dashed border-white/10 text-xs text-white/35">
                            You are on the last slide
                          </div>
                        )}
                      </section>
                    </aside>
                  </div>
                </main>
              ) : (
                <main className="absolute inset-0 z-10 flex h-full w-full items-center justify-center">
                <button
                  type="button"
                  aria-label="Previous slide"
                  disabled={activeSlideIndex === 0}
                  onClick={presentPrevious}
                  className={cn(
                    "group pointer-events-auto absolute left-5 top-1/2 z-20 flex h-12 w-12 -translate-y-1/2 items-center justify-center rounded-full border border-white/10 bg-black/20 text-white/60 shadow-lg backdrop-blur-md transition-all hover:scale-105 hover:bg-black/45 hover:text-white disabled:pointer-events-none disabled:opacity-0",
                    isPresentControlsVisible ? "opacity-100" : "pointer-events-none opacity-0",
                  )}
                >
                  <ChevronLeft className="h-6 w-6 transition-transform group-hover:-translate-x-0.5" />
                </button>

                <div
                  className="relative isolate overflow-hidden rounded-[3px] bg-white shadow-[0_25px_80px_rgba(0,0,0,0.55),0_0_0_1px_rgba(255,255,255,0.12)]"
                  style={{ width: presentSlideWidth, height: presentSlideHeight }}
                >
                  {outgoingSlide && presentTransition && renderPresentSlide(
                    outgoingSlide,
                    `present-out-${presentTransition.from}-${presentTransition.nonce}`,
                    { zIndex: outgoingZIndex, ...outgoingAnimationStyle },
                    outgoingAnimationName !== "none",
                  )}
                  {renderPresentSlide(
                    resolvedActiveSlide,
                    `present-in-${activeSlideIndex}-${presentTransition?.nonce || "steady"}`,
                    { zIndex: incomingZIndex, ...incomingAnimationStyle },
                    Boolean(incomingTransition && incomingAnimationName !== "none"),
                  )}
                </div>

                <button
                  type="button"
                  aria-label="Next slide"
                  disabled={activeSlideIndex >= slideCount - 1}
                  onClick={presentNext}
                  className={cn(
                    "group pointer-events-auto absolute right-5 top-1/2 z-20 flex h-12 w-12 -translate-y-1/2 items-center justify-center rounded-full border border-white/10 bg-black/20 text-white/60 shadow-lg backdrop-blur-md transition-all hover:scale-105 hover:bg-black/45 hover:text-white disabled:pointer-events-none disabled:opacity-0",
                    isPresentControlsVisible ? "opacity-100" : "pointer-events-none opacity-0",
                  )}
                >
                  <ChevronRight className="h-6 w-6 transition-transform group-hover:translate-x-0.5" />
                </button>
                </main>
              )}

              <div className={cn(
                "pointer-events-none absolute inset-x-0 bottom-0 z-30 flex justify-center bg-gradient-to-t from-black/75 via-black/20 to-transparent px-5 pb-5 pt-16 transition-all duration-300",
                isPresentControlsVisible ? "translate-y-0 opacity-100" : "translate-y-5 opacity-0",
              )}>
                <div className="pointer-events-auto flex w-full max-w-xl items-center gap-3 rounded-2xl border border-white/10 bg-[#111722]/85 px-3 py-2.5 shadow-2xl backdrop-blur-xl">
                  <button
                    type="button"
                    aria-label="Previous slide"
                    disabled={activeSlideIndex === 0}
                    onClick={presentPrevious}
                    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-white/60 transition-colors hover:bg-white/10 hover:text-white disabled:opacity-30"
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </button>
                  <div className="min-w-0 flex-1">
                    <div className="mb-1.5 flex items-center justify-between text-[10px] text-white/50">
                      <span>Slide {activeSlideIndex + 1}</span>
                      <span>{slideCount} total</span>
                    </div>
                    <div className="h-1 overflow-hidden rounded-full bg-white/10">
                      <div className="h-full rounded-full bg-white transition-[width] duration-300" style={{ width: `${progress}%` }} />
                    </div>
                  </div>
                  <button
                    type="button"
                    aria-label="Next slide"
                    disabled={activeSlideIndex >= slideCount - 1}
                    onClick={presentNext}
                    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-white/60 transition-colors hover:bg-white/10 hover:text-white disabled:opacity-30"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </button>
                  <div className="hidden h-5 w-px bg-white/10 sm:block" />
                  <span className="hidden whitespace-nowrap text-[10px] text-white/40 sm:block">Esc exit · ← → navigate · P presenter · N notes · T timer</span>
                </div>
              </div>
            </div>
          );
        })()}
      </div>
      {isExporting && (
        <div
          className="xml-export-loading fixed inset-0 z-[10000] flex items-center justify-center bg-slate-950/55 px-4 backdrop-blur-[2px]"
          role="status"
          aria-live="polite"
          aria-busy="true"
        >
          <div className="flex min-w-[250px] flex-col items-center rounded-2xl border border-white/15 bg-slate-900/95 px-8 py-7 text-center text-white shadow-2xl">
            <Loader2 aria-hidden="true" className="mb-4 h-12 w-12 animate-spin text-primary" />
            <p className="text-base font-semibold">
              {isExportingPptx ? "Exporting presentation…" : "Preparing PDF…"}
            </p>
            <p className="mt-1 text-sm text-white/60">Please wait</p>
          </div>
        </div>
      )}
      {isExportingPdf && (
        <div className="xml-pdf-print-deck">
          {xmlDocument.slides.map((slide, index) => {
            const scale = Math.min(
              (13.333 * 96) / xmlDocument.width,
              (7.5 * 96) / xmlDocument.height,
            );
            return (
              <div
                className="xml-pdf-print-page"
                data-xml-export-page="true"
                key={`print-${slide.id}-${index}`}
              >
                <div
                  style={{
                    width: xmlDocument.width,
                    height: xmlDocument.height,
                    transform: `scale(${scale})`,
                    transformOrigin: "top left",
                  }}
                >
                  <XmlSlideCanvas
                    slide={slide}
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
            );
          })}
        </div>
      )}
    </TooltipProvider>
  );
};

const PanelLabel = ({ icon: Icon, label }: { icon: React.ElementType; label: string }) => (
  <div className="mb-2 flex items-center gap-1.5">
    <Icon className="h-3 w-3 text-muted-foreground/70" />
    <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">{label}</span>
  </div>
);

const IconField = ({
  label,
  value,
  type = "text",
  step,
  min,
  max,
  onChange,
}: {
  label: string;
  value: string;
  type?: "text" | "color" | "number";
  step?: number;
  min?: number;
  max?: number;
  onChange: (value: string) => void;
}) => (
  <div className="flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
    <span className="w-8 shrink-0 text-[10px] font-bold text-muted-foreground">{label}</span>
    <input
      type={type}
      step={step}
      min={min}
      max={max}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className={cn("min-w-0 flex-1 bg-transparent text-xs outline-none", type === "color" && "h-5 cursor-pointer p-0")}
    />
  </div>
);

const SliderRow = ({
  icon: Icon,
  value,
  min,
  max,
  step,
  suffix,
  onChange,
}: {
  icon: React.ElementType;
  value: number;
  min: number;
  max: number;
  step: number;
  suffix: string;
  onChange: (value: number) => void;
}) => (
  <div className="flex items-center gap-2">
    <Icon className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
    <Slider min={min} max={max} step={step} value={[value]} onValueChange={(next) => onChange(next[0])} className="flex-1" />
    <span className="w-11 shrink-0 text-right text-[10px] tabular-nums text-muted-foreground">{value}{suffix}</span>
  </div>
);

export default XmlSlideEditor;
