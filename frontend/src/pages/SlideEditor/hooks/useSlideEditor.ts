import { useState, useRef, useCallback, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import type { DragItem } from "../types";
import type { SlideCanvasHandle } from "@/components/SlideCanvas";
import { useSlideData } from "./useSlideData";
import { useSlideActions } from "./useSlideActions";
import { useElementActions } from "./useElementActions";
import { useCanvasInteraction } from "./useCanvasInteraction";
import { useKeyboardShortcuts } from "./useKeyboardShortcuts";
import { useAutoSave } from "./useAutoSave";

/**
 * Main SlideEditor hook — thin aggregator that composes all sub-hooks into
 * a single public API consumed by the SlideEditor page.
 *
 * Responsibilities are split by concern:
 *   useSlideData          → load project + slides from the API
 *   useSlideActions       → add / delete / duplicate slides
 *   useElementActions     → add / update / delete / duplicate / reorder elements
 *   useCanvasInteraction  → element selection from canvas + drag-and-drop
 *   useKeyboardShortcuts  → Delete, Ctrl+S shortcuts
 *   useAutoSave           → debounced 1-second auto-save
 */
export const useSlideEditor = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // ── UI state ────────────────────────────────────────────────────────
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [selectedElementId, setSelectedElementId] = useState<string | null>(null);
  const [zoom, setZoom] = useState(0.48);
  const [draggedItem, setDraggedItem] = useState<DragItem | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // ── Refs ─────────────────────────────────────────────────────────────
  const canvasRef = useRef<HTMLDivElement>(null);
  const slideCanvasRef = useRef<SlideCanvasHandle>(null);

  // ── Data loading ──────────────────────────────────────────────────────
  const { slides, setSlides, projectName, loading } = useSlideData(projectId);
  const currentSlide = slides[currentSlideIndex];
  const selectedElement = currentSlide?.elements.find(el => el.id === selectedElementId);

  // Apply initial slide from URL query once after data is loaded.
  const didApplyInitialSlideRef = useRef(false);
  useEffect(() => {
    if (didApplyInitialSlideRef.current || loading || slides.length === 0) return;

    const rawSlideParam = searchParams.get("slide");
    if (!rawSlideParam) {
      didApplyInitialSlideRef.current = true;
      return;
    }

    const requestedIndex = Number.parseInt(rawSlideParam, 10);
    if (Number.isNaN(requestedIndex)) {
      didApplyInitialSlideRef.current = true;
      return;
    }

    const boundedIndex = Math.max(0, Math.min(requestedIndex, slides.length - 1));
    setCurrentSlideIndex(boundedIndex);
    didApplyInitialSlideRef.current = true;
  }, [loading, slides.length, searchParams, setCurrentSlideIndex]);

  // Restore history state from sessionStorage after mount
  useEffect(() => {
    if (!projectId || !slideCanvasRef.current || loading) return;
    
    const savedHistoryKey = `slide-history-${projectId}`;
    const savedHistory = sessionStorage.getItem(savedHistoryKey);
    
    if (savedHistory) {
      try {
        const historyState = JSON.parse(savedHistory);
        slideCanvasRef.current.restoreHistoryState?.(historyState);
        sessionStorage.removeItem(savedHistoryKey);
        console.log('[SlideEditor] Restored history state from sessionStorage');
      } catch (e) {
        console.warn('[SlideEditor] Failed to restore history state:', e);
      }
    }
  }, [projectId, loading, slideCanvasRef]);

  // ── Slide CRUD ────────────────────────────────────────────────────────
  const { addSlide, addSlideFromTemplate, deleteSlide, duplicateSlide, reorderSlides } = useSlideActions({
    slides,
    setSlides,
    currentSlideIndex,
    setCurrentSlideIndex,
    projectId,
  });

  // ── Element CRUD ──────────────────────────────────────────────────────
  const { addElement, updateElement, deleteElement, duplicateElement, bringForward, sendBackward } =
    useElementActions({
      currentSlide,
      currentSlideIndex,
      setSlides,
      setSelectedElementId,
      slideCanvasRef,
    });

  // ── Auto-save ─────────────────────────────────────────────────────────
  const { handleSave, handleCanvasChange, flushSave } = useAutoSave({
    currentSlide,
    setSlides,
    slideCanvasRef,
  });

  // ── Slide selection — flush pending save before switching ─────────────
  const selectSlide = useCallback(async (index: number) => {
    if (index === currentSlideIndex) return;
    await flushSave();
    setCurrentSlideIndex(index);
  }, [currentSlideIndex, flushSave, setCurrentSlideIndex]);

  // ── Canvas interaction ────────────────────────────────────────────────
  const { handleElementSelectFromCanvas, handleDrop } = useCanvasInteraction({
    currentSlide,
    currentSlideIndex,
    setSlides,
    setSelectedElementId,
    draggedItem,
    setDraggedItem,
    zoom,
    addElement,
    canvasRef,
  });

  // ── Keyboard shortcuts ────────────────────────────────────────────────
  useKeyboardShortcuts({
    selectedElementId,
    deleteElement,
    duplicateElement,
    bringForward,
    sendBackward,
    handleSave,
    slideCanvasRef,
  });

  return {
    // State
    slides, currentSlide, currentSlideIndex, selectedElementId, selectedElement,
    zoom, draggedItem, isSidebarOpen, projectName, loading,

    // Refs
    canvasRef, slideCanvasRef,

    // Setters
    setCurrentSlideIndex, setSelectedElementId, setZoom, setDraggedItem, setIsSidebarOpen,

    // Actions
    navigate,
    addSlide, addSlideFromTemplate, deleteSlide, duplicateSlide, reorderSlides,
    addElement, updateElement, deleteElement, duplicateElement, bringForward, sendBackward,
    handleDrop, handleSave, handleElementSelectFromCanvas, handleCanvasChange, selectSlide,
  };
};
