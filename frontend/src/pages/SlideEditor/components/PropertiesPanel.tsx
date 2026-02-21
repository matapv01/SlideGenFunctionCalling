import { MousePointer, AlignLeft, AlignCenter, AlignRight, Bold, Italic, Underline } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { SlideElement } from "../types";

// Font Family Options
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

// Đối chiếu fontFamily từ element với FONT_FAMILIES
const matchFontFamily = (fontFamily: string | undefined): string => {
  if (!fontFamily) return FONT_FAMILIES[0].value;
  
  // Chuẩn hóa: loại bỏ dấu ngoặc kép và khoảng trắng thừa
  const normalized = fontFamily.replace(/["']/g, '').toLowerCase().trim();
  
  // Tìm font phù hợp (so khớp phần đầu - tên font chính)
  const match = FONT_FAMILIES.find(f => {
    const labelLower = f.label.toLowerCase();
    const valueLower = f.value.replace(/["']/g, '').toLowerCase();
    return normalized.includes(labelLower) || 
           normalized.startsWith(labelLower) ||
           valueLower.startsWith(normalized.split(',')[0].trim());
  });
  
  return match?.value || FONT_FAMILIES[0].value;
};

interface PropertiesPanelProps {
  selectedElement: SlideElement | undefined;
  onUpdateElement: (id: string, updates: Partial<SlideElement>) => void;
}

export const PropertiesPanel = ({
  selectedElement,
  onUpdateElement,
}: PropertiesPanelProps) => {
  if (!selectedElement) {
    return (
      <div className="w-72 border-l bg-background p-6 flex flex-col items-center justify-center text-muted-foreground">
        <MousePointer className="h-12 w-12 mb-4 opacity-20" />
        <p className="text-sm text-center">Select an element to edit its properties</p>
      </div>
    );
  }

  return (
    <div className="w-72 border-l bg-background flex flex-col h-full overflow-y-auto">
      <div className="p-4 border-b">
        <h3 className="font-semibold text-sm flex items-center gap-2">
          Properties <span className="text-xs text-muted-foreground font-normal">({selectedElement.type})</span>
        </h3>
      </div>
      
      <div className="p-4 space-y-6">
        {/* Position & Transform */}
        <div className="space-y-4">
          <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Position & Size</h4>
          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1">
              <Label className="text-xs">X</Label>
              <Input 
                type="number" 
                value={Math.round(selectedElement.x)} 
                onChange={(e) => onUpdateElement(selectedElement.id, { x: Number(e.target.value) })}
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Y</Label>
              <Input 
                type="number" 
                value={Math.round(selectedElement.y)} 
                onChange={(e) => onUpdateElement(selectedElement.id, { y: Number(e.target.value) })}
                className="h-8" 
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Width</Label>
              <Input 
                type="number" 
                value={Math.round(selectedElement.width)} 
                onChange={(e) => onUpdateElement(selectedElement.id, { width: Number(e.target.value) })} 
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Height</Label>
              <Input 
                type="number" 
                value={Math.round(selectedElement.height)} 
                onChange={(e) => onUpdateElement(selectedElement.id, { height: Number(e.target.value) })} 
                className="h-8"
              />
            </div>
            <div className="col-span-2 space-y-1">
              <Label className="text-xs">Rotation ({selectedElement.rotation}°)</Label>
              <Slider 
                min={0} max={360} step={1}
                value={[selectedElement.rotation || 0]}
                onValueChange={(vals) => onUpdateElement(selectedElement.id, { rotation: vals[0] })}
              />
            </div>
          </div>
        </div>

        <Separator />

        {/* Appearance */}
        <div className="space-y-4">
          <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Appearance</h4>
          
          <div className="space-y-2">
            <Label className="text-xs">Opacity</Label>
            <Slider 
              min={0} max={1} step={0.1}
              value={[selectedElement.opacity ?? 1]} 
              onValueChange={(v) => onUpdateElement(selectedElement.id, { opacity: v[0] })}
            />
          </div>

          <div className="space-y-2">
            <Label className="text-xs">Fill Color</Label>
            <div className="flex gap-2">
              <Input 
                type="color" 
                value={selectedElement.fillColor || "#000000"} 
                onChange={(e) => onUpdateElement(selectedElement.id, { fillColor: e.target.value })}
                className="w-10 h-8 p-0 border-0"
              />
              <Input 
                type="text" 
                value={selectedElement.fillColor || ""} 
                onChange={(e) => onUpdateElement(selectedElement.id, { fillColor: e.target.value })}
                className="h-8 flex-1 font-mono text-xs"
              />
            </div>
          </div>

          {selectedElement.type !== 'text' && (
            <div className="space-y-2">
              <Label className="text-xs">Border Radius</Label>
              <Slider 
                min={0} max={100} 
                value={[selectedElement.borderRadius || 0]} 
                onValueChange={(v) => onUpdateElement(selectedElement.id, { borderRadius: v[0] })}
              />
            </div>
          )}
        </div>

        <Separator />

        {/* Typography (Conditional) */}
        {selectedElement.type === 'text' && (
          <div className="space-y-4">
            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Typography</h4>
            
            {/* Font Family Selector */}
            <div className="space-y-2">
              <Label className="text-xs">Font Family</Label>
              <Select
                value={matchFontFamily(selectedElement.fontFamily)}
                onValueChange={(value) => onUpdateElement(selectedElement.id, { fontFamily: value })}
              >
                <SelectTrigger className="h-8 text-xs">
                  <SelectValue placeholder="Select font" />
                </SelectTrigger>
                <SelectContent>
                  {FONT_FAMILIES.map((font) => (
                    <SelectItem 
                      key={font.value} 
                      value={font.value}
                      style={{ fontFamily: font.value }}
                    >
                      {font.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-1">
                <Label className="text-xs">Font Size</Label>
                <Input 
                  type="number" 
                  value={selectedElement.fontSize || 16} 
                  onChange={(e) => onUpdateElement(selectedElement.id, { fontSize: Number(e.target.value) })}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Color</Label>
                <Input 
                  type="color" 
                  value={selectedElement.color || "#000000"} 
                  onChange={(e) => onUpdateElement(selectedElement.id, { color: e.target.value })}
                  className="h-8 w-full p-0"
                />
              </div>
            </div>

            <div className="flex justify-between border rounded-md p-1 bg-muted/20">
              <Button 
                variant={selectedElement.textAlign === 'left' ? "secondary" : "ghost"} 
                size="icon" 
                className="h-6 w-8"
                onClick={() => onUpdateElement(selectedElement.id, { textAlign: 'left' })}
              >
                <AlignLeft className="h-3 w-3" />
              </Button>
              <Button 
                variant={selectedElement.textAlign === 'center' ? "secondary" : "ghost"} 
                size="icon" 
                className="h-6 w-8"
                onClick={() => onUpdateElement(selectedElement.id, { textAlign: 'center' })}
              >
                <AlignCenter className="h-3 w-3" />
              </Button>
              <Button 
                variant={selectedElement.textAlign === 'right' ? "secondary" : "ghost"} 
                size="icon" 
                className="h-6 w-8"
                onClick={() => onUpdateElement(selectedElement.id, { textAlign: 'right' })}
              >
                <AlignRight className="h-3 w-3" />
              </Button>
            </div>

            <div className="flex justify-between border rounded-md p-1 bg-muted/20">
              <Button 
                variant={selectedElement.fontWeight === 'bold' ? "secondary" : "ghost"} 
                size="icon" 
                className="h-6 w-8"
                onClick={() => onUpdateElement(selectedElement.id, { 
                  fontWeight: selectedElement.fontWeight === 'bold' ? 'normal' : 'bold' 
                })}
              >
                <Bold className="h-3 w-3" />
              </Button>
              <Button 
                variant={selectedElement.fontStyle === 'italic' ? "secondary" : "ghost"} 
                size="icon" 
                className="h-6 w-8"
                onClick={() => onUpdateElement(selectedElement.id, { 
                  fontStyle: selectedElement.fontStyle === 'italic' ? 'normal' : 'italic' 
                })}
              >
                <Italic className="h-3 w-3" />
              </Button>
              <Button 
                variant={selectedElement.textDecoration === 'underline' ? "secondary" : "ghost"} 
                size="icon" 
                className="h-6 w-8"
                onClick={() => onUpdateElement(selectedElement.id, { 
                  textDecoration: selectedElement.textDecoration === 'underline' ? 'none' : 'underline' 
                })}
              >
                <Underline className="h-3 w-3" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
