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
  History,
  Image,
  LayoutDashboard,
  Layers,
  Lock,
  Unlock,
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
  Search,
  SendToBack,
  Shapes,
  Sparkles,
  StickyNote,
  MessageSquare,
  Share2,
  Square,
  Table2,
  Timer,
  Triangle,
  Quote,
  List,
  Trash2,
  Type,
  Upload,
  UserPlus,
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
import { api, type ImageSearchResult, type ProjectCollaborator, type ProjectComment, type ProjectVersion, type ProjectRole } from "@/lib/api";
import { useLanguage, type Language } from "@/contexts/LanguageContext";
import { useToast } from "@/hooks/use-toast";
import SlidegenConfirmDialog from "@/components/SlidegenConfirmDialog";
import SlidegenLogo from "@/components/SlidegenLogo";
import { XmlSlideCanvas } from "@/components/XmlSlideCanvas";
import "../features/slidegenius/slidegenius-editor.css";
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
  | "image" | "line" | "line-chart" | "pie-chart" | "table" | "polygon" | "bar-chart";

const EDITOR_LABELS_VI: Record<string, string> = {
  Back: "Quay lại",
  "Back to projects": "Quay lại danh sách dự án",
  Select: "Chọn",
  "Add text": "Thêm văn bản",
  "Add shape": "Thêm hình",
  Undo: "Hoàn tác",
  Redo: "Làm lại",
  Delete: "Xóa",
  Group: "Nhóm",
  Ungroup: "Bỏ nhóm",
  "Exporting…": "Đang xuất…",
  "Preparing PDF…": "Đang chuẩn bị PDF…",
  "PowerPoint (.pptx)": "PowerPoint (.pptx)",
  "PDF / Save as PDF": "PDF / Lưu thành PDF",
  Slides: "Trang chiếu",
  Elements: "Thành phần",
  Slide: "Trang chiếu",
  "New slide": "Trang chiếu mới",
  "Add elements to the current slide.": "Thêm thành phần vào trang chiếu hiện tại.",
  Templates: "Mẫu",
  Blank: "Trống",
  Title: "Tiêu đề",
  Content: "Nội dung",
  Text: "Văn bản",
  Quote: "Trích dẫn",
  Bullets: "Danh sách",
  Image: "Ảnh",
  Connector: "Đường nối",
  Rectangle: "Chữ nhật",
  Rounded: "Bo góc",
  Ellipse: "Elip",
  Triangle: "Tam giác",
  Diamond: "Hình thoi",
  Hexagon: "Lục giác",
  Chevron: "Mũi nhọn",
  "Bar chart": "Biểu đồ cột",
  "Line chart": "Biểu đồ đường",
  "Pie chart": "Biểu đồ tròn",
  Copy: "Sao chép",
  Paste: "Dán",
  Duplicate: "Nhân bản",
  "Bring Forward": "Đưa lên trước",
  "Send Backward": "Đưa ra sau",
  "elements selected": "thành phần được chọn",
  "Grouped elements": "Các thành phần đã nhóm",
  "Multiple selection": "Chọn nhiều",
  "Move and duplicate these elements together.": "Di chuyển và nhân bản các thành phần cùng nhau.",
  "Group them to keep their layout together.": "Nhóm để giữ nguyên bố cục.",
  "Hold Shift or Ctrl while clicking to add or remove elements from the selection.": "Giữ Shift hoặc Ctrl khi bấm để thêm hoặc bỏ thành phần khỏi vùng chọn.",
  "Notes are only visible to you in Present mode and are not placed on the slide.": "Ghi chú chỉ hiển thị trong chế độ trình chiếu và không nằm trên trang.",
  "Add talking points for this slide…": "Thêm ý chính cho trang chiếu…",
  "Saved with this slide": "Đã lưu cùng trang chiếu",
  characters: "ký tự",
  "Applied when this slide appears in Present mode and in PowerPoint export.": "Áp dụng khi trang xuất hiện trong chế độ trình chiếu và khi xuất PowerPoint.",
  "On click": "Khi bấm",
  "After delay": "Sau thời gian",
  "Click or delay": "Bấm hoặc hết giờ",
  "Select an element to edit its position, content, appearance, and layer order.": "Chọn một thành phần để sửa vị trí, nội dung, hiển thị và thứ tự lớp.",
  Transform: "Biến đổi",
  Typography: "Kiểu chữ",
  "Selected text": "Văn bản đã chọn",
  "Text color": "Màu chữ",
  Highlight: "Tô sáng",
  Font: "Phông chữ",
  Size: "Cỡ chữ",
  Color: "Màu",
  Align: "Căn lề",
  Left: "Trái",
  Center: "Giữa",
  Right: "Phải",
  Justify: "Đều",
  Style: "Kiểu",
  Line: "Giãn dòng",
  "Line width": "Độ dày đường",
  Indent: "Thụt lề",
  Weight: "Độ đậm",
  Light: "Mảnh",
  Regular: "Thường",
  Medium: "Vừa",
  Semibold: "Bán đậm",
  Bold: "Đậm",
  Black: "Đậm nhất",
  Top: "Trên",
  Middle: "Giữa",
  Bottom: "Dưới",
  "Shrink text": "Thu nhỏ chữ",
  "Resize box": "Đổi kích thước hộp",
  Clip: "Cắt",
  Media: "Phương tiện",
  "Import image from device": "Nhập ảnh từ thiết bị",
  "Search online": "Tìm ảnh online",
  "Search images": "Tìm kiếm ảnh",
  "Search image keywords": "Nhập từ khóa tìm ảnh...",
  "Searching...": "Đang tìm...",
  "No images found": "Không tìm thấy ảnh",
  "Choose an image to replace the selected one.": "Chọn ảnh để thay cho ảnh đang chọn.",
  Alt: "Mô tả",
  Fit: "Cách vừa ảnh",
  Cover: "Cắt vừa",
  Contain: "Chứa vừa",
  Stretch: "Kéo giãn",
  Shape: "Hình khối",
  Type: "Loại",
  Radius: "Bo góc",
  Stroke: "Viền",
  Width: "Độ dày",
  Start: "Đầu",
  End: "Cuối",
  None: "Không",
  Arrow: "Mũi tên",
  Table: "Bảng",
  Header: "Tiêu đề",
  Border: "Viền",
  Chart: "Biểu đồ",
  Data: "Dữ liệu",
  Appearance: "Hiển thị",
  Fill: "Màu nền",
  Opacity: "Độ trong suốt",
  Layer: "Lớp",
  "Speaker notes": "Ghi chú thuyết trình",
  "Slide transition": "Chuyển cảnh",
  Effect: "Hiệu ứng",
  Direction: "Hướng",
  Duration: "Thời lượng",
  Advance: "Chuyển trang",
  Wait: "Chờ",
  "Slide background": "Nền trang chiếu",
  "No slides available": "Không có trang chiếu",
  "The presentation does not contain a valid slide.": "Bản trình bày không có trang chiếu hợp lệ.",
  "Collapse slide sidebar": "Thu gọn thanh bên trang chiếu",
  "Expand slide sidebar": "Mở rộng thanh bên trang chiếu",
  "Collapse properties panel": "Thu gọn bảng thuộc tính",
  "Expand properties panel": "Mở rộng bảng thuộc tính",
  Backward: "Lùi một lớp",
  Forward: "Tiến một lớp",
  "Distribute X": "Phân bố ngang",
  "Distribute Y": "Phân bố dọc",
  "Only the selected characters will change.": "Chỉ các ký tự đã chọn sẽ thay đổi.",
  "LaTeX formula": "Công thức LaTeX",
  "Double-click the formula on the slide to edit it directly.": "Nhấp đúp công thức trên trang chiếu để sửa trực tiếp.",
  "Only visible in Presenter View": "Chỉ hiển thị trong chế độ Người trình bày",
  "Import image": "Nhập ảnh",
  "Rounded rectangle": "Hình chữ nhật bo góc",
  "Use ; between rows and | between columns.": "Dùng ; giữa các hàng và | giữa các cột.",
  "Comma-separated values": "Các giá trị, cách nhau bằng dấu phẩy",
  "Lock element": "Khóa thành phần",
  "Unlock element": "Mở khóa thành phần",
  "Send backward": "Đưa ra sau",
  "Bring forward": "Đưa lên trước",
  Solid: "Liền nét",
  Dashed: "Nét đứt",
  Dotted: "Nét chấm",
  "Table data": "Dữ liệu bảng",
  "Bold selected text": "Đậm văn bản đã chọn",
  "Italic selected text": "Nghiêng văn bản đã chọn",
  "Underline selected text": "Gạch chân văn bản đã chọn",
  "Selected text color": "Màu văn bản đã chọn",
  "Selected text highlight": "Màu đánh dấu văn bản đã chọn",
  "Presentation timer": "Đồng hồ trình chiếu",
  "Pause timer": "Tạm dừng đồng hồ",
  "Resume timer": "Tiếp tục đồng hồ",
  "Reset timer": "Đặt lại đồng hồ",
  "Toggle Presenter View": "Bật/tắt chế độ Người trình bày",
  Presenter: "Người trình bày",
  "Show speaker notes": "Hiện ghi chú thuyết trình",
  Notes: "Ghi chú",
  "Exit fullscreen": "Thoát toàn màn hình",
  Fullscreen: "Toàn màn hình",
  Exit: "Thoát",
  "Hide speaker notes": "Ẩn ghi chú thuyết trình",
  "No notes for this slide.": "Không có ghi chú cho trang chiếu này.",
  "Current slide": "Trang chiếu hiện tại",
  "Next slide": "Trang chiếu tiếp theo",
  "End of presentation": "Kết thúc bản trình bày",
  "You are on the last slide": "Bạn đang ở trang chiếu cuối",
  "Previous slide": "Trang chiếu trước",
  "Go to slide": "Đi tới trang chiếu",
  total: "tổng số",
  "Exporting presentation…": "Đang xuất bản trình bày…",
  "Please wait": "Vui lòng chờ",
  "Delete selected element": "Xóa thành phần đã chọn",
  "Presentation mode": "Chế độ trình chiếu",
  "Select slide": "Chọn trang chiếu",
  "Speaker notes for slide": "Ghi chú thuyết trình cho trang chiếu",
  Presentation: "Trình chiếu",
  "Presenter View": "Chế độ Người trình bày",
  of: "trên",
  Italic: "Nghiêng",
  Underline: "Gạch chân",
  History: "Lịch sử phiên bản",
  Share: "Chia sẻ",
  Comments: "Bình luận",
  Restore: "Khôi phục",
  "No versions yet": "Chưa có phiên bản nào",
  "Invite collaborator": "Mời thành viên",
  "Viewer": "Chỉ xem",
  "Editor": "Có thể chỉnh sửa",
  "Remove access": "Gỡ quyền truy cập",
  Close: "Đóng",
  "No collaborators yet": "Chưa có thành viên nào",
  "No comments yet": "Chưa có bình luận nào",
  "Add a comment": "Thêm bình luận",
  "Resolve comment": "Đánh dấu đã giải quyết",
  "Reopen comment": "Mở lại bình luận",
  "View only": "Chỉ xem",
};

const translateEditorLabel = (label: string, language: Language) =>
  language === "vi" ? EDITOR_LABELS_VI[label] || label : label;

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
}) => {
  const { language } = useLanguage();
  return (
    <Tooltip delayDuration={350}>
      <TooltipTrigger asChild>{children}</TooltipTrigger>
      <TooltipContent side={side} className="sg-editor-tooltip max-w-[180px] text-left">
        <p className="text-xs font-semibold">
          {translateEditorLabel(label, language)}
          {shortcut && <span className="ml-1.5 rounded bg-muted/40 px-1 py-0.5 text-[10px] font-normal opacity-60">{shortcut}</span>}
        </p>
      </TooltipContent>
    </Tooltip>
  );
};

const elementLabel = (element: XmlSlideElement) => {
  const tag = element.tag.toLowerCase();
  if (tag === "textbox" || tag === "text") return element.text.trim().slice(0, 32) || "Text";
  if (tag === "image") return "Image";
  if (tag === "line") return "Connector";
  if (tag === "polygon") return "Polygon";
  if (["barchart", "linechart", "piechart"].includes(tag)) return "Chart";
  if (tag === "table") return "Table";
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
        src: new URL("./placeholder.svg", document.baseURI).toString(),
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
        arrow_end: "true",
      },
    };
  }

  if (kind === "bar-chart" || kind === "line-chart" || kind === "pie-chart") {
    return {
      ...common,
      tag: kind === "bar-chart" ? "barchart" : kind === "line-chart" ? "linechart" : "piechart",
      attrs: {
        x: "260",
        y: "230",
        width: "620",
        height: "360",
        title: kind === "pie-chart" ? "Share" : "Chart title",
        color: "#3B82F6",
        data: "28,46,64,38,78",
      },
    };
  }

  if (kind === "table") {
    return {
      ...common,
      tag: "table",
      attrs: {
        x: "180",
        y: "220",
        width: "860",
        height: "360",
        data: "Metric|Q1|Q2|Change;Revenue|120|145|+21%;Users|2400|2800|+17%;Conversion|3.2%|4.1%|+0.9pp",
        header_fill: "#1E3A8A",
        header_color: "#FFFFFF",
        row_fill: "#FFFFFF",
        stripe_fill: "#EFF6FF",
        border_color: "#CBD5E1",
        font_size: "20",
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
  const { language } = useLanguage();
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
        aria-label={`${translateEditorLabel("Select slide", language)} ${slideIndex + 1}`}
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
  const { language } = useLanguage();
  const { toast } = useToast();
  const projectId = searchParams.get("project");
  const slideParam = searchParams.get("slide");
  const editorCopy = language === "vi"
    ? {
      loading: "Đang tải bản trình chiếu…",
      loadError: "Không thể tải bản trình chiếu",
      retry: "Thử lại",
      save: "Đã lưu",
      saving: "Đang lưu…",
      saveRetry: "Lưu thất bại — thử lại",
      addText: "Văn bản",
      addShape: "Hình khối",
      present: "Trình chiếu",
      export: "Xuất file",
    }
    : {
      loading: "Loading presentation…",
      loadError: "Could not load this presentation",
      retry: "Try again",
      save: "Saved",
      saving: "Saving…",
      saveRetry: "Save failed — retry",
      addText: "Text",
      addShape: "Shape",
      present: "Present",
      export: "Export",
    };
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
  const [isLoadingProject, setIsLoadingProject] = useState(Boolean(projectId));
  const [projectTitle, setProjectTitle] = useState("Slide Editor");
  const [accessRole, setAccessRole] = useState<ProjectRole>("owner");
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [loadAttempt, setLoadAttempt] = useState(0);
  const [historyVersion, setHistoryVersion] = useState(0);
  const [versions, setVersions] = useState<ProjectVersion[]>([]);
  const [pendingVersionRestore, setPendingVersionRestore] = useState<ProjectVersion | null>(null);
  const [pendingDraftRestore, setPendingDraftRestore] = useState<XmlSlideDocument | null>(null);
  const [collaborators, setCollaborators] = useState<ProjectCollaborator[]>([]);
  const [comments, setComments] = useState<ProjectComment[]>([]);
  const [activeOverlay, setActiveOverlay] = useState<"history" | "share" | "comments" | null>(null);
  const [versionLoading, setVersionLoading] = useState(false);
  const [collaborationLoading, setCollaborationLoading] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<"viewer" | "editor">("viewer");
  const [commentDraft, setCommentDraft] = useState("");
  const [commentLoading, setCommentLoading] = useState(false);
  const [collaborationError, setCollaborationError] = useState("");
  const [imageSearchQuery, setImageSearchQuery] = useState("");
  const [imageSearchResults, setImageSearchResults] = useState<ImageSearchResult[]>([]);
  const [imageSearchLoading, setImageSearchLoading] = useState(false);
  const [imageSearchError, setImageSearchError] = useState("");
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
  const dirtySlideIdsRef = useRef<Set<string>>(new Set());
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
  const editableSelectedElements = useMemo(
    () => selectedElements.filter((element) => element.attrs.locked !== "true"),
    [selectedElements],
  );
  const selectionGroupId = selectedElements.length > 0
    ? selectedElements[0].attrs[XML_GROUP_ATTR] || null
    : null;
  const canUngroup = Boolean(
    selectionGroupId
    && selectedElements.every((element) => element.attrs[XML_GROUP_ATTR] === selectionGroupId)
    && selectedElements.every((element) => element.attrs.locked !== "true"),
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
  const canEdit = accessRole !== "viewer";
  const sidebarLayout: SidebarLayout = isSidebarOpen
    ? isPropsPanelOpen ? "both-open" : "left-open"
    : isPropsPanelOpen ? "right-open" : "both-closed";

  const draftStorageKey = projectId ? `slidegen:draft:${projectId}` : null;

  const writeLocalDraft = useCallback((documentToSave: XmlSlideDocument) => {
    if (!draftStorageKey || !documentLoadedRef.current) return;
    try {
      const serialized = serializeXmlSlide(documentToSave);
      // localStorage is a recovery safety net, not the primary media store.
      // Avoid throwing/quota failures for very large image-heavy documents.
      if (serialized.length > 4_000_000) return;
      localStorage.setItem(draftStorageKey, JSON.stringify({
        updatedAt: Date.now(),
        xml: serialized,
      }));
    } catch (error) {
      console.warn("Could not persist local editor draft", error);
    }
  }, [draftStorageKey]);

  const clearLocalDraft = useCallback(() => {
    if (!draftStorageKey) return;
    try {
      localStorage.removeItem(draftStorageKey);
    } catch {
      // Storage may be disabled by the browser; server persistence still works.
    }
  }, [draftStorageKey]);

  const markDirtySlides = (previous: XmlSlideDocument, next: XmlSlideDocument) => {
    const previousIds = previous.slides.map((slide) => slide.id);
    const nextIds = next.slides.map((slide) => slide.id);
    const structureChanged = previousIds.length !== nextIds.length
      || previousIds.some((id, index) => id !== nextIds[index]);

    if (structureChanged) {
      next.slides.forEach((slide) => dirtySlideIdsRef.current.add(slide.id));
      return;
    }

    next.slides.forEach((slide, index) => {
      const previousSlide = previous.slides[index];
      if (!previousSlide || serializeXmlSlide({ ...next, slides: [slide] }) !== serializeXmlSlide({ ...previous, slides: [previousSlide] })) {
        dirtySlideIdsRef.current.add(slide.id);
      }
    });
  };

  const applyDocument = (next: XmlSlideDocument, recordHistory = false) => {
    if (recordHistory && !canEdit) return;
    if (recordHistory) {
      markDirtySlides(documentRef.current, next);
      // Canvas drag/resize updates the live document before the final commit,
      // so the previous and next references can be identical here. Mark the
      // active slide explicitly to ensure the committed gesture is persisted.
      const activeSlideAfterChange = next.slides[activeSlideIndex];
      if (activeSlideAfterChange) dirtySlideIdsRef.current.add(activeSlideAfterChange.id);
      setHasUnsavedChanges(true);
    }
    documentRef.current = next;
    setXmlDocument(next);
    if (recordHistory) {
      const history = historyRef.current;
      history.items = [...history.items.slice(0, history.index + 1), next].slice(-60);
      history.index = history.items.length - 1;
      setHistoryVersion((version) => version + 1);
    }
  };

  const resetDocument = useCallback((next: XmlSlideDocument) => {
    documentRef.current = next;
    setXmlDocument(next);
    historyRef.current = { items: [next], index: 0 };
    dirtySlideIdsRef.current.clear();
    setHasUnsavedChanges(false);
    setHistoryVersion((version) => version + 1);
    setActiveSlideIndex(0);
    setSelectedId(null);
  }, []);

  const restoreLocalDraft = useCallback(() => {
    const draft = pendingDraftRestore;
    setPendingDraftRestore(null);
    if (!draft) return;
    resetDocument(draft);
    draft.slides.forEach((slide) => dirtySlideIdsRef.current.add(slide.id));
    setHasUnsavedChanges(true);
  }, [pendingDraftRestore, resetDocument]);

  const dismissLocalDraft = useCallback(() => {
    setPendingDraftRestore(null);
    if (projectId) localStorage.removeItem(`slidegen:draft:${projectId}`);
  }, [projectId]);

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
      const dirtyIdsAtStart = new Set(dirtySlideIdsRef.current);
      const createdDuringSave: string[] = [];
      const slidesToPersist = dirtyIdsAtStart.size === 0
        ? documentToSave.slides
        : documentToSave.slides.filter((slide) => dirtyIdsAtStart.has(slide.id) || !previousSlideIds.has(slide.id));

      try {
        // Persist only changed/new slides. Structural operations mark the whole
        // deck dirty so slide indexes remain correct after reorder/delete.
        await Promise.all(slidesToPersist.map(async (slide) => {
          const index = documentToSave.slides.findIndex((item) => item.id === slide.id);
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
          createdDuringSave.push(String(createdId));
          persistedSlideIds.set(slide.id, String(createdId));
        }));

        // Carry forward IDs for unchanged slides; otherwise a partial save
        // would incorrectly delete valid database rows.
        previousSlideIds.forEach((databaseId, slideId) => {
          if (documentToSave.slides.some((slide) => slide.id === slideId) && !persistedSlideIds.has(slideId)) {
            persistedSlideIds.set(slideId, databaseId);
          }
        });

        const idsToKeep = new Set(persistedSlideIds.values());
        const staleIds = [...new Set(previousSlideIds.values())].filter((id) => !idsToKeep.has(id));
        await Promise.all(staleIds.map((slideId) => api.deleteSlide(slideId)));

        databaseSlideIdsRef.current = persistedSlideIds;
        await api.updateProject(projectId, { slide_count: documentToSave.slides.length });
        const versionSnapshot = {
          xml: serializedDocument,
          slides: documentToSave.slides.map((slide, index) => ({
            slide_index: index,
            slide_type: index === 0 ? "intro" : "content",
            title: `Slide ${index + 1}`,
            content_text: "",
            html_content: serializeXmlSlide({ ...documentToSave, slides: [slide] }),
            design_settings: { format: "xml" },
          })),
        };
        void api.createProjectVersion(projectId, { snapshot: versionSnapshot, label: language === "vi" ? "Tự động lưu" : "Autosave" })
          .then((version) => setVersions((current) => [version, ...current.filter((item) => item.id !== version.id)].slice(0, 50)))
          .catch((error) => console.warn("Could not create project version", error));
        lastSavedXmlRef.current = serializedDocument;
        dirtyIdsAtStart.forEach((slideId) => {
          const currentSlide = documentRef.current.slides.find((slide) => slide.id === slideId);
          const savedSlide = documentToSave.slides.find((slide) => slide.id === slideId);
          if (!currentSlide || !savedSlide || serializeXmlSlide({ ...documentRef.current, slides: [currentSlide] }) === serializeXmlSlide({ ...documentToSave, slides: [savedSlide] })) {
            dirtySlideIdsRef.current.delete(slideId);
          }
        });
        const stillDirty = dirtySlideIdsRef.current.size > 0;
        setHasUnsavedChanges(stillDirty);
        if (!stillDirty) clearLocalDraft();
        setSaveStatus("saved");
      } catch (error) {
        // Best-effort rollback of rows created by a failed multi-slide save.
        // Existing rows may still need a retry, but this prevents duplicate
        // slides on the next autosave attempt.
        await Promise.all(createdDuringSave.map((slideId) => api.deleteSlide(slideId).catch(() => undefined)));
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
  }, [clearLocalDraft, language, projectId]);

  useEffect(() => {
    if (!projectId) {
      setIsLoadingProject(false);
      return;
    }

    setIsLoadingProject(true);
    setParseError("");
    documentLoadedRef.current = false;
    if (saveTimerRef.current !== null) {
      window.clearTimeout(saveTimerRef.current);
      saveTimerRef.current = null;
    }

    let cancelled = false;
    Promise.all([
      api.getSlides(projectId),
      api.getProject(projectId).catch(() => null),
    ])
      .then(([response, project]) => {
        if (project) {
          setProjectTitle(String(project.title || project.name || "Slide Editor"));
          const projectRole = project.metadata?.access_role || project.access_role || "owner";
          setAccessRole(projectRole === "viewer" || projectRole === "editor" ? projectRole : "owner");
        }
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
        let documentToLoad = next;
        const draftKey = `slidegen:draft:${projectId}`;
        try {
          const rawDraft = localStorage.getItem(draftKey);
          if (rawDraft) {
            const draft = JSON.parse(rawDraft) as { updatedAt?: number; xml?: string };
            if (draft.xml && Number(draft.updatedAt) > 0) {
              const draftUpdatedAt = Number(draft.updatedAt);
              const serverUpdatedAt = project?.updated_at ? Date.parse(String(project.updated_at)) : 0;
              if (!serverUpdatedAt || draftUpdatedAt > serverUpdatedAt) {
                const draftDocument = parseXmlSlide(draft.xml);
                setPendingDraftRestore(draftDocument);
              } else {
                localStorage.removeItem(draftKey);
              }
            }
          }
        } catch (error) {
          console.warn("Could not inspect local editor draft", error);
        }
        lastSavedXmlRef.current = serializeXmlSlide(next);
        resetDocument(documentToLoad);
        if (documentToLoad !== next) {
          documentToLoad.slides.forEach((slide) => dirtySlideIdsRef.current.add(slide.id));
          setHasUnsavedChanges(true);
        }
        const requestedSlide = Number(slideParam);
        if (Number.isInteger(requestedSlide) && requestedSlide >= 0 && requestedSlide < documentToLoad.slides.length) {
          setActiveSlideIndex(requestedSlide);
        }
        setParseError("");
        setImportMessage("");
        if (canEdit) {
          const initialSnapshot = {
            xml: serializeXmlSlide(next),
            slides: next.slides.map((slide, index) => ({
              slide_index: index,
              slide_type: index === 0 ? "intro" : "content",
              title: `Slide ${index + 1}`,
              content_text: "",
              html_content: serializeXmlSlide({ ...next, slides: [slide] }),
              design_settings: { format: "xml" },
            })),
          };
          void api.getProjectVersions(projectId).then((existing) => {
            if (existing.versions.length > 0) return;
            return api.createProjectVersion(projectId, {
              snapshot: initialSnapshot,
              label: language === "vi" ? "Phiên bản ban đầu" : "Initial version",
            }).then((version) => setVersions((current) => [version, ...current]));
          }).catch((error) => console.warn("Could not create initial project version", error));
        }
        setIsLoadingProject(false);
      })
      .catch((error) => {
        if (cancelled) return;
        setParseError(error instanceof Error ? error.message : "Could not load project");
        setIsLoadingProject(false);
      });

    return () => {
      cancelled = true;
    };
  }, [canEdit, language, loadAttempt, projectId, resetDocument, slideParam]);

  useEffect(() => {
    if (!projectId) return;
    let cancelled = false;
    setCollaborationLoading(true);
    Promise.all([
      api.getProjectVersions(projectId),
      api.getProjectCollaborators(projectId),
      api.getProjectComments(projectId),
    ])
      .then(([versionResponse, collaboratorResponse, commentResponse]) => {
        if (cancelled) return;
        setVersions((current) => versionResponse.versions?.length ? versionResponse.versions : current);
        setCollaborators(collaboratorResponse.collaborators || []);
        setComments(commentResponse.comments || []);
      })
      .catch((error) => {
        if (!cancelled) setCollaborationError(error instanceof Error ? error.message : "Không thể tải dữ liệu cộng tác");
      })
      .finally(() => {
        if (!cancelled) setCollaborationLoading(false);
      });
    return () => { cancelled = true; };
  }, [projectId, loadAttempt]);

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

  useEffect(() => {
    if (!documentLoadedRef.current || !hasUnsavedChanges) return;
    writeLocalDraft(xmlDocument);
  }, [hasUnsavedChanges, writeLocalDraft, xmlDocument]);

  useEffect(() => {
    const persistDraftBeforeUnload = () => {
      if (documentLoadedRef.current && hasUnsavedChanges) writeLocalDraft(documentRef.current);
    };
    window.addEventListener("beforeunload", persistDraftBeforeUnload);
    window.addEventListener("pagehide", persistDraftBeforeUnload);
    return () => {
      window.removeEventListener("beforeunload", persistDraftBeforeUnload);
      window.removeEventListener("pagehide", persistDraftBeforeUnload);
    };
  }, [hasUnsavedChanges, writeLocalDraft]);

  const flushXmlSave = useCallback(async () => {
    if (saveTimerRef.current !== null) {
      window.clearTimeout(saveTimerRef.current);
      saveTimerRef.current = null;
    }
    if (documentLoadedRef.current) await saveXmlDocument(documentRef.current);
    if (saveInFlightRef.current) await saveInFlightRef.current;
  }, [saveXmlDocument]);

  const refreshCollaborationData = async () => {
    if (!projectId) return;
    const [versionResponse, collaboratorResponse, commentResponse] = await Promise.all([
      api.getProjectVersions(projectId),
      api.getProjectCollaborators(projectId),
      api.getProjectComments(projectId),
    ]);
    setVersions(versionResponse.versions || []);
    setCollaborators(collaboratorResponse.collaborators || []);
    setComments(commentResponse.comments || []);
  };

  const restoreVersion = (version: ProjectVersion) => {
    if (!projectId || !canEdit) return;
    setPendingVersionRestore(version);
  };

  const confirmRestoreVersion = async () => {
    const version = pendingVersionRestore;
    setPendingVersionRestore(null);
    if (!projectId || !canEdit || !version) return;
    setVersionLoading(true);
    setCollaborationError("");
    try {
      await flushXmlSave();
      await api.restoreProjectVersion(projectId, version.id);
      setActiveOverlay(null);
      setLoadAttempt((attempt) => attempt + 1);
    } catch (error) {
      setCollaborationError(error instanceof Error ? error.message : "Không thể khôi phục phiên bản");
    } finally {
      setVersionLoading(false);
    }
  };

  const inviteCollaborator = async () => {
    if (!projectId || accessRole !== "owner" || !inviteEmail.trim()) return;
    setCollaborationLoading(true);
    setCollaborationError("");
    try {
      await api.inviteProjectCollaborator(projectId, inviteEmail.trim(), inviteRole);
      setInviteEmail("");
      await refreshCollaborationData();
    } catch (error) {
      setCollaborationError(error instanceof Error ? error.message : "Không thể mời thành viên");
    } finally {
      setCollaborationLoading(false);
    }
  };

  const changeCollaboratorRole = async (member: ProjectCollaborator, role: "viewer" | "editor") => {
    if (!projectId || accessRole !== "owner") return;
    try {
      await api.updateProjectCollaborator(projectId, member.user_id, role);
      await refreshCollaborationData();
    } catch (error) {
      setCollaborationError(error instanceof Error ? error.message : "Không thể cập nhật quyền");
    }
  };

  const removeCollaborator = async (member: ProjectCollaborator) => {
    if (!projectId || accessRole !== "owner") return;
    try {
      await api.removeProjectCollaborator(projectId, member.user_id);
      await refreshCollaborationData();
    } catch (error) {
      setCollaborationError(error instanceof Error ? error.message : "Không thể gỡ quyền truy cập");
    }
  };

  const addComment = async () => {
    if (!projectId || !commentDraft.trim()) return;
    setCommentLoading(true);
    setCollaborationError("");
    try {
      const comment = await api.createProjectComment(projectId, {
        body: commentDraft.trim(),
        slide_index: activeSlideIndex,
        element_id: selectedId || undefined,
      });
      setComments((current) => [comment, ...current]);
      setCommentDraft("");
    } catch (error) {
      setCollaborationError(error instanceof Error ? error.message : "Không thể thêm bình luận");
    } finally {
      setCommentLoading(false);
    }
  };

  const toggleCommentResolved = async (comment: ProjectComment) => {
    if (!projectId || !canEdit) return;
    try {
      const updated = await api.updateProjectComment(projectId, comment.id, { resolved: !comment.resolved });
      setComments((current) => current.map((item) => item.id === updated.id ? updated : item));
    } catch (error) {
      setCollaborationError(error instanceof Error ? error.message : "Không thể cập nhật bình luận");
    }
  };

  const deleteComment = async (comment: ProjectComment) => {
    if (!projectId) return;
    try {
      await api.deleteProjectComment(projectId, comment.id);
      setComments((current) => current.filter((item) => item.id !== comment.id));
    } catch (error) {
      setCollaborationError(error instanceof Error ? error.message : "Không thể xóa bình luận");
    }
  };

  const handleExitEditor = async () => {
    try {
      await flushXmlSave();
      window.history.back();
    } catch (error) {
      toast({
        title: language === "vi" ? "Không thể lưu thay đổi" : "Could not save changes",
        description: error instanceof Error ? error.message : undefined,
        variant: "destructive",
      });
    }
  };

  const updateElement = (id: string, update: Parameters<typeof updateXmlElement>[2], recordHistory = false) => {
    const currentElement = documentRef.current.slides[activeSlideIndex]?.elements.find((element) => element.id === id);
    const isUnlockOnlyUpdate = Boolean(
      update.attrs
      && Object.keys(update).length === 1
      && Object.keys(update.attrs).every((name) => name === "locked"),
    );
    if (currentElement?.attrs.locked === "true" && !isUnlockOnlyUpdate) return;
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
    next.slides.forEach((slide) => dirtySlideIdsRef.current.add(slide.id));
    setHasUnsavedChanges(true);
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
    next.slides.forEach((slide) => dirtySlideIdsRef.current.add(slide.id));
    setHasUnsavedChanges(true);
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
    if (file.size > 5 * 1024 * 1024) {
      setImportMessage("Image is too large. Please choose a file smaller than 5 MB.");
      return;
    }

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

  const searchOnlineImages = async () => {
    const query = imageSearchQuery.trim();
    if (!canEdit || !query) return;
    setImageSearchLoading(true);
    setImageSearchError("");
    try {
      const response = await api.searchImages(query, { size: "Large", maxResults: 12 });
      setImageSearchResults(response.images || []);
      if (!response.images?.length) setImageSearchError(translateEditorLabel("No images found", language));
    } catch (error) {
      setImageSearchResults([]);
      setImageSearchError(error instanceof Error ? error.message : translateEditorLabel("No images found", language));
    } finally {
      setImageSearchLoading(false);
    }
  };

  const applySearchedImage = (url: string) => {
    if (!selected || selected.tag.toLowerCase() !== "image" || !canEdit) return;
    updateAttr("src", url);
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
    updateSlideElements(documentRef.current.slides[activeSlideIndex].elements.filter((element) => !selectedSet.has(element.id) || element.attrs.locked === "true"));
    setSelectedId(null);
  };

  const duplicateSelected = () => {
    if (editableSelectedElements.length === 0) return;
    const clones = cloneXmlElements(editableSelectedElements);
    updateSlideElements([...documentRef.current.slides[activeSlideIndex].elements, ...clones]);
    setSelectedIds(clones.map((clone) => clone.id));
  };

  const moveLayer = (direction: "up" | "down") => {
    const editableIds = editableSelectedElements.map((element) => element.id);
    if (editableIds.length === 0) return;
    updateSlideElements(moveXmlSelectionLayer(
      documentRef.current.slides[activeSlideIndex].elements,
      editableIds,
      direction,
    ));
  };

  const alignSelected = (alignment: "left" | "center" | "right" | "top" | "middle" | "bottom") => {
    if (editableSelectedElements.length < 2) return;
    const reference = editableSelectedElements[0];
    const referenceX = Number(reference.attrs.x || 0);
    const referenceY = Number(reference.attrs.y || 0);
    const referenceWidth = Number(reference.attrs.width || 0);
    const referenceHeight = Number(reference.attrs.height || 0);
    const nextElements = documentRef.current.slides[activeSlideIndex].elements.map((element) => {
      if (!editableSelectedElements.some((selectedElement) => selectedElement.id === element.id) || element.attrs.x === undefined || element.attrs.y === undefined) return element;
      const width = Number(element.attrs.width || 0);
      const height = Number(element.attrs.height || 0);
      const attrs = { ...element.attrs };
      if (alignment === "left") attrs.x = String(Math.round(referenceX));
      if (alignment === "center") attrs.x = String(Math.round(referenceX + (referenceWidth - width) / 2));
      if (alignment === "right") attrs.x = String(Math.round(referenceX + referenceWidth - width));
      if (alignment === "top") attrs.y = String(Math.round(referenceY));
      if (alignment === "middle") attrs.y = String(Math.round(referenceY + (referenceHeight - height) / 2));
      if (alignment === "bottom") attrs.y = String(Math.round(referenceY + referenceHeight - height));
      return { ...element, attrs };
    });
    updateSlideElements(nextElements);
  };

  const distributeSelected = (axis: "horizontal" | "vertical") => {
    if (editableSelectedElements.length < 3) return;
    const sorted = [...editableSelectedElements]
      .filter((element) => element.attrs.x !== undefined && element.attrs.y !== undefined)
      .sort((a, b) => Number(a.attrs[axis === "horizontal" ? "x" : "y"] || 0) - Number(b.attrs[axis === "horizontal" ? "x" : "y"] || 0));
    if (sorted.length < 3) return;
    const positionKey = axis === "horizontal" ? "x" : "y";
    const sizeKey = axis === "horizontal" ? "width" : "height";
    const firstPosition = Number(sorted[0].attrs[positionKey] || 0);
    const lastPosition = Number(sorted[sorted.length - 1].attrs[positionKey] || 0);
    const lastSize = Number(sorted[sorted.length - 1].attrs[sizeKey] || 0);
    const totalSize = sorted.reduce((sum, element) => sum + Number(element.attrs[sizeKey] || 0), 0);
    const gap = (lastPosition + lastSize - firstPosition - totalSize) / (sorted.length - 1);
    let cursor = firstPosition;
    const positions = new Map<string, number>();
    sorted.forEach((element) => {
      positions.set(element.id, cursor);
      cursor += Number(element.attrs[sizeKey] || 0) + gap;
    });
    updateSlideElements(documentRef.current.slides[activeSlideIndex].elements.map((element) => {
      const position = positions.get(element.id);
      if (position === undefined) return element;
      return { ...element, attrs: { ...element.attrs, [positionKey]: String(Math.round(position)) } };
    }));
  };

  const groupSelected = () => {
    const editableIds = editableSelectedElements.map((element) => element.id);
    if (editableIds.length < 2) return;
    updateSlideElements(groupXmlElements(
      documentRef.current.slides[activeSlideIndex].elements,
      editableIds,
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
      toast({
        title: language === "vi" ? "Xuất PowerPoint thất bại" : "PowerPoint export failed",
        description: error instanceof Error ? error.message : undefined,
        variant: "destructive",
      });
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
          toast({
            title: language === "vi" ? "Xuất PDF thất bại" : "PDF export failed",
            description: error instanceof Error ? error.message : undefined,
            variant: "destructive",
          });
        }
      } finally {
        if (!cancelled) setIsExportingPdf(false);
      }
    }, 100);

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [isExportingPdf, xmlDocument.height, xmlDocument.slides.length, xmlDocument.width, language, toast]);

  const fitZoom = useCallback(() => {
    const el = canvasShellRef.current;
    if (!el) return;
    const availW = el.clientWidth - PAD * 2;
    const availH = el.clientHeight - PAD * 2;
    const fit = Math.min(availW / xmlDocument.width, availH / xmlDocument.height);
    if (Number.isFinite(fit)) setZoom(clampZoom(Math.floor(fit * 100) / 100));
  }, [xmlDocument.height, xmlDocument.width]);

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
  }, [activeSlideIndex, fitZoom, sidebarLayout, xmlDocument.height, xmlDocument.width]);

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
      if (!typing && (event.key === "Delete" || event.key === "Backspace") && selectedIds.length > 0) {
        event.preventDefault();
        deleteSelected();
        return;
      }
      if (!typing && event.key.toLowerCase() === "v") {
        event.preventDefault();
        setSelectedId(null);
        return;
      }
      if (!typing && event.key.toLowerCase() === "t") {
        event.preventDefault();
        addElement("textbox");
        return;
      }
      const modifier = event.ctrlKey || event.metaKey;
      if (!modifier || typing) return;
      const key = event.key.toLowerCase();
      if (key === "s") {
        event.preventDefault();
        void flushXmlSave();
      } else if (key === "z" && !event.shiftKey) {
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

  if (isLoadingProject) {
    return (
      <TooltipProvider>
        <div className="sg-editor-shell flex h-screen w-screen items-center justify-center bg-background p-6 text-center text-muted-foreground">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="h-7 w-7 animate-spin text-primary" aria-hidden="true" />
            <p className="text-sm font-semibold">{editorCopy.loading}</p>
          </div>
        </div>
      </TooltipProvider>
    );
  }

  if (projectId && parseError) {
    return (
      <TooltipProvider>
        <div className="sg-editor-shell flex h-screen w-screen items-center justify-center bg-background p-6 text-center text-muted-foreground">
          <div className="max-w-md rounded-2xl border border-destructive/30 bg-destructive/5 p-6">
            <p className="text-sm font-semibold text-destructive">{editorCopy.loadError}</p>
            <p className="mt-2 text-xs leading-relaxed">{parseError}</p>
            <Button className="mt-4 h-8 text-xs" onClick={() => setLoadAttempt((attempt) => attempt + 1)}>
              {editorCopy.retry}
            </Button>
          </div>
        </div>
      </TooltipProvider>
    );
  }

  if (!resolvedActiveSlide) {
    return (
      <TooltipProvider>
        <div className="sg-editor-shell flex h-screen w-screen items-center justify-center bg-background p-6 text-center text-muted-foreground">
          <div>
            <p className="text-sm font-semibold">{translateEditorLabel("No slides available", language)}</p>
            <p className="mt-1 text-xs">{translateEditorLabel("The presentation does not contain a valid slide.", language)}</p>
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
        aria-label={translateEditorLabel("Import image", language)}
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
      <div className="xml-editor-shell sg-editor-shell flex h-screen w-screen flex-col overflow-hidden bg-background text-foreground">
        <div className="sg-editor-toolbar sticky top-0 z-50 flex h-14 items-center justify-between border-b bg-background/95 px-3 shadow-sm backdrop-blur-sm">
          <div className="flex items-center gap-2.5">
            <span className="sg-editor-brand" aria-label="Slidegen"><SlidegenLogo /></span>
            <span className="h-5 w-px bg-border/70" aria-hidden="true" />
            <Tip label="Back">
              <Button aria-label={translateEditorLabel("Back to projects", language)} variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" onClick={() => void handleExitEditor()}>
                <ArrowLeft className="h-4 w-4" />
              </Button>
            </Tip>
          <div className="flex min-w-0 items-center gap-2">
             <span className="max-w-[180px] truncate text-sm font-semibold text-foreground" title={projectTitle}>{projectTitle}</span>
             {!canEdit && <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-semibold text-muted-foreground">{translateEditorLabel("View only", language)}</span>}
            {saveStatus !== "idle" && (
              <button
                type="button"
                className={cn(
                  "hidden text-[10px] sm:inline",
                  saveStatus === "saving" && "text-muted-foreground",
                  saveStatus === "saved" && "text-emerald-600",
                  saveStatus === "error" && "text-destructive underline underline-offset-2",
                )}
                disabled={saveStatus === "saving" || !hasUnsavedChanges}
                onClick={() => void flushXmlSave()}
                title={saveStatus === "error" ? "Retry save" : undefined}
              >
                {saveStatus === "saving" ? editorCopy.saving : saveStatus === "saved" && !hasUnsavedChanges ? editorCopy.save : editorCopy.saveRetry}
              </button>
            )}
          </div>
          </div>

          <div className="absolute left-1/2 flex -translate-x-1/2 items-center gap-0.5 rounded-xl border border-border/40 bg-muted/60 p-1">
            <Tip label="Select" shortcut="V">
                <Button variant={!selectedId ? "secondary" : "ghost"} size="sm" className="h-8 rounded-lg px-3 text-xs" onClick={() => setSelectedId(null)}>
                <MousePointer className="mr-1.5 h-3.5 w-3.5" /> {translateEditorLabel("Select", language)}
              </Button>
            </Tip>
            <Tip label="Add text" shortcut="T">
              <Button variant="ghost" size="sm" className="h-8 rounded-lg px-3 text-xs" onClick={() => addElement("textbox")}>
                <Type className="mr-1.5 h-3.5 w-3.5" /> {editorCopy.addText}
              </Button>
            </Tip>
            <Tip label="Add shape">
              <Button variant="ghost" size="sm" className="h-8 rounded-lg px-3 text-xs" onClick={() => addElement("shape")}>
                <Square className="mr-1.5 h-3.5 w-3.5" /> {editorCopy.addShape}
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
                  {translateEditorLabel(canUngroup ? "Ungroup" : "Group", language)}
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
                  {isExportingPptx ? translateEditorLabel("Exporting…", language) : isExportingPdf ? translateEditorLabel("Preparing PDF…", language) : editorCopy.export}
                  {!isExporting && <ChevronDown className="ml-1 h-3.5 w-3.5 opacity-70" />}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="center" className="sg-editor-popover w-52">
                <DropdownMenuItem onClick={downloadPowerPoint} disabled={isExportingPptx}>
                  <Download className="mr-2 h-4 w-4" />
                  {isExportingPptx ? translateEditorLabel("Exporting…", language) : translateEditorLabel("PowerPoint (.pptx)", language)}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={exportPdf}>
                  <Download className="mr-2 h-4 w-4" />
                  {translateEditorLabel("PDF / Save as PDF", language)}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <Button size="sm" className="ml-0.5 h-8 rounded-lg px-3 text-xs" onClick={startPresent}>
              <Play className="mr-1.5 h-3.5 w-3.5" /> {editorCopy.present}
            </Button>
          </div>

          <div className="flex items-center gap-1">
            <Tip label="History">
              <Button aria-label={translateEditorLabel("History", language)} variant="ghost" size="icon" className="h-8 w-8" onClick={() => setActiveOverlay("history")}>
                <History className="h-4 w-4" />
              </Button>
            </Tip>
            <Tip label="Share">
              <Button aria-label={translateEditorLabel("Share", language)} variant="ghost" size="icon" className="h-8 w-8" onClick={() => setActiveOverlay("share")}>
                <Share2 className="h-4 w-4" />
              </Button>
            </Tip>
            <Tip label="Comments">
              <Button aria-label={translateEditorLabel("Comments", language)} variant="ghost" size="icon" className="relative h-8 w-8" onClick={() => setActiveOverlay("comments")}>
                <MessageSquare className="h-4 w-4" />
                {comments.filter((comment) => !comment.resolved).length > 0 && <span className="absolute -right-0.5 -top-0.5 min-w-3 rounded-full bg-primary px-0.5 text-[8px] leading-3 text-primary-foreground">{comments.filter((comment) => !comment.resolved).length}</span>}
              </Button>
            </Tip>
            <Separator orientation="vertical" className="mx-1 h-5 opacity-40" />
            <Tip label="Undo" shortcut="Ctrl+Z">
              <Button aria-label={translateEditorLabel("Undo", language)} variant="ghost" size="icon" disabled={!canUndo} className="h-8 w-8 text-muted-foreground hover:text-foreground disabled:opacity-30" onClick={undo}>
                <Undo2 className="h-4 w-4" />
              </Button>
            </Tip>
            <Tip label="Redo" shortcut="Ctrl+Y">
              <Button aria-label={translateEditorLabel("Redo", language)} variant="ghost" size="icon" disabled={!canRedo} className="h-8 w-8 text-muted-foreground hover:text-foreground disabled:opacity-30" onClick={redo}>
                <Redo2 className="h-4 w-4" />
              </Button>
            </Tip>
            <Separator orientation="vertical" className="mx-1 h-5 opacity-40" />
            <Tip label="Delete" shortcut="Del">
              <Button aria-label={translateEditorLabel("Delete selected element", language)} variant="ghost" size="icon" disabled={selectedIds.length === 0} className="h-8 w-8 text-destructive hover:text-destructive disabled:opacity-30" onClick={deleteSelected}>
                <Trash2 className="h-4 w-4" />
              </Button>
            </Tip>
          </div>
        </div>

        <div className="sg-editor-workspace flex flex-1 overflow-hidden">
          <div className="relative flex shrink-0">
            <div className={cn("sg-editor-sidebar flex shrink-0 overflow-hidden border-r bg-background transition-[width] duration-300 ease-in-out", isSidebarOpen ? "w-56" : "w-12")}>
              <div className={cn("flex flex-col items-center gap-1 py-2 transition-opacity duration-200", isSidebarOpen ? "w-0 overflow-hidden opacity-0 pointer-events-none" : "w-12 opacity-100")}>
                {xmlDocument.slides.map((_, index) => (
                  <button
                    key={xmlDocument.slides[index].id}
                    onClick={() => {
                      setActiveSlideIndex(index);
                      setSelectedId(null);
                    }}
                    className={cn("relative h-5 w-8 shrink-0 overflow-hidden rounded border-2", activeSlideIndex === index ? "border-primary" : "border-transparent hover:border-border")}
                    title={`${translateEditorLabel("Slide", language)} ${index + 1}`}
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
                       {translateEditorLabel("Slides", language)}
                     </TabsTrigger>
                     <TabsTrigger value="elements" className="h-full flex-1 rounded-none text-xs data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:bg-transparent">
                       {translateEditorLabel("Elements", language)}
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
                      <Plus className="mr-1.5 h-3.5 w-3.5" /> {translateEditorLabel("New slide", language)}
                    </Button>
                  </TabsContent>

                  <TabsContent value="elements" className="mt-0 flex-1 overflow-y-auto p-2.5 [&::-webkit-scrollbar]:hidden" style={{ scrollbarWidth: "none" }}>
                    <p className="mb-2 px-0.5 text-[10px] text-muted-foreground">{translateEditorLabel("Add elements to the current slide.", language)}</p>
                    <div className="grid grid-cols-3 gap-1.5">
                      {[
                        { kind: "textbox" as const, label: "Text", icon: Type },
                        { kind: "quote" as const, label: "Quote", icon: Quote },
                        { kind: "bullets" as const, label: "Bullets", icon: List },
                        { kind: "image" as const, label: "Image", icon: Image },
                        { kind: "table" as const, label: "Table", icon: Table2 },
                      ].map((item) => (
                        <button
                          key={item.kind}
                          type="button"
                          className="flex flex-col items-center justify-center gap-1 rounded-lg border border-transparent p-2 text-muted-foreground transition-all hover:border-border hover:bg-muted/50 hover:text-foreground"
                          onClick={() => addElement(item.kind)}
                        >
                          <item.icon className="h-5 w-5" />
                          <span className="text-[9px] leading-tight">{translateEditorLabel(item.label, language)}</span>
                        </button>
                      ))}
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <button type="button" className="flex flex-col items-center justify-center gap-1 rounded-lg border border-transparent p-2 text-muted-foreground transition-all hover:border-border hover:bg-muted/50 hover:text-foreground">
                            <Shapes className="h-5 w-5" />
                            <span className="text-[9px] leading-tight">{translateEditorLabel("Shape", language)}</span>
                          </button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="start" className="sg-editor-popover w-40">
                          {[
                            { kind: "shape" as const, label: "Rectangle" },
                            { kind: "rounded" as const, label: "Rounded" },
                            { kind: "ellipse" as const, label: "Ellipse" },
                            { kind: "triangle" as const, label: "Triangle" },
                            { kind: "diamond" as const, label: "Diamond" },
                            { kind: "hexagon" as const, label: "Hexagon" },
                            { kind: "arrow" as const, label: "Arrow" },
                            { kind: "chevron" as const, label: "Chevron" },
                          ].map((item) => (
                            <DropdownMenuItem key={item.kind} onSelect={() => addElement(item.kind)}>{translateEditorLabel(item.label, language)}</DropdownMenuItem>
                          ))}
                        </DropdownMenuContent>
                      </DropdownMenu>
                      <button type="button" className="flex flex-col items-center justify-center gap-1 rounded-lg border border-transparent p-2 text-muted-foreground transition-all hover:border-border hover:bg-muted/50 hover:text-foreground" onClick={() => addElement("line")}>
                        <ArrowRight className="h-5 w-5" />
                        <span className="text-[9px] leading-tight">{translateEditorLabel("Connector", language)}</span>
                      </button>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <button type="button" className="flex flex-col items-center justify-center gap-1 rounded-lg border border-transparent p-2 text-muted-foreground transition-all hover:border-border hover:bg-muted/50 hover:text-foreground">
                            <BarChart3 className="h-5 w-5" />
                            <span className="text-[9px] leading-tight">{translateEditorLabel("Chart", language)}</span>
                          </button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="start" className="sg-editor-popover w-40">
                          <DropdownMenuItem onSelect={() => addElement("bar-chart")}>{translateEditorLabel("Bar chart", language)}</DropdownMenuItem>
                          <DropdownMenuItem onSelect={() => addElement("line-chart")}>{translateEditorLabel("Line chart", language)}</DropdownMenuItem>
                          <DropdownMenuItem onSelect={() => addElement("pie-chart")}>{translateEditorLabel("Pie chart", language)}</DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                    <Separator className="my-4" />
                    <p className="mb-2 px-0.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">{translateEditorLabel("Templates", language)}</p>
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
                          <span className="block w-full truncate px-0.5 text-center text-[10px] text-muted-foreground group-hover:text-foreground">{translateEditorLabel(template.label, language)}</span>
                        </button>
                      ))}
                   </div>
                  </TabsContent>
                </Tabs>
              </div>
            </div>
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              aria-label={translateEditorLabel(isSidebarOpen ? "Collapse slide sidebar" : "Expand slide sidebar", language)}
              className="absolute right-0 top-1/2 z-20 flex h-10 w-4 -translate-y-1/2 translate-x-full items-center justify-center rounded-r-md border border-l-0 bg-background shadow-sm transition-colors hover:bg-muted"
            >
              {isSidebarOpen ? <ChevronLeft className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
            </button>
          </div>

          <div
            ref={canvasShellRef}
            className="sg-editor-canvas relative flex flex-1 items-center justify-center overflow-auto"
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
                        readOnly={!canEdit}
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
              <ContextMenuContent className="sg-editor-popover w-56">
                <ContextMenuItem disabled={selectedElements.length === 0} onClick={copySelected}>
                  {translateEditorLabel("Copy", language)} <ContextMenuShortcut>Ctrl+C</ContextMenuShortcut>
                </ContextMenuItem>
                <ContextMenuItem onClick={pasteSelected}>
                  {translateEditorLabel("Paste", language)} <ContextMenuShortcut>Ctrl+V</ContextMenuShortcut>
                </ContextMenuItem>
                <ContextMenuItem disabled={selectedElements.length === 0} onClick={duplicateSelected}>
                  {translateEditorLabel("Duplicate", language)} <ContextMenuShortcut>Ctrl+D</ContextMenuShortcut>
                </ContextMenuItem>
                <ContextMenuSeparator />
                {canUngroup ? (
                  <ContextMenuItem onClick={ungroupSelected}>
                    {translateEditorLabel("Ungroup", language)} <ContextMenuShortcut>Ctrl+Shift+G</ContextMenuShortcut>
                  </ContextMenuItem>
                ) : (
                  <ContextMenuItem disabled={selectedIds.length < 2} onClick={groupSelected}>
                    {translateEditorLabel("Group", language)} <ContextMenuShortcut>Ctrl+G</ContextMenuShortcut>
                  </ContextMenuItem>
                )}
                <ContextMenuSeparator />
                <ContextMenuItem disabled={selectedElements.length === 0} onClick={() => moveLayer("up")}>
                  {translateEditorLabel("Bring Forward", language)} <ContextMenuShortcut>Ctrl+]</ContextMenuShortcut>
                </ContextMenuItem>
                <ContextMenuItem disabled={selectedElements.length === 0} onClick={() => moveLayer("down")}>
                  {translateEditorLabel("Send Backward", language)} <ContextMenuShortcut>Ctrl+[</ContextMenuShortcut>
                </ContextMenuItem>
                <ContextMenuSeparator />
                <ContextMenuItem disabled={selectedElements.length === 0} className="text-destructive focus:text-destructive" onClick={deleteSelected}>
                  {translateEditorLabel("Delete", language)} <ContextMenuShortcut>Del</ContextMenuShortcut>
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
                  aria-label={translateEditorLabel(isPropsPanelOpen ? "Collapse properties panel" : "Expand properties panel", language)}
              className="absolute left-0 top-1/2 z-20 flex h-10 w-4 -translate-x-full -translate-y-1/2 items-center justify-center rounded-l-md border border-r-0 bg-background shadow-sm transition-colors hover:bg-muted"
            >
              {isPropsPanelOpen ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
            </button>
            <div className={cn("overflow-hidden transition-[width] duration-300 ease-in-out", isPropsPanelOpen ? "w-72" : "w-0")}>
              <aside className="sg-editor-properties flex h-full w-72 flex-col overflow-y-auto border-l bg-background [&::-webkit-scrollbar]:hidden" style={{ scrollbarWidth: "none" }}>
                {selectedIds.length > 1 ? (
                  <div className="flex h-full flex-col">
                    <div className="flex items-center justify-between border-b px-3 py-2.5">
                      <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
                        {selectedIds.length} {translateEditorLabel("elements selected", language)}
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
                            <p className="text-xs font-semibold">{translateEditorLabel(canUngroup ? "Grouped elements" : "Multiple selection", language)}</p>
                            <p className="text-[10px] text-muted-foreground">
                              {translateEditorLabel(canUngroup ? "Move and duplicate these elements together." : "Group them to keep their layout together.", language)}
                            </p>
                          </div>
                        </div>
                        <Button className="h-8 w-full text-xs" onClick={canUngroup ? ungroupSelected : groupSelected}>
                          {canUngroup ? <Ungroup className="mr-1.5 h-3.5 w-3.5" /> : <GroupIcon className="mr-1.5 h-3.5 w-3.5" />}
                          {translateEditorLabel(canUngroup ? "Ungroup" : "Group", language)}
                          <span className="ml-auto text-[10px] opacity-70">{canUngroup ? "Ctrl+Shift+G" : "Ctrl+G"}</span>
                        </Button>
                      </div>
                      <div>
                        <PanelLabel icon={Layers} label="Layer" />
                        <div className="grid grid-cols-2 gap-1.5">
                          <Button variant="outline" size="sm" className="h-8 text-xs" onClick={() => moveLayer("down")}>
                            <SendToBack className="mr-1.5 h-3.5 w-3.5" /> {translateEditorLabel("Backward", language)}
                          </Button>
                          <Button variant="outline" size="sm" className="h-8 text-xs" onClick={() => moveLayer("up")}>
                            <BringToFront className="mr-1.5 h-3.5 w-3.5" /> {translateEditorLabel("Forward", language)}
                          </Button>
                        </div>
                        <div className="mt-2 grid grid-cols-3 gap-1">
                          {(["left", "center", "right", "top", "middle", "bottom"] as const).map((alignment) => (
                            <Button key={alignment} variant="outline" size="sm" className="h-7 px-1 text-[10px]" onClick={() => alignSelected(alignment)}>
                              {translateEditorLabel(alignment === "left" ? "Left" : alignment === "center" ? "Center" : alignment === "right" ? "Right" : alignment === "top" ? "Top" : alignment === "middle" ? "Middle" : "Bottom", language)}
                            </Button>
                          ))}
                        </div>
                        {selectedElements.length >= 3 && (
                          <div className="mt-1 grid grid-cols-2 gap-1">
                            <Button variant="outline" size="sm" className="h-7 px-1 text-[10px]" onClick={() => distributeSelected("horizontal")}>{translateEditorLabel("Distribute X", language)}</Button>
                            <Button variant="outline" size="sm" className="h-7 px-1 text-[10px]" onClick={() => distributeSelected("vertical")}>{translateEditorLabel("Distribute Y", language)}</Button>
                          </div>
                        )}
                      </div>
                      <p className="text-[10px] leading-relaxed text-muted-foreground">
                        {translateEditorLabel("Hold Shift or Ctrl while clicking to add or remove elements from the selection.", language)}
                      </p>
                    </div>
                  </div>
                ) : !selected ? (
                  <div className="flex h-full flex-col overflow-y-auto p-3 [&::-webkit-scrollbar]:hidden" style={{ scrollbarWidth: "none" }}>
                    <div className="mb-3 rounded-xl border border-amber-500/25 bg-amber-500/5 p-3">
                      <PanelLabel icon={StickyNote} label="Speaker notes" />
                      <p className="mb-2 text-[10px] leading-relaxed text-muted-foreground">
                         {translateEditorLabel("Notes are only visible to you in Present mode and are not placed on the slide.", language)}
                      </p>
                      <Textarea
                        value={activeSlideNotes}
                        onChange={(event) => updateSlideNotes(event.target.value)}
                         placeholder={translateEditorLabel("Add talking points for this slide…", language)}
                         aria-label={`${translateEditorLabel("Speaker notes for slide", language)} ${activeSlideIndex + 1}`}
                        className="min-h-[128px] resize-y bg-background/70 text-xs leading-relaxed"
                      />
                      <div className="mt-1.5 flex items-center justify-between text-[10px] text-muted-foreground/70">
                         <span>{translateEditorLabel("Saved with this slide", language)}</span>
                         <span className="tabular-nums">{activeSlideNotes.length} {translateEditorLabel("characters", language)}</span>
                      </div>
                    </div>
                    <div className="rounded-xl border border-primary/20 bg-primary/5 p-3">
                      <PanelLabel icon={Sparkles} label="Slide transition" />
                      <p className="mb-2 text-[10px] leading-relaxed text-muted-foreground">
                         {translateEditorLabel("Applied when this slide appears in Present mode and in PowerPoint export.", language)}
                      </p>
                      <label className="mb-1.5 flex h-9 items-center gap-2 rounded-md border border-border/50 bg-background/70 px-2">
                         <span className="w-16 shrink-0 text-[10px] font-bold text-muted-foreground">{translateEditorLabel("Effect", language)}</span>
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
                               <option key={option.value} value={option.value}>{translateEditorLabel(option.label, language)}</option>
                          ))}
                        </select>
                      </label>
                      {transitionNeedsDirection(activeTransition.type) && (
                        <label className="mb-1.5 flex h-9 items-center gap-2 rounded-md border border-border/50 bg-background/70 px-2">
                           <span className="w-16 shrink-0 text-[10px] font-bold text-muted-foreground">{translateEditorLabel("Direction", language)}</span>
                          <select
                            value={activeTransition.direction}
                            onChange={(event) => updateSlideTransition({ transition_direction: event.target.value })}
                            className="min-w-0 flex-1 bg-transparent text-xs outline-none"
                          >
                            {XML_TRANSITION_DIRECTIONS.filter((direction) => (activeTransition.type === "zoom"
                              ? ["in", "out"].includes(direction.value)
                              : ["l", "r", "u", "d"].includes(direction.value))).map((direction) => (
                               <option key={direction.value} value={direction.value}>{translateEditorLabel(direction.label, language)}</option>
                            ))}
                          </select>
                        </label>
                      )}
                      <div className="mb-2 rounded-md border border-border/50 bg-background/50 px-2 py-2">
                        <div className="mb-1 flex items-center justify-between text-[10px] text-muted-foreground">
                           <span className="flex items-center gap-1.5 font-bold"><Timer className="h-3 w-3" /> {translateEditorLabel("Duration", language)}</span>
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
                         <span className="w-16 shrink-0 text-[10px] font-bold text-muted-foreground">{translateEditorLabel("Advance", language)}</span>
                        <select
                          value={activeTransition.advance}
                          onChange={(event) => updateSlideTransition({ transition_advance: event.target.value })}
                          className="min-w-0 flex-1 bg-transparent text-xs outline-none"
                        >
                           <option value="click">{translateEditorLabel("On click", language)}</option>
                           <option value="after">{translateEditorLabel("After delay", language)}</option>
                           <option value="both">{translateEditorLabel("Click or delay", language)}</option>
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
                      <p className="text-center text-xs leading-relaxed text-muted-foreground/70">{translateEditorLabel("Select an element to edit its position, content, appearance, and layer order.", language)}</p>
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
                                  <span className="text-[10px] font-bold uppercase tracking-wider text-primary">{translateEditorLabel("Selected text", language)}</span>
                                  <span className="max-w-[130px] truncate text-[10px] text-muted-foreground">“{selectedTextSnippet}”</span>
                                </div>
                                <div className="grid grid-cols-3 gap-1.5">
                                  <button
                                    type="button"
                                    className="flex h-10 items-center justify-center rounded-lg border bg-background text-base font-black transition-colors hover:bg-muted"
                                  title={translateEditorLabel("Bold selected text", language)}
                                    onMouseDown={(event) => event.preventDefault()}
                                    onClick={() => formatSelectedTextFromPanel({ bold: "toggle" })}
                                  >
                                    B
                                  </button>
                                  <button
                                    type="button"
                                    className="flex h-10 items-center justify-center rounded-lg border bg-background text-base font-serif italic transition-colors hover:bg-muted"
                                  title={translateEditorLabel("Italic selected text", language)}
                                    onMouseDown={(event) => event.preventDefault()}
                                    onClick={() => formatSelectedTextFromPanel({ italic: "toggle" })}
                                  >
                                    I
                                  </button>
                                  <button
                                    type="button"
                                    className="flex h-10 items-center justify-center rounded-lg border bg-background text-base font-serif underline transition-colors hover:bg-muted"
                                  title={translateEditorLabel("Underline selected text", language)}
                                    onMouseDown={(event) => event.preventDefault()}
                                    onClick={() => formatSelectedTextFromPanel({ underline: "toggle" })}
                                  >
                                    U
                                  </button>
                                  <label className="col-span-3 flex h-9 cursor-pointer items-center gap-2 rounded-lg border bg-background px-2 text-xs hover:bg-muted">
                                    <span className="font-semibold text-muted-foreground">{translateEditorLabel("Text color", language)}</span>
                                    <input
                                      type="color"
                                      aria-label={translateEditorLabel("Selected text color", language)}
                                      defaultValue="#ef4444"
                                      className="ml-auto h-6 w-10 cursor-pointer rounded border-0 bg-transparent p-0"
                                      onChange={(event) => formatSelectedTextFromPanel({ color: event.target.value })}
                                    />
                                  </label>
                                  <label className="col-span-3 flex h-9 cursor-pointer items-center gap-2 rounded-lg border bg-background px-2 text-xs hover:bg-muted">
                                    <span className="font-semibold text-muted-foreground">{translateEditorLabel("Highlight", language)}</span>
                                    <input
                                      type="color"
                                      aria-label={translateEditorLabel("Selected text highlight", language)}
                                      defaultValue="#fef08a"
                                      className="ml-auto h-6 w-10 cursor-pointer rounded border-0 bg-transparent p-0"
                                      onChange={(event) => formatSelectedTextFromPanel({ highlight: event.target.value })}
                                    />
                                  </label>
                                </div>
                                <p className="mt-2 text-[10px] leading-relaxed text-muted-foreground">{translateEditorLabel("Only the selected characters will change.", language)}</p>
                              </div>
                            )}
                            <textarea value={selected.text} onChange={(event) => updateElement(selected.id, { text: event.target.value }, true)} className="mb-2 min-h-24 w-full rounded-md border bg-muted/30 p-2 text-xs outline-none" />
                            {selectedMathFields.length > 0 && (
                              <div className="mb-2 space-y-1.5 rounded-md border border-primary/30 bg-primary/5 p-2">
                                <div className="text-[10px] font-bold uppercase tracking-wide text-primary">{translateEditorLabel("LaTeX formula", language)}</div>
                                {selectedMathFields.map(({ child, index }, formulaIndex) => (
                                  <textarea
                                    key={`${selected.id}-formula-${index}`}
                                    value={child.attrs.value || child.text}
                                    onChange={(event) => updateMathField(selected.id, index, event.target.value)}
                                    className="min-h-16 w-full rounded-md border bg-background p-2 font-mono text-xs outline-none"
                                    placeholder={formulaIndex === 0 ? "\\frac{a}{b}" : "LaTeX"}
                                  />
                                ))}
                                <p className="text-[10px] text-muted-foreground">{translateEditorLabel("Double-click the formula on the slide to edit it directly.", language)}</p>
                              </div>
                            )}
                            <div className="grid grid-cols-2 gap-1.5">
                              <label className="flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                                <span className="w-8 shrink-0 text-[10px] font-bold text-muted-foreground">{translateEditorLabel("Font", language)}</span>
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
                                <span className="w-8 shrink-0 text-[10px] font-bold text-muted-foreground">{translateEditorLabel("Align", language)}</span>
                                <select value={selected.attrs.align || "left"} onChange={(event) => updateAttr("align", event.target.value)} className="min-w-0 flex-1 bg-transparent text-xs outline-none">
                                  <option value="left">{translateEditorLabel("Left", language)}</option>
                                  <option value="center">{translateEditorLabel("Center", language)}</option>
                                  <option value="right">{translateEditorLabel("Right", language)}</option>
                                  <option value="justify">{translateEditorLabel("Justify", language)}</option>
                                </select>
                              </label>
                            </div>
                            <div className="mt-1.5 flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                              <span className="w-8 shrink-0 text-[10px] font-bold text-muted-foreground">{translateEditorLabel("Style", language)}</span>
                              <div className="flex h-6 flex-1 overflow-hidden rounded border border-border/50 bg-background/40">
                                <button
                                  type="button"
                                  className={cn("flex-1 text-xs font-bold transition-colors", selected.attrs.bold === "true" ? "bg-primary/20 text-primary" : "text-muted-foreground hover:bg-muted")}
                                  onClick={() => updateAttr("bold", String(selected.attrs.bold !== "true"))}
                                     title={translateEditorLabel("Bold", language)}
                                >
                                  B
                                </button>
                                <div className="w-px bg-border/50" />
                                <button
                                  type="button"
                                  className={cn("flex-1 text-xs italic transition-colors", selected.attrs.italic === "true" ? "bg-primary/20 text-primary" : "text-muted-foreground hover:bg-muted")}
                                  onClick={() => updateAttr("italic", String(selected.attrs.italic !== "true"))}
                                     title={translateEditorLabel("Italic", language)}
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
                              <span className="w-8 shrink-0 text-[10px] font-bold text-muted-foreground">{translateEditorLabel("Weight", language)}</span>
                              <select
                                value={selected.attrs.font_weight || (selected.attrs.bold === "true" ? "700" : "400")}
                                onChange={(event) => updateElement(selected.id, { attrs: { font_weight: event.target.value, bold: String(Number(event.target.value) >= 700) } }, true)}
                                className="min-w-0 flex-1 bg-transparent text-xs outline-none"
                              >
                                <option value="300">{translateEditorLabel("Light", language)}</option>
                                <option value="400">{translateEditorLabel("Regular", language)}</option>
                                <option value="500">{translateEditorLabel("Medium", language)}</option>
                                <option value="600">{translateEditorLabel("Semibold", language)}</option>
                                <option value="700">{translateEditorLabel("Bold", language)}</option>
                                <option value="900">{translateEditorLabel("Black", language)}</option>
                              </select>
                            </label>
                            <div className="mt-1.5 grid grid-cols-2 gap-1.5">
                              <label className="flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                                <span className="text-[10px] font-bold text-muted-foreground">V</span>
                                <select value={selected.attrs.vertical_align || "top"} onChange={(event) => updateAttr("vertical_align", event.target.value)} className="min-w-0 flex-1 bg-transparent text-xs outline-none">
                                  <option value="top">{translateEditorLabel("Top", language)}</option>
                                  <option value="middle">{translateEditorLabel("Middle", language)}</option>
                                  <option value="bottom">{translateEditorLabel("Bottom", language)}</option>
                                </select>
                              </label>
                              <label className="flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                                <span className="text-[10px] font-bold text-muted-foreground">O</span>
                                <select value={selected.attrs.overflow || "shrink"} onChange={(event) => updateAttr("overflow", event.target.value)} className="min-w-0 flex-1 bg-transparent text-xs outline-none">
                                  <option value="shrink">{translateEditorLabel("Shrink text", language)}</option>
                                  <option value="resize">{translateEditorLabel("Resize box", language)}</option>
                                  <option value="clip">{translateEditorLabel("Clip", language)}</option>
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
                              {translateEditorLabel("Import image from device", language)}
                            </Button>
                            <div className="mt-2 rounded-lg border border-border/50 bg-muted/20 p-2">
                              <div className="mb-1.5 flex items-center gap-1.5 text-[10px] font-semibold text-muted-foreground">
                                <Search className="h-3 w-3" />
                                {translateEditorLabel("Search online", language)}
                              </div>
                              <div className="flex gap-1.5">
                                <Input
                                  value={imageSearchQuery}
                                  onChange={(event) => setImageSearchQuery(event.target.value)}
                                  onKeyDown={(event) => {
                                    if (event.key === "Enter") {
                                      event.preventDefault();
                                      void searchOnlineImages();
                                    }
                                  }}
                                  placeholder={translateEditorLabel("Search image keywords", language)}
                                  className="h-8 min-w-0 text-xs"
                                  disabled={!canEdit || imageSearchLoading}
                                />
                                <Button
                                  type="button"
                                  size="icon"
                                  variant="outline"
                                  className="h-8 w-8 shrink-0"
                                  onClick={() => void searchOnlineImages()}
                                  disabled={!canEdit || !imageSearchQuery.trim() || imageSearchLoading}
                                  aria-label={translateEditorLabel("Search images", language)}
                                >
                                  <Search className="h-3.5 w-3.5" />
                                </Button>
                              </div>
                              {imageSearchLoading && <p className="mt-2 text-[10px] text-muted-foreground">{translateEditorLabel("Searching...", language)}</p>}
                              {imageSearchError && <p className="mt-2 text-[10px] text-destructive">{imageSearchError}</p>}
                              {imageSearchResults.length > 0 && (
                                <>
                                  <p className="mt-2 text-[10px] leading-relaxed text-muted-foreground">{translateEditorLabel("Choose an image to replace the selected one.", language)}</p>
                                  <div className="mt-1.5 grid grid-cols-3 gap-1.5">
                                    {imageSearchResults.map((result, index) => (
                                      <button
                                        key={`${result.url}-${index}`}
                                        type="button"
                                        className="group aspect-square overflow-hidden rounded border border-border/60 bg-background transition-colors hover:border-primary"
                                        onClick={() => applySearchedImage(result.url)}
                                        title={result.url}
                                      >
                                        <img
                                          src={result.url}
                                          alt={`${imageSearchQuery} ${index + 1}`}
                                          className="h-full w-full object-cover transition-transform group-hover:scale-105"
                                          loading="lazy"
                                          onError={(event) => {
                                            if (event.currentTarget.dataset.proxyAttempted === "true") return;
                                            event.currentTarget.dataset.proxyAttempted = "true";
                                            event.currentTarget.src = api.imageProxyUrl(result.url);
                                          }}
                                        />
                                      </button>
                                    ))}
                                  </div>
                                </>
                              )}
                            </div>
                            <div className="mt-1.5 grid grid-cols-2 gap-1.5">
                              <IconField label="Alt" value={selected.attrs.alt || ""} onChange={(value) => updateAttr("alt", value)} />
                              <label className="flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                                <span className="text-[10px] font-bold text-muted-foreground">{translateEditorLabel("Fit", language)}</span>
                                <select value={selected.attrs.fit || "cover"} onChange={(event) => updateAttr("fit", event.target.value)} className="min-w-0 flex-1 bg-transparent text-xs outline-none">
                                  <option value="cover">{translateEditorLabel("Cover", language)}</option>
                                  <option value="contain">{translateEditorLabel("Contain", language)}</option>
                                  <option value="fill">{translateEditorLabel("Stretch", language)}</option>
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
                                <span className="text-[10px] font-bold text-muted-foreground">{translateEditorLabel("Type", language)}</span>
                                <select value={selected.attrs.type || "rectangle"} onChange={(event) => updateAttr("type", event.target.value)} className="min-w-0 flex-1 bg-transparent text-xs outline-none">
                                  <option value="rectangle">{translateEditorLabel("Rectangle", language)}</option>
                                  <option value="rounded_rectangle">{translateEditorLabel("Rounded rectangle", language)}</option>
                                  <option value="ellipse">{translateEditorLabel("Ellipse", language)}</option>
                                  <option value="triangle">{translateEditorLabel("Triangle", language)}</option>
                                  <option value="diamond">{translateEditorLabel("Diamond", language)}</option>
                                  <option value="hexagon">{translateEditorLabel("Hexagon", language)}</option>
                                  <option value="right_arrow">{translateEditorLabel("Arrow", language)}</option>
                                  <option value="chevron">{translateEditorLabel("Chevron", language)}</option>
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
                               <PanelLabel icon={Shapes} label="Connector" />
                            <div className="grid grid-cols-2 gap-1.5">
                              <IconField label="Width" type="number" value={selected.attrs.width || "2"} onChange={(value) => updateAttr("width", value)} />
                              <IconField label="Color" type="color" value={selected.attrs.color || "#111827"} onChange={(value) => updateAttr("color", value)} />
                              <label className="col-span-2 flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                                 <span className="text-[10px] font-bold text-muted-foreground">{translateEditorLabel("Style", language)}</span>
                                <select value={selected.attrs.dash || "solid"} onChange={(event) => updateAttr("dash", event.target.value)} className="min-w-0 flex-1 bg-transparent text-xs outline-none">
                                   <option value="solid">{translateEditorLabel("Solid", language)}</option>
                                   <option value="dashed">{translateEditorLabel("Dashed", language)}</option>
                                   <option value="dotted">{translateEditorLabel("Dotted", language)}</option>
                                </select>
                              </label>
                              <label className="flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                                <span className="text-[10px] font-bold text-muted-foreground">{translateEditorLabel("Start", language)}</span>
                                <select value={selected.attrs.arrow_start === "true" ? "arrow" : "none"} onChange={(event) => updateAttr("arrow_start", String(event.target.value === "arrow"))} className="min-w-0 flex-1 bg-transparent text-xs outline-none">
                                   <option value="none">{translateEditorLabel("None", language)}</option>
                                   <option value="arrow">{translateEditorLabel("Arrow", language)}</option>
                                </select>
                              </label>
                              <label className="flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
                                <span className="text-[10px] font-bold text-muted-foreground">{translateEditorLabel("End", language)}</span>
                                <select value={selected.attrs.arrow_end === "true" ? "arrow" : "none"} onChange={(event) => updateAttr("arrow_end", String(event.target.value === "arrow"))} className="min-w-0 flex-1 bg-transparent text-xs outline-none">
                                   <option value="none">{translateEditorLabel("None", language)}</option>
                                   <option value="arrow">{translateEditorLabel("Arrow", language)}</option>
                                </select>
                              </label>
                            </div>
                          </div>
                          <Separator />
                        </>
                      )}

                      {selected.tag.toLowerCase() === "table" && (
                        <>
                          <div>
                            <PanelLabel icon={Table2} label="Table" />
                            <Textarea
                              value={selected.attrs.data || "Metric|Value;Revenue|120;Users|2400"}
                              onChange={(event) => updateAttr("data", event.target.value)}
                              className="min-h-[120px] resize-y bg-muted/30 font-mono text-[11px]"
                               aria-label={translateEditorLabel("Table data", language)}
                               placeholder={language === "vi" ? "Tiêu đề 1|Tiêu đề 2;Hàng 1|Giá trị" : "Header 1|Header 2;Row 1|Value"}
                            />
                             <p className="mt-1 text-[10px] leading-relaxed text-muted-foreground">{translateEditorLabel("Use ; between rows and | between columns.", language)}</p>
                            <div className="mt-2 grid grid-cols-2 gap-1.5">
                              <IconField label="Header" type="color" value={selected.attrs.header_fill || "#1E3A8A"} onChange={(value) => updateAttr("header_fill", value)} />
                              <IconField label="Border" type="color" value={selected.attrs.border_color || "#CBD5E1"} onChange={(value) => updateAttr("border_color", value)} />
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
                            <div className="mt-1.5">
                              <IconField label="Data" value={selected.attrs.data || "28,46,64,38,78"} onChange={(value) => updateAttr("data", value)} />
                               <p className="mt-1 text-[10px] text-muted-foreground">{translateEditorLabel("Comma-separated values", language)}</p>
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
                            label="Line width"
                            value={selected.tag.toLowerCase() === "line" ? selected.attrs.width || "" : selected.attrs.line_width || ""}
                            onChange={(value) => selected.tag.toLowerCase() === "line" ? updateAttr("width", value) : updateAttr("line_width", value)}
                          />
                          <IconField label="Opacity" type="number" step={0.1} min={0} max={1} value={selected.attrs.opacity ?? "1"} onChange={(value) => updateAttr("opacity", value)} />
                        </div>
                        <div className="mt-2">
                          <label className="mb-1 block text-[10px] text-muted-foreground">{translateEditorLabel("Slide background", language)}</label>
                          <Input type="color" value={resolvedActiveSlide.attrs.background || "#ffffff"} onChange={(event) => updateSlideBackground(event.target.value)} className="h-8 p-1" />
                        </div>
                      </div>

                      <Separator />

                      <div>
                        <PanelLabel icon={Layers} label="Layer" />
                        <div className="flex items-center gap-1.5">
                          <Button aria-label={translateEditorLabel("Send backward", language)} variant="outline" size="icon" className="h-8 w-8" onClick={() => moveLayer("down")}>
                            <ChevronDown className="h-4 w-4" />
                          </Button>
                          <div className="flex-1 rounded-md border bg-muted/30 px-2 py-1.5 text-center text-xs text-muted-foreground">
                            {resolvedActiveSlide.elements.findIndex((element) => element.id === selected.id) + 1} / {resolvedActiveSlide.elements.length}
                          </div>
                          <Button aria-label={translateEditorLabel("Bring forward", language)} variant="outline" size="icon" className="h-8 w-8" onClick={() => moveLayer("up")}>
                            <ChevronUp className="h-4 w-4" />
                          </Button>
                        </div>
                        <Button
                          variant="outline"
                          className="mt-1.5 h-8 w-full text-xs"
                           aria-label={translateEditorLabel(selected.attrs.locked === "true" ? "Unlock element" : "Lock element", language)}
                          onClick={() => updateAttr("locked", selected.attrs.locked === "true" ? "false" : "true")}
                        >
                          {selected.attrs.locked === "true" ? <Unlock className="mr-1.5 h-3.5 w-3.5" /> : <Lock className="mr-1.5 h-3.5 w-3.5" />}
                           {translateEditorLabel(selected.attrs.locked === "true" ? "Unlock element" : "Lock element", language)}
                        </Button>
                      </div>
                    </div>
                  </>
                )}
              </aside>
            </div>
          </div>
        </div>

        {activeOverlay && (
          <div className="fixed inset-0 z-[200] flex items-center justify-center bg-slate-950/45 p-4 backdrop-blur-sm" onMouseDown={() => setActiveOverlay(null)}>
            <div className="flex max-h-[min(720px,calc(100vh-2rem))] w-full max-w-xl flex-col overflow-hidden rounded-2xl border bg-background shadow-2xl" onMouseDown={(event) => event.stopPropagation()}>
              <div className="flex items-center justify-between border-b px-4 py-3">
                <div className="flex items-center gap-2">
                  {activeOverlay === "history" ? <History className="h-4 w-4 text-primary" /> : activeOverlay === "share" ? <Share2 className="h-4 w-4 text-primary" /> : <MessageSquare className="h-4 w-4 text-primary" />}
                  <div>
                    <p className="text-sm font-semibold">{translateEditorLabel(activeOverlay === "history" ? "History" : activeOverlay === "share" ? "Share" : "Comments", language)}</p>
                    <p className="text-[10px] text-muted-foreground">{projectTitle}</p>
                  </div>
                </div>
                <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setActiveOverlay(null)} aria-label={translateEditorLabel("Close", language)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {activeOverlay === "history" && (
                <div className="min-h-0 flex-1 overflow-y-auto p-4">
                  {collaborationError && <p className="mb-3 rounded-md bg-destructive/10 px-3 py-2 text-xs text-destructive">{collaborationError}</p>}
                  {versionLoading || collaborationLoading ? (
                    <div className="flex items-center justify-center py-12 text-sm text-muted-foreground"><Loader2 className="mr-2 h-4 w-4 animate-spin" /> {editorCopy.loading}</div>
                  ) : versions.length === 0 ? (
                    <p className="py-12 text-center text-sm text-muted-foreground">{translateEditorLabel("No versions yet", language)}</p>
                  ) : (
                    <div className="space-y-2">
                      {versions.map((version) => (
                        <div key={version.id} className="flex items-center justify-between gap-3 rounded-xl border bg-muted/20 px-3 py-2.5">
                          <div className="min-w-0">
                            <p className="truncate text-xs font-semibold">{version.label || (language === "vi" ? "Phiên bản" : "Version")} <span className="font-normal text-muted-foreground">#{version.id}</span></p>
                            <p className="mt-0.5 text-[10px] text-muted-foreground">
                              {version.created_by?.name || version.created_by?.email || (language === "vi" ? "Người dùng" : "User")} · {version.created_at ? new Date(version.created_at).toLocaleString(language === "vi" ? "vi-VN" : "en-US") : ""}
                            </p>
                          </div>
                          <Button size="sm" variant="outline" className="h-8 shrink-0 text-xs" disabled={!canEdit || versionLoading} onClick={() => void restoreVersion(version)}>
                            <RotateCcw className="mr-1.5 h-3.5 w-3.5" /> {translateEditorLabel("Restore", language)}
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {activeOverlay === "share" && (
                <div className="min-h-0 flex-1 overflow-y-auto p-4">
                  {collaborationError && <p className="mb-3 rounded-md bg-destructive/10 px-3 py-2 text-xs text-destructive">{collaborationError}</p>}
                  {accessRole === "owner" ? (
                    <div className="mb-4 rounded-xl border bg-muted/20 p-3">
                      <p className="mb-2 text-xs font-semibold">{translateEditorLabel("Invite collaborator", language)}</p>
                      <div className="flex gap-2">
                        <Input value={inviteEmail} onChange={(event) => setInviteEmail(event.target.value)} placeholder="email@example.com" className="h-9 text-xs" onKeyDown={(event) => { if (event.key === "Enter") void inviteCollaborator(); }} />
                        <select value={inviteRole} onChange={(event) => setInviteRole(event.target.value as "viewer" | "editor")} className="h-9 rounded-md border bg-background px-2 text-xs">
                          <option value="viewer">{translateEditorLabel("Viewer", language)}</option>
                          <option value="editor">{translateEditorLabel("Editor", language)}</option>
                        </select>
                        <Button size="sm" className="h-9 shrink-0" disabled={!inviteEmail.trim() || collaborationLoading} onClick={() => void inviteCollaborator()}>
                          <UserPlus className="mr-1.5 h-3.5 w-3.5" /> {language === "vi" ? "Mời" : "Invite"}
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="mb-4 rounded-xl border border-primary/20 bg-primary/5 px-3 py-2 text-xs text-muted-foreground">
                      {translateEditorLabel("View only", language)} · {translateEditorLabel(accessRole === "editor" ? "Editor" : "Viewer", language)}
                    </div>
                  )}
                  <div className="space-y-2">
                    {collaborators.map((member) => (
                      <div key={member.user_id} className="flex items-center justify-between gap-3 rounded-xl border px-3 py-2.5">
                        <div className="min-w-0"><p className="truncate text-xs font-semibold">{member.name}</p><p className="truncate text-[10px] text-muted-foreground">{member.email}</p></div>
                        <div className="flex items-center gap-1.5">
                          {member.owner ? <span className="rounded bg-primary/10 px-2 py-1 text-[10px] font-semibold text-primary">{language === "vi" ? "Chủ sở hữu" : "Owner"}</span> : accessRole === "owner" ? <><select value={member.role} onChange={(event) => void changeCollaboratorRole(member, event.target.value as "viewer" | "editor")} className="h-7 rounded border bg-background px-1.5 text-[10px]"><option value="viewer">{translateEditorLabel("Viewer", language)}</option><option value="editor">{translateEditorLabel("Editor", language)}</option></select><Button variant="ghost" size="icon" className="h-7 w-7 text-destructive" onClick={() => void removeCollaborator(member)} aria-label={translateEditorLabel("Remove access", language)}><X className="h-3.5 w-3.5" /></Button></> : <span className="rounded bg-muted px-2 py-1 text-[10px]">{translateEditorLabel(member.role === "editor" ? "Editor" : "Viewer", language)}</span>}
                        </div>
                      </div>
                    ))}
                    {collaborators.length === 0 && <p className="py-8 text-center text-sm text-muted-foreground">{translateEditorLabel("No collaborators yet", language)}</p>}
                  </div>
                </div>
              )}

              {activeOverlay === "comments" && (
                <div className="min-h-0 flex-1 overflow-y-auto p-4">
                  {collaborationError && <p className="mb-3 rounded-md bg-destructive/10 px-3 py-2 text-xs text-destructive">{collaborationError}</p>}
                  <div className="mb-4 rounded-xl border bg-muted/20 p-3">
                    <p className="mb-2 text-[10px] text-muted-foreground">{language === "vi" ? `Trang chiếu ${activeSlideIndex + 1}${selectedId ? ` · ${selectedId}` : ""}` : `Slide ${activeSlideIndex + 1}${selectedId ? ` · ${selectedId}` : ""}`}</p>
                    <Textarea value={commentDraft} onChange={(event) => setCommentDraft(event.target.value)} placeholder={translateEditorLabel("Add a comment", language)} className="min-h-20 bg-background text-xs" />
                    <div className="mt-2 flex justify-end"><Button size="sm" className="h-8 text-xs" disabled={!commentDraft.trim() || commentLoading} onClick={() => void addComment()}>{commentLoading && <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />} {language === "vi" ? "Gửi bình luận" : "Post comment"}</Button></div>
                  </div>
                  <div className="space-y-2">
                    {comments.map((comment) => (
                      <div key={comment.id} className={cn("rounded-xl border px-3 py-2.5", comment.resolved && "opacity-60")}>
                        <div className="flex items-start justify-between gap-3"><div><p className="text-xs font-semibold">{comment.author?.name || comment.author?.email}</p><p className="text-[10px] text-muted-foreground">{comment.slide_index !== null && comment.slide_index !== undefined ? `${language === "vi" ? "Trang chiếu" : "Slide"} ${comment.slide_index + 1}` : ""} · {comment.created_at ? new Date(comment.created_at).toLocaleString(language === "vi" ? "vi-VN" : "en-US") : ""}</p></div><div className="flex gap-1">{canEdit && <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => void toggleCommentResolved(comment)} aria-label={translateEditorLabel(comment.resolved ? "Reopen comment" : "Resolve comment", language)}><span className="text-xs">{comment.resolved ? "↩" : "✓"}</span></Button>}<Button variant="ghost" size="icon" className="h-7 w-7 text-destructive" onClick={() => void deleteComment(comment)} aria-label={language === "vi" ? "Xóa bình luận" : "Delete comment"}><X className="h-3.5 w-3.5" /></Button></div></div>
                        <p className="mt-2 whitespace-pre-wrap text-xs leading-relaxed">{comment.body}</p>
                      </div>
                    ))}
                    {comments.length === 0 && <p className="py-8 text-center text-sm text-muted-foreground">{translateEditorLabel("No comments yet", language)}</p>}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

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
             aria-label={translateEditorLabel("Presentation mode", language)}
            >
              <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_42%,rgba(55,65,81,0.32),transparent_58%)]" />
              <div className="pointer-events-none absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-black/60 to-transparent" />

              <div className={cn(
                "pointer-events-none absolute inset-x-0 top-0 z-30 flex items-center justify-between bg-gradient-to-b from-black/75 via-black/25 to-transparent px-6 py-5 transition-all duration-300",
                isPresentControlsVisible ? "translate-y-0 opacity-100" : "-translate-y-full opacity-0",
              )}>
                <div className="flex items-center gap-3">
                  <div>
                      <p className="text-sm font-semibold tracking-wide drop-shadow">{translateEditorLabel(isPresenterView ? "Presenter View" : "Presentation", language)}</p>
                    <p className="text-[11px] text-white/60">Slide {activeSlideIndex + 1} of {slideCount}</p>
                  </div>
                </div>
                <div className="pointer-events-auto flex items-center gap-1.5">
                  <div className="flex h-9 items-center gap-1.5 rounded-lg bg-white/10 px-2.5 text-xs text-white/80" title={translateEditorLabel("Presentation timer", language)}>
                    <Timer className="h-3.5 w-3.5 text-white/60" />
                    <span className="min-w-[42px] font-mono tabular-nums">{formatPresentTime(presentElapsedSeconds)}</span>
                    <button
                      type="button"
                      onClick={() => setIsPresentTimerRunning((running) => !running)}
                      className="rounded p-0.5 text-white/60 transition-colors hover:bg-white/10 hover:text-white"
                       aria-label={translateEditorLabel(isPresentTimerRunning ? "Pause timer" : "Resume timer", language)}
                       title={translateEditorLabel(isPresentTimerRunning ? "Pause timer" : "Resume timer", language)}
                    >
                      {isPresentTimerRunning ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
                    </button>
                    <button
                      type="button"
                      onClick={() => setPresentElapsedSeconds(0)}
                      className="rounded p-0.5 text-white/60 transition-colors hover:bg-white/10 hover:text-white"
                       aria-label={translateEditorLabel("Reset timer", language)}
                       title={translateEditorLabel("Reset timer", language)}
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
                     title={translateEditorLabel("Toggle Presenter View", language)}
                  >
                    <LayoutDashboard className="h-4 w-4" />
                     <span className="hidden sm:inline">{translateEditorLabel("Presenter", language)}</span>
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
                       title={translateEditorLabel("Show speaker notes", language)}
                    >
                      <StickyNote className="h-4 w-4" />
                       <span className="hidden sm:inline">{translateEditorLabel("Notes", language)}</span>
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={togglePresentFullscreen}
                    className="flex h-9 items-center gap-2 rounded-lg px-3 text-xs text-white/70 transition-colors hover:bg-white/10 hover:text-white"
                     title={translateEditorLabel(isPresentFullscreen ? "Exit fullscreen" : "Fullscreen", language)}
                  >
                    {isPresentFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                     <span className="hidden sm:inline">{translateEditorLabel(isPresentFullscreen ? "Exit fullscreen" : "Fullscreen", language)}</span>
                  </button>
                  <button
                    type="button"
                    onClick={closePresent}
                    className="flex h-9 items-center gap-2 rounded-lg bg-white/10 px-3 text-xs font-medium text-white transition-colors hover:bg-white/20"
                  >
                    <X className="h-4 w-4" />
                     <span>{translateEditorLabel("Exit", language)}</span>
                  </button>
                </div>
              </div>

              {isPresentNotesVisible && !isPresenterView && (
                <aside
                  className="pointer-events-auto absolute right-5 top-20 z-40 flex w-[min(360px,calc(100vw-2.5rem))] flex-col overflow-hidden rounded-2xl border border-amber-200/20 bg-[#111722]/95 text-white shadow-2xl backdrop-blur-xl"
                  role="region"
                   aria-label={`${translateEditorLabel("Speaker notes for slide", language)} ${activeSlideIndex + 1}`}
                >
                  <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
                    <div className="flex items-center gap-2">
                      <StickyNote className="h-4 w-4 text-amber-200" />
                      <div>
                       <p className="text-xs font-semibold">{translateEditorLabel("Speaker notes", language)}</p>
                       <p className="text-[10px] text-white/45">{translateEditorLabel("Slide", language)} {activeSlideIndex + 1} {translateEditorLabel("of", language)} {slideCount}</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => setIsPresentNotesVisible(false)}
                      className="rounded-md p-1 text-white/45 transition-colors hover:bg-white/10 hover:text-white"
                       aria-label={translateEditorLabel("Hide speaker notes", language)}
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="max-h-[min(70vh,520px)] overflow-y-auto whitespace-pre-wrap px-4 py-4 text-sm leading-relaxed text-white/85">
                     {activeSlideNotes || <span className="italic text-white/40">{translateEditorLabel("No notes for this slide.", language)}</span>}
                  </div>
                </aside>
              )}

              {isPresenterView ? (
                <main className="absolute inset-x-5 bottom-20 top-20 z-10 flex min-h-0 items-stretch justify-center">
                  <div className="grid h-full w-full min-h-0 grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(280px,360px)]">
                    <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-2xl border border-white/10 bg-[#111722]/85 shadow-2xl backdrop-blur-xl">
                      <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
                        <div>
                           <p className="text-xs font-semibold uppercase tracking-[0.18em] text-white/80">{translateEditorLabel("Current slide", language)}</p>
                           <p className="mt-0.5 text-[10px] text-white/45">{translateEditorLabel("Slide", language)} {activeSlideIndex + 1} {translateEditorLabel("of", language)} {slideCount}</p>
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
                             <p className="text-xs font-semibold">{translateEditorLabel("Speaker notes", language)}</p>
                             <p className="text-[10px] text-white/45">{translateEditorLabel("Only visible in Presenter View", language)}</p>
                          </div>
                        </div>
                        <div className="flex-1 overflow-y-auto whitespace-pre-wrap px-4 py-4 text-sm leading-relaxed text-white/85">
                           {activeSlideNotes || <span className="italic text-white/40">{translateEditorLabel("No notes for this slide.", language)}</span>}
                        </div>
                      </section>

                      <section className="shrink-0 rounded-2xl border border-white/10 bg-[#111722]/85 p-3 shadow-2xl backdrop-blur-xl">
                        <div className="mb-2 flex items-center justify-between">
                          <div>
                           <p className="text-xs font-semibold text-white/80">{translateEditorLabel("Next slide", language)}</p>
                            <p className="text-[10px] text-white/45">
                               {nextSlide ? `${translateEditorLabel("Slide", language)} ${activeSlideIndex + 2}` : translateEditorLabel("End of presentation", language)}
                            </p>
                          </div>
                          {nextSlide && <ChevronRight className="h-4 w-4 text-white/35" />}
                        </div>
                        {nextSlide ? (
                          <button
                            type="button"
                            onClick={presentNext}
                            className="block w-full overflow-hidden rounded-lg bg-white text-left shadow-lg transition-transform hover:scale-[1.01]"
                             aria-label={`${translateEditorLabel("Go to slide", language)} ${activeSlideIndex + 2}`}
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
                           {translateEditorLabel("You are on the last slide", language)}
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
                   aria-label={translateEditorLabel("Previous slide", language)}
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
                   aria-label={translateEditorLabel("Next slide", language)}
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
                     aria-label={translateEditorLabel("Previous slide", language)}
                    disabled={activeSlideIndex === 0}
                    onClick={presentPrevious}
                    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-white/60 transition-colors hover:bg-white/10 hover:text-white disabled:opacity-30"
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </button>
                  <div className="min-w-0 flex-1">
                    <div className="mb-1.5 flex items-center justify-between text-[10px] text-white/50">
                       <span>{translateEditorLabel("Slide", language)} {activeSlideIndex + 1}</span>
                       <span>{slideCount} {translateEditorLabel("total", language)}</span>
                    </div>
                    <div className="h-1 overflow-hidden rounded-full bg-white/10">
                      <div className="h-full rounded-full bg-white transition-[width] duration-300" style={{ width: `${progress}%` }} />
                    </div>
                  </div>
                  <button
                    type="button"
                     aria-label={translateEditorLabel("Next slide", language)}
                    disabled={activeSlideIndex >= slideCount - 1}
                    onClick={presentNext}
                    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-white/60 transition-colors hover:bg-white/10 hover:text-white disabled:opacity-30"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </button>
                  <div className="hidden h-5 w-px bg-white/10 sm:block" />
                   <span className="hidden whitespace-nowrap text-[10px] text-white/40 sm:block">{language === "vi" ? "Esc thoát · ← → điều hướng · P người trình bày · N ghi chú · T đồng hồ" : "Esc exit · ← → navigate · P presenter · N notes · T timer"}</span>
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
              {isExportingPptx ? translateEditorLabel("Exporting presentation…", language) : translateEditorLabel("Preparing PDF…", language)}
            </p>
            <p className="mt-1 text-sm text-white/60">{translateEditorLabel("Please wait", language)}</p>
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
      <SlidegenConfirmDialog
        open={Boolean(pendingDraftRestore)}
        onOpenChange={(open) => {
          if (!open) dismissLocalDraft();
        }}
        title={language === "vi" ? "Khôi phục bản nháp local?" : "Restore local draft?"}
        description={language === "vi"
          ? "Đã tìm thấy bản nháp mới hơn trên thiết bị. Khôi phục bản nháp sẽ thay thế nội dung hiện tại trong trình chỉnh sửa."
          : "A newer local draft was found on this device. Restoring it will replace the current editor content."}
        confirmLabel={language === "vi" ? "Khôi phục bản nháp" : "Restore draft"}
        cancelLabel={language === "vi" ? "Bỏ qua" : "Keep current version"}
        onConfirm={restoreLocalDraft}
      />
      <SlidegenConfirmDialog
        open={Boolean(pendingVersionRestore)}
        onOpenChange={(open) => {
          if (!open) setPendingVersionRestore(null);
        }}
        title={language === "vi" ? "Khôi phục phiên bản?" : "Restore this version?"}
        description={language === "vi"
          ? "Thay đổi hiện tại sẽ được thay thế bằng phiên bản đã chọn."
          : "Your current changes will be replaced by the selected version."}
        confirmLabel={language === "vi" ? "Khôi phục" : "Restore"}
        cancelLabel={language === "vi" ? "Hủy" : "Cancel"}
        onConfirm={() => void confirmRestoreVersion()}
        destructive
        busy={versionLoading}
      />
    </TooltipProvider>
  );
};

const PanelLabel = ({ icon: Icon, label }: { icon: React.ElementType; label: string }) => {
  const { language } = useLanguage();
  return (
    <div className="mb-2 flex items-center gap-1.5">
      <Icon className="h-3 w-3 text-muted-foreground/70" />
      <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">{translateEditorLabel(label, language)}</span>
    </div>
  );
};

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
}) => {
  const { language } = useLanguage();
  return (
    <div className="flex h-8 items-center gap-1.5 rounded-md border border-border/50 bg-muted/30 px-2">
      <span className="w-8 shrink-0 text-[10px] font-bold text-muted-foreground">{translateEditorLabel(label, language)}</span>
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
};

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
