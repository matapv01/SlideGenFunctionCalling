import { useEffect } from "react";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";

interface UseKeyboardShortcutsParams {
  selectedElementId: string | null;
  deleteElement: (id: string) => void;
  duplicateElement: (id: string) => void;
  bringForward: (id: string) => void;
  sendBackward: (id: string) => void;
  handleSave: () => Promise<void>;
  slideCanvasRef: React.RefObject<SlideCanvasHandle>;
}

/**
 * Hook để quản lý keyboard shortcuts (Delete, Ctrl+S, Ctrl+Z, Ctrl+Y, etc.)
 */
export const useKeyboardShortcuts = ({
  selectedElementId,
  deleteElement,
  duplicateElement,
  bringForward,
  sendBackward,
  handleSave,
  slideCanvasRef,
}: UseKeyboardShortcutsParams): void => {
  
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const active = document.activeElement as HTMLElement | null;
      const activeTag = active?.tagName?.toLowerCase();
      const activeInShadow = active?.shadowRoot?.activeElement as HTMLElement | null;
      const activeShadowTag = activeInShadow?.tagName?.toLowerCase();
      const isEditorTextEditing = slideCanvasRef.current?.isTextEditing?.() ?? false;
      const isTypingInRegularField = !!active && (
        active.getAttribute('contenteditable') === 'true' ||
        activeTag === 'input' ||
        activeTag === 'textarea' ||
        activeTag === 'select'
      );
      const isContentEditableInShadow = activeInShadow?.getAttribute('contenteditable') === 'true';
      const isTypingInShadowField = !!activeInShadow && (
        activeShadowTag === 'input' ||
        activeShadowTag === 'textarea' ||
        activeShadowTag === 'select' ||
        (isContentEditableInShadow && isEditorTextEditing)
      );
      const isTypingContext = isTypingInRegularField || isTypingInShadowField;
      const hasModifier = e.ctrlKey || e.metaKey;
      const lowerKey = e.key.toLowerCase();

      // Delete/Backspace - delete selected element
      if (e.key === "Delete" || e.key === "Backspace") {
        if (selectedElementId && !isTypingContext) {
          e.preventDefault();
          deleteElement(selectedElementId);
          return;
        }
      }

      if (!hasModifier) return;

      // Ctrl/Cmd + C - copy selected element
      if (lowerKey === 'c') {
        if (selectedElementId && !isTypingContext) {
          e.preventDefault();
          slideCanvasRef.current?.copySelectedElement(selectedElementId);
        }
        return;
      }

      // Ctrl/Cmd + V - paste copied element
      if (lowerKey === 'v') {
        if (!isTypingContext) {
          e.preventDefault();
          slideCanvasRef.current?.pasteElement();
        }
        return;
      }

      // Ctrl/Cmd + D - duplicate selected element
      if (lowerKey === 'd') {
        if (selectedElementId && !isTypingContext) {
          e.preventDefault();
          duplicateElement(selectedElementId);
        }
        return;
      }

      // Ctrl/Cmd + G - group selection; Ctrl/Cmd + Shift + G - ungroup
      if (lowerKey === 'g') {
        if (!isTypingContext) {
          e.preventDefault();
          if (e.shiftKey) {
            slideCanvasRef.current?.ungroupSelectedElements();
          } else {
            slideCanvasRef.current?.groupSelectedElements();
          }
        }
        return;
      }

      // Ctrl/Cmd + ] (or + Shift + ]) - layer up / bring to front
      if (e.key === ']') {
        if (selectedElementId && !isTypingContext) {
          e.preventDefault();
          if (e.shiftKey) {
            slideCanvasRef.current?.bringToFront(selectedElementId);
          } else {
            bringForward(selectedElementId);
          }
        }
        return;
      }

      // Ctrl/Cmd + [ (or + Shift + [) - layer down / send to back
      if (e.key === '[') {
        if (selectedElementId && !isTypingContext) {
          e.preventDefault();
          if (e.shiftKey) {
            slideCanvasRef.current?.sendToBack(selectedElementId);
          } else {
            sendBackward(selectedElementId);
          }
        }
        return;
      }
      
      // Ctrl+S / Cmd+S - manual save
      if (lowerKey === 's') {
        e.preventDefault();
        handleSave();
        return;
      }

      // Ctrl+Z / Cmd+Z - undo
      if (lowerKey === 'z' && !e.shiftKey) {
        // Skip if user is actively editing text inside the shadow DOM
        const shadowHost = document.activeElement as HTMLElement;
        const shadowActive = shadowHost?.shadowRoot?.activeElement as HTMLElement | null;
        const isEditingInShadow = shadowActive?.getAttribute('contenteditable') === 'true';
        if (!isEditingInShadow && !isTypingInRegularField) {
          e.preventDefault();
          // Flush any unsaved properties-panel DOM changes into history before undoing
          slideCanvasRef.current?.saveHistory(true);
          slideCanvasRef.current?.undo();
        }
        return;
      }

      // Ctrl+Y / Cmd+Y / Ctrl+Shift+Z - redo
      if (
        lowerKey === 'y' ||
        (e.shiftKey && lowerKey === 'z')
      ) {
        const shadowHost = document.activeElement as HTMLElement;
        const shadowActive = shadowHost?.shadowRoot?.activeElement as HTMLElement | null;
        const isEditingInShadow = shadowActive?.getAttribute('contenteditable') === 'true';
        if (!isEditingInShadow && !isTypingInRegularField) {
          e.preventDefault();
          slideCanvasRef.current?.redo();
        }
      }
    };
    
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedElementId, deleteElement, duplicateElement, bringForward, sendBackward, handleSave, slideCanvasRef]);
};
