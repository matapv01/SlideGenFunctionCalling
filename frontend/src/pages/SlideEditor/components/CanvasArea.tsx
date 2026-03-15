import React, { useRef } from "react";
import type { Slide, SlideElement } from "../types";
import { useEditorStore } from "../store/useEditorStore";
import { ElementRenderer } from "./ElementRenderer";

interface CanvasAreaProps {
  currentSlide: Slide | undefined;
  zoom: number;
}

export const CanvasArea = ({ currentSlide, zoom }: CanvasAreaProps) => {
  const canvasRef = useRef<HTMLDivElement>(null);
  const { clearSelection, addElement, selectedElementIds } = useEditorStore();

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const draggedData = e.dataTransfer.getData("application/json");
    if (!draggedData || !canvasRef.current || !currentSlide) return;

    try {
      const item = JSON.parse(draggedData);
      const rect = canvasRef.current.getBoundingClientRect();
      const x = (e.clientX - rect.left) / zoom;
      const y = (e.clientY - rect.top) / zoom;
      
      const defaults: Partial<SlideElement> = { x, y, width: 200, height: 100, rotation: 0, zIndex: 100, opacity: 1 };
      
      if (item.type === "text") {
        defaults.type = "text";
        defaults.content = item.subType === "heading" ? "Heading" : "Text block";
        defaults.fontSize = item.subType === "heading" ? 48 : 24;
        defaults.color = "#000000";
        defaults.width = 400;
        defaults.height = item.subType === "heading" ? 80 : 50;
      } else if (item.type === "shape") {
        defaults.type = "shape";
        defaults.fillColor = "#4f6ef7";
        if (item.subType === "circle") { defaults.width = 150; defaults.height = 150; }
        else { defaults.width = 200; defaults.height = 120; }
        defaults.borderRadius = item.subType === "circle" ? 999 : 0;
      } else if (item.type === "math") {
        defaults.type = "math";
        defaults.content = "x=\\frac{-b\\pm\\sqrt{b^2-4ac}}{2a}";
        defaults.width = 360;
        defaults.height = 120;
      }

      addElement(currentSlide.id, defaults as Omit<SlideElement, 'id'>);
    } catch (err) {
      console.error("Drop error:", err);
    }
  };

  const handleCanvasClick = (e: React.MouseEvent) => {
    // Only clear selection if clicking on the canvas background, not on an element
    if (e.target === e.currentTarget || (e.target as HTMLElement).id === "canvas") {
      clearSelection();
    }
  };

  return (
    <div 
      className="flex-1 bg-neutral-200 overflow-auto relative flex items-center justify-center"
      style={{ padding: "60px" }}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      {/* The actual slide canvas at 1920x1080 */}
      <div 
        className="relative shadow-2xl flex-shrink-0"
        style={{ 
          transformOrigin: "top left",
          transform: `scale(${zoom})`,
          marginBottom: 1080 * zoom - 1080,
          marginRight: 1920 * zoom - 1920,
          width: 1920,
          height: 1080,
          backgroundColor: currentSlide?.backgroundColor || "#ffffff",
          overflow: "hidden",
        }}
        ref={canvasRef}
        id="canvas"
        onClick={handleCanvasClick}
      >
        {/* ── Layer 1: Legacy HTML Background (non-interactive) ─────────────────
            Renders the raw HTML from the backend as a visual background.
            pointer-events: none means it cannot be clicked/selected.           */}
        {currentSlide?.htmlBackground && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              width: "100%",
              height: "100%",
              pointerEvents: "none",
              userSelect: "none",
              zIndex: 0,
            }}
            dangerouslySetInnerHTML={{ __html: currentSlide.htmlBackground }}
          />
        )}

        {/* ── Layer 2: Interactive Elements ────────────────────────────────────
            New elements added by the user. These are draggable/selectable.     */}
        {currentSlide && currentSlide.elements.map(el => (
          <ElementRenderer 
            key={el.id} 
            element={el} 
            isSelected={selectedElementIds.includes(el.id)} 
            zoom={zoom} 
          />
        ))}
        
        {/* Empty state */}
        {!currentSlide && (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <p>Loading slide...</p>
          </div>
        )}
      </div>
    </div>
  );
};
