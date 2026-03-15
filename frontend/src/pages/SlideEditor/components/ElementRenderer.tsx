import React, { useState, useRef, useEffect } from "react";
import type { SlideElement } from "../types";
import { useEditorStore } from "../store/useEditorStore";
import { MathLiveElement } from "./MathLiveElement";
import { GripHorizontal } from "lucide-react";

interface ElementRendererProps {
  element: SlideElement;
  isSelected: boolean;
  zoom: number;
}

export const ElementRenderer = ({ element, isSelected, zoom }: ElementRendererProps) => {
  const { selectElement, updateElement, currentSlideId } = useEditorStore();
  
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [resizeDir, setResizeDir] = useState<string | null>(null);

  const dragStartPos = useRef({ x: 0, y: 0 });
  const elementStartPos = useRef({ x: 0, y: 0 });
  
  const resizeStartPos = useRef({ x: 0, y: 0 });
  const resizeStartDims = useRef({ x: 0, y: 0, width: 0, height: 0 });

  const handlePointerDown = (e: React.PointerEvent) => {
    e.stopPropagation();
    
    // Only select the element on pointer down, don't start dragging the whole element
    selectElement(element.id);
  };
  
  const handleDragHandleDown = (e: React.PointerEvent) => {
    e.stopPropagation();
    selectElement(element.id);
    
    if (e.button !== 0) return;
    
    setIsDragging(true);
    dragStartPos.current = { x: e.clientX, y: e.clientY };
    elementStartPos.current = { x: element.x, y: element.y };
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  const handleResizeStart = (e: React.PointerEvent, dir: string) => {
    e.stopPropagation();
    selectElement(element.id);
    
    if (e.button !== 0) return;
    
    setIsResizing(true);
    setResizeDir(dir);
    resizeStartPos.current = { x: e.clientX, y: e.clientY };
    resizeStartDims.current = { 
      x: element.x, 
      y: element.y, 
      width: element.width, 
      height: element.height 
    };
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if ((!isDragging && !isResizing) || !currentSlideId) return;

    if (isDragging) {
      const dx = (e.clientX - dragStartPos.current.x) / zoom;
      const dy = (e.clientY - dragStartPos.current.y) / zoom;

      updateElement(currentSlideId, element.id, {
        x: elementStartPos.current.x + dx,
        y: elementStartPos.current.y + dy,
      });
    } else if (isResizing && resizeDir) {
      const dx = (e.clientX - resizeStartPos.current.x) / zoom;
      const dy = (e.clientY - resizeStartPos.current.y) / zoom;

      let newX = resizeStartDims.current.x;
      let newY = resizeStartDims.current.y;
      let newWidth = resizeStartDims.current.width;
      let newHeight = resizeStartDims.current.height;

      if (resizeDir.includes('e')) {
        newWidth = Math.max(20, resizeStartDims.current.width + dx);
      }
      if (resizeDir.includes('s')) {
        newHeight = Math.max(20, resizeStartDims.current.height + dy);
      }
      if (resizeDir.includes('w')) {
        const potentialWidth = resizeStartDims.current.width - dx;
        if (potentialWidth > 20) {
          newWidth = potentialWidth;
          newX = resizeStartDims.current.x + dx;
        }
      }
      if (resizeDir.includes('n')) {
        const potentialHeight = resizeStartDims.current.height - dy;
        if (potentialHeight > 20) {
          newHeight = potentialHeight;
          newY = resizeStartDims.current.y + dy;
        }
      }

      updateElement(currentSlideId, element.id, {
        x: newX,
        y: newY,
        width: newWidth,
        height: newHeight,
      });
    }
  };

  const handlePointerUp = (e: React.PointerEvent) => {
    if (isDragging || isResizing) {
      setIsDragging(false);
      setIsResizing(false);
      setResizeDir(null);
      e.currentTarget.releasePointerCapture(e.pointerId);
    }
  };

  // Prevent default drag behaviors to avoid HTML5 drag & drop collision
  const handleDragStart = (e: React.DragEvent) => {
    e.preventDefault();
  };

  return (
    <div
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerCancel={handlePointerUp}
      onDragStart={handleDragStart}
      style={{
        position: "absolute",
        left: element.x,
        top: element.y,
        width: element.width,
        height: element.height,
        transform: `rotate(${element.rotation || 0}deg)`,
        zIndex: element.zIndex,
        backgroundColor: element.fillColor || "transparent",
        color: element.color || "#000",
        opacity: element.opacity ?? 1,
        fontSize: element.fontSize ? `${element.fontSize}px` : undefined,
        fontFamily: element.fontFamily,
        fontWeight: element.fontWeight,
        fontStyle: element.fontStyle,
        textDecoration: element.textDecoration,
        textAlign: element.textAlign,
        lineHeight: element.lineHeight || undefined,
        letterSpacing: element.letterSpacing || undefined,
        borderRadius: element.borderRadius ? `${element.borderRadius}px` : undefined,
        border: element.strokeColor && element.strokeWidth 
          ? `${element.strokeWidth}px solid ${element.strokeColor}` 
          : undefined,
        overflow: "visible", 
        cursor: isDragging ? "grabbing" : "default",
        userSelect: "none",
        boxSizing: "border-box",
        // Make sure pointer events hit the wrapper for selection
        pointerEvents: "auto"
      }}
    >
      {/* Show selection handles ONLY when selected */}
      {isSelected && (
        <>
          <div className="absolute inset-0 border-[2px] border-[#3b82f6] pointer-events-none" style={{ zIndex: 9999 }} />
          
          {/* Top-middle drag handle */}
          <div 
            className="absolute -top-[22px] left-1/2 -translate-x-1/2 bg-[#3b82f6] text-white rounded-t-md px-[10px] py-[2px] cursor-grab active:cursor-grabbing flex items-center justify-center pointer-events-auto"
            style={{ zIndex: 10000, height: '22px' }}
            onPointerDown={handleDragHandleDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerCancel={handlePointerUp}
          >
            <GripHorizontal className="w-3 h-3" />
          </div>

          {/* Resizing handles (pink dots) */}
          <div 
            className="absolute -top-[5px] -left-[5px] w-[10px] h-[10px] bg-pink-400 border-[1.5px] border-white rounded-full pointer-events-auto cursor-nwse-resize" 
            style={{ zIndex: 10000 }} 
            onPointerDown={(e) => handleResizeStart(e, 'nw')}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerCancel={handlePointerUp}
          />
          <div 
            className="absolute -top-[5px] -right-[5px] w-[10px] h-[10px] bg-pink-400 border-[1.5px] border-white rounded-full pointer-events-auto cursor-nesw-resize" 
            style={{ zIndex: 10000 }} 
            onPointerDown={(e) => handleResizeStart(e, 'ne')}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerCancel={handlePointerUp}
          />
          <div 
            className="absolute -bottom-[5px] -left-[5px] w-[10px] h-[10px] bg-pink-400 border-[1.5px] border-white rounded-full pointer-events-auto cursor-nesw-resize" 
            style={{ zIndex: 10000 }} 
            onPointerDown={(e) => handleResizeStart(e, 'sw')}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerCancel={handlePointerUp}
          />
          <div 
            className="absolute -bottom-[5px] -right-[5px] w-[10px] h-[10px] bg-pink-400 border-[1.5px] border-white rounded-full pointer-events-auto cursor-nwse-resize" 
            style={{ zIndex: 10000 }} 
            onPointerDown={(e) => handleResizeStart(e, 'se')}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerCancel={handlePointerUp}
          />
        </>
      )}

      {/* Render content based on type */}
      {element.type === "text" && (
        <div 
          style={{ 
            width: "100%", 
            height: "100%", 
            overflow: "hidden", 
            outline: "none", 
            cursor: "text", 
            userSelect: "text",
            // Allow pointer events on content when selected to edit, otherwise ignore
            pointerEvents: isSelected ? "auto" : "none"
          }}
          contentEditable={isSelected}
          suppressContentEditableWarning
          onPointerDown={(e) => {
             if (isSelected) e.stopPropagation(); // Stop drag if editing
          }}
          onBlur={(e) => {
            if (currentSlideId) {
              updateElement(currentSlideId, element.id, { content: e.currentTarget.innerHTML });
            }
          }}
          dangerouslySetInnerHTML={{ __html: element.content || '' }}
        />
      )}

      {element.type === "image" && element.src && (
        <img 
          src={element.src} 
          alt="" 
          style={{ width: "100%", height: "100%", objectFit: "cover", pointerEvents: "none" }} 
          draggable={false}
        />
      )}
      
      {element.type === "shape" && (
        <div style={{ 
          width: "100%", 
          height: "100%", 
          borderRadius: element.width === element.height && element.subType === 'circle' ? "50%" : "0" 
        }} />
      )}
      
      {element.type === "math" && (
        <div 
          style={{ 
            width: "100%", 
            height: "100%", 
            cursor: "text", 
            userSelect: "text",
            pointerEvents: isSelected ? "auto" : "none" 
          }}
          onPointerDown={(e) => {
             if (isSelected) e.stopPropagation();
          }}
        >
          <MathLiveElement element={element} />
        </div>
      )}
    </div>
  );
};
