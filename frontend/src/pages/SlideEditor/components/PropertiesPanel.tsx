import React from "react";
import {
  MousePointer, AlignLeft, AlignCenter, AlignRight, AlignJustify,
  Bold, Italic, Underline, Strikethrough, Eraser,
  ChevronUp, ChevronDown, Copy, Trash2,
  Move, Maximize2, RotateCw, Type, Eye, Sun, Droplets,
  PaintBucket, Layers, SquareDashed, Blend, Space,
  BringToFront, SendToBack, Ban,
  Sigma, Divide, Variable, Parentheses, Calculator,
  Plus, ArrowRight,
} from "lucide-react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import type { SlideElement } from "../types";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";
import { useLanguage } from "@/contexts/LanguageContext";

// ─── Tooltip helper ───────────────────────────────────────────────────────────
const Tip = ({
  label,
  shortcut,
  desc,
  side = "left",
  children,
}: {
  label: string;
  shortcut?: string;
  desc?: string;
  side?: "top" | "bottom" | "left" | "right";
  children: React.ReactNode;
}) => (
  <Tooltip delayDuration={350}>
    <TooltipTrigger asChild>{children}</TooltipTrigger>
    <TooltipContent side={side} className="max-w-[200px] text-left">
      <p className="font-semibold text-xs leading-snug">
        {label}
        {shortcut && (
          <span className="ml-1.5 text-[10px] opacity-60 font-normal bg-muted/40 px-1 py-0.5 rounded">
            {shortcut}
          </span>
        )}
      </p>
      {desc && <p className="text-[11px] text-muted-foreground mt-0.5 leading-snug">{desc}</p>}
    </TooltipContent>
  </Tooltip>
);

// ─── Font options ─────────────────────────────────────────────────────────────
const FONT_FAMILIES = [
  // ── Google Fonts for Vietnamese & Slides ──
  { value: "'Be Vietnam Pro', sans-serif", label: "Be Vietnam Pro" },
  { value: "'Nunito', sans-serif", label: "Nunito" },
  { value: "'Nunito Sans', sans-serif", label: "Nunito Sans" },
  { value: "'Lato', sans-serif", label: "Lato" },
  { value: "'Raleway', sans-serif", label: "Raleway" },
  { value: "'Source Sans Pro', sans-serif", label: "Source Sans Pro" },
  { value: "'Poppins', sans-serif", label: "Poppins" },
  { value: "'Montserrat', sans-serif", label: "Montserrat" },
  { value: "'Roboto', sans-serif", label: "Roboto" },
  { value: "'Open Sans', sans-serif", label: "Open Sans" },
  { value: "'Inter', sans-serif", label: "Inter" },
  // ── Serif ──
  { value: "'Playfair Display', serif", label: "Playfair Display" },
  { value: "'Lora', serif", label: "Lora" },
  { value: "Georgia, serif", label: "Georgia" },
  { value: "'Times New Roman', serif", label: "Times New Roman" },
  // ── System ──
  { value: "Arial, sans-serif", label: "Arial" },
  { value: "Helvetica, sans-serif", label: "Helvetica" },
  { value: "Verdana, sans-serif", label: "Verdana" },
  { value: "Tahoma, sans-serif", label: "Tahoma" },
  { value: "'Trebuchet MS', sans-serif", label: "Trebuchet MS" },
  { value: "'Courier New', monospace", label: "Courier New" },
];

const FONT_WEIGHTS = [
  { value: "100", label: "Thin" },
  { value: "200", label: "ExtraLight" },
  { value: "300", label: "Light" },
  { value: "400", label: "Regular" },
  { value: "500", label: "Medium" },
  { value: "600", label: "SemiBold" },
  { value: "700", label: "Bold" },
  { value: "800", label: "ExtraBold" },
  { value: "900", label: "Black" },
];

const BORDER_STYLES = [
  { value: "none", label: "None" },
  { value: "solid", label: "Solid" },
  { value: "dashed", label: "Dashed" },
  { value: "dotted", label: "Dotted" },
];

// ─── Helpers ──────────────────────────────────────────────────────────────────
const matchFontFamily = (fontFamily: string | undefined): string => {
  if (!fontFamily) return FONT_FAMILIES[0].value;
  const normalized = fontFamily.replace(/["']/g, '').toLowerCase().trim();
  const match = FONT_FAMILIES.find(f => {
    const labelLower = f.label.toLowerCase();
    const valueLower = f.value.replace(/["']/g, '').toLowerCase();
    return normalized.includes(labelLower) ||
      normalized.startsWith(labelLower) ||
      valueLower.startsWith(normalized.split(',')[0].trim());
  });
  // Return original fontFamily if not in list — preserves slide's custom font instead of defaulting to Inter
  return match?.value || fontFamily;
};

const normalizeFontWeight = (fw: string | undefined): string => {
  if (!fw) return '400';
  if (fw === 'bold') return '700';
  if (fw === 'normal') return '400';
  return fw;
};

// ─── Reusable atoms ───────────────────────────────────────────────────────────
const SectionLabel = ({ icon: Icon, label }: { icon: React.ElementType; label: string }) => (
  <div className="flex items-center gap-1.5 mb-2">
    <Icon className="h-3 w-3 text-muted-foreground/70" />
    <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">{label}</span>
  </div>
);

// icon-labelled input row: icon | input
const IconInput = ({
  icon: Icon,
  title,
  ...inputProps
}: { icon: React.ElementType; title: string } & React.InputHTMLAttributes<HTMLInputElement>) => (
  <div className="flex items-center gap-1.5 bg-muted/30 rounded-md px-2 h-8 border border-border/50">
    <Icon className="h-3 w-3 text-muted-foreground shrink-0" title={title} />
    <input
      {...inputProps}
      className="flex-1 bg-transparent text-xs outline-none min-w-0 tabular-nums"
    />
  </div>
);

// slim slider row:  icon | slider | value badge
const IconSlider = ({
  icon: Icon,
  title,
  desc,
  min,
  max,
  step,
  value,
  onValueChange,
  displayValue,
}: {
  icon: React.ElementType;
  title: string;
  desc?: string;
  min: number; max: number; step: number;
  value: number;
  onValueChange: (v: number[]) => void;
  displayValue: string;
}) => (
  <Tooltip delayDuration={350}>
    <TooltipTrigger asChild>
      <div className="flex items-center gap-2 cursor-default">
        <Icon className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
        <Slider min={min} max={max} step={step} value={[value]} onValueChange={onValueChange} className="flex-1" />
        <span className="text-[10px] tabular-nums text-muted-foreground w-9 text-right shrink-0">{displayValue}</span>
      </div>
    </TooltipTrigger>
    <TooltipContent side="left" className="max-w-[180px]">
      <p className="font-semibold text-xs">{title}</p>
      {desc && <p className="text-[11px] text-muted-foreground mt-0.5 leading-snug">{desc}</p>}
    </TooltipContent>
  </Tooltip>
);

// ─── Props ────────────────────────────────────────────────────────────────────
interface PropertiesPanelProps {
  selectedElement: SlideElement | undefined;
  onUpdateElement: (id: string, updates: Partial<SlideElement> & { _filter?: string }) => void;
  slideCanvasRef?: React.RefObject<SlideCanvasHandle>;
  onDeleteElement?: () => void;
  onDuplicateElement?: () => void;
  onBringForward?: () => void;
  onSendBackward?: () => void;
}

// ─── Component ────────────────────────────────────────────────────────────────
export const PropertiesPanel = ({
  selectedElement,
  onUpdateElement,
  slideCanvasRef,
  onDeleteElement,
  onDuplicateElement,
  onBringForward,
  onSendBackward,
}: PropertiesPanelProps) => {
  const { t } = useLanguage();
  const el = selectedElement;

  if (!el) {
    return (
      <div className="w-72 border-l bg-background flex flex-col items-center justify-center gap-4 text-muted-foreground px-8">
        <div className="rounded-2xl bg-muted/60 p-5 flex items-center justify-center">
          <MousePointer className="h-7 w-7 opacity-30" />
        </div>
        <div className="text-center space-y-1.5">
          <p className="text-sm font-medium text-foreground/70">{t.editor_no_element}</p>
          <p className="text-xs text-muted-foreground/70 leading-relaxed">{t.editor_no_element_desc}</p>
        </div>
      </div>
    );
  }

  // Helper: update with filter recalculation
  const updateFilter = (patch: Partial<Pick<SlideElement, 'blur' | 'brightness' | 'saturation'>>) => {
    const blur = patch.blur ?? el.blur ?? 0;
    const brightness = patch.brightness ?? el.brightness ?? 100;
    const saturation = patch.saturation ?? el.saturation ?? 100;
    const filterStr = [
      blur > 0 ? `blur(${blur}px)` : '',
      brightness !== 100 ? `brightness(${brightness}%)` : '',
      saturation !== 100 ? `saturate(${saturation}%)` : '',
    ].filter(Boolean).join(' ');
    onUpdateElement(el.id, { ...patch, _filter: filterStr || 'none' } as any);
  };

  const handleFormat = (command: string, value?: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    slideCanvasRef?.current?.execFormat(command, value);
  };

  const typeLabel: Record<string, string> = {
    text: t.editor_type_text,
    image: t.editor_type_image,
    shape: t.editor_type_shape,
    video: t.editor_type_video,
    equation: 'Equation',
  };

  return (
    <TooltipProvider>
    <div
      className="w-72 border-l bg-background flex flex-col h-full overflow-y-auto overflow-x-hidden [&::-webkit-scrollbar]:hidden"
      style={{ scrollbarWidth: "none" }}
    >

      {/* ── Header + actions ── */}
      <div className="px-3 py-2.5 border-b flex items-center justify-between">
        <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-widest">
          {typeLabel[el.type] ?? el.type}
        </span>
        <div className="flex items-center gap-0.5">
          <Tip label={t.editor_send_backward} desc={t.editor_send_backward_desc}>
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => onSendBackward?.()}>
              <SendToBack className="h-3.5 w-3.5" />
            </Button>
          </Tip>
          <Tip label={t.editor_bring_forward} desc={t.editor_bring_forward_desc}>
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => onBringForward?.()}>
              <BringToFront className="h-3.5 w-3.5" />
            </Button>
          </Tip>
          <Separator orientation="vertical" className="h-4 mx-0.5" />
          <Tip label={t.editor_duplicate} shortcut="Ctrl+D" desc={t.editor_duplicate_desc}>
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => onDuplicateElement?.()}>
              <Copy className="h-3.5 w-3.5" />
            </Button>
          </Tip>
          <Tip label={t.editor_delete} shortcut="Del" desc={t.editor_delete_desc}>
            <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive hover:text-destructive" onClick={() => onDeleteElement?.()}>
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </Tip>
        </div>
      </div>

      <div
        className="p-3 space-y-4 overflow-y-auto [&::-webkit-scrollbar]:hidden"
        style={{ scrollbarWidth: "none" }}
      >

        {/* ── 1. POSITION & SIZE ── */}
        <div>
          <SectionLabel icon={Move} label={t.editor_section_transform} />
          <div className="grid grid-cols-2 gap-1.5">
            <IconInput icon={() => <span className="text-[10px] font-bold text-muted-foreground">X</span>} title={t.editor_prop_x}
              type="number" step={0.01} value={el.x}
              onChange={e => onUpdateElement(el.id, { x: Number((e.target as HTMLInputElement).value) })} />
            <IconInput icon={() => <span className="text-[10px] font-bold text-muted-foreground">Y</span>} title={t.editor_prop_y}
              type="number" step={0.01} value={el.y}
              onChange={e => onUpdateElement(el.id, { y: Number((e.target as HTMLInputElement).value) })} />
            <IconInput icon={() => <span className="text-[10px] font-bold text-muted-foreground">W</span>} title={t.editor_prop_width}
              type="number" step={0.01} value={el.width}
              onChange={e => onUpdateElement(el.id, { width: Number((e.target as HTMLInputElement).value) })} />
            <IconInput icon={() => <span className="text-[10px] font-bold text-muted-foreground">H</span>} title={t.editor_prop_height}
              type="number" step={0.01} value={el.height}
              onChange={e => onUpdateElement(el.id, { height: Number((e.target as HTMLInputElement).value) })} />
          </div>
          <div className="mt-1.5">
            <IconSlider
              icon={RotateCw} title={t.editor_prop_rotation}
              min={-180} max={180} step={1}
              value={el.rotation || 0}
              onValueChange={v => onUpdateElement(el.id, { rotation: v[0] })}
              displayValue={`${el.rotation || 0}°`}
            />
          </div>
        </div>

        <Separator />

        {/* ── 2. TYPOGRAPHY (text only) ── */}
        {el.type === 'text' && (
          <>
            <div>
              <SectionLabel icon={Type} label={t.editor_section_typography} />

              {/* Font family */}
              <Select value={matchFontFamily(el.fontFamily)}
                onValueChange={v => onUpdateElement(el.id, { fontFamily: v })}>
                <SelectTrigger className="h-8 text-xs w-full mb-1.5"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {FONT_FAMILIES.map(f => (
                    <SelectItem key={f.value} value={f.value} style={{ fontFamily: f.value }}>{f.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Weight + Size + LineH row */}
              <div className="grid grid-cols-3 gap-1.5 mb-1.5">
                <Select value={normalizeFontWeight(el.fontWeight)}
                  onValueChange={v => onUpdateElement(el.id, { fontWeight: v })}>
                  <SelectTrigger className="h-8 text-xs col-span-1"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {FONT_WEIGHTS.map(w => (
                      <SelectItem key={w.value} value={w.value}>{w.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <IconInput icon={() => <span className="text-[9px] font-bold text-muted-foreground">Aa</span>} title={t.editor_prop_font_size}
                  type="number" value={el.fontSize || 16} min={8} max={500}
                  onChange={e => onUpdateElement(el.id, { fontSize: Number((e.target as HTMLInputElement).value) })} />
                <IconInput icon={() => <span className="text-[9px] font-bold text-muted-foreground">≡</span>} title={t.editor_prop_line_height}
                  type="number" value={parseFloat(el.lineHeight || '1.4')} min={0.5} max={5} step={0.1}
                  onChange={e => onUpdateElement(el.id, { lineHeight: (e.target as HTMLInputElement).value })} />
              </div>

              {/* Letter spacing + Text color */}
              <div className="grid grid-cols-2 gap-1.5 mb-1.5">
                <IconInput icon={Space} title={t.editor_prop_letter_spacing}
                  type="number" value={parseFloat(el.letterSpacing || '0')} step={0.5}
                  onChange={e => onUpdateElement(el.id, { letterSpacing: `${(e.target as HTMLInputElement).value}px` })} />
                {/* Text color swatch */}
                <div className="flex items-center gap-1.5 bg-muted/30 rounded-md px-2 h-8 border border-border/50" title={t.editor_prop_text_color}>
                  <span className="text-[9px] font-bold text-muted-foreground shrink-0">A</span>
                  <input type="color" value={el.color || '#000000'}
                    onChange={e => onUpdateElement(el.id, { color: e.target.value })}
                    className="flex-1 h-5 rounded cursor-pointer border-0 outline-none bg-transparent" />
                </div>
              </div>

              {/* Text align */}
              <div className="flex border rounded-md p-0.5 bg-muted/20 gap-0.5 mb-1.5">
                {([
                  { value: 'left', Icon: AlignLeft, title: t.editor_align_left, desc: t.editor_align_left_desc },
                  { value: 'center', Icon: AlignCenter, title: t.editor_align_center, desc: t.editor_align_center_desc },
                  { value: 'right', Icon: AlignRight, title: t.editor_align_right, desc: t.editor_align_right_desc },
                  { value: 'justify', Icon: AlignJustify, title: t.editor_align_justify, desc: t.editor_align_justify_desc },
                ] as const).map(({ value, Icon, title, desc }) => (
                  <Tip key={value} label={title} desc={desc} side="bottom">
                    <Button
                      variant={el.textAlign === value ? 'secondary' : 'ghost'}
                      size="icon" className="h-7 flex-1"
                      onClick={() => onUpdateElement(el.id, { textAlign: value })}>
                      <Icon className="h-3.5 w-3.5" />
                    </Button>
                  </Tip>
                ))}
              </div>

              {/* Format buttons */}
              <div className="flex border rounded-md p-0.5 bg-muted/20 gap-0.5">
                {[
                  { cmd: 'bold', title: t.editor_fmt_bold, desc: t.editor_fmt_bold_desc, Icon: Bold },
                  { cmd: 'italic', title: t.editor_fmt_italic, desc: t.editor_fmt_italic_desc, Icon: Italic },
                  { cmd: 'underline', title: t.editor_fmt_underline, desc: t.editor_fmt_underline_desc, Icon: Underline },
                  { cmd: 'strikeThrough', title: t.editor_fmt_strikethrough, desc: t.editor_fmt_strikethrough_desc, Icon: Strikethrough },
                  { cmd: 'removeFormat', title: t.editor_fmt_clear, desc: t.editor_fmt_clear_desc, Icon: Eraser },
                ].map(({ cmd, title, desc, Icon }) => (
                  <Tip key={cmd} label={title} desc={desc} side="bottom">
                    <Button variant="ghost" size="icon" className="h-7 flex-1"
                      onMouseDown={handleFormat(cmd)}>
                      <Icon className="h-3.5 w-3.5" />
                    </Button>
                  </Tip>
                ))}
              </div>
            </div>

            <Separator />
          </>
        )}



        {/* ── 2b. INSERT MATH (equation only) ── */}
        {el.type === 'equation' && (
          <div className="space-y-3">
            <SectionLabel icon={Type} label={t.editor_section_typography} />

            <div className="grid grid-cols-2 gap-1.5">
              {/* Size */}
              <IconInput icon={() => <span className="text-[9px] font-bold text-muted-foreground">Aa</span>} title={t.editor_prop_font_size}
                type="number" value={el.fontSize || 32} min={8} max={500}
                onChange={e => onUpdateElement(el.id, { fontSize: Number((e.target as HTMLInputElement).value) })} />

              {/* Color */}
              <div className="flex items-center gap-1.5 bg-muted/30 rounded-md px-2 h-8 border border-border/50" title={t.editor_prop_text_color}>
                <span className="text-[9px] font-bold text-muted-foreground shrink-0">A</span>
                <input type="color" value={el.color || '#333333'}
                  onChange={e => onUpdateElement(el.id, { color: e.target.value })}
                  className="flex-1 h-5 rounded cursor-pointer border-0 outline-none bg-transparent" />
              </div>
            </div>

            {/* Align Buttons for Equation */}
            <div className="flex border rounded-md p-0.5 bg-muted/20 gap-0.5">
              {([
                { value: 'left', Icon: AlignLeft, title: t.editor_align_left },
                { value: 'center', Icon: AlignCenter, title: t.editor_align_center },
                { value: 'right', Icon: AlignRight, title: t.editor_align_right },
              ] as const).map(({ value, Icon, title }) => (
                <Tip key={value} label={title} side="bottom">
                  <Button
                    variant={el.textAlign === value ? 'secondary' : 'ghost'}
                    size="icon" className="h-7 flex-1"
                    onClick={() => onUpdateElement(el.id, { textAlign: value } as any)}>
                    <Icon className="h-3.5 w-3.5" />
                  </Button>
                </Tip>
              ))}
            </div>

            <Separator className="mt-2" />
            
            <SectionLabel icon={Sigma} label="Insert Math" />
            <Accordion type="multiple" className="w-full space-y-1">
              {[
                { id: 'frac', label: 'Phân số & Căn', icon: Divide, items: [
                  { s: '\\frac{\\placeholder}{\\placeholder}', l: 'a/b' },
                  { s: '\\sqrt{\\placeholder}', l: '√x' },
                  { s: '\\sqrt[\\placeholder]{\\placeholder}', l: 'ⁿ√x' }
                ]},
                { id: 'script', label: 'Chỉ số', icon: Variable, items: [
                  { s: '{\\placeholder}^{\\placeholder}', l: 'xⁿ' },
                  { s: '{\\placeholder}_{\\placeholder}', l: 'xₙ' },
                  { s: '{\\placeholder}^{\\placeholder}_{\\placeholder}', l: 'xⁿₘ' }
                ]},
                { id: 'op', label: 'Tổng & Tích phân', icon: Sigma, items: [
                  { s: '\\int_{\\placeholder}^{\\placeholder}', l: '∫' },
                  { s: '\\sum_{\\placeholder}^{\\placeholder}', l: 'Σ' },
                  { s: '\\prod_{\\placeholder}^{\\placeholder}', l: 'Π' },
                  { s: '\\lim_{\\placeholder \\to \\placeholder}', l: 'lim' }
                ]},
                { id: 'bracket', label: 'Ngoặc', icon: Parentheses, items: [
                  { s: '\\left( \\placeholder \\right)', l: '( )' },
                  { s: '\\left[ \\placeholder \\right]', l: '[ ]' },
                  { s: '\\left\\{ \\placeholder \\right\\}', l: '{ }' },
                  { s: '\\left| \\placeholder \\right|', l: '| |' }
                ]},
                { id: 'greek', label: 'Ký hiệu Hy Lạp', icon: () => <span className="text-xs font-serif">αβ</span>, items: [
                  { s: '\\alpha', l: 'α' }, { s: '\\beta', l: 'β' }, { s: '\\gamma', l: 'γ' },
                  { s: '\\delta', l: 'δ' }, { s: '\\epsilon', l: 'ε' }, { s: '\\theta', l: 'θ' },
                  { s: '\\lambda', l: 'λ' }, { s: '\\pi', l: 'π' }, { s: '\\sigma', l: 'σ' },
                  { s: '\\omega', l: 'ω' }, { s: '\\Delta', l: 'Δ' }, { s: '\\Omega', l: 'Ω' }
                ]},
                { id: 'symbol', label: 'Toán tử & Ký hiệu', icon: Plus, items: [
                  { s: '\\pm', l: '±' }, { s: '\\infty', l: '∞' }, { s: '\\neq', l: '≠' },
                  { s: '\\approx', l: '≈' }, { s: '\\leq', l: '≤' }, { s: '\\geq', l: '≥' },
                  { s: '\\forall', l: '∀' }, { s: '\\exists', l: '∃' }, { s: '\\in', l: '∈' },
                  { s: '\\notin', l: '∉' }, { s: '\\subset', l: '⊂' }, { s: '\\cup', l: '∪' }
                ]},
                { id: 'arrow', label: 'Mũi tên', icon: ArrowRight, items: [
                  { s: '\\rightarrow', l: '→' }, { s: '\\leftarrow', l: '←' },
                  { s: '\\Rightarrow', l: '⇒' }, { s: '\\Leftarrow', l: '⇐' },
                  { s: '\\Leftrightarrow', l: '⇔' }, { s: '\\implies', l: '⟹' }
                ]},
                { id: 'common', label: 'Công thức mẫu', icon: Calculator, items: [
                  { s: 'a^2 + b^2 = c^2', l: 'Pythagore' },
                  { s: 'x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}', l: 'Bậc 2' },
                  { s: 'E = mc^2', l: 'Einstein' },
                  { s: 'e^{i\\pi} + 1 = 0', l: 'Euler' }
                ]},
                { id: 'matrix', label: 'Ma trận', icon: () => <span className="grid grid-cols-2 gap-0.5 w-3 h-3"><div className="bg-current opacity-50" /><div className="bg-current opacity-50" /><div className="bg-current opacity-50" /><div className="bg-current opacity-50" /></span>, items: [
                  { s: '\\begin{pmatrix} \\placeholder & \\placeholder \\\\ \\placeholder & \\placeholder \\end{pmatrix}', l: '2x2' },
                  { s: '\\begin{bmatrix} \\placeholder & \\placeholder \\\\ \\placeholder & \\placeholder \\end{bmatrix}', l: '[2x2]' }
                ]},
              ].map(cat => (
                <AccordionItem key={cat.id} value={cat.id} className="border rounded-md px-2 bg-muted/10">
                  <AccordionTrigger className="py-2 hover:no-underline">
                    <div className="flex items-center gap-2">
                      <cat.icon className="h-3.5 w-3.5 text-muted-foreground" />
                      <span className="text-xs font-medium text-foreground/80">{cat.label}</span>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="pb-2 pt-1">
                    <div className="flex flex-wrap gap-1.5 ">
                      {cat.items.map((item, idx) => (
                        <Button
                          key={idx}
                          variant="outline"
                          size="sm"
                          className="h-8 min-w-[40px] px-2 text-[11px] font-serif hover:bg-primary/5 hover:text-primary hover:border-primary/30"
                          onClick={() => slideCanvasRef?.current?.insertMath(item.s)}
                        >
                          {item.l}
                        </Button>
                      ))}
                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
            <Separator className="mt-4" />
          </div>
        )}

        {/* ── 3. APPEARANCE ── */}
        <div>
          <SectionLabel icon={PaintBucket} label={t.editor_section_appearance} />

          {/* Fill */}
          {(() => {
            const isTransparent = !el.fillColor || el.fillColor === 'transparent' || el.fillColor === 'none';
            return (
              <div className="flex items-center gap-1.5 mb-1.5">
                <div className={cn(
                  "flex items-center gap-1.5 flex-1 rounded-md px-2 py-1.5 border",
                  isTransparent
                    ? "bg-muted/10 border-border/30 opacity-40 pointer-events-none"
                    : "bg-muted/30 border-border/50"
                )}>
                  <PaintBucket className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                  <input type="color" value={isTransparent ? '#ffffff' : (el.fillColor || '#ffffff')}
                    onChange={e => onUpdateElement(el.id, { fillColor: e.target.value })}
                    className="h-5 w-7 rounded cursor-pointer border-0 outline-none bg-transparent shrink-0" />
                  <input type="text" value={isTransparent ? '' : (el.fillColor || '')}
                    onChange={e => onUpdateElement(el.id, { fillColor: e.target.value })}
                    className="flex-1 bg-transparent text-xs outline-none font-mono min-w-0" placeholder="#ffffff" />
                </div>
                <Tip label={t.editor_no_fill} desc={t.editor_no_fill_desc} side="left">
                  <Button
                    variant={isTransparent ? 'secondary' : 'ghost'}
                    size="icon"
                    className="h-8 w-8 shrink-0"
                    onClick={() => onUpdateElement(el.id, { fillColor: isTransparent ? '#ffffff' : 'transparent' })}>
                    <Ban className="h-3.5 w-3.5" />
                  </Button>
                </Tip>
              </div>
            );
          })()}

          {/* Border – row 1: width + color */}
          <div className="flex items-center gap-1.5 mb-1">
            <div className="flex items-center gap-1 flex-1 bg-muted/30 rounded-md px-2 h-8 border border-border/50" title={t.editor_prop_border_width}>
              <SquareDashed className="h-3 w-3 text-muted-foreground shrink-0" />
              <input type="number" value={el.strokeWidth || 0} min={0}
                onChange={e => onUpdateElement(el.id, { strokeWidth: Number((e.target as HTMLInputElement).value) })}
                className="flex-1 bg-transparent text-xs outline-none min-w-0 tabular-nums" />
            </div>
            <input type="color" value={el.strokeColor || '#000000'}
              onChange={e => onUpdateElement(el.id, { strokeColor: e.target.value })}
              title={t.editor_prop_border_color}
              className="h-8 w-8 rounded-md cursor-pointer border border-border/50 bg-muted/30 p-0.5 shrink-0" />
          </div>
          {/* Border – row 2: style */}
          <div className="mb-1.5">
            <Select value={el.strokeStyle || 'none'} onValueChange={v => onUpdateElement(el.id, { strokeStyle: v })}>
              <SelectTrigger className="h-8 text-xs w-full"><SelectValue /></SelectTrigger>
              <SelectContent>
                {BORDER_STYLES.map(b => <SelectItem key={b.value} value={b.value}>{b.label}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>

          {/* Border radius */}
          <IconSlider icon={Maximize2} title={t.editor_prop_border_radius} desc={t.editor_prop_border_radius_desc}
            min={0} max={200} step={1}
            value={el.borderRadius || 0}
            onValueChange={v => onUpdateElement(el.id, { borderRadius: v[0] })}
            displayValue={`${el.borderRadius || 0}px`}
          />

          {/* Shadow */}
          <div className="flex items-center gap-1.5 bg-muted/30 rounded-md px-2 h-8 border border-border/50 mt-1.5" title={t.editor_prop_box_shadow}>
            <Layers className="h-3 w-3 text-muted-foreground shrink-0" />
            <input type="text" value={el.shadow || ''}
              placeholder="2px 4px 12px rgba(0,0,0,.3)"
              onChange={e => onUpdateElement(el.id, { shadow: e.target.value })}
              className="flex-1 bg-transparent text-xs outline-none min-w-0 font-mono" />
          </div>
        </div>

        <Separator />

        {/* ── 4. EFFECTS ── */}
        <div>
          <SectionLabel icon={Blend} label={t.editor_section_effects} />
          <div className="space-y-2.5">
            <IconSlider icon={Eye} title={t.editor_prop_opacity} desc={t.editor_prop_opacity_desc}
              min={0} max={1} step={0.05}
              value={el.opacity ?? 1}
              onValueChange={v => onUpdateElement(el.id, { opacity: v[0] })}
              displayValue={`${Math.round((el.opacity ?? 1) * 100)}%`}
            />
            <IconSlider icon={Blend} title={t.editor_prop_blur} desc={t.editor_prop_blur_desc}
              min={0} max={20} step={0.5}
              value={el.blur ?? 0}
              onValueChange={v => updateFilter({ blur: v[0] })}
              displayValue={`${el.blur || 0}px`}
            />
            <IconSlider icon={Sun} title={t.editor_prop_brightness} desc={t.editor_prop_brightness_desc}
              min={0} max={200} step={5}
              value={el.brightness ?? 100}
              onValueChange={v => updateFilter({ brightness: v[0] })}
              displayValue={`${el.brightness ?? 100}%`}
            />
            <IconSlider icon={Droplets} title={t.editor_prop_saturation} desc={t.editor_prop_saturation_desc}
              min={0} max={200} step={5}
              value={el.saturation ?? 100}
              onValueChange={v => updateFilter({ saturation: v[0] })}
              displayValue={`${el.saturation ?? 100}%`}
            />
          </div>
        </div>

        <Separator />

        {/* ── 5. LAYER ORDER ── */}
        <div>
          <SectionLabel icon={Layers} label={t.editor_section_layer} />
          <div className="flex items-center gap-1.5">
            <Tip label={t.editor_send_backward} desc={t.editor_send_backward_desc}>
              <Button variant="outline" size="icon" className="h-8 w-8 shrink-0" onClick={() => onSendBackward?.()}>
                <ChevronDown className="h-4 w-4" />
              </Button>
            </Tip>
            <input type="number" value={el.zIndex || 0}
              onChange={e => onUpdateElement(el.id, { zIndex: Number((e.target as HTMLInputElement).value) })}
              className="flex-1 h-8 text-center text-xs bg-muted/30 border border-border/50 rounded-md outline-none tabular-nums" />
            <Tip label={t.editor_bring_forward} desc={t.editor_bring_forward_desc}>
              <Button variant="outline" size="icon" className="h-8 w-8 shrink-0" onClick={() => onBringForward?.()}>
                <ChevronUp className="h-4 w-4" />
              </Button>
            </Tip>
          </div>

          {/* Padding */}
          <div className="mt-3">
            <div className="flex items-center gap-1 mb-1.5">
              <Maximize2 className="h-3 w-3 text-muted-foreground" />
              <span className="text-[10px] text-muted-foreground">{t.editor_padding}</span>
            </div>
            <div className="grid grid-cols-4 gap-1">
              {([
                { key: 'paddingTop' as const, title: '↑ Top' },
                { key: 'paddingRight' as const, title: '→ Right' },
                { key: 'paddingBottom' as const, title: '↓ Bottom' },
                { key: 'paddingLeft' as const, title: '← Left' },
              ]).map(({ key, title }) => (
                <input key={key} type="number" value={el[key] || 0} min={0} title={title}
                  onChange={e => onUpdateElement(el.id, { [key]: Number((e.target as HTMLInputElement).value) })}
                  className="h-7 text-xs text-center bg-muted/30 border border-border/50 rounded-md outline-none tabular-nums" />
              ))}
            </div>
            <div className="grid grid-cols-4 gap-1 mt-0.5">
              {['T','R','B','L'].map(l => (
                <span key={l} className="text-[9px] text-muted-foreground text-center">{l}</span>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
    </TooltipProvider>
  );
};
