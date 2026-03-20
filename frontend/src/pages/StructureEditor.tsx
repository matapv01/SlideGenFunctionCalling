import { useState, useEffect, useCallback, useRef } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import {
  Check, RotateCcw, Sparkles, Loader2, FileText, ChevronRight,
  PlayCircle, Trash2, Type, AlignLeft, ArrowLeft, XCircle,
  Search, Undo2, Redo2, ZoomIn, ZoomOut, ChevronUp, ChevronDown, X, Plus,
  Bold, Italic, Underline
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
  DialogDescription
} from "@/components/ui/dialog";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle
} from "@/components/ui/alert-dialog";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { AppLayout } from "@/components/AppLayout";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/contexts/LanguageContext";

// ============ TYPES ============

interface IntroSlide {
  id: string;
  level: number;
  title: string;
  content: string;
  type: "title";
  children: never[];
}

interface StructureNode {
  node_id: string;
  level: number;
  title: string;
  content: string;
  children: StructureNode[];
  is_transition?: boolean;
}

interface SlidePreview {
  id: string;
  title: string;
  content: string;
  bullets: { level: number; text: string }[];
  isIntro?: boolean;
  isTransition?: boolean;
}

interface FlatEditorBlock {
  node_id: string;
  level: number;
  type: "title" | "content";
  text: string;
  is_transition: boolean;
}

interface ValidationIssue {
  message: string;
  nodeId: string;
}

// ============ MAIN COMPONENT ============

const StructureEditor = () => {
  const DEFAULT_MAX_LEVEL = 6;
  const VISIBLE_LEVEL_LIMIT = 6;

  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get("session");
  const navigate = useNavigate();
  const { toast } = useToast();
  const { t } = useLanguage();

  // Core state
  const [documentTitle, setDocumentTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Structure state (synced from DOM)
  const documentStructureRef = useRef<StructureNode[]>([]);
  const introSlideRef = useRef<IntroSlide | null>(null);
  const [introSlide, setIntroSlide] = useState<IntroSlide | null>(null);
  const [slides, setSlides] = useState<SlidePreview[]>([]);
  const [stats, setStats] = useState({ blocks: 0, chars: 0, slides: 0, words: 0 });

  // UI state
  const [introModalOpen, setIntroModalOpen] = useState(false);
  const [introModalText, setIntroModalText] = useState("");
  const [resetDialogOpen, setResetDialogOpen] = useState(false);
  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const [selectionInfo, setSelectionInfo] = useState<{ text: string; length: number } | null>(null);
  const [quickToolbar, setQuickToolbar] = useState<{ visible: boolean; x: number; y: number }>({
    visible: false,
    x: 0,
    y: 0,
  });

  // Pending formatting state (two-step: Level then Type)
  const [pendingLevel, setPendingLevel] = useState<number | "normal" | null>(null);
  const [pendingType, setPendingType] = useState<"title" | "content" | null>(null);

  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);

  // Find & Replace
  const [findReplaceOpen, setFindReplaceOpen] = useState(false);
  const [findText, setFindText] = useState("");
  const [replaceText, setReplaceText] = useState("");
  const [matchCount, setMatchCount] = useState(0);
  const [currentMatchIndex, setCurrentMatchIndex] = useState(0);
  const [caseSensitive, setCaseSensitive] = useState(false);
  const findInputRef = useRef<HTMLInputElement>(null);

  // Zoom
  const [zoomLevel, setZoomLevel] = useState(100);
  const [maxLevel, setMaxLevel] = useState(DEFAULT_MAX_LEVEL);

  // Save/validation state
  const [isDirty, setIsDirty] = useState(false);
  const [lastSavedAt, setLastSavedAt] = useState<number | null>(null);
  const [validationIssues, setValidationIssues] = useState<ValidationIssue[]>([]);
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);

  // Refs
  const editorRef = useRef<HTMLDivElement>(null);
  const quickToolbarRef = useRef<HTMLDivElement>(null);
  const savedSelectionRangeRef = useRef<Range | null>(null);
  const isPointerSelectingRef = useRef(false);
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const documentTextRef = useRef("");
  const listenersSetupRef = useRef(false);
  const historyRef = useRef<string[]>([]);
  const historyIndexRef = useRef(-1);
  const isApplyingHistoryRef = useRef(false);

  const handleGoBack = () => {
    if (isDirty) {
      setCancelDialogOpen(true);
      return;
    }
    navigate(-1);
  };

  const confirmCancel = () => {
    setCancelDialogOpen(false);
    navigate(-1);
  };

  // ---- Utilities ----
  const escapeHtml = (text: string): string => {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  };

  const escapeHtmlPreserveLineBreaks = (text: string): string => {
    return escapeHtml(text).replace(/\n/g, "<br>");
  };

  const generateNodeId = (): string => {
    return "node_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9);
  };

  const extractTextSafely = (node: Element): string => {
    const clone = node.cloneNode(true) as Element;
    const handle = clone.querySelector(".drag-handle");
    if (handle) handle.remove();
    // Strip find-highlight marks (keep their text)
    clone.querySelectorAll(".find-highlight").forEach((mark) => {
      const text = document.createTextNode(mark.textContent || "");
      mark.parentNode?.replaceChild(text, mark);
    });
    clone.normalize();
    clone.innerHTML = clone.innerHTML.replace(/<br\s*\/?>/gi, "\n");
    return clone.textContent || "";
  };

  const collectFlatBlocksFromEditor = useCallback(
    (includeEmpty = false): FlatEditorBlock[] => {
      const editor = editorRef.current;
      if (!editor) return [];

      const blocks = editor.querySelectorAll(".text-block");
      const result: FlatEditorBlock[] = [];

      blocks.forEach((block) => {
        const el = block as HTMLElement;
        const text = extractTextSafely(block);
        const trimmed = text.trim();
        if (!includeEmpty && !trimmed) return;

        const type = (el.dataset.type === "title" ? "title" : "content") as "title" | "content";
        result.push({
          node_id: el.dataset.nodeId || generateNodeId(),
          level: el.dataset.level !== undefined ? parseInt(el.dataset.level, 10) : 1,
          type,
          text: trimmed,
          is_transition: el.dataset.transition === "true",
        });
      });

      return result;
    },
    []
  );

  const clearValidationHighlights = useCallback(() => {
    const editor = editorRef.current;
    if (!editor) return;
    editor.querySelectorAll(".text-block.validation-error").forEach((block) => {
      block.classList.remove("validation-error");
    });
  }, []);

  const updateHistoryButtons = useCallback(() => {
    setCanUndo(historyIndexRef.current > 0);
    setCanRedo(historyIndexRef.current >= 0 && historyIndexRef.current < historyRef.current.length - 1);
  }, []);

  const initializeHistoryFromEditor = useCallback(() => {
    const editor = editorRef.current;
    if (!editor) return;
    historyRef.current = [editor.innerHTML];
    historyIndexRef.current = 0;
    updateHistoryButtons();
  }, [updateHistoryButtons]);

  const updateSelectionInfo = useCallback(() => {
    const editor = editorRef.current;
    const selection = window.getSelection();
    if (!editor || !selection || selection.rangeCount === 0) {
      setSelectionInfo(null);
      return;
    }

    const selectedText = selection.toString().replace(/\s+/g, " ").trim();
    const inEditor =
      !!selection.anchorNode &&
      !!selection.focusNode &&
      editor.contains(selection.anchorNode) &&
      editor.contains(selection.focusNode);

    if (!inEditor || selectedText.length === 0) {
      setSelectionInfo(null);
      return;
    }

    setSelectionInfo({
      text: selectedText.length > 80 ? selectedText.substring(0, 80) + "..." : selectedText,
      length: selectedText.length,
    });
  }, []);

  const rememberEditorSelection = useCallback(() => {
    const editor = editorRef.current;
    const selection = window.getSelection();
    if (!editor || !selection || selection.rangeCount === 0 || selection.isCollapsed) return;

    const inEditor =
      !!selection.anchorNode &&
      !!selection.focusNode &&
      editor.contains(selection.anchorNode) &&
      editor.contains(selection.focusNode);
    if (!inEditor) return;

    savedSelectionRangeRef.current = selection.getRangeAt(0).cloneRange();
  }, []);

  const restoreEditorSelection = useCallback((): boolean => {
    const editor = editorRef.current;
    const savedRange = savedSelectionRangeRef.current;
    if (!editor || !savedRange) return false;

    if (!editor.contains(savedRange.startContainer) || !editor.contains(savedRange.endContainer)) {
      savedSelectionRangeRef.current = null;
      return false;
    }

    const selection = window.getSelection();
    if (!selection) return false;
    selection.removeAllRanges();
    selection.addRange(savedRange.cloneRange());
    return true;
  }, []);

  const updateQuickToolbarPosition = useCallback(() => {
    const editor = editorRef.current;
    const selection = window.getSelection();
    if (!editor || !selection || selection.rangeCount === 0 || selection.isCollapsed) {
      setQuickToolbar((prev) => ({ ...prev, visible: false }));
      return;
    }

    const selectedText = selection.toString().trim();
    const inEditor =
      !!selection.anchorNode &&
      !!selection.focusNode &&
      editor.contains(selection.anchorNode) &&
      editor.contains(selection.focusNode);

    if (!selectedText || !inEditor) {
      setQuickToolbar((prev) => ({ ...prev, visible: false }));
      return;
    }

    const rect = selection.getRangeAt(0).getBoundingClientRect();
    if (rect.width === 0 && rect.height === 0) {
      setQuickToolbar((prev) => ({ ...prev, visible: false }));
      return;
    }

    const viewportPadding = 12;
    const editorRect = editor.getBoundingClientRect();
    const leftBound = Math.max(viewportPadding, editorRect.left + 8);
    const rightBound = Math.min(window.innerWidth - viewportPadding, editorRect.right - 8);
    const availableWidth = Math.max(220, rightBound - leftBound);
    const estimatedWidth = Math.min(availableWidth, 280 + (maxLevel + 3) * 36);
    const rawCenterX = rect.left + rect.width / 2;
    const clampedX = Math.max(
      leftBound + estimatedWidth / 2,
      Math.min(rightBound - estimatedWidth / 2, rawCenterX)
    );

    const aboveY = rect.top - 56;
    const belowY = rect.bottom + 10;
    let finalY = aboveY;
    if (aboveY < viewportPadding) {
      finalY = belowY;
    }

    rememberEditorSelection();
    setQuickToolbar({
      visible: true,
      x: clampedX,
      y: finalY,
    });
  }, [maxLevel, rememberEditorSelection]);

  const recordHistorySnapshot = useCallback(() => {
    if (isApplyingHistoryRef.current) return;
    const editor = editorRef.current;
    if (!editor) return;
    const html = editor.innerHTML;

    const current =
      historyIndexRef.current >= 0 ? historyRef.current[historyIndexRef.current] : null;
    if (current === html) return;

    if (historyIndexRef.current < historyRef.current.length - 1) {
      historyRef.current = historyRef.current.slice(0, historyIndexRef.current + 1);
    }

    historyRef.current.push(html);
    if (historyRef.current.length > 120) {
      historyRef.current.shift();
    }
    historyIndexRef.current = historyRef.current.length - 1;
    updateHistoryButtons();
  }, [updateHistoryButtons]);

  // ---- Build hierarchy from flat blocks ----
  const buildHierarchy = useCallback(
    (
      flatBlocks: Array<{
        node_id: string;
        level: number;
        type: string;
        text: string;
        is_transition: boolean;
      }>
    ): StructureNode[] => {
      const introBlocks = flatBlocks.filter((b) => b.level === 0);
      if (introBlocks.length > 0) {
        const combinedText = introBlocks.map((b) => b.text).join("\n");
        const intro: IntroSlide = {
          id: "intro_slide_0",
          level: 0,
          title: "Intro",
          content: combinedText,
          type: "title",
          children: [] as never[],
        };
        introSlideRef.current = intro;
        setIntroSlide(intro);
      }

      const blocks = flatBlocks.filter((b) => b.level > 0);
      const result: StructureNode[] = [];
      const stack: Array<{ level: number; children: StructureNode[] }> = [{ level: 0, children: result }];

      // Group consecutive title + content at same level
      const grouped: StructureNode[] = [];
      for (let i = 0; i < blocks.length; i++) {
        const block = blocks[i];
        if (block.type === "title" && i + 1 < blocks.length) {
          const next = blocks[i + 1];
          if (next.type === "content" && next.level === block.level) {
            grouped.push({
              node_id: block.node_id,
              level: block.level,
              title: block.text,
              content: next.text,
              children: [],
              is_transition: block.is_transition,
            });
            i++;
            continue;
          }
        }
        grouped.push({
          node_id: block.node_id,
          level: block.level,
          title: block.type === "title" ? block.text : "",
          content: block.type === "content" ? block.text : "",
          children: [],
          is_transition: block.is_transition,
        });
      }

      for (const node of grouped) {
        while (stack.length > 1 && stack[stack.length - 1].level >= node.level) {
          stack.pop();
        }
        stack[stack.length - 1].children.push(node);
        stack.push({ level: node.level, children: node.children });
      }

      return result;
    },
    []
  );

  // ---- Build slides from structure ----
  const buildSlides = useCallback(
    (structure: StructureNode[], intro: IntroSlide | null): SlidePreview[] => {
      const result: SlidePreview[] = [];

      if (intro) {
        result.push({
          id: "intro",
          title: "Intro Slide",
          content: intro.content || intro.title,
          bullets: [],
          isIntro: true,
        });
      }

      const flattenChildren = (children: StructureNode[]): { level: number; text: string }[] => {
        const bullets: { level: number; text: string }[] = [];
        for (const child of children) {
          let text = child.title;
          if (child.content) text = text ? `${text}: ${child.content}` : child.content;
          if (text) bullets.push({ level: child.level, text });
          if (child.children?.length) bullets.push(...flattenChildren(child.children));
        }
        return bullets;
      };

      for (const node of structure) {
        if (node.level === 1) {
          result.push({
            id: node.node_id,
            title: node.title || "Untitled",
            content: node.content || "",
            bullets: flattenChildren(node.children),
            isTransition: node.is_transition,
          });
        }
      }

      return result;
    },
    []
  );

  // ---- Sync editor DOM → structure state ----
  const syncEditorToStructure = useCallback(() => {
    const editor = editorRef.current;
    if (!editor) return;
    const blocks = editor.querySelectorAll(".text-block");
    const flatBlocks = collectFlatBlocksFromEditor(false);

    const structure = buildHierarchy(flatBlocks);
    documentStructureRef.current = structure;

    const newSlides = buildSlides(structure, introSlideRef.current);
    setSlides(newSlides);

    const charCount = editor.textContent?.length || 0;
    const wordCount = (editor.textContent || "").trim().split(/\s+/).filter((w) => w.length > 0).length;
    setStats({ blocks: blocks.length, chars: charCount, slides: newSlides.length, words: wordCount });
  }, [buildHierarchy, buildSlides, collectFlatBlocksFromEditor]);

  // ---- Save structure to backend ----
  const saveStructure = useCallback(async () => {
    if (!sessionId) return;

    const convertToBackendFormat = (nodes: StructureNode[]): any[] => {
      return nodes.map((node) => ({
        level: node.level,
        title: node.title || "",
        content: node.content || "",
        children: node.children ? convertToBackendFormat(node.children) : [],
        is_transition: node.is_transition || false,
        node_id: node.node_id,
      }));
    };

    try {
      const backendStructure = convertToBackendFormat(documentStructureRef.current);
      await api.updateStructure(sessionId, backendStructure, introSlideRef.current || undefined);
      setIsDirty(false);
      setLastSavedAt(Date.now());
    } catch {
      // Silent fail for auto-save
    }
  }, [sessionId]);

  // ---- Full sync: sync DOM → state → save ----
  const fullSync = useCallback(() => {
    setIsDirty(true);
    if (validationIssues.length > 0) {
      setValidationIssues([]);
      clearValidationHighlights();
    }
    syncEditorToStructure();
    recordHistorySnapshot();
    if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    saveTimeoutRef.current = setTimeout(() => {
      saveStructure();
    }, 1500);
  }, [
    syncEditorToStructure,
    saveStructure,
    validationIssues.length,
    clearValidationHighlights,
    recordHistorySnapshot,
  ]);

  // ---- Render existing structure into editor ----
  const renderExistingStructure = useCallback(
    (structure: any[]) => {
      const editor = editorRef.current;
      if (!editor) return;

      const renderNodes = (nodes: any[]): string => {
        let result = "";
        for (const node of nodes) {
          if (node.title) {
            result += `<span class="text-block text-level-${node.level} text-title${node.is_transition ? " transition-hidden" : ""}" data-level="${node.level}" data-type="title" data-node-id="${node.node_id || generateNodeId()}"${node.is_transition ? ' data-transition="true"' : ''}><span class="drag-handle" contenteditable="false">⠿</span>${escapeHtml(node.title)}</span>\n`;
          }
          if (node.content) {
            result += `<span class="text-block text-level-${node.level} text-content${node.is_transition ? " transition-hidden" : ""}" data-level="${node.level}" data-type="content" data-node-id="${(node.node_id || generateNodeId()) + "_c"}"${node.is_transition ? ' data-transition="true"' : ''}><span class="drag-handle" contenteditable="false">⠿</span>${escapeHtml(node.content)}</span>\n`;
          }
          if (node.children?.length) {
            result += renderNodes(node.children);
          }
        }
        return result;
      };

      const html = renderNodes(structure);
      editor.innerHTML = html || escapeHtml(documentTextRef.current);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  // ---- Setup editor event listeners (called once after content loaded) ----
  const setupEditorListeners = useCallback(() => {
    const editor = editorRef.current;
    if (!editor || listenersSetupRef.current) return;
    listenersSetupRef.current = true;

    // Text selection
    const handleSelectionCommit = () => {
      window.requestAnimationFrame(() => {
        updateSelectionInfo();
        updateQuickToolbarPosition();
      });
    };
    const handlePointerDown = (e: MouseEvent) => {
      if (e.button !== 0) return;
      isPointerSelectingRef.current = true;
      setQuickToolbar((prev) => ({ ...prev, visible: false }));
    };
    const handlePointerUp = () => {
      if (!isPointerSelectingRef.current) return;
      isPointerSelectingRef.current = false;
      handleSelectionCommit();
    };

    editor.addEventListener("mousedown", handlePointerDown);
    editor.addEventListener("mouseup", handlePointerUp);
    editor.addEventListener("keyup", handleSelectionCommit);

    // Content changes (debounced)
    let inputTimeout: ReturnType<typeof setTimeout>;
    editor.addEventListener("input", () => {
      clearTimeout(inputTimeout);
      inputTimeout = setTimeout(() => fullSync(), 500);
    });

    // Prevent drag unless using handle
    editor.addEventListener("dragstart", (e: DragEvent) => {
      if (!(e.target as Element)?.closest(".drag-handle")) {
        e.preventDefault();
      }
    });

    // Enter key: break out of text blocks
    editor.addEventListener("keydown", (e: KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        const selection = window.getSelection();
        if (!selection?.rangeCount) return;
        const range = selection.getRangeAt(0);
        let node: Node | null = range.commonAncestorContainer;
        if (node.nodeType === 3) node = node.parentElement;
        const block = (node as Element)?.closest?.(".text-block");
        if (block) {
          e.preventDefault();
          const newLine = document.createElement("div");
          newLine.innerHTML = "<br>";
          if (block.nextSibling) {
            block.parentNode!.insertBefore(newLine, block.nextSibling);
          } else {
            block.parentNode!.appendChild(newLine);
          }
          const newRange = document.createRange();
          newRange.setStart(newLine, 0);
          newRange.collapse(true);
          selection.removeAllRanges();
          selection.addRange(newRange);
        }
      }
    });

    // Drag & Drop
    setupDragDrop(editor);
  }, [fullSync, updateQuickToolbarPosition, updateSelectionInfo]);

  useEffect(() => {
    const handleDocumentMouseUp = () => {
      if (!isPointerSelectingRef.current) return;
      isPointerSelectingRef.current = false;
      window.requestAnimationFrame(() => {
        updateSelectionInfo();
        updateQuickToolbarPosition();
      });
    };

    const handleSelectionChange = () => {
      if (isPointerSelectingRef.current) return;
      const selection = window.getSelection();
      const editor = editorRef.current;
      if (!selection || !editor || selection.rangeCount === 0) {
        setSelectionInfo(null);
        setQuickToolbar((prev) => ({ ...prev, visible: false }));
        return;
      }

      const inEditor =
        !!selection.anchorNode &&
        !!selection.focusNode &&
        editor.contains(selection.anchorNode) &&
        editor.contains(selection.focusNode);

      if (!inEditor) {
        setSelectionInfo(null);
        setQuickToolbar((prev) => ({ ...prev, visible: false }));
      }
    };

    const handleDocumentMouseDown = (e: MouseEvent) => {
      const editor = editorRef.current;
      const target = e.target as Node | null;
      if (!editor || !target) return;

      if (quickToolbarRef.current && quickToolbarRef.current.contains(target)) {
        return;
      }

      if (!editor.contains(target)) {
        setQuickToolbar((prev) => ({ ...prev, visible: false }));
      }
    };

    document.addEventListener("mouseup", handleDocumentMouseUp);
    document.addEventListener("mousedown", handleDocumentMouseDown);
    document.addEventListener("selectionchange", handleSelectionChange);
    return () => {
      document.removeEventListener("mouseup", handleDocumentMouseUp);
      document.removeEventListener("mousedown", handleDocumentMouseDown);
      document.removeEventListener("selectionchange", handleSelectionChange);
    };
  }, [updateQuickToolbarPosition, updateSelectionInfo]);

  useEffect(() => {
    if (!quickToolbar.visible) return;
    const toolbar = quickToolbarRef.current;
    const editor = editorRef.current;
    if (!toolbar || !editor) return;

    const rect = toolbar.getBoundingClientRect();
    const padding = 10;
    const editorRect = editor.getBoundingClientRect();

    const leftLimit = Math.max(padding, editorRect.left + 6);
    const rightLimit = Math.min(window.innerWidth - padding, editorRect.right - 6);
    const topLimit = padding;
    const bottomLimit = window.innerHeight - padding;

    let dx = 0;
    let dy = 0;

    if (rect.left < leftLimit) dx = leftLimit - rect.left;
    else if (rect.right > rightLimit) dx = rightLimit - rect.right;

    if (rect.top < topLimit) dy = topLimit - rect.top;
    else if (rect.bottom > bottomLimit) dy = bottomLimit - rect.bottom;

    if (dx !== 0 || dy !== 0) {
      setQuickToolbar((prev) => ({
        ...prev,
        x: prev.x + dx,
        y: prev.y + dy,
      }));
    }
  }, [quickToolbar.visible, quickToolbar.x, quickToolbar.y]);

  // ---- Drag & Drop ----
  const setupDragDrop = (editor: HTMLDivElement) => {
    let draggedBlock: HTMLElement | null = null;

    const observer = new MutationObserver(() => addDragListeners());
    observer.observe(editor, { childList: true, subtree: true });
    addDragListeners();

    function addDragListeners() {
      const blocks = editor.querySelectorAll(".text-block");
      blocks.forEach((block) => {
        if (block.getAttribute("data-drag-setup") === "true") return;
        block.setAttribute("data-drag-setup", "true");
        block.setAttribute("draggable", "true");

        block.addEventListener(
          "dragstart",
          ((e: DragEvent) => {
            if (!(e.target as Element)?.closest(".drag-handle")) {
              e.preventDefault();
              return;
            }
            const bl = (e.target as Element).closest(".text-block") as HTMLElement;
            if (!bl) return;
            draggedBlock = bl;
            bl.style.opacity = "0.5";
            e.dataTransfer!.effectAllowed = "move";
            e.dataTransfer!.setData("text/plain", bl.dataset.nodeId || "");
          }) as EventListener
        );

        block.addEventListener(
          "dragend",
          (() => {
            if (draggedBlock) draggedBlock.style.opacity = "1";
            draggedBlock = null;
            editor.querySelectorAll(".text-block").forEach((b) => {
              (b as HTMLElement).style.borderTop = "";
              (b as HTMLElement).style.borderBottom = "";
            });
          }) as EventListener
        );

        block.addEventListener(
          "dragover",
          ((e: DragEvent) => {
            e.preventDefault();
            e.dataTransfer!.dropEffect = "move";
            const target = (e.target as Element).closest(".text-block") as HTMLElement;
            if (target && target !== draggedBlock) {
              const rect = target.getBoundingClientRect();
              const midY = rect.top + rect.height / 2;
              target.style.borderTop = "";
              target.style.borderBottom = "";
              if (e.clientY < midY) {
                target.style.borderTop = "3px solid hsl(var(--primary))";
              } else {
                target.style.borderBottom = "3px solid hsl(var(--primary))";
              }
            }
          }) as EventListener
        );

        block.addEventListener(
          "dragleave",
          ((e: DragEvent) => {
            const target = (e.target as Element).closest(".text-block") as HTMLElement;
            if (target) {
              target.style.borderTop = "";
              target.style.borderBottom = "";
            }
          }) as EventListener
        );

        block.addEventListener(
          "drop",
          ((e: DragEvent) => {
            e.preventDefault();
            if (!draggedBlock) return;
            draggedBlock.style.opacity = "1";
            const targetBlock = (e.target as Element).closest(".text-block") as HTMLElement;
            if (!targetBlock || targetBlock === draggedBlock) return;

            const rect = targetBlock.getBoundingClientRect();
            const midY = rect.top + rect.height / 2;
            if (e.clientY < midY) {
              targetBlock.parentNode!.insertBefore(draggedBlock, targetBlock);
            } else {
              if (targetBlock.nextSibling) {
                targetBlock.parentNode!.insertBefore(draggedBlock, targetBlock.nextSibling);
              } else {
                targetBlock.parentNode!.appendChild(draggedBlock);
              }
            }

            targetBlock.style.borderTop = "";
            targetBlock.style.borderBottom = "";
            draggedBlock = null;
            fullSync();
          }) as EventListener
        );
      });
    }
  };

  // ---- Load data ----
  useEffect(() => {
    if (sessionId) {
      loadStructure();
    } else {
      setLoading(false);
      toast({
        title: "Không có session ID",
        description: "Vui lòng tải lên tài liệu trước",
        variant: "destructive",
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  const loadStructure = async () => {
    try {
      const data = await api.getStructure(sessionId!);
      setDocumentTitle(data.document_title || "Untitled");
      documentTextRef.current = data.document_text || "";

      const editor = editorRef.current;
      if (!editor) return;

      if (data.document_structure?.length) {
        renderExistingStructure(data.document_structure);
      } else {
        // Show plain text - user will select and format
        editor.innerHTML = escapeHtmlPreserveLineBreaks(data.document_text || "");
      }

      setupEditorListeners();
      syncEditorToStructure();
      initializeHistoryFromEditor();
      setIsDirty(false);
      setLastSavedAt(Date.now());
      setValidationIssues([]);
      clearValidationHighlights();
    } catch (err: any) {
      toast({
        title: "Lỗi tải cấu trúc",
        description: err.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getSelectedBlocksInEditor = useCallback((editor: HTMLElement): HTMLElement[] => {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return [];

    const allBlocks = Array.from(editor.querySelectorAll(".text-block")) as HTMLElement[];
    let selectedBlocks = allBlocks.filter((block) => selection.containsNode(block, true));

    if (selectedBlocks.length === 0) {
      const range = selection.getRangeAt(0);
      let node: Node | null = range.commonAncestorContainer;
      if (node.nodeType === 3) node = node.parentElement;
      const block = (node as Element)?.closest?.(".text-block") as HTMLElement;
      if (block) selectedBlocks = [block];
    }

    return selectedBlocks;
  }, []);

  const validateStructureBeforeApprove = useCallback((): ValidationIssue[] => {
    const flatBlocksAll = collectFlatBlocksFromEditor(true);
    const flatBlocks = flatBlocksAll.filter((b) => b.text.length > 0);
    const issues: ValidationIssue[] = [];

    clearValidationHighlights();

    // Rule 1: Empty block
    flatBlocksAll.forEach((block) => {
      if (!block.text) {
        issues.push({
          nodeId: block.node_id,
          message: "Phát hiện block rỗng. Hãy nhập nội dung hoặc chuyển về normal text.",
        });
      }
    });

    // Rule 2: Invalid level jump (e.g. L1 -> L4)
    for (let i = 1; i < flatBlocks.length; i++) {
      const prev = flatBlocks[i - 1];
      const current = flatBlocks[i];
      if (current.level > prev.level + 1) {
        issues.push({
          nodeId: current.node_id,
          message: `Level nhảy sai từ L${prev.level} lên L${current.level}. Chỉ nên tăng tối đa 1 cấp.`,
        });
      }
    }

    // Rule 3: Missing slide title on level 1 node
    const structure = buildHierarchy(flatBlocks);
    structure.forEach((node) => {
      if (node.level === 1 && !node.title?.trim()) {
        issues.push({
          nodeId: node.node_id,
          message: "Slide cấp L1 đang thiếu title.",
        });
      }
    });

    if (issues.length > 0) {
      setValidationIssues(issues);
      const editor = editorRef.current;
      if (editor) {
        const issueIds = new Set(issues.map((issue) => issue.nodeId.replace(/_c$/, "")));
        editor.querySelectorAll(".text-block").forEach((block) => {
          const el = block as HTMLElement;
          const id = el.dataset.nodeId || "";
          const baseId = id.replace(/_c$/, "");
          if (issueIds.has(baseId)) {
            el.classList.add("validation-error");
          }
        });
      }
    } else {
      setValidationIssues([]);
    }

    return issues;
  }, [buildHierarchy, clearValidationHighlights, collectFlatBlocksFromEditor]);

  // ---- Formatting: Apply level/type to selected text ----
  const applyFormatting = (newLevel: number | "normal" | null, newType: "title" | "content" | null) => {
    const editor = editorRef.current;
    if (!editor) return;
    const selection = window.getSelection();
    if (!selection) return;

    // Find selected blocks (existing formatted blocks in selection)
    const selectedBlocks = selection.rangeCount > 0 ? getSelectedBlocksInEditor(editor) : [];

    // CASE 1: Editing existing block(s) - immediate effect
    if (selectedBlocks.length > 0) {
      if (newLevel === "normal") {
        selectedBlocks.forEach((block) => {
          const text = extractTextSafely(block);
          const textNode = document.createTextNode(text);
          if (block.nextSibling && (block.nextSibling as Element).tagName === "BR") {
            block.nextSibling.remove();
          }
          block.replaceWith(textNode);
          textNode.parentElement?.normalize();
        });
        setPendingLevel(null);
        setPendingType(null);
        fullSync();
        return;
      }

      selectedBlocks.forEach((block) => {
        const level = newLevel !== null ? newLevel : parseInt(block.dataset.level || "1");
        const type = newType !== null ? newType : (block.dataset.type || "content");
        block.className = `text-block text-level-${level} text-${type}`;
        block.dataset.level = String(level);
        block.dataset.type = type as string;
      });
      setPendingLevel(null);
      setPendingType(null);
      fullSync();
      return;
    }

    // CASE 2: Creating new block (two-step: select Level → select Type)
    let currentPendingLevel = pendingLevel;
    let currentPendingType = pendingType;

    if (newLevel !== null) currentPendingLevel = newLevel;
    if (newType !== null) currentPendingType = newType;

    if (currentPendingLevel === "normal") {
      setPendingLevel(null);
      setPendingType(null);
      return;
    }

    // Intro (L0) defaults to title type
    if (currentPendingLevel === 0 && !currentPendingType) {
      currentPendingType = "title";
    }

    setPendingLevel(currentPendingLevel);
    setPendingType(currentPendingType);

    // When we have BOTH level and type, create formatted block from selection
    if (currentPendingLevel !== null && currentPendingType !== null) {
      createFormattedBlock(currentPendingLevel as number, currentPendingType);
      setPendingLevel(null);
      setPendingType(null);
    }
  };

  // ---- Create formatted block from text selection ----
  const createFormattedBlock = (level: number, type: "title" | "content") => {
    const selection = window.getSelection();
    if (!selection?.rangeCount) return;
    const range = selection.getRangeAt(0);
    const nodeId = generateNodeId();

    const isBoundaryEmptyLine = (node: Node | null): boolean => {
      if (!node) return false;
      if (node.nodeType === Node.ELEMENT_NODE) {
        const el = node as HTMLElement;
        if (el.tagName === "BR") return true;
        if ((el.tagName === "DIV" || el.tagName === "P") && !(el.textContent || "").trim()) return true;
      }
      if (node.nodeType === Node.TEXT_NODE && !(node.textContent || "").trim()) return true;
      return false;
    };

    try {
      const wrapper = document.createElement("span");
      wrapper.className = `text-block text-level-${level} text-${type}`;
      wrapper.dataset.level = String(level);
      wrapper.dataset.type = type;
      wrapper.dataset.nodeId = nodeId;

      const contents = range.extractContents();

      const handle = document.createElement("span");
      handle.className = "drag-handle";
      handle.contentEditable = "false";
      handle.textContent = "⠿";
      wrapper.appendChild(handle);
      wrapper.appendChild(contents);

      // Trim leading/trailing empty line nodes from extracted content to avoid accidental blank lines.
      while (wrapper.childNodes.length > 1 && isBoundaryEmptyLine(wrapper.childNodes[1])) {
        wrapper.removeChild(wrapper.childNodes[1]);
      }
      while (wrapper.lastChild && wrapper.lastChild !== handle && isBoundaryEmptyLine(wrapper.lastChild)) {
        wrapper.removeChild(wrapper.lastChild);
      }

      range.insertNode(wrapper);

      selection.removeAllRanges();
      fullSync();
    } catch {
      toast({ title: "Không thể áp dụng định dạng", variant: "destructive" });
    }
  };

  // ---- Intro Slide ----
  const openIntroModal = () => {
    setIntroModalText(introSlide?.content || documentTitle || "");
    setIntroModalOpen(true);
  };

  const saveIntro = () => {
    if (!introModalText.trim()) {
      toast({ title: "Vui lòng nhập nội dung intro", variant: "destructive" });
      return;
    }
    const intro: IntroSlide = {
      id: "intro_slide_0",
      level: 0,
      title: "Intro",
      content: introModalText.trim(),
      type: "title",
      children: [] as never[],
    };
    introSlideRef.current = intro;
    setIntroSlide(intro);

    // Add/replace block in editor at beginning
    const editor = editorRef.current;
    if (editor) {
      const existing = editor.querySelector('[data-node-id="intro_slide_0"]');
      if (existing) {
        if (existing.nextSibling && (existing.nextSibling as Element).tagName === "BR") {
          existing.nextSibling.remove();
        }
        existing.remove();
      }

      const introBlock = document.createElement("span");
      introBlock.className = "text-block text-level-0 text-title";
      introBlock.dataset.level = "0";
      introBlock.dataset.type = "title";
      introBlock.dataset.nodeId = "intro_slide_0";
      introBlock.innerHTML = `<span class="drag-handle" contenteditable="false">⠿</span>${escapeHtml(introModalText.trim())}`;

      const firstChild = editor.firstChild;
      if (firstChild) {
        editor.insertBefore(introBlock, firstChild);
        editor.insertBefore(document.createElement("br"), introBlock.nextSibling);
      } else {
        editor.appendChild(introBlock);
      }
    }

    setIntroModalOpen(false);
    fullSync();
  };

  // ---- Delete Intro ----
  const deleteIntroSlide = () => {
    const editor = editorRef.current;
    if (editor) {
      const block = editor.querySelector('[data-node-id="intro_slide_0"]');
      if (block) {
        if (block.nextSibling && (block.nextSibling as Element).tagName === "BR") {
          block.nextSibling.remove();
        }
        block.remove();
      }
    }
    introSlideRef.current = null;
    setIntroSlide(null);
    fullSync();
  };

  // ---- Reset ----
  const handleReset = () => {
    const editor = editorRef.current;
    if (editor) {
      const plainText = editor.innerText || editor.textContent || "";
      editor.innerHTML = escapeHtmlPreserveLineBreaks(plainText);
    }
    documentStructureRef.current = [];
    introSlideRef.current = null;
    setIntroSlide(null);
    setResetDialogOpen(false);
    fullSync();
    toast({ title: "Đã reset cấu trúc" });
  };

  // ---- Approve ----
  const handleApprove = async () => {
    if (!sessionId) return;

    syncEditorToStructure();
    const issues = validateStructureBeforeApprove();
    if (issues.length > 0) {
      setApproveDialogOpen(false);
      toast({
        title: "Không thể duyệt cấu trúc",
        description: `Có ${issues.length} lỗi cần sửa trước khi Approve.`,
        variant: "destructive",
      });
      return;
    }

    setValidationIssues([]);
    clearValidationHighlights();
    setApproveDialogOpen(false);
    setSaving(true);
    try {
      const convertToBackendFormat = (nodes: StructureNode[]): any[] => {
        return nodes.map((node) => ({
          level: node.level,
          title: node.title || "",
          content: node.content || "",
          children: node.children ? convertToBackendFormat(node.children) : [],
          is_transition: node.is_transition || false,
          node_id: node.node_id,
        }));
      };
      await api.updateStructure(
        sessionId,
        convertToBackendFormat(documentStructureRef.current),
        introSlideRef.current || undefined
      );

      const result = await api.approveStructure(sessionId);
      if (result.success) {
        toast({
          title: "Đã duyệt cấu trúc!",
          description: `${result.slide_types?.length || 0} slides đã chuẩn bị`,
        });
        navigate(`/streaming/manual`, { state: { sessionId, documentTitle } });
      } else {
        toast({ title: "Lỗi duyệt", description: result.message, variant: "destructive" });
      }
    } catch (err: any) {
      toast({ title: "Lỗi", description: err.message, variant: "destructive" });
    } finally {
      setSaving(false);
    }
  };

  // ---- Transition Slide ----
  const createTransitionSlide = (slideId: string) => {
    const structure = documentStructureRef.current;
    const nodeIndex = structure.findIndex((n) => n.node_id === slideId);
    if (nodeIndex === -1) return;
    const node = structure[nodeIndex];
    if (node.level !== 1) return;

    if (nodeIndex > 0 && structure[nodeIndex - 1].is_transition) {
      toast({ title: "Transition đã tồn tại", variant: "destructive" });
      return;
    }

    const transitionNodeId = generateNodeId();
    const transitionNode: StructureNode = {
      node_id: transitionNodeId,
      level: 1,
      title: node.title,
      content: node.content || "",
      children: [],
      is_transition: true,
    };
    structure.splice(nodeIndex, 0, transitionNode);

    const editor = editorRef.current;
    if (editor) {
      const beforeBlock = editor.querySelector(`[data-node-id="${slideId}"]`);
      if (beforeBlock) {
        const transBlock = document.createElement("span");
        transBlock.className = "text-block text-level-1 text-title transition-hidden";
        transBlock.dataset.level = "1";
        transBlock.dataset.type = "title";
        transBlock.dataset.nodeId = transitionNodeId;
        transBlock.dataset.transition = "true";
        transBlock.innerHTML = `<span class="drag-handle" contenteditable="false">⠿</span>${escapeHtml(transitionNode.title)}`;
        transBlock.style.borderColor = "#0dcaf0";
        transBlock.style.background = "rgba(13, 202, 240, 0.15)";

        beforeBlock.parentNode!.insertBefore(transBlock, beforeBlock);

        if (transitionNode.content) {
          const contentBlock = document.createElement("span");
          contentBlock.className = "text-block text-level-1 text-content transition-hidden";
          contentBlock.dataset.level = "1";
          contentBlock.dataset.type = "content";
          contentBlock.dataset.nodeId = transitionNodeId + "_c";
          contentBlock.dataset.transition = "true";
          contentBlock.innerHTML = `<span class="drag-handle" contenteditable="false">⠿</span>${escapeHtml(transitionNode.content)}`;
          contentBlock.style.borderColor = "#0dcaf0";
          contentBlock.style.background = "rgba(13, 202, 240, 0.1)";
          beforeBlock.parentNode!.insertBefore(contentBlock, beforeBlock);
        }
      }
    }
    fullSync();
  };

  // ---- Delete Transition ----
  const deleteTransitionSlide = (slideId: string) => {
    const structure = documentStructureRef.current;
    const nodeIndex = structure.findIndex((n) => n.node_id === slideId);
    if (nodeIndex === -1 || !structure[nodeIndex].is_transition) return;

    structure.splice(nodeIndex, 1);

    const editor = editorRef.current;
    if (editor) {
      const block = editor.querySelector(`[data-node-id="${slideId}"]`);
      if (block) {
        if (block.nextElementSibling?.tagName === "BR") block.nextElementSibling.remove();
        block.remove();
      }
      const contentBlock = editor.querySelector(`[data-node-id="${slideId}_c"]`);
      if (contentBlock) {
        if (contentBlock.nextElementSibling?.tagName === "BR") contentBlock.nextElementSibling.remove();
        contentBlock.remove();
      }
    }
    fullSync();
  };

  // ---- Find & Replace ----
  const clearHighlights = useCallback(() => {
    const editor = editorRef.current;
    if (!editor) return;
    editor.querySelectorAll(".find-highlight").forEach((mark) => {
      mark.replaceWith(document.createTextNode(mark.textContent || ""));
    });
    editor.normalize();
  }, []);

  const runFind = useCallback(
    (searchText: string, cs: boolean = caseSensitive) => {
      const editor = editorRef.current;
      if (!editor) return;
      clearHighlights();
      if (!searchText.trim()) {
        setMatchCount(0);
        setCurrentMatchIndex(0);
        return;
      }

      const walker = document.createTreeWalker(editor, NodeFilter.SHOW_TEXT, {
        acceptNode(node) {
          const parent = node.parentElement;
          if (!parent) return NodeFilter.FILTER_REJECT;
          if (parent.classList.contains("drag-handle")) return NodeFilter.FILTER_REJECT;
          return NodeFilter.FILTER_ACCEPT;
        },
      });

      const textNodes: Text[] = [];
      let node;
      while ((node = walker.nextNode())) textNodes.push(node as Text);

      const flags = cs ? "g" : "gi";
      const escaped = searchText.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const regex = new RegExp(escaped, flags);

      let count = 0;
      textNodes.forEach((textNode) => {
        const text = textNode.nodeValue || "";
        if (!regex.test(text)) return;
        regex.lastIndex = 0;
        const fragment = document.createDocumentFragment();
        let lastIndex = 0;
        let match;
        while ((match = regex.exec(text)) !== null) {
          if (match.index > lastIndex) {
            fragment.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
          }
          const mark = document.createElement("mark");
          mark.className = "find-highlight";
          mark.setAttribute("data-match-index", String(count));
          mark.textContent = match[0];
          fragment.appendChild(mark);
          count++;
          lastIndex = match.index + match[0].length;
        }
        if (lastIndex < text.length) {
          fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
        }
        textNode.parentNode?.replaceChild(fragment, textNode);
      });

      setMatchCount(count);
      if (count > 0) {
        setCurrentMatchIndex(0);
        const firstMark = editor.querySelector(".find-highlight");
        if (firstMark) {
          firstMark.classList.add("find-current");
          firstMark.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      } else {
        setCurrentMatchIndex(0);
      }
    },
    [caseSensitive, clearHighlights]
  );

  const navigateMatch = useCallback(
    (direction: "next" | "prev") => {
      const editor = editorRef.current;
      if (!editor) return;
      const marks = Array.from(editor.querySelectorAll(".find-highlight"));
      if (!marks.length) return;
      marks.forEach((m) => m.classList.remove("find-current"));
      const newIndex =
        direction === "next"
          ? (currentMatchIndex + 1) % marks.length
          : (currentMatchIndex - 1 + marks.length) % marks.length;
      setCurrentMatchIndex(newIndex);
      marks[newIndex].classList.add("find-current");
      marks[newIndex].scrollIntoView({ behavior: "smooth", block: "center" });
    },
    [currentMatchIndex]
  );

  const replaceCurrentMatch = useCallback(() => {
    const editor = editorRef.current;
    if (!editor) return;
    const marks = editor.querySelectorAll(".find-highlight");
    const mark = marks[currentMatchIndex] as HTMLElement;
    if (!mark) return;
    mark.replaceWith(document.createTextNode(replaceText));
    editor.normalize();
    fullSync();
    setTimeout(() => runFind(findText), 50);
  }, [currentMatchIndex, replaceText, findText, runFind, fullSync]);

  const replaceAllMatches = useCallback(() => {
    const editor = editorRef.current;
    if (!editor) return;
    const marks = editor.querySelectorAll(".find-highlight");
    if (!marks.length) return;
    const count = marks.length;
    marks.forEach((mark) => mark.replaceWith(document.createTextNode(replaceText)));
    editor.normalize();
    fullSync();
    setMatchCount(0);
    setCurrentMatchIndex(0);
    toast({ title: `Đã thay thế ${count} kết quả` });
  }, [replaceText, fullSync, toast]);

  const handleUndo = () => {
    const editor = editorRef.current;
    if (!editor || historyIndexRef.current <= 0) return;

    historyIndexRef.current -= 1;
    const snapshot = historyRef.current[historyIndexRef.current];
    if (typeof snapshot !== "string") return;

    isApplyingHistoryRef.current = true;
    editor.innerHTML = snapshot;
    syncEditorToStructure();
    setIsDirty(true);
    updateHistoryButtons();
    if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    saveTimeoutRef.current = setTimeout(() => {
      saveStructure();
    }, 1500);
    setTimeout(() => {
      isApplyingHistoryRef.current = false;
    }, 0);
  };

  const handleRedo = () => {
    const editor = editorRef.current;
    if (!editor || historyIndexRef.current >= historyRef.current.length - 1) return;

    historyIndexRef.current += 1;
    const snapshot = historyRef.current[historyIndexRef.current];
    if (typeof snapshot !== "string") return;

    isApplyingHistoryRef.current = true;
    editor.innerHTML = snapshot;
    syncEditorToStructure();
    setIsDirty(true);
    updateHistoryButtons();
    if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    saveTimeoutRef.current = setTimeout(() => {
      saveStructure();
    }, 1500);
    setTimeout(() => {
      isApplyingHistoryRef.current = false;
    }, 0);
  };

  const adjustSelectedBlockLevels = useCallback(
    (delta: number) => {
      const editor = editorRef.current;
      if (!editor) return;
      const selectedBlocks = getSelectedBlocksInEditor(editor);
      if (selectedBlocks.length === 0) return;

      selectedBlocks.forEach((block) => {
        const currentLevel = parseInt(block.dataset.level || "1", 10);
        const nextLevel = Math.max(0, Math.min(maxLevel, currentLevel + delta));
        const type = (block.dataset.type || "content") as "title" | "content";
        block.className = `text-block text-level-${nextLevel} text-${type}`;
        block.dataset.level = String(nextLevel);
      });

      fullSync();
    },
    [fullSync, getSelectedBlocksInEditor, maxLevel]
  );

  const addOneMoreLevel = () => {
    setMaxLevel((prev) => prev + 1);
    toast({ title: `Đã thêm level L${maxLevel + 1}` });
  };

  const removeHighestLevel = () => {
    if (maxLevel <= DEFAULT_MAX_LEVEL) {
      toast({ title: `Không thể xóa dưới L${DEFAULT_MAX_LEVEL}`, variant: "destructive" });
      return;
    }

    const editor = editorRef.current;
    if (editor?.querySelector(`.text-block[data-level="${maxLevel}"]`)) {
      toast({
        title: `Không thể xóa L${maxLevel}`,
        description: `Vẫn còn block đang dùng level này. Hãy đổi về level thấp hơn trước.`,
        variant: "destructive",
      });
      return;
    }

    if (pendingLevel === maxLevel) {
      setPendingLevel(null);
    }

    setMaxLevel((prev) => prev - 1);
    toast({ title: `Đã xóa level L${maxLevel}` });
  };

  const visibleLevels = Array.from({ length: VISIBLE_LEVEL_LIMIT }, (_, idx) => idx + 1);
  const overflowLevels =
    maxLevel > VISIBLE_LEVEL_LIMIT
      ? Array.from({ length: maxLevel - VISIBLE_LEVEL_LIMIT }, (_, idx) => VISIBLE_LEVEL_LIMIT + idx + 1)
      : [];

  const applyInlineCommand = (command: "bold" | "italic" | "underline") => {
    if (!restoreEditorSelection()) return;
    document.execCommand(command);
    fullSync();
    updateSelectionInfo();
    window.requestAnimationFrame(() => updateQuickToolbarPosition());
  };

  const applyFormattingFromQuickToolbar = (level: number | "normal" | null, type: "title" | "content" | null) => {
    if (!restoreEditorSelection()) return;
    applyFormatting(level, type);
    updateSelectionInfo();
    window.requestAnimationFrame(() => updateQuickToolbarPosition());
  };

  // Keyboard shortcuts
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      const isInputField = target?.tagName === "INPUT" || target?.tagName === "TEXTAREA";
      const isEditorFocused = !!target?.closest?.("#wordEditor");

      // Global shortcuts
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "f") {
        e.preventDefault();
        setFindReplaceOpen(true);
        setTimeout(() => findInputRef.current?.focus(), 100);
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "h") {
        e.preventDefault();
        setFindReplaceOpen(true);
        setTimeout(() => findInputRef.current?.focus(), 100);
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
        e.preventDefault();
        syncEditorToStructure();
        saveStructure();
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        setApproveDialogOpen(true);
        return;
      }

      if (e.key === "Escape" && findReplaceOpen) {
        setFindReplaceOpen(false);
        clearHighlights();
        setFindText("");
        setMatchCount(0);
        return;
      }

      // Editor shortcuts
      if (!isEditorFocused || isInputField) return;

      if (e.key === "Tab") {
        e.preventDefault();
        adjustSelectedBlockLevels(e.shiftKey ? -1 : 1);
        return;
      }

      if ((e.ctrlKey || e.metaKey) && !e.shiftKey) {
        const key = e.key.toLowerCase();
        if (key === "z") {
          e.preventDefault();
          handleUndo();
          return;
        }
        if (key === "y") {
          e.preventDefault();
          handleRedo();
          return;
        }
        if (key === "b" || key === "i" || key === "u") {
          e.preventDefault();
          const command = key === "b" ? "bold" : key === "i" ? "italic" : "underline";
          document.execCommand(command);
          fullSync();
        }
      }

      if (e.altKey && !e.ctrlKey && !e.metaKey) {
        if (/^[0-9]$/.test(e.key)) {
          e.preventDefault();
          const targetLevel = parseInt(e.key, 10);
          if (targetLevel > maxLevel) {
            setMaxLevel(targetLevel);
          }
          applyFormatting(targetLevel, null);
          return;
        }
        if (e.key.toLowerCase() === "t") {
          e.preventDefault();
          applyFormatting(null, "title");
          return;
        }
        if (e.key.toLowerCase() === "c") {
          e.preventDefault();
          applyFormatting(null, "content");
        }
      }
    };

    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [
    adjustSelectedBlockLevels,
    applyFormatting,
    clearHighlights,
    findReplaceOpen,
    fullSync,
    maxLevel,
    saveStructure,
    syncEditorToStructure,
  ]);

  useEffect(() => {
    const onBeforeUnload = (e: BeforeUnloadEvent) => {
      if (!isDirty) return;
      e.preventDefault();
      e.returnValue = "";
    };

    window.addEventListener("beforeunload", onBeforeUnload);
    return () => window.removeEventListener("beforeunload", onBeforeUnload);
  }, [isDirty]);

  const disableStructureActions = loading || saving;
  const headerActions = (
    <>
      <button
        className="btn btn-sm btn-secondary"
        onClick={() => setResetDialogOpen(true)}
        disabled={loading || (stats.blocks === 0 && !introSlide)}
      >
        <RotateCcw className="mr-1.5 h-4 w-4" /> Reset
      </button>
      <button className="btn btn-sm btn-danger" onClick={() => setCancelDialogOpen(true)} disabled={loading}>
        <XCircle className="mr-1.5 h-4 w-4" /> Cancel
      </button>
      <button
        className="btn btn-sm btn-success"
        onClick={() => setApproveDialogOpen(true)}
        disabled={disableStructureActions || !sessionId || (stats.blocks === 0 && !introSlide)}
      >
        {saving ? <Loader2 className="mr-1.5 h-4 w-4 animate-spin" /> : <Check className="mr-1.5 h-4 w-4" />}
        {saving ? "Processing..." : "Approve & Continue"}
      </button>
    </>
  );

  const desktopHeaderBar = (
    <div className="legacy-app-header">
      <button className="btn btn-outline-light" onClick={handleGoBack} disabled={disableStructureActions}>
        <ArrowLeft className="mr-2 h-4 w-4" /> Back
      </button>
      <h2 className="header-title">
        <FileText className="mr-2 h-5 w-5" /> Structure Editor
      </h2>
      <div className="document-info">
        <FileText className="mr-2 h-4 w-4" />
        <span>{documentTitle || "Untitled document"}</span>
      </div>
      <div
        className={cn("save-indicator", saving ? "saving" : isDirty ? "unsaved" : "saved")}
        title={lastSavedAt ? `Lưu lúc ${new Date(lastSavedAt).toLocaleTimeString()}` : undefined}
      >
        {saving ? "Saving..." : isDirty ? "Unsaved changes" : "Saved"}
      </div>
      <div className="header-actions">{headerActions}</div>
    </div>
  );

  return (
    <AppLayout headerContent={desktopHeaderBar}>
      <div className="legacy-structure-page">
        <div className="legacy-aurora" aria-hidden />
        <div className="legacy-particles" aria-hidden>
          {Array.from({ length: 14 }).map((_, index) => (
            <span key={index} className={`legacy-particle legacy-particle-${index + 1}`} />
          ))}
        </div>
        <div className="legacy-structure-content">
          <div className="header-section header-section-mobile">
            <button className="btn btn-outline-light" onClick={handleGoBack} disabled={disableStructureActions}>
              <ArrowLeft className="mr-2 h-4 w-4" /> Back
            </button>
            <h2 className="header-title">
              <FileText className="mr-2 h-5 w-5" /> Structure Editor
            </h2>
            <div className="document-info">
              <FileText className="mr-2 h-4 w-4" />
              <span>{documentTitle || "Untitled document"}</span>
            </div>
            <div
              className={cn("save-indicator", saving ? "saving" : isDirty ? "unsaved" : "saved")}
              title={lastSavedAt ? `Lưu lúc ${new Date(lastSavedAt).toLocaleTimeString()}` : undefined}
            >
              {saving ? "Saving..." : isDirty ? "Unsaved changes" : "Saved"}
            </div>
            <div className="header-actions">{headerActions}</div>
          </div>

          <div className="main-content">
            <div className="editor-column">
              <div className="panel-container">
                <div className="editor-toolbar">
                  <div className="style-group level-group">
                    <div className="group-label">Level</div>
                    <div className="style-row level-row">
                      <button
                        className={cn("style-card style-normal", pendingLevel === "normal" && "active")}
                        onClick={() => applyFormatting("normal", null)}
                        title="Normal Text"
                      >
                        <span className="style-preview">Aa</span>
                        <span className="style-name">Normal</span>
                      </button>
                      <button
                        className={cn("style-card style-intro", pendingLevel === 0 && "active")}
                        onClick={() => applyFormatting(0, null)}
                        title="Intro Slide"
                      >
                        <span className="style-preview">Intro</span>
                        <span className="style-name">Slide</span>
                      </button>
                      {visibleLevels.map((level) => (
                        <button
                          key={level}
                          className={cn(`style-card style-l${level}`, pendingLevel === level && "active")}
                          onClick={() => applyFormatting(level, null)}
                          title={`Level ${level}`}
                        >
                          <span className="style-preview">
                            {level === 1 ? (
                              <strong>1</strong>
                            ) : level === 2 ? (
                              <span>2</span>
                            ) : (
                              `L${level}`
                            )}
                          </span>
                          <span className="style-name">
                            {level === 1 ? "Slide" : level === 2 ? "Bullet" : level === 3 ? "Sub" : `L${level}`}
                          </span>
                        </button>
                      ))}
                      <label className="level-overflow-select-wrap" title="Level bổ sung">
                        <span className="level-overflow-label">More</span>
                        <select
                          className="level-overflow-select"
                          defaultValue=""
                          disabled={overflowLevels.length === 0}
                          onChange={(e) => {
                            const value = Number(e.target.value);
                            if (!Number.isNaN(value) && value > 0) {
                              applyFormatting(value, null);
                            }
                            e.target.value = "";
                          }}
                        >
                          <option value="">Level...</option>
                          {overflowLevels.map((level) => (
                            <option key={`overflow-${level}`} value={level}>
                              L{level}
                            </option>
                          ))}
                        </select>
                      </label>
                      <button
                        className="style-card style-add-level"
                        onClick={addOneMoreLevel}
                        title="Thêm level con"
                      >
                        <Plus className="style-preview" style={{ width: 14, height: 14 }} />
                        <span className="style-name">+Level</span>
                      </button>
                      <button
                        className="style-card style-remove-level"
                        onClick={removeHighestLevel}
                        title={`Xóa level cao nhất (L${maxLevel})`}
                        disabled={maxLevel <= DEFAULT_MAX_LEVEL}
                      >
                        <span className="style-preview">-</span>
                        <span className="style-name">-Level</span>
                      </button>
                    </div>
                  </div>
                  <div className="style-separator-group" />
                  <div className="style-group">
                    <div className="group-label">Type</div>
                    <div className="style-row">
                      <button
                        className={cn("style-card style-type-title", pendingType === "title" && "active")}
                        onClick={() => applyFormatting(null, "title")}
                        title="Title"
                      >
                        <Type className="style-preview" />
                        <span className="style-name">Title</span>
                      </button>
                      <button
                        className={cn("style-card style-type-content", pendingType === "content" && "active")}
                        onClick={() => applyFormatting(null, "content")}
                        title="Content"
                      >
                        <AlignLeft className="style-preview" />
                        <span className="style-name">Content</span>
                      </button>
                    </div>
                  </div>
                  <div className="style-separator-group" />
                  <div className="style-group">
                    <div className="group-label">Edit</div>
                    <div className="style-row">
                      <button className="style-card" onClick={handleUndo} title="Undo (Ctrl+Z)" disabled={!canUndo}>
                        <Undo2 className="style-preview" style={{ width: 14, height: 14 }} />
                        <span className="style-name">Undo</span>
                      </button>
                      <button className="style-card" onClick={handleRedo} title="Redo (Ctrl+Y)" disabled={!canRedo}>
                        <Redo2 className="style-preview" style={{ width: 14, height: 14 }} />
                        <span className="style-name">Redo</span>
                      </button>
                      <button
                        className={cn("style-card", findReplaceOpen && "active")}
                        onClick={() => {
                          const next = !findReplaceOpen;
                          setFindReplaceOpen(next);
                          if (next) setTimeout(() => findInputRef.current?.focus(), 100);
                          else { clearHighlights(); setFindText(""); setMatchCount(0); }
                        }}
                        title="Find & Replace (Ctrl+F)"
                      >
                        <Search className="style-preview" style={{ width: 14, height: 14 }} />
                        <span className="style-name">Find</span>
                      </button>
                    </div>
                  </div>
                  <div className="style-separator-group" />
                  <div className="style-group toolbar-zoom-group">
                    <div className="group-label">Zoom</div>
                    <div className="zoom-controls">
                      <button
                        className="zoom-btn"
                        onClick={() => setZoomLevel((l) => Math.max(60, l - 10))}
                        disabled={zoomLevel <= 60}
                        title="Thu nhỏ"
                      >
                        <ZoomOut className="h-3.5 w-3.5" />
                      </button>
                      <span className="zoom-value">{zoomLevel}%</span>
                      <button
                        className="zoom-btn"
                        onClick={() => setZoomLevel((l) => Math.min(200, l + 10))}
                        disabled={zoomLevel >= 200}
                        title="Phóng to"
                      >
                        <ZoomIn className="h-3.5 w-3.5" />
                      </button>
                      <button className="zoom-btn" onClick={() => setZoomLevel(100)} title="Reset zoom (100%)">
                        <RotateCcw className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
                </div>

                <div className={cn("selection-info", selectionInfo && "visible")}>
                  <AlignLeft className="h-4 w-4" />
                  <span className="selection-text">{selectionInfo?.text || "No text selected"}</span>
                  <span className="badge bg-secondary">
                    {selectionInfo ? `${selectionInfo.length} chars` : "0 chars"}
                  </span>
                </div>

                {quickToolbar.visible && (
                  <div
                    ref={quickToolbarRef}
                    className="quick-format-toolbar"
                    style={{ left: quickToolbar.x, top: quickToolbar.y }}
                    onMouseDown={(e) => e.preventDefault()}
                  >
                    <div className="quick-tool-group">
                      <div className="quick-tool-group-label">Format</div>
                      <div className="quick-tool-group-row">
                        <button
                          className="quick-tool-btn"
                          title="Bold"
                          onMouseDown={(e) => e.preventDefault()}
                          onClick={() => applyInlineCommand("bold")}
                        >
                          <Bold className="h-3.5 w-3.5" />
                        </button>
                        <button
                          className="quick-tool-btn"
                          title="Italic"
                          onMouseDown={(e) => e.preventDefault()}
                          onClick={() => applyInlineCommand("italic")}
                        >
                          <Italic className="h-3.5 w-3.5" />
                        </button>
                        <button
                          className="quick-tool-btn"
                          title="Underline"
                          onMouseDown={(e) => e.preventDefault()}
                          onClick={() => applyInlineCommand("underline")}
                        >
                          <Underline className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>

                    <div className="quick-tool-group">
                      <div className="quick-tool-group-label">Level</div>
                      <div className="quick-tool-group-row">
                        <button
                          className="quick-tool-btn quick-level-btn"
                          title="Normal Text"
                          onMouseDown={(e) => e.preventDefault()}
                          onClick={() => applyFormattingFromQuickToolbar("normal", null)}
                        >
                          N
                        </button>
                        <button
                          className="quick-tool-btn quick-level-btn"
                          title="Level 0"
                          onMouseDown={(e) => e.preventDefault()}
                          onClick={() => applyFormattingFromQuickToolbar(0, null)}
                        >
                          L0
                        </button>
                        {Array.from({ length: maxLevel }, (_, idx) => idx + 1).map((level) => (
                          <button
                            key={`quick-level-${level}`}
                            className="quick-tool-btn quick-level-btn"
                            title={`Level ${level}`}
                            onMouseDown={(e) => e.preventDefault()}
                            onClick={() => applyFormattingFromQuickToolbar(level, null)}
                          >
                            L{level}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="quick-tool-group">
                      <div className="quick-tool-group-label">Type</div>
                      <div className="quick-tool-group-row">
                        <button
                          className="quick-tool-btn"
                          title="Type: Title"
                          onMouseDown={(e) => e.preventDefault()}
                          onClick={() => applyFormattingFromQuickToolbar(null, "title")}
                        >
                          <Type className="h-3.5 w-3.5" />
                        </button>
                        <button
                          className="quick-tool-btn"
                          title="Type: Content"
                          onMouseDown={(e) => e.preventDefault()}
                          onClick={() => applyFormattingFromQuickToolbar(null, "content")}
                        >
                          <AlignLeft className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {validationIssues.length > 0 && (
                  <div className="validation-panel">
                    <div className="validation-title">Cần sửa trước khi Approve ({validationIssues.length})</div>
                    <ul className="validation-list">
                      {validationIssues.slice(0, 4).map((issue, idx) => (
                        <li key={`${issue.nodeId}-${idx}`}>{issue.message}</li>
                      ))}
                      {validationIssues.length > 4 && <li>...và {validationIssues.length - 4} lỗi khác</li>}
                    </ul>
                  </div>
                )}

                {/* Find & Replace Panel */}
                {findReplaceOpen && (
                  <div className="find-replace-panel">
                    <div className="find-replace-row">
                      <div className="find-replace-input-wrap">
                        <Search className="h-3.5 w-3.5 find-replace-icon" />
                        <input
                          ref={findInputRef}
                          type="text"
                          className="find-replace-input"
                          placeholder="Tìm kiếm..."
                          value={findText}
                          onChange={(e) => { setFindText(e.target.value); runFind(e.target.value); }}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") navigateMatch(e.shiftKey ? "prev" : "next");
                            if (e.key === "Escape") { setFindReplaceOpen(false); clearHighlights(); setFindText(""); setMatchCount(0); }
                          }}
                        />
                        <span className={cn("find-count", matchCount > 0 ? "find-count-found" : "find-count-none")}>
                          {findText ? `${matchCount > 0 ? currentMatchIndex + 1 : 0}/${matchCount}` : ""}
                        </span>
                      </div>
                      <button className="find-nav-btn" onClick={() => navigateMatch("prev")} disabled={matchCount === 0} title="Kết quả trước (Shift+Enter)">
                        <ChevronUp className="h-3.5 w-3.5" />
                      </button>
                      <button className="find-nav-btn" onClick={() => navigateMatch("next")} disabled={matchCount === 0} title="Kết quả tiếp (Enter)">
                        <ChevronDown className="h-3.5 w-3.5" />
                      </button>
                      <label className="find-case-label" title="Phân biệt hoa/thường">
                        <input
                          type="checkbox"
                          checked={caseSensitive}
                          onChange={(e) => { setCaseSensitive(e.target.checked); runFind(findText, e.target.checked); }}
                        />
                        <span>Aa</span>
                      </label>
                      <button
                        className="find-close-btn"
                        onClick={() => { setFindReplaceOpen(false); clearHighlights(); setFindText(""); setMatchCount(0); }}
                      >
                        <X className="h-3.5 w-3.5" />
                      </button>
                    </div>
                    <div className="find-replace-row">
                      <div className="find-replace-input-wrap">
                        <span className="find-replace-spacer" />
                        <input
                          type="text"
                          className="find-replace-input"
                          placeholder="Thay thế bằng..."
                          value={replaceText}
                          onChange={(e) => setReplaceText(e.target.value)}
                          onKeyDown={(e) => { if (e.key === "Enter") replaceCurrentMatch(); }}
                        />
                      </div>
                      <button className="find-action-btn" onClick={replaceCurrentMatch} disabled={matchCount === 0}>
                        Thay thế
                      </button>
                      <button className="find-action-btn find-action-btn-all" onClick={replaceAllMatches} disabled={matchCount === 0}>
                        Tất cả
                      </button>
                    </div>
                  </div>
                )}

                <div
                  ref={editorRef}
                  id="wordEditor"
                  contentEditable
                  suppressContentEditableWarning
                  spellCheck={false}
                  className="word-editor"
                  style={zoomLevel !== 100 ? { fontSize: `${zoomLevel}%` } : undefined}
                >
                  <div className="legacy-empty-state">
                    <Loader2 className="h-8 w-8 animate-spin" />
                    <p>Loading document...</p>
                  </div>
                </div>

                <div className="stats-bar">
                  <div className="stat-item">
                    <FileText className="h-4 w-4" />
                    <span>Blocks:</span>
                    <span className="stat-value">{stats.blocks}</span>
                  </div>
                  <div className="stat-item">
                    <ChevronRight className="h-4 w-4" />
                    <span>Slides:</span>
                    <span className="stat-value">{stats.slides}</span>
                  </div>
                  <div className="stat-item">
                    <AlignLeft className="h-4 w-4" />
                    <span>Words:</span>
                    <span className="stat-value">{stats.words}</span>
                  </div>
                  <div className="stat-item">
                    <Loader2 className="h-4 w-4" />
                    <span>Characters:</span>
                    <span className="stat-value">{stats.chars}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="preview-column">
              <div className="panel-container">
                <div className="panel-header">
                  <h5>
                    <FileText className="mr-2 h-4 w-4" /> Slide Previews
                  </h5>
                  <div className="preview-header-actions">
                    <button className="btn btn-sm btn-info intro-preview-btn" onClick={openIntroModal} disabled={loading}>
                      {introSlide ? "Edit Intro Slide" : "Add Intro Slide"}
                    </button>
                    <span className="badge bg-success">{stats.slides} slides</span>
                  </div>
                </div>
                <div className="slides-container">
                  {slides.length === 0 ? (
                    <div className="legacy-empty-state">
                      <FileText className="h-10 w-10" />
                      <p>Format text to generate slides</p>
                    </div>
                  ) : (
                    slides.map((slide, index) => {
                      const classes = ["slide-thumbnail"];
                      if (slide.isTransition) classes.push("slide-transition");
                      if (slide.isIntro) classes.push("slide-intro");
                      return (
                        <div key={slide.id} className={classes.join(" ")}>
                          <div className="slide-number">Slide {index + 1}</div>
                          <div className="slide-title">
                            {slide.title || "Untitled"}
                            {slide.isTransition && <span className="badge bg-info">Transition</span>}
                            {slide.isIntro && <span className="badge bg-warning">Intro</span>}
                          </div>
                          {slide.content && <div className="slide-content">{slide.content}</div>}
                          {slide.bullets.length > 0 && (
                            <ul className="slide-bullets">
                              {slide.bullets.map((bullet, idx) => (
                                <li key={`${slide.id}-bullet-${idx}`} className={`slide-bullet level-${bullet.level}`}>
                                  {bullet.text}
                                </li>
                              ))}
                            </ul>
                          )}
                          <div className="slide-actions">
                            {slide.isIntro && (
                              <button className="btn btn-sm btn-danger" onClick={deleteIntroSlide}>
                                <Trash2 className="mr-1.5 h-3.5 w-3.5" /> Delete Intro
                              </button>
                            )}
                            {slide.isTransition && (
                              <button className="btn btn-sm btn-danger" onClick={() => deleteTransitionSlide(slide.id)}>
                                <Trash2 className="mr-1.5 h-3.5 w-3.5" /> Delete Transition
                              </button>
                            )}
                            {!slide.isTransition && !slide.isIntro && (
                              <button className="btn btn-sm btn-info" onClick={() => createTransitionSlide(slide.id)}>
                                <PlayCircle className="mr-1.5 h-3.5 w-3.5" /> Add Transition
                              </button>
                            )}
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ====== DIALOGS ====== */}

      {/* Intro Slide Modal */}
      <Dialog open={introModalOpen} onOpenChange={setIntroModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple-500" />
              {introSlide ? "Chỉnh sửa Intro Slide" : "Thêm Intro Slide"}
            </DialogTitle>
            <DialogDescription>
              Nội dung hiển thị trên slide đầu tiên của bài thuyết trình
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <Textarea
              value={introModalText}
              onChange={(e) => setIntroModalText(e.target.value)}
              placeholder="Nhập tiêu đề bài thuyết trình..."
              className="min-h-[100px]"
              autoFocus
            />
            <p className="text-xs text-muted-foreground text-right">{introModalText.length} ký tự</p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIntroModalOpen(false)}>
              Hủy
            </Button>
            <Button onClick={saveIntro} className="gradient-primary text-primary-foreground">
              <Check className="mr-1.5 h-3.5 w-3.5" /> Lưu
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reset Confirmation */}
      <AlertDialog open={resetDialogOpen} onOpenChange={setResetDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Reset cấu trúc?</AlertDialogTitle>
            <AlertDialogDescription>
              Đưa tất cả về dạng plain text. Bạn không thể hoàn tác.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Hủy</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleReset}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Reset
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Cancel Confirmation */}
      <AlertDialog open={cancelDialogOpen} onOpenChange={setCancelDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Cancel editing?</AlertDialogTitle>
            <AlertDialogDescription>
              Các thay đổi chưa lưu sẽ bị mất. Bạn chắc chắn muốn thoát chứ?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Tiếp tục chỉnh sửa</AlertDialogCancel>
            <AlertDialogAction onClick={confirmCancel} className="bg-secondary text-secondary-foreground">
              Thoát
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Approve Confirmation */}
      <AlertDialog open={approveDialogOpen} onOpenChange={setApproveDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Duyệt cấu trúc?</AlertDialogTitle>
            <AlertDialogDescription>
              Xác nhận cấu trúc với {stats.slides} slide? Hệ thống sẽ bắt đầu thiết kế slide tự động.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Hủy</AlertDialogCancel>
            <AlertDialogAction onClick={handleApprove} className="gradient-primary text-primary-foreground">
              <Check className="mr-1.5 h-3.5 w-3.5" /> Duyệt
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </AppLayout>
  );
};

export default StructureEditor;
