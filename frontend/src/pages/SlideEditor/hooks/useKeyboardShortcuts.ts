import { useEffect } from "react";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";

interface UseKeyboardShortcutsParams {
  selectedElementId: string | null;
  deleteElement: (id: string) => void;
  handleSave: () => Promise<void>;
  slideCanvasRef: React.RefObject<SlideCanvasHandle>;
}

/**
 * Hook để quản lý keyboard shortcuts (Delete, Ctrl+S, Ctrl+Z, Ctrl+Y, etc.)
 */
export const useKeyboardShortcuts = ({
  selectedElementId,
  deleteElement,
  handleSave,
  slideCanvasRef,
}: UseKeyboardShortcutsParams): void => {
  
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Delete/Backspace - delete selected element
      if (e.key === "Delete" || e.key === "Backspace") {
        // Only delete if not editing text (contenteditable)
        if (selectedElementId && document.activeElement?.getAttribute('contenteditable') !== 'true') {
          deleteElement(selectedElementId);
        }
      }
      
      // Ctrl+S / Cmd+S - manual save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handleSave();
      }

      // Ctrl+Z / Cmd+Z - undo
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
        // Skip if user is actively editing text inside the shadow DOM
        const shadowHost = document.activeElement as HTMLElement;
        const shadowActive = shadowHost?.shadowRoot?.activeElement as HTMLElement | null;
        const isEditingInShadow = shadowActive?.getAttribute('contenteditable') === 'true';
        if (!isEditingInShadow) {
          e.preventDefault();
          // Flush any unsaved properties-panel DOM changes into history before undoing
          slideCanvasRef.current?.saveHistory(true);
          slideCanvasRef.current?.undo();
          // Re-sync React state (properties panel) from the restored DOM
          if (selectedElementId) slideCanvasRef.current?.reselectById(selectedElementId);
        }
      }

      // Ctrl+Y / Cmd+Y / Ctrl+Shift+Z - redo
      if (
        ((e.ctrlKey || e.metaKey) && e.key === 'y') ||
        ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'z')
      ) {
        const shadowHost = document.activeElement as HTMLElement;
        const shadowActive = shadowHost?.shadowRoot?.activeElement as HTMLElement | null;
        const isEditingInShadow = shadowActive?.getAttribute('contenteditable') === 'true';
        if (!isEditingInShadow) {
          e.preventDefault();
          slideCanvasRef.current?.redo();
          // Re-sync React state (properties panel) from the restored DOM
          if (selectedElementId) slideCanvasRef.current?.reselectById(selectedElementId);
        }
      }
    };
    
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedElementId, deleteElement, handleSave, slideCanvasRef]);
};
