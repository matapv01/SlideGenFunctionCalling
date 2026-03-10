import { useEffect } from "react";

interface UseKeyboardShortcutsParams {
  selectedElementId: string | null;
  deleteElement: (id: string) => void;
  handleSave: () => Promise<void>;
}

/**
 * Hook để quản lý keyboard shortcuts (Delete, Ctrl+S, etc.)
 */
export const useKeyboardShortcuts = ({
  selectedElementId,
  deleteElement,
  handleSave
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
    };
    
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedElementId, deleteElement, handleSave]);
};
