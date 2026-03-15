import { useState, useEffect } from "react";
import { MousePointer, AlignLeft, AlignCenter, AlignRight, Bold, Italic, Underline, Sigma, Keyboard, Menu, Divide, Subscript, SquareRadical, Parentheses, Grid3x3 } from "lucide-react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
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
  const [isKeyboardOpen, setIsKeyboardOpen] = useState(false);

  useEffect(() => {
    const handleKeyboardChange = () => {
      // @ts-ignore
      if (window.mathVirtualKeyboard) {
        // @ts-ignore
        setIsKeyboardOpen(window.mathVirtualKeyboard.visible);
      }
    };

    // @ts-ignore
    if (window.mathVirtualKeyboard) {
      // @ts-ignore
      window.mathVirtualKeyboard.addEventListener('geometrychange', handleKeyboardChange);
    }

    return () => {
      // @ts-ignore
      if (window.mathVirtualKeyboard) {
        // @ts-ignore
        window.mathVirtualKeyboard.removeEventListener('geometrychange', handleKeyboardChange);
      }
    };
  }, []);

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

        {/* Math Options (Conditional) */}
        {selectedElement.type === 'math' && (
          <div className="space-y-4">
            <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
              <Sigma className="w-4 h-4" /> Math Options
            </h4>

            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-1">
                <Label className="text-xs">Size (px)</Label>
                <Input 
                  type="number" 
                  value={selectedElement.fontSize || 32} 
                  onChange={(e) => onUpdateElement(selectedElement.id, { fontSize: Number(e.target.value) })}
                  className="h-8 bg-muted/30"
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Color</Label>
                <div className="h-8 rounded-md overflow-hidden border">
                  <Input 
                    type="color" 
                    value={selectedElement.color || "#000000"} 
                    onChange={(e) => onUpdateElement(selectedElement.id, { color: e.target.value })}
                    className="h-10 w-full p-0 -mt-1 -ml-1 border-0"
                  />
                </div>
              </div>
            </div>

            <div className="space-y-2 pt-2">
              <Label className="text-xs text-muted-foreground">Controls</Label>
              <div className="grid grid-cols-2 gap-2">
                <Button 
                  variant={isKeyboardOpen ? "default" : "outline"}
                  size="sm" 
                  className={`h-8 text-xs font-normal ${isKeyboardOpen ? "bg-pink-500 hover:bg-pink-600 text-white border-transparent" : ""}`}
                  onClick={() => {
                    // Trigger keyboard using custom event or ref in the future
                    const mathField = document.querySelector('math-field') as any;
                    // @ts-ignore
                    if (mathField && window.mathVirtualKeyboard) {
                        // @ts-ignore
                        if (window.mathVirtualKeyboard.visible) {
                            // @ts-ignore
                            window.mathVirtualKeyboard.hide();
                            setIsKeyboardOpen(false);
                        } else {
                            // @ts-ignore
                            window.mathVirtualKeyboard.show();
                            setIsKeyboardOpen(true);
                        }
                    }
                  }}
                >
                  <Keyboard className={`w-3 h-3 justify-self-center mr-2 ${isKeyboardOpen ? "text-white" : "text-muted-foreground"}`} />
                  Keyboard
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="h-8 text-xs font-normal"
                  onClick={() => {
                   const mathField = document.querySelector('math-field') as any;
                   if (mathField) mathField.executeCommand('toggleMenu');
                  }}
                >
                  <Menu className="w-3 h-3 mr-2" />
                  Menu
                </Button>
              </div>
            </div>

            <div className="space-y-2 pt-2">
              <Label className="text-xs text-muted-foreground">Insert Math</Label>
              <div className="space-y-2">
                
                {/* Math Insert Accordion */}
                <Accordion type="single" collapsible className="w-full">
                  
                  {/* Phân số */}
                  <AccordionItem value="item-1" className="border-b border-white/5">
                    <AccordionTrigger className="hover:no-underline py-3 px-2 text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-md transition-colors">
                      <div className="flex items-center gap-3">
                        <Divide className="w-4 h-4" />
                        <span className="font-medium text-sm">Phân số</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pb-3 px-2">
                      <div className="grid grid-cols-4 gap-2 pt-1">
                        <Button variant="outline" className="h-10 px-0" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\frac{#?}{#?}"); mf.focus(); }
                        }}>x/y</Button>
                        <Button variant="outline" className="h-10 px-0 text-sm font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\frac{\\mathrm{d}y}{\\mathrm{d}x}"); mf.focus(); }
                        }}>dy/dx</Button>
                        <Button variant="outline" className="h-10 px-0 text-sm font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\frac{\\partial}{\\partial x}"); mf.focus(); }
                        }}>∂/∂x</Button>
                        <Button variant="outline" className="h-10 px-0 text-sm font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\frac{\\pi}{2}"); mf.focus(); }
                        }}>π/2</Button>
                      </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Chỉ số */}
                  <AccordionItem value="item-2" className="border-b border-white/5">
                    <AccordionTrigger className="hover:no-underline py-3 px-2 text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-md transition-colors">
                      <div className="flex items-center gap-3">
                        <Subscript className="w-4 h-4" />
                        <span className="font-medium text-sm">Chỉ số</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pb-3 px-2">
                      <div className="grid grid-cols-4 gap-2 pt-1">
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("^{#?}"); mf.focus(); }
                        }}>x²</Button>
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("_{#?}"); mf.focus(); }
                        }}>x₂</Button>
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif flex-col leading-none" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("_{#?}^{#?}"); mf.focus(); }
                        }}>
                          <span className="text-[10px] ml-2">2</span>
                          <span className="text-sm -mt-1">x</span>
                          <span className="text-[10px] ml-2 -mt-1">1</span>
                        </Button>
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("e^{x}"); mf.focus(); }
                        }}>eˣ</Button>
                      </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Căn thức */}
                  <AccordionItem value="item-3" className="border-b border-white/5">
                    <AccordionTrigger className="hover:no-underline py-3 px-2 text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-md transition-colors">
                      <div className="flex items-center gap-3">
                        <SquareRadical className="w-4 h-4" />
                        <span className="font-medium text-sm">Căn thức</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pb-3 px-2">
                      <div className="grid grid-cols-4 gap-2 pt-1">
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\sqrt{#?}"); mf.focus(); }
                        }}>√</Button>
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\sqrt[3]{#?}"); mf.focus(); }
                        }}>∛</Button>
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\sqrt[#?]{#?}"); mf.focus(); }
                        }}>ⁿ√</Button>
                        <Button variant="outline" className="h-10 px-0 text-sm font-serif flex items-center justify-center" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\frac{-\\mathbf{b}\\pm\\sqrt{\\mathbf{b}^2-4\\mathbf{a}\\mathbf{c}}}{2\\mathbf{a}}"); mf.focus(); }
                        }}>
                          <span>±√</span>
                        </Button>
                      </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Tích phân */}
                  <AccordionItem value="item-4" className="border-b border-white/5">
                    <AccordionTrigger className="hover:no-underline py-3 px-2 text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-md transition-colors">
                      <div className="flex items-center gap-3">
                        <b className="font-serif w-4 text-center text-sm">∫</b>
                        <span className="font-medium text-sm">Tích phân</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pb-3 px-2">
                      <div className="grid grid-cols-4 gap-2 pt-1">
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\int_{#?}^{#?}"); mf.focus(); }
                        }}>∫</Button>
                        <Button variant="outline" className="h-10 px-0 text-sm font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\int_{a}^{b}"); mf.focus(); }
                        }}>∫ab</Button>
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\iint_{#?}^{#?}"); mf.focus(); }
                        }}>∬</Button>
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\oint_{#?}^{#?}"); mf.focus(); }
                        }}>∮</Button>
                      </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Toán tử lớn */}
                  <AccordionItem value="item-5" className="border-b border-white/5">
                    <AccordionTrigger className="hover:no-underline py-3 px-2 text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-md transition-colors">
                      <div className="flex items-center gap-3">
                        <Sigma className="w-4 h-4" />
                        <span className="font-medium text-sm">Toán tử lớn</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pb-3 px-2">
                      <div className="grid grid-cols-4 gap-2 pt-1">
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\sum_{n=1}^{\\infty}"); mf.focus(); }
                        }}>∑</Button>
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\prod_{n=1}^{\\infty}"); mf.focus(); }
                        }}>∏</Button>
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\bigcup_{i=1}^{n}"); mf.focus(); }
                        }}>⋃</Button>
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\bigcap_{i=1}^{n}"); mf.focus(); }
                        }}>⋂</Button>
                      </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Giới hạn & Log */}
                  <AccordionItem value="item-6" className="border-b border-white/5">
                    <AccordionTrigger className="hover:no-underline py-3 px-2 text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-md transition-colors">
                      <div className="flex items-center gap-3">
                        <b className="font-serif w-4 text-center text-sm">lim</b>
                        <span className="font-medium text-sm">Giới hạn & Log</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pb-3 px-2">
                      <div className="grid grid-cols-4 gap-2 pt-1">
                        <Button variant="outline" className="h-10 px-0 text-sm font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\lim_{x \\to \\infty}"); mf.focus(); }
                        }}>lim<br/><span className="text-[8px] leading-none text-muted-foreground">x→∞</span></Button>
                        <Button variant="outline" className="h-10 px-0 text-sm font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\log_{2}(x)"); mf.focus(); }
                        }}>log₂</Button>
                        <Button variant="outline" className="h-10 px-0 text-sm font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\ln(x)"); mf.focus(); }
                        }}>ln</Button>
                        <Button variant="outline" className="h-10 px-0 text-sm font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\lg(x)"); mf.focus(); }
                        }}>lg</Button>
                      </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Ngoặc */}
                  <AccordionItem value="item-7" className="border-b border-white/5">
                    <AccordionTrigger className="hover:no-underline py-3 px-2 text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-md transition-colors">
                      <div className="flex items-center gap-3">
                        <Parentheses className="w-4 h-4" />
                        <span className="font-medium text-sm">Ngoặc</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pb-3 px-2">
                      <div className="grid grid-cols-4 gap-2 pt-1">
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\left( #? \\right)"); mf.focus(); }
                        }}>( )</Button>
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\left[ #? \\right]"); mf.focus(); }
                        }}>[ ]</Button>
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\left\\{ #? \\right\\}"); mf.focus(); }
                        }}>{"{ }"}</Button>
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\left| #? \\right|"); mf.focus(); }
                        }}>| |</Button>
                      </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Lượng giác */}
                  <AccordionItem value="item-8" className="border-b border-white/5">
                    <AccordionTrigger className="hover:no-underline py-3 px-2 text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-md transition-colors">
                      <div className="flex items-center gap-3">
                        <b className="font-serif w-4 text-center text-sm">sin</b>
                        <span className="font-medium text-sm">Lượng giác</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pb-3 px-2">
                      <div className="grid grid-cols-4 gap-2 pt-1">
                        <Button variant="outline" className="h-10 px-0 text-sm font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\sin(#?)"); mf.focus(); }
                        }}>sin</Button>
                        <Button variant="outline" className="h-10 px-0 text-sm font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\cos(#?)"); mf.focus(); }
                        }}>cos</Button>
                        <Button variant="outline" className="h-10 px-0 text-sm font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\tan(#?)"); mf.focus(); }
                        }}>tan</Button>
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\theta"); mf.focus(); }
                        }}>θ</Button>
                      </div>
                    </AccordionContent>
                  </AccordionItem>

                  {/* Ma trận */}
                  <AccordionItem value="item-9" className="border-b-0">
                    <AccordionTrigger className="hover:no-underline py-3 px-2 text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-md transition-colors">
                      <div className="flex items-center gap-3">
                        <Grid3x3 className="w-4 h-4" />
                        <span className="font-medium text-sm">Ma trận</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pb-3 px-2">
                      <div className="grid grid-cols-4 gap-2 pt-1">
                        <Button variant="outline" className="h-10 px-0 text-[10px] sm:text-xs font-serif leading-tight" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\begin{pmatrix} #? & #? \\\\ #? & #? \\end{pmatrix}"); mf.focus(); }
                        }}>( )<br/>( )</Button>
                        <Button variant="outline" className="h-10 px-0 text-[10px] sm:text-xs font-serif leading-tight" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\begin{bmatrix} #? & #? \\\\ #? & #? \\end{bmatrix}"); mf.focus(); }
                        }}>[ ]<br/>[ ]</Button>
                        <Button variant="outline" className="h-10 px-0 text-[10px] sm:text-xs font-serif leading-tight" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\begin{vmatrix} #? & #? \\\\ #? & #? \\end{vmatrix}"); mf.focus(); }
                        }}>| |<br/>| |</Button>
                        <Button variant="outline" className="h-10 px-0 text-lg font-serif" onClick={() => {
                          const mf = document.querySelector('math-field') as any;
                          if (mf) { mf.insert("\\dots"); mf.focus(); }
                        }}>⋯</Button>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
                
                
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
};
