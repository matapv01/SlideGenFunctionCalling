import React from "react";
import { MousePointer, AlignLeft, AlignCenter, AlignRight, AlignJustify, Bold, Italic, Underline, Strikethrough, Eraser, ChevronUp, ChevronDown, Copy, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { SlideElement } from "../types";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";

// ─── Font options ─────────────────────────────────────────────────────────────
const FONT_FAMILIES = [
  { value: "Inter, sans-serif", label: "Inter" },
  { value: "Arial, sans-serif", label: "Arial" },
  { value: "Helvetica, sans-serif", label: "Helvetica" },
  { value: "'Times New Roman', serif", label: "Times New Roman" },
  { value: "Georgia, serif", label: "Georgia" },
  { value: "'Courier New', monospace", label: "Courier New" },
  { value: "Verdana, sans-serif", label: "Verdana" },
  { value: "Tahoma, sans-serif", label: "Tahoma" },
  { value: "'Trebuchet MS', sans-serif", label: "Trebuchet MS" },
  { value: "'Roboto', sans-serif", label: "Roboto" },
  { value: "'Open Sans', sans-serif", label: "Open Sans" },
  { value: "'Montserrat', sans-serif", label: "Montserrat" },
  { value: "'Playfair Display', serif", label: "Playfair Display" },
  { value: "'Lora', serif", label: "Lora" },
  { value: "'Poppins', sans-serif", label: "Poppins" },
  { value: "Nunito, sans-serif", label: "Nunito" },
];

const FONT_WEIGHTS = [
  { value: "100", label: "Thin (100)" },
  { value: "200", label: "Extra Light (200)" },
  { value: "300", label: "Light (300)" },
  { value: "400", label: "Regular (400)" },
  { value: "500", label: "Medium (500)" },
  { value: "600", label: "Semi Bold (600)" },
  { value: "700", label: "Bold (700)" },
  { value: "800", label: "Extra Bold (800)" },
  { value: "900", label: "Black (900)" },
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
  return match?.value || FONT_FAMILIES[0].value;
};

const normalizeFontWeight = (fw: string | undefined): string => {
  if (!fw) return '400';
  if (fw === 'bold') return '700';
  if (fw === 'normal') return '400';
  return fw;
};

// Section header
const SectionTitle = ({ children }: { children: React.ReactNode }) => (
  <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">{children}</h4>
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
  const el = selectedElement;

  if (!el) {
    return (
      <div className="w-72 border-l bg-background p-6 flex flex-col items-center justify-center text-muted-foreground">
        <MousePointer className="h-12 w-12 mb-4 opacity-20" />
        <p className="text-sm text-center">Select an element to edit its properties</p>
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

  // execFormat handler (mousedown to preserve selection)
  const handleFormat = (command: string, value?: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    slideCanvasRef?.current?.execFormat(command, value);
  };

  return (
    <div className="w-72 border-l bg-background flex flex-col h-full overflow-y-auto">
      {/* Header */}
      <div className="p-4 border-b">
        <h3 className="font-semibold text-sm flex items-center gap-2">
          Properties <span className="text-xs text-muted-foreground font-normal">({el.type})</span>
        </h3>
      </div>

      <div className="p-4 space-y-6">

        {/* ── 1. POSITION & SIZE ── */}
        <div className="space-y-3">
          <SectionTitle>Position &amp; Size</SectionTitle>
          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1">
              <Label className="text-xs">X</Label>
              <Input type="number" value={Math.round(el.x)}
                onChange={e => onUpdateElement(el.id, { x: Number(e.target.value) })} className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Y</Label>
              <Input type="number" value={Math.round(el.y)}
                onChange={e => onUpdateElement(el.id, { y: Number(e.target.value) })} className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Width</Label>
              <Input type="number" value={Math.round(el.width)}
                onChange={e => onUpdateElement(el.id, { width: Number(e.target.value) })} className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Height</Label>
              <Input type="number" value={Math.round(el.height)}
                onChange={e => onUpdateElement(el.id, { height: Number(e.target.value) })} className="h-8" />
            </div>
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Rotation ({el.rotation || 0}°)</Label>
            <Slider min={-180} max={180} step={1}
              value={[el.rotation || 0]}
              onValueChange={v => onUpdateElement(el.id, { rotation: v[0] })} />
          </div>
        </div>

        <Separator />

        {/* ── 2. TYPOGRAPHY (text only) ── */}
        {el.type === 'text' && (
          <>
            <div className="space-y-3">
              <SectionTitle>Typography</SectionTitle>

              <div className="space-y-1">
                <Label className="text-xs">Font Family</Label>
                <Select value={matchFontFamily(el.fontFamily)}
                  onValueChange={v => onUpdateElement(el.id, { fontFamily: v })}>
                  <SelectTrigger className="h-8 text-xs"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {FONT_FAMILIES.map(f => (
                      <SelectItem key={f.value} value={f.value} style={{ fontFamily: f.value }}>
                        {f.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1">
                <Label className="text-xs">Font Weight</Label>
                <Select value={normalizeFontWeight(el.fontWeight)}
                  onValueChange={v => onUpdateElement(el.id, { fontWeight: v })}>
                  <SelectTrigger className="h-8 text-xs"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {FONT_WEIGHTS.map(w => (
                      <SelectItem key={w.value} value={w.value}>{w.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <Label className="text-xs">Font Size</Label>
                  <Input type="number" value={el.fontSize || 16} min={8} max={500}
                    onChange={e => onUpdateElement(el.id, { fontSize: Number(e.target.value) })} className="h-8" />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Line Height</Label>
                  <Input type="number" value={parseFloat(el.lineHeight || '1.4')} min={0.5} max={5} step={0.1}
                    onChange={e => onUpdateElement(el.id, { lineHeight: e.target.value })} className="h-8" />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Letter Spacing</Label>
                  <Input type="number" value={parseFloat(el.letterSpacing || '0')} step={0.5}
                    onChange={e => onUpdateElement(el.id, { letterSpacing: `${e.target.value}px` })} className="h-8" />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Text Color</Label>
                  <Input type="color" value={el.color || '#000000'}
                    onChange={e => onUpdateElement(el.id, { color: e.target.value })} className="h-8 w-full p-0" />
                </div>
              </div>

              {/* Text Align */}
              <div className="flex border rounded-md p-1 bg-muted/20 gap-1">
                {([
                  { value: 'left', Icon: AlignLeft },
                  { value: 'center', Icon: AlignCenter },
                  { value: 'right', Icon: AlignRight },
                  { value: 'justify', Icon: AlignJustify },
                ] as const).map(({ value, Icon }) => (
                  <Button key={value}
                    variant={el.textAlign === value ? 'secondary' : 'ghost'}
                    size="icon" className="h-6 flex-1"
                    onClick={() => onUpdateElement(el.id, { textAlign: value })}>
                    <Icon className="h-3 w-3" />
                  </Button>
                ))}
              </div>
            </div>

            {/* Text formatting for selected text (execCommand) */}
            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">Format Selected Text</Label>
              <div className="flex border rounded-md p-1 bg-muted/20 gap-1">
                {[
                  { cmd: 'bold', title: 'Bold', Icon: Bold },
                  { cmd: 'italic', title: 'Italic', Icon: Italic },
                  { cmd: 'underline', title: 'Underline', Icon: Underline },
                  { cmd: 'strikeThrough', title: 'Strikethrough', Icon: Strikethrough },
                  { cmd: 'removeFormat', title: 'Clear', Icon: Eraser },
                ].map(({ cmd, title, Icon }) => (
                  <Button key={cmd} variant="ghost" size="icon" className="h-6 flex-1" title={title}
                    onMouseDown={handleFormat(cmd)}>
                    <Icon className="h-3 w-3" />
                  </Button>
                ))}
              </div>
            </div>

            <Separator />
          </>
        )}

        {/* ── 3. APPEARANCE ── */}
        <div className="space-y-3">
          <SectionTitle>Appearance</SectionTitle>

          <div className="space-y-1">
            <Label className="text-xs">Fill Color</Label>
            <div className="flex gap-2">
              <Input type="color" value={el.fillColor || '#ffffff'}
                onChange={e => onUpdateElement(el.id, { fillColor: e.target.value })} className="w-10 h-8 p-0 border-0" />
              <Input type="text" value={el.fillColor || ''}
                onChange={e => onUpdateElement(el.id, { fillColor: e.target.value })} className="h-8 flex-1 font-mono text-xs" />
            </div>
          </div>

          {/* Border */}
          <div className="space-y-1">
            <Label className="text-xs">Border</Label>
            <div className="grid grid-cols-3 gap-1">
              <Input type="number" value={el.strokeWidth || 0} min={0} placeholder="Width"
                onChange={e => onUpdateElement(el.id, { strokeWidth: Number(e.target.value) })} className="h-8 text-xs" />
              <Select value={el.strokeStyle || 'none'}
                onValueChange={v => onUpdateElement(el.id, { strokeStyle: v })}>
                <SelectTrigger className="h-8 text-xs"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {BORDER_STYLES.map(b => (
                    <SelectItem key={b.value} value={b.value}>{b.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Input type="color" value={el.strokeColor || '#000000'}
                onChange={e => onUpdateElement(el.id, { strokeColor: e.target.value })} className="h-8 p-0 border-0" />
            </div>
          </div>

          <div className="space-y-1">
            <Label className="text-xs">Border Radius ({el.borderRadius || 0}px)</Label>
            <Slider min={0} max={200} step={1}
              value={[el.borderRadius || 0]}
              onValueChange={v => onUpdateElement(el.id, { borderRadius: v[0] })} />
          </div>

          {/* Box Shadow */}
          <div className="space-y-1">
            <Label className="text-xs">Box Shadow</Label>
            <Input type="text" value={el.shadow || ''}
              placeholder="e.g. 2px 4px 12px rgba(0,0,0,0.3)"
              onChange={e => onUpdateElement(el.id, { shadow: e.target.value })} className="h-8 text-xs font-mono" />
          </div>
        </div>

        <Separator />

        {/* ── 4. EFFECTS ── */}
        <div className="space-y-3">
          <SectionTitle>Effects</SectionTitle>

          <div className="space-y-1">
            <Label className="text-xs">Opacity ({Math.round((el.opacity ?? 1) * 100)}%)</Label>
            <Slider min={0} max={1} step={0.05}
              value={[el.opacity ?? 1]}
              onValueChange={v => onUpdateElement(el.id, { opacity: v[0] })} />
          </div>

          <div className="space-y-1">
            <Label className="text-xs">Blur ({el.blur || 0}px)</Label>
            <Slider min={0} max={20} step={0.5}
              value={[el.blur ?? 0]}
              onValueChange={v => updateFilter({ blur: v[0] })} />
          </div>

          <div className="space-y-1">
            <Label className="text-xs">Brightness ({el.brightness ?? 100}%)</Label>
            <Slider min={0} max={200} step={5}
              value={[el.brightness ?? 100]}
              onValueChange={v => updateFilter({ brightness: v[0] })} />
          </div>

          <div className="space-y-1">
            <Label className="text-xs">Saturation ({el.saturation ?? 100}%)</Label>
            <Slider min={0} max={200} step={5}
              value={[el.saturation ?? 100]}
              onValueChange={v => updateFilter({ saturation: v[0] })} />
          </div>
        </div>

        <Separator />

        {/* ── 5. LAYOUT ── */}
        <div className="space-y-3">
          <SectionTitle>Layout</SectionTitle>

          <div className="space-y-1">
            <Label className="text-xs">Z-Index (Layer Order)</Label>
            <div className="flex items-center gap-1">
              <Button variant="outline" size="icon" className="h-8 w-8 shrink-0"
                onClick={() => onSendBackward?.()}
                title="Send Backward">
                <ChevronDown className="h-4 w-4" />
              </Button>
              <Input type="number" value={el.zIndex || 0}
                onChange={e => onUpdateElement(el.id, { zIndex: Number(e.target.value) })} className="h-8 text-center" />
              <Button variant="outline" size="icon" className="h-8 w-8 shrink-0"
                onClick={() => onBringForward?.()}
                title="Bring Forward">
                <ChevronUp className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="space-y-1">
            <Label className="text-xs">Padding (T / R / B / L)</Label>
            <div className="grid grid-cols-4 gap-1">
              {([ 
                { key: 'paddingTop' as const, label: 'T' },
                { key: 'paddingRight' as const, label: 'R' },
                { key: 'paddingBottom' as const, label: 'B' },
                { key: 'paddingLeft' as const, label: 'L' },
              ]).map(({ key, label }) => (
                <div key={key} className="space-y-0.5">
                  <Label className="text-[10px] text-muted-foreground">{label}</Label>
                  <Input type="number" value={el[key] || 0} min={0}
                    onChange={e => onUpdateElement(el.id, { [key]: Number(e.target.value) })}
                    className="h-7 text-xs px-1" />
                </div>
              ))}
            </div>
          </div>
        </div>

        <Separator />

        {/* ── 6. QUICK ACTIONS ── */}
        <div className="space-y-2">
          <SectionTitle>Quick Actions</SectionTitle>
          <div className="flex gap-2">
            <Button variant="outline" className="flex-1 h-8 text-xs gap-1"
              onClick={() => onDuplicateElement?.()}>
              <Copy className="h-3 w-3" /> Duplicate
            </Button>
            <Button variant="destructive" className="flex-1 h-8 text-xs gap-1"
              onClick={() => onDeleteElement?.()}>
              <Trash2 className="h-3 w-3" /> Delete
            </Button>
          </div>
        </div>

      </div>
    </div>
  );
};
