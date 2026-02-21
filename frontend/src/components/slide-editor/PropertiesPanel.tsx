import { MousePointer, AlignLeft, AlignCenter, AlignRight, Bold, Italic, Underline } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Separator } from "@/components/ui/separator";
import { SlideElement } from "@/types/slide";

interface PropertiesPanelProps {
    selectedElement: SlideElement | undefined;
    updateElement: (id: string, updates: Partial<SlideElement>) => void;
}

export const PropertiesPanel = ({ selectedElement, updateElement }: PropertiesPanelProps) => {
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
                {/* Position & Size */}
                <div className="space-y-4">
                    <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Position & Size</h4>
                    <div className="grid grid-cols-2 gap-2">
                        <div className="space-y-1">
                            <Label className="text-xs">X</Label>
                            <Input type="number" value={Math.round(selectedElement.x)} onChange={(e) => updateElement(selectedElement.id, { x: Number(e.target.value) })} className="h-8" />
                        </div>
                        <div className="space-y-1">
                            <Label className="text-xs">Y</Label>
                            <Input type="number" value={Math.round(selectedElement.y)} onChange={(e) => updateElement(selectedElement.id, { y: Number(e.target.value) })} className="h-8" />
                        </div>
                        <div className="space-y-1">
                            <Label className="text-xs">Width</Label>
                            <Input type="number" value={Math.round(selectedElement.width)} onChange={(e) => updateElement(selectedElement.id, { width: Number(e.target.value) })} className="h-8" />
                        </div>
                        <div className="space-y-1">
                            <Label className="text-xs">Height</Label>
                            <Input type="number" value={Math.round(selectedElement.height)} onChange={(e) => updateElement(selectedElement.id, { height: Number(e.target.value) })} className="h-8" />
                        </div>
                    </div>
                </div>
                
                <Separator />

                {/* Appearance */}
                <div className="space-y-4">
                    <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Appearance</h4>
                    <div className="space-y-2">
                        <Label className="text-xs">Fill Color</Label>
                        <div className="flex gap-2">
                            <Input type="color" value={selectedElement.fillColor || "#000000"} onChange={(e) => updateElement(selectedElement.id, { fillColor: e.target.value })} className="w-10 h-8 p-0 border-0" />
                            <Input type="text" value={selectedElement.fillColor || ""} onChange={(e) => updateElement(selectedElement.id, { fillColor: e.target.value })} className="h-8 flex-1 font-mono text-xs" />
                        </div>
                    </div>
                </div>

                <Separator />

                {/* Typography (Only for Text) */}
                {selectedElement.type === 'text' && (
                    <div className="space-y-4">
                        <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Typography</h4>
                        <div className="space-y-2">
                            <Label className="text-xs">Content</Label>
                            <Textarea value={selectedElement.content || ""} onChange={(e) => updateElement(selectedElement.id, { content: e.target.value })} className="min-h-[100px] font-mono text-xs" />
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                            <div className="space-y-1">
                                <Label className="text-xs">Size</Label>
                                <Input type="number" value={selectedElement.fontSize || 16} onChange={(e) => updateElement(selectedElement.id, { fontSize: Number(e.target.value) })} className="h-8" />
                            </div>
                            <div className="space-y-1">
                                <Label className="text-xs">Color</Label>
                                <Input type="color" value={selectedElement.color || "#000000"} onChange={(e) => updateElement(selectedElement.id, { color: e.target.value })} className="h-8 w-full p-0" />
                            </div>
                        </div>
                        <div className="flex justify-between border rounded-md p-1 bg-muted/20">
                            <Button variant={selectedElement.fontWeight === 'bold' ? "secondary" : "ghost"} size="icon" className="h-6 w-8" onClick={() => updateElement(selectedElement.id, { fontWeight: selectedElement.fontWeight === 'bold' ? 'normal' : 'bold' })}>
                                <Bold className="h-3 w-3" />
                            </Button>
                            <Button variant={selectedElement.fontStyle === 'italic' ? "secondary" : "ghost"} size="icon" className="h-6 w-8" onClick={() => updateElement(selectedElement.id, { fontStyle: selectedElement.fontStyle === 'italic' ? 'normal' : 'italic' })}>
                                <Italic className="h-3 w-3" />
                            </Button>
                            <Button variant={selectedElement.textDecoration === 'underline' ? "secondary" : "ghost"} size="icon" className="h-6 w-8" onClick={() => updateElement(selectedElement.id, { textDecoration: selectedElement.textDecoration === 'underline' ? 'none' : 'underline' })}>
                                <Underline className="h-3 w-3" />
                            </Button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};