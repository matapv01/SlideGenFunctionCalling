import {
  AlignCenter,
  AlignLeft,
  AlignRight,
  ArrowDown,
  ArrowDownToLine,
  ArrowUp,
  ArrowUpToLine,
  Circle,
  Copy,
  Group as GroupIcon,
  Image as ImageIcon,
  Layers3,
  Minus,
  Palette,
  PaintBucket,
  RotateCcw,
  RotateCw,
  Sigma,
  SlidersHorizontal,
  Square,
  Trash2,
  Type,
  Ungroup,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Slider } from "@/components/ui/slider";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/contexts/LanguageContext";
import {
  buildElementFilter,
  getCanvasAlignmentUpdates,
  getElementStylePresets,
  type CanvasAlignment,
  type ElementStyleUpdate,
} from "../editorActions";
import type { SelectionInfo, SlideElement } from "../types";

interface ContextualEditBarProps {
  selectedElement?: SlideElement;
  selectionInfo: SelectionInfo;
  slideCanvasRef: React.RefObject<SlideCanvasHandle>;
  onAddElement: (type: string, subType: string) => void;
  onUpdateElement: (id: string, updates: ElementStyleUpdate) => void;
  onDeleteElement: () => void;
  onDuplicateElement: () => void;
  onBringForward: () => void;
  onSendBackward: () => void;
}

const copyByLanguage = {
  vi: {
    add: "Thêm nhanh",
    text: "Văn bản",
    shape: "Hình khối",
    image: "Hình ảnh",
    equation: "Công thức",
    paste: "Dán",
    selected: "Đang chọn",
    styles: "Kiểu",
    color: "Màu",
    opacity: "Độ mờ",
    position: "Vị trí",
    copy: "Sao chép",
    duplicate: "Nhân đôi",
    delete: "Xóa",
    alignToSlide: "Căn theo slide",
    left: "Trái",
    center: "Giữa",
    right: "Phải",
    top: "Trên",
    middle: "Giữa dọc",
    bottom: "Dưới",
    layers: "Thứ tự lớp",
    toFront: "Lên trên cùng",
    forward: "Lên một lớp",
    backward: "Xuống một lớp",
    toBack: "Xuống dưới cùng",
    rotate: "Xoay nhanh",
    styleHint: "Áp dụng nhanh một bộ màu và hiệu ứng",
    opacityHint: "Điều chỉnh độ trong suốt của phần tử",
    group: "Nhóm",
    ungroup: "Bỏ nhóm",
    items: "phần tử",
    multiHint: "Giữ Shift hoặc Ctrl để thêm/bớt phần tử khỏi vùng chọn",
  },
  en: {
    add: "Quick add",
    text: "Text",
    shape: "Shape",
    image: "Image",
    equation: "Equation",
    paste: "Paste",
    selected: "Selected",
    styles: "Styles",
    color: "Color",
    opacity: "Opacity",
    position: "Position",
    copy: "Copy",
    duplicate: "Duplicate",
    delete: "Delete",
    alignToSlide: "Align to slide",
    left: "Left",
    center: "Center",
    right: "Right",
    top: "Top",
    middle: "Middle",
    bottom: "Bottom",
    layers: "Layer order",
    toFront: "Bring to front",
    forward: "Bring forward",
    backward: "Send backward",
    toBack: "Send to back",
    rotate: "Quick rotate",
    styleHint: "Apply a color and effect preset",
    opacityHint: "Adjust element transparency",
    group: "Group",
    ungroup: "Ungroup",
    items: "elements",
    multiHint: "Hold Shift or Ctrl to add or remove elements from the selection",
  },
};

const presetNames: Record<string, { vi: string; en: string }> = {
  "text-modern": { vi: "Hiện đại", en: "Modern" },
  "text-editorial": { vi: "Tạp chí", en: "Editorial" },
  "text-clean": { vi: "Tối giản", en: "Clean" },
  "media-soft": { vi: "Mềm mại", en: "Soft" },
  "media-mono": { vi: "Đơn sắc", en: "Monochrome" },
  "media-vivid": { vi: "Rực rỡ", en: "Vivid" },
  "accent-blue": { vi: "Xanh lam", en: "Blue" },
  "accent-violet": { vi: "Tím", en: "Violet" },
  "accent-ink": { vi: "Mực đen", en: "Ink" },
  "shape-ocean": { vi: "Đại dương", en: "Ocean" },
  "shape-coral": { vi: "San hô", en: "Coral" },
  "shape-outline": { vi: "Viền nét", en: "Outline" },
};

const CompactTip = ({ label, children }: { label: string; children: React.ReactNode }) => (
  <Tooltip delayDuration={350}>
    <TooltipTrigger asChild>{children}</TooltipTrigger>
    <TooltipContent side="bottom" className="text-xs">{label}</TooltipContent>
  </Tooltip>
);

const Group = ({ children }: { children: React.ReactNode }) => (
  <div className="flex h-8 items-center gap-0.5 rounded-lg border border-border/60 bg-muted/20 p-0.5">
    {children}
  </div>
);

export const ContextualEditBar = ({
  selectedElement,
  selectionInfo,
  slideCanvasRef,
  onAddElement,
  onUpdateElement,
  onDeleteElement,
  onDuplicateElement,
  onBringForward,
  onSendBackward,
}: ContextualEditBarProps) => {
  const { language, t } = useLanguage();
  const c = copyByLanguage[language];

  const update = (updates: ElementStyleUpdate) => {
    if (!selectedElement) return;
    onUpdateElement(selectedElement.id, updates);
  };

  const applyPreset = (updates: ElementStyleUpdate) => {
    if (!selectedElement) return;
    const next = { ...selectedElement, ...updates };
    const hasFilterUpdate = updates.blur !== undefined
      || updates.brightness !== undefined
      || updates.saturation !== undefined;
    update(hasFilterUpdate ? { ...updates, _filter: buildElementFilter(next) } : updates);
  };

  const align = (alignment: CanvasAlignment) => {
    if (!selectedElement) return;
    update(getCanvasAlignmentUpdates(selectedElement, alignment));
  };

  const rotate = (delta: number) => {
    if (!selectedElement) return;
    let next = (selectedElement.rotation || 0) + delta;
    if (next > 180) next -= 360;
    if (next < -180) next += 360;
    update({ rotation: next });
  };

  const primaryColor = selectedElement?.type === "text"
    || selectedElement?.type === "equation"
    || selectedElement?.type === "icon"
    ? (selectedElement.color || "#111827")
    : (selectedElement?.fillColor && selectedElement.fillColor !== "transparent"
      ? selectedElement.fillColor
      : "#ffffff");

  const typeName = selectedElement
    ? ({
        text: t.editor_type_text,
        image: t.editor_type_image,
        shape: t.editor_type_shape,
        video: t.editor_type_video,
        equation: c.equation,
        icon: language === "vi" ? "Biểu tượng" : "Icon",
      }[selectedElement.type] || selectedElement.type)
    : "";

  if (!selectedElement) {
    return (
      <TooltipProvider>
        <div className="h-11 shrink-0 border-b bg-background/90 px-3 flex items-center gap-2 overflow-x-auto [&::-webkit-scrollbar]:hidden">
          <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground shrink-0">{c.add}</span>
          <Group>
            <Button variant="ghost" size="sm" className="h-7 px-2.5 text-xs" onClick={() => onAddElement("text", "heading")}>
              <Type className="mr-1.5 h-3.5 w-3.5" />{c.text}
            </Button>
            <Button variant="ghost" size="sm" className="h-7 px-2.5 text-xs" onClick={() => onAddElement("shape", "rectangle")}>
              <Square className="mr-1.5 h-3.5 w-3.5" />{c.shape}
            </Button>
            <Button variant="ghost" size="sm" className="h-7 px-2.5 text-xs" onClick={() => onAddElement("image", "")}>
              <ImageIcon className="mr-1.5 h-3.5 w-3.5" />{c.image}
            </Button>
            <Button variant="ghost" size="sm" className="h-7 px-2.5 text-xs" onClick={() => onAddElement("equation", "equation")}>
              <Sigma className="mr-1.5 h-3.5 w-3.5" />{c.equation}
            </Button>
          </Group>
          <Button variant="ghost" size="sm" className="h-8 text-xs" onClick={() => slideCanvasRef.current?.pasteElement()}>
            <Copy className="mr-1.5 h-3.5 w-3.5" />{c.paste}
          </Button>
          <span className="ml-auto text-[11px] text-muted-foreground whitespace-nowrap">
            {language === "vi" ? "Chọn một phần tử để mở công cụ chỉnh sửa" : "Select an element to open editing tools"}
          </span>
        </div>
      </TooltipProvider>
    );
  }

  if (selectionInfo.count > 1) {
    const isGrouped = Boolean(selectionInfo.groupId);
    return (
      <TooltipProvider>
        <div className="h-11 shrink-0 border-b bg-background/90 px-3 flex items-center gap-2 overflow-x-auto [&::-webkit-scrollbar]:hidden">
          <div className="flex items-center gap-1.5 shrink-0 pr-1">
            <span className="h-2 w-2 rounded-full bg-primary" />
            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{c.selected}</span>
            <span className="text-xs font-medium">{selectionInfo.count} {c.items}</span>
          </div>

          <Button
            variant={isGrouped ? "secondary" : "default"}
            size="sm"
            className="h-8 px-3 text-xs shrink-0"
            onClick={() => {
              if (isGrouped) slideCanvasRef.current?.ungroupSelectedElements();
              else slideCanvasRef.current?.groupSelectedElements();
            }}
          >
            {isGrouped
              ? <Ungroup className="mr-1.5 h-3.5 w-3.5" />
              : <GroupIcon className="mr-1.5 h-3.5 w-3.5" />}
            {isGrouped ? c.ungroup : c.group}
            <span className="ml-1.5 rounded bg-background/50 px-1 py-0.5 text-[9px] opacity-70">
              {isGrouped ? "Ctrl+Shift+G" : "Ctrl+G"}
            </span>
          </Button>

          <span className="text-[11px] text-muted-foreground whitespace-nowrap">{c.multiHint}</span>
          <div className="ml-auto" />

          <Group>
            <CompactTip label={`${c.copy} (Ctrl+C)`}>
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => slideCanvasRef.current?.copySelectedElement(selectedElement.id)}>
                <Copy className="h-3.5 w-3.5" />
              </Button>
            </CompactTip>
            <CompactTip label={`${c.duplicate} (Ctrl+D)`}>
              <Button variant="ghost" size="sm" className="h-7 px-2 text-xs" onClick={onDuplicateElement}>
                <Circle className="mr-1.5 h-3 w-3 fill-current opacity-20" />{c.duplicate}
              </Button>
            </CompactTip>
            <CompactTip label={`${c.delete} (Del)`}>
              <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive hover:text-destructive" onClick={onDeleteElement}>
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            </CompactTip>
          </Group>
        </div>
      </TooltipProvider>
    );
  }

  const presets = getElementStylePresets(selectedElement.type);

  return (
    <TooltipProvider>
      <div className="h-11 shrink-0 border-b bg-background/90 px-3 flex items-center gap-2 overflow-x-auto [&::-webkit-scrollbar]:hidden">
        <div className="flex items-center gap-1.5 shrink-0 pr-1">
          <span className="h-2 w-2 rounded-full bg-primary" />
          <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{c.selected}</span>
          <span className="text-xs font-medium">{typeName}</span>
        </div>

        <Popover>
          <PopoverTrigger asChild>
            <Button variant="ghost" size="sm" className="h-8 px-2.5 text-xs shrink-0">
              <Palette className="mr-1.5 h-3.5 w-3.5" />{c.styles}
            </Button>
          </PopoverTrigger>
          <PopoverContent align="start" className="w-72 p-3">
            <div className="mb-3">
              <p className="text-xs font-semibold">{c.styles}</p>
              <p className="mt-0.5 text-[11px] text-muted-foreground">{c.styleHint}</p>
            </div>
            <div className="grid grid-cols-3 gap-2">
              {presets.map((preset) => (
                <button
                  key={preset.id}
                  className="group rounded-lg border border-border/70 p-1.5 text-left hover:border-primary/60 hover:bg-muted/40 transition-colors"
                  onClick={() => applyPreset(preset.updates)}
                >
                  <span
                    className="block h-10 rounded-md border border-black/5 shadow-sm"
                    style={{ background: preset.swatch }}
                  />
                  <span className="mt-1.5 block truncate text-[10px] font-medium">
                    {presetNames[preset.id]?.[language] || preset.id}
                  </span>
                </button>
              ))}
            </div>
          </PopoverContent>
        </Popover>

        <CompactTip label={c.color}>
          <label className="relative flex h-8 cursor-pointer items-center gap-1.5 rounded-md px-2.5 text-xs hover:bg-accent shrink-0">
            <PaintBucket className="h-3.5 w-3.5" />
            <span>{c.color}</span>
            <span className="h-4 w-4 rounded-full border shadow-sm" style={{ background: primaryColor }} />
            <input
              aria-label={c.color}
              type="color"
              value={primaryColor}
              className="absolute inset-0 cursor-pointer opacity-0"
              onChange={(event) => {
                const color = event.target.value;
                const isForeground = selectedElement.type === "text"
                  || selectedElement.type === "equation"
                  || selectedElement.type === "icon";
                update(isForeground ? { color } : { fillColor: color });
              }}
            />
          </label>
        </CompactTip>

        <Popover>
          <PopoverTrigger asChild>
            <Button variant="ghost" size="sm" className="h-8 px-2.5 text-xs shrink-0">
              <SlidersHorizontal className="mr-1.5 h-3.5 w-3.5" />
              {c.opacity} {Math.round((selectedElement.opacity ?? 1) * 100)}%
            </Button>
          </PopoverTrigger>
          <PopoverContent align="start" className="w-64 p-3">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold">{c.opacity}</p>
                <p className="mt-0.5 text-[11px] text-muted-foreground">{c.opacityHint}</p>
              </div>
              <span className="text-xs font-semibold tabular-nums">{Math.round((selectedElement.opacity ?? 1) * 100)}%</span>
            </div>
            <Slider
              min={0}
              max={1}
              step={0.05}
              value={[selectedElement.opacity ?? 1]}
              onValueChange={(value) => update({ opacity: value[0] })}
            />
          </PopoverContent>
        </Popover>

        <div className="h-5 w-px bg-border shrink-0" />

        <Popover>
          <PopoverTrigger asChild>
            <Button variant="ghost" size="sm" className="h-8 px-2.5 text-xs shrink-0">
              <Layers3 className="mr-1.5 h-3.5 w-3.5" />{c.position}
            </Button>
          </PopoverTrigger>
          <PopoverContent align="start" className="w-80 p-3">
            <p className="mb-2 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{c.alignToSlide}</p>
            <div className="grid grid-cols-3 gap-1.5">
              {([
                ["left", AlignLeft, c.left],
                ["horizontal-center", AlignCenter, c.center],
                ["right", AlignRight, c.right],
                ["top", ArrowUp, c.top],
                ["vertical-center", Minus, c.middle],
                ["bottom", ArrowDown, c.bottom],
              ] as const).map(([alignment, Icon, label]) => (
                <Button key={alignment} variant="outline" size="sm" className="h-8 justify-start px-2 text-[11px]" onClick={() => align(alignment)}>
                  <Icon className="mr-1.5 h-3.5 w-3.5" />{label}
                </Button>
              ))}
            </div>

            <p className="mb-2 mt-4 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{c.layers}</p>
            <div className="grid grid-cols-2 gap-1.5">
              <Button variant="outline" size="sm" className="h-8 justify-start px-2 text-[11px]" onClick={() => slideCanvasRef.current?.bringToFront(selectedElement.id)}>
                <ArrowUpToLine className="mr-1.5 h-3.5 w-3.5" />{c.toFront}
              </Button>
              <Button variant="outline" size="sm" className="h-8 justify-start px-2 text-[11px]" onClick={onBringForward}>
                <ArrowUp className="mr-1.5 h-3.5 w-3.5" />{c.forward}
              </Button>
              <Button variant="outline" size="sm" className="h-8 justify-start px-2 text-[11px]" onClick={onSendBackward}>
                <ArrowDown className="mr-1.5 h-3.5 w-3.5" />{c.backward}
              </Button>
              <Button variant="outline" size="sm" className="h-8 justify-start px-2 text-[11px]" onClick={() => slideCanvasRef.current?.sendToBack(selectedElement.id)}>
                <ArrowDownToLine className="mr-1.5 h-3.5 w-3.5" />{c.toBack}
              </Button>
            </div>

            <p className="mb-2 mt-4 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{c.rotate}</p>
            <div className="grid grid-cols-2 gap-1.5">
              <Button variant="outline" size="sm" className="h-8 text-[11px]" onClick={() => rotate(-90)}>
                <RotateCcw className="mr-1.5 h-3.5 w-3.5" />-90°
              </Button>
              <Button variant="outline" size="sm" className="h-8 text-[11px]" onClick={() => rotate(90)}>
                <RotateCw className="mr-1.5 h-3.5 w-3.5" />+90°
              </Button>
            </div>
          </PopoverContent>
        </Popover>

        <Group>
          <CompactTip label={`${c.copy} (Ctrl+C)`}>
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => slideCanvasRef.current?.copySelectedElement(selectedElement.id)}>
              <Copy className="h-3.5 w-3.5" />
            </Button>
          </CompactTip>
          <CompactTip label={`${c.duplicate} (Ctrl+D)`}>
            <Button variant="ghost" size="sm" className="h-7 px-2 text-xs" onClick={onDuplicateElement}>
              <Circle className="mr-1.5 h-3 w-3 fill-current opacity-20" />{c.duplicate}
            </Button>
          </CompactTip>
          <CompactTip label={`${c.delete} (Del)`}>
            <Button variant="ghost" size="icon" className={cn("h-7 w-7", "text-destructive hover:text-destructive")} onClick={onDeleteElement}>
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </CompactTip>
        </Group>
      </div>
    </TooltipProvider>
  );
};
