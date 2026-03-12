import { useState, useEffect, useCallback, useRef } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import {
  Check, RotateCcw, Sparkles, Loader2, FileText, ChevronRight,
  PlayCircle, Trash2, Type, AlignLeft, ArrowLeft, XCircle
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

// ============ MAIN COMPONENT ============

const StructureEditor = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get("session");
  const navigate = useNavigate();
  const { toast } = useToast();

  // Core state
  const [documentTitle, setDocumentTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Structure state (synced from DOM)
  const documentStructureRef = useRef<StructureNode[]>([]);
  const introSlideRef = useRef<IntroSlide | null>(null);
  const [introSlide, setIntroSlide] = useState<IntroSlide | null>(null);
  const [slides, setSlides] = useState<SlidePreview[]>([]);
  const [stats, setStats] = useState({ blocks: 0, chars: 0, slides: 0 });

  // UI state
  const [introModalOpen, setIntroModalOpen] = useState(false);
  const [introModalText, setIntroModalText] = useState("");
  const [resetDialogOpen, setResetDialogOpen] = useState(false);
  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const [selectionInfo, setSelectionInfo] = useState<{ text: string; length: number } | null>(null);

  // Pending formatting state (two-step: Level then Type)
  const [pendingLevel, setPendingLevel] = useState<number | "normal" | null>(null);
  const [pendingType, setPendingType] = useState<"title" | "content" | null>(null);

  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);

  // Refs
  const editorRef = useRef<HTMLDivElement>(null);
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const documentTextRef = useRef("");
  const listenersSetupRef = useRef(false);

  const handleGoBack = () => {
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
    clone.innerHTML = clone.innerHTML.replace(/<br\s*\/?>/gi, "\n");
    return clone.textContent || "";
  };

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
    const flatBlocks: Array<{
      node_id: string;
      level: number;
      type: string;
      text: string;
      is_transition: boolean;
    }> = [];

    blocks.forEach((block) => {
      const text = extractTextSafely(block).trim();
      if (!text) return;
      const el = block as HTMLElement;
      flatBlocks.push({
        node_id: el.dataset.nodeId || generateNodeId(),
        level: el.dataset.level !== undefined ? parseInt(el.dataset.level) : 1,
        type: el.dataset.type || "content",
        text,
        is_transition: el.dataset.transition === "true",
      });
    });

    const structure = buildHierarchy(flatBlocks);
    documentStructureRef.current = structure;

    const newSlides = buildSlides(structure, introSlideRef.current);
    setSlides(newSlides);

    const charCount = editor.textContent?.length || 0;
    setStats({ blocks: blocks.length, chars: charCount, slides: newSlides.length });
  }, [buildHierarchy, buildSlides]);

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
    } catch {
      // Silent fail for auto-save
    }
  }, [sessionId]);

  // ---- Full sync: sync DOM → state → save ----
  const fullSync = useCallback(() => {
    syncEditorToStructure();
    if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    saveTimeoutRef.current = setTimeout(() => {
      saveStructure();
    }, 1500);
  }, [syncEditorToStructure, saveStructure]);

  // ---- Render existing structure into editor ----
  const renderExistingStructure = useCallback(
    (structure: any[]) => {
      const editor = editorRef.current;
      if (!editor) return;

      const renderNodes = (nodes: any[]): string => {
        let result = "";
        for (const node of nodes) {
          if (node.title) {
            result += `<span class="text-block text-level-${node.level} text-title" data-level="${node.level}" data-type="title" data-node-id="${node.node_id || generateNodeId()}"${node.is_transition ? ' data-transition="true"' : ''}><span class="drag-handle" contenteditable="false">⠿</span>${escapeHtml(node.title)}</span>\n`;
          }
          if (node.content) {
            result += `<span class="text-block text-level-${node.level} text-content" data-level="${node.level}" data-type="content" data-node-id="${(node.node_id || generateNodeId()) + "_c"}"><span class="drag-handle" contenteditable="false">⠿</span>${escapeHtml(node.content)}</span>\n`;
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
    const handleSelection = () => {
      const selection = window.getSelection();
      const selectedText = selection?.toString().trim() || "";
      if (selectedText.length > 0) {
        setSelectionInfo({
          text: selectedText.length > 80 ? selectedText.substring(0, 80) + "..." : selectedText,
          length: selectedText.length,
        });
      } else {
        setSelectionInfo(null);
      }
    };
    editor.addEventListener("mouseup", handleSelection);
    editor.addEventListener("keyup", handleSelection);

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
  }, [fullSync]);

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

  // ---- Formatting: Apply level/type to selected text ----
  const applyFormatting = (newLevel: number | "normal" | null, newType: "title" | "content" | null) => {
    const editor = editorRef.current;
    if (!editor) return;
    const selection = window.getSelection();
    if (!selection) return;

    // Find selected blocks (existing formatted blocks in selection)
    let selectedBlocks: HTMLElement[] = [];
    if (selection.rangeCount > 0) {
      const allBlocks = Array.from(editor.querySelectorAll(".text-block")) as HTMLElement[];
      selectedBlocks = allBlocks.filter((block) => selection.containsNode(block, true));

      // Fallback: check if cursor is inside a block
      if (selectedBlocks.length === 0) {
        const range = selection.getRangeAt(0);
        let node: Node | null = range.commonAncestorContainer;
        if (node.nodeType === 3) node = node.parentElement;
        const block = (node as Element)?.closest?.(".text-block") as HTMLElement;
        if (block) selectedBlocks = [block];
      }
    }

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
      range.insertNode(wrapper);

      const br = document.createElement("br");
      wrapper.after(br);

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
        transBlock.className = "text-block text-level-1 text-title";
        transBlock.dataset.level = "1";
        transBlock.dataset.type = "title";
        transBlock.dataset.nodeId = transitionNodeId;
        transBlock.dataset.transition = "true";
        transBlock.innerHTML = `<span class="drag-handle" contenteditable="false">⠿</span>${escapeHtml(transitionNode.title)}`;
        transBlock.style.borderColor = "#0dcaf0";
        transBlock.style.background = "rgba(13, 202, 240, 0.15)";

        beforeBlock.parentNode!.insertBefore(transBlock, beforeBlock);
        beforeBlock.parentNode!.insertBefore(document.createElement("br"), beforeBlock);

        if (transitionNode.content) {
          const contentBlock = document.createElement("span");
          contentBlock.className = "text-block text-level-1 text-content";
          contentBlock.dataset.level = "1";
          contentBlock.dataset.type = "content";
          contentBlock.dataset.nodeId = transitionNodeId + "_c";
          contentBlock.dataset.transition = "true";
          contentBlock.innerHTML = `<span class="drag-handle" contenteditable="false">⠿</span>${escapeHtml(transitionNode.content)}`;
          contentBlock.style.borderColor = "#0dcaf0";
          contentBlock.style.background = "rgba(13, 202, 240, 0.1)";
          beforeBlock.parentNode!.insertBefore(contentBlock, beforeBlock);
          beforeBlock.parentNode!.insertBefore(document.createElement("br"), beforeBlock);
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

  const disableStructureActions = loading || saving;

  return (
    <AppLayout>
      <div className="legacy-structure-page">
        <div className="legacy-aurora" aria-hidden />
        <div className="legacy-particles" aria-hidden>
          {Array.from({ length: 5 }).map((_, index) => (
            <span key={index} className={`legacy-particle legacy-particle-${index + 1}`} />
          ))}
        </div>
        <div className="legacy-structure-content">
          <div className="header-section">
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
            <div className="header-actions">
              <button className="btn btn-sm btn-info" onClick={openIntroModal} disabled={loading}>
                <Sparkles className="mr-1.5 h-4 w-4" /> Intro
              </button>
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
            </div>
          </div>

          <div className="main-content">
            <div className="editor-column">
              <div className="panel-container">
                <div className="editor-toolbar">
                  <div className="style-group">
                    <div className="group-label">Level</div>
                    <div className="style-row">
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
                        <span className="style-name">L0</span>
                      </button>
                      {[1, 2, 3, 4, 5, 6].map((level) => (
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
                </div>

                <div className={cn("selection-info", selectionInfo && "visible")}>
                  <AlignLeft className="h-4 w-4" />
                  <span className="selection-text">{selectionInfo?.text || "No text selected"}</span>
                  <span className="badge bg-secondary">
                    {selectionInfo ? `${selectionInfo.length} chars` : "0 chars"}
                  </span>
                </div>

                <div
                  ref={editorRef}
                  id="wordEditor"
                  contentEditable
                  suppressContentEditableWarning
                  spellCheck={false}
                  className="word-editor"
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
                  <span className="badge bg-success">{stats.slides} slides</span>
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
