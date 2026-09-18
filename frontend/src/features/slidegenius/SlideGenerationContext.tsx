import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useLanguage } from "@/contexts/LanguageContext";
import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/lib/api";
import {
  NOTIFICATIONS_CHANGED_EVENT,
  playSlideGenerationCompleteSound,
  unlockNotificationSound,
} from "@/lib/notificationSound";
import {
  loadActiveChatSlideGeneration,
  loadChatSlideContent,
  streamChatSlideGeneration,
  streamChatSlideGenerationJob,
  streamManualSlideGeneration,
  type ChatSlideGeneration,
  type ChatSlideStreamEvent,
} from "./data/workspaceApi";
import type {
  ChatSlideStreamSlide,
  ChatSlideStreamStatus,
} from "./ChatSlideStreamPanel";

export type SlideGenerationPhase = "idle" | "running" | "completed" | "error";
export type SlideGenerationSource = "chat" | "manual" | null;

export interface SlideGenerationState {
  phase: SlideGenerationPhase;
  source: SlideGenerationSource;
  sessionId: string | null;
  panelOpen: boolean;
  status: ChatSlideStreamStatus;
  progress: number;
  slides: ChatSlideStreamSlide[];
  totalSlides: number | null;
  targetSlideCount: number | null;
  projectId: number | null;
  projectName: string;
  error: string;
}

interface StartSlideGenerationInput {
  sessionId: string;
  content: string;
  model: string;
  effort: string;
  slideCount?: number;
  documentIds?: string[];
}

interface SlideGenerationContextValue {
  generation: SlideGenerationState;
  isGenerating: boolean;
  openRequest: number;
  startSlideGeneration: (input: StartSlideGenerationInput) => boolean;
  startManualSlideGeneration: (sessionId: string, slideCount?: number) => boolean;
  openSlideStream: () => void;
  closeSlideStream: () => void;
}

const initialState: SlideGenerationState = {
  phase: "idle",
  source: null,
  sessionId: null,
  panelOpen: false,
  status: {
    stage: "idle",
    title: "Slide stream",
    description: "",
    message: "",
  },
  progress: 0,
  slides: [],
  totalSlides: null,
  targetSlideCount: null,
  projectId: null,
  projectName: "",
  error: "",
};

function stateFromSlideGenerationSnapshot(
  snapshot: ChatSlideGeneration,
): SlideGenerationState {
  const status = snapshot.status || {};
  return {
    phase: snapshot.phase,
    source: "chat",
    sessionId: snapshot.session_id,
    panelOpen: true,
    status: {
      stage: status.stage || "starting",
      title: status.title || "Creating slides",
      description: status.description || "The presentation is being generated...",
      message: status.message || "Working",
    },
    progress: Number.isFinite(snapshot.progress) ? snapshot.progress : 0,
    slides: (snapshot.slides || []).map((slide) => ({
      index: Number(slide.index),
      title: slide.title || `Slide ${Number(slide.index) + 1}`,
      content: "",
    })),
    totalSlides: snapshot.total_slides ?? null,
    targetSlideCount: snapshot.target_slide_count ?? null,
    projectId: snapshot.project_id ?? null,
    projectName: snapshot.project_name || "",
    error: snapshot.error || "",
  };
}

const SlideGenerationContext = createContext<SlideGenerationContextValue | null>(null);

function stringValue(value: unknown) {
  return typeof value === "string" ? value.trim() : "";
}

function numberValue(value: unknown) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function localStatus(
  language: "vi" | "en",
  data: Record<string, unknown>,
  stage: string,
): ChatSlideStreamStatus {
  const sourceText = `${stage} ${stringValue(data.title)} ${stringValue(data.message)}`.toLowerCase();
  if (language !== "vi") {
    return {
      stage,
      title: stringValue(data.title) || "Creating slides",
      description: stringValue(data.description) || "The presentation is being generated...",
      message: stringValue(data.message) || "Working",
    };
  }
  if (stage === "retrieval") {
    return { stage, title: "Đang chuẩn bị nội dung", description: "Đang lấy ngữ cảnh tài liệu cho bài trình bày...", message: "Chuẩn bị nội dung" };
  }
  if (stage === "script") {
    return { stage, title: "Đang viết kịch bản", description: "Đang chuyển brief thành kịch bản slide...", message: "Viết kịch bản" };
  }
  if (stage === "starting") {
    return { stage, title: "Đang bắt đầu tạo slide", description: "Đang khởi động quy trình tạo slide...", message: "Đang bắt đầu" };
  }
  if (stage === "completed" || sourceText.includes("completed")) {
    return { stage: "completed", title: "Đã hoàn thành", description: "Deck đã được lưu vào project.", message: "Đã hoàn thành" };
  }
  return { stage: "design", title: "Đang thiết kế slide", description: "Đang dựng từng slide theo kịch bản...", message: "Thiết kế slide" };
}

function stageFromEvent(data: Record<string, unknown>) {
  const rawStage = stringValue(data.stage).toLowerCase();
  if (rawStage) return rawStage;
  const sourceText = `${stringValue(data.title)} ${stringValue(data.message)}`.toLowerCase();
  if (sourceText.includes("script")) return "script";
  if (sourceText.includes("design") || sourceText.includes("slide")) return "design";
  return "starting";
}

function isAbortError(value: unknown) {
  return value instanceof DOMException && value.name === "AbortError";
}

export function SlideGenerationProvider({ children }: { children: ReactNode }) {
  const { language } = useLanguage();
  const { token, isLoading: authLoading } = useAuth();
  const [generation, setGeneration] = useState<SlideGenerationState>(initialState);
  const [openRequest, setOpenRequest] = useState(0);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const generationRef = useRef(initialState);
  const controllerRef = useRef<AbortController | null>(null);
  const previousGenerationPhaseRef = useRef<SlideGenerationPhase>(initialState.phase);
  const notificationArmedRef = useRef(false);

  useEffect(() => {
    const handleNotificationsChanged = (event: Event) => {
      const enabled = (event as CustomEvent<{ enabled?: unknown }>).detail?.enabled;
      if (typeof enabled === "boolean") setNotificationsEnabled(enabled);
    };
    window.addEventListener(NOTIFICATIONS_CHANGED_EVENT, handleNotificationsChanged);
    return () => window.removeEventListener(NOTIFICATIONS_CHANGED_EVENT, handleNotificationsChanged);
  }, []);

  useEffect(() => {
    if (authLoading || !token) return;
    let active = true;
    api.getSettings().then((settings) => {
      if (!active || typeof settings?.notifications_enabled !== "boolean") return;
      setNotificationsEnabled(settings.notifications_enabled);
    }).catch(() => {
      // Keep the cached preference when settings are temporarily unavailable.
    });
    return () => { active = false; };
  }, [authLoading, token]);

  useEffect(() => {
    const previousPhase = previousGenerationPhaseRef.current;
    if (
      previousPhase === "running"
      && generation.phase === "completed"
      && notificationArmedRef.current
      && notificationsEnabled
    ) {
      playSlideGenerationCompleteSound();
    }
    previousGenerationPhaseRef.current = generation.phase;
    if (generation.phase === "idle") notificationArmedRef.current = false;
  }, [generation.phase, notificationsEnabled]);

  const commit = useCallback((update: (previous: SlideGenerationState) => SlideGenerationState) => {
    setGeneration((previous) => {
      const next = update(previous);
      generationRef.current = next;
      return next;
    });
  }, []);

  const handleSlideStreamEvent = useCallback(async (event: ChatSlideStreamEvent) => {
    const data = event.data;
    if (event.type === "status") {
      const stage = stageFromEvent(data);
      commit((previous) => ({ ...previous, status: localStatus(language, data, stage) }));
      return;
    }

    if (event.type === "progress") {
      const current = numberValue(data.current);
      const total = numberValue(data.total);
      const percentage = numberValue(data.percentage);
      const progress = percentage !== null
        ? percentage
        : current !== null && total !== null && total > 0
          ? (current / total) * 100
          : undefined;
      commit((previous) => ({
        ...previous,
        progress: progress === undefined ? previous.progress : Math.min(100, Math.max(0, progress)),
        totalSlides: total !== null && total > 0 ? total : previous.totalSlides,
        status: {
          ...previous.status,
          stage: "design",
          title: language === "vi" ? "Đang thiết kế slide" : (stringValue(data.title) || "Creating slides"),
          message: language === "vi"
            ? `Đã hoàn thành ${current ?? 0}${total ? `/${total}` : ""} slide`
            : stringValue(data.message) || `Completed ${current ?? 0}${total ? `/${total}` : ""} slides`,
        },
      }));
      return;
    }

    if (event.type === "slide_completed") {
      const index = numberValue(data.index ?? data.slide_index);
      if (index === null) return;
      const total = numberValue(data.total);
      const current = numberValue(data.current);
      const inlineCandidates = [stringValue(data.xml), stringValue(data.content)];
      let content = inlineCandidates.find((candidate) => /^\s*</.test(candidate)) || "";
      const filePath = stringValue(data.xml_path) || stringValue(data.content_path) || (
        inlineCandidates.find((candidate) => candidate && !/^\s*</.test(candidate)) || ""
      );
      if (!content && filePath) {
        try {
          content = await loadChatSlideContent(filePath);
        } catch {
          // The slide card stays visible even when a temporary preview expires.
        }
      }
      const title = stringValue(data.title) || `${language === "vi" ? "Slide" : "Slide"} ${index + 1}`;
      commit((previous) => ({
        ...previous,
        slides: [
          ...previous.slides.filter((slide) => slide.index !== index),
          { index, title, content },
        ].sort((left, right) => left.index - right.index),
        totalSlides: total !== null && total > 0 ? total : previous.totalSlides,
        progress: current !== null && total !== null && total > 0
          ? (current / total) * 100
          : previous.progress,
        status: {
          ...previous.status,
          stage: "design",
          title: language === "vi" ? "Đang thiết kế slide" : "Design Slides",
          message: language === "vi" ? `Đã nhận slide ${index + 1}` : `Slide ${index + 1} is ready`,
        },
      }));
      return;
    }

    if (event.type === "complete") {
      const projectId = numberValue(data.project_id);
      const total = numberValue(data.total_slides);
      commit((previous) => ({
        ...previous,
        phase: "completed",
        progress: 100,
        projectId: projectId !== null ? projectId : previous.projectId,
        projectName: stringValue(data.project_name) || previous.projectName,
        totalSlides: total !== null && total > 0 ? total : previous.totalSlides,
        status: language === "vi"
          ? { stage: "completed", title: "Đã hoàn thành", description: "Deck đã được lưu vào project.", message: "Đã hoàn thành" }
          : { stage: "completed", title: "Completed", description: "The deck has been saved to your project.", message: "Completed" },
      }));
      return;
    }

    if (event.type === "limit_event" || event.type === "error_event") {
      const message = stringValue(data.message) || (language === "vi" ? "Không thể tạo slide lúc này." : "Unable to create slides right now.");
      commit((previous) => ({
        ...previous,
        phase: "error",
        error: message,
        status: language === "vi"
          ? { stage: "error", title: "Không thể tạo slide", description: message, message: "Có lỗi xảy ra" }
          : { stage: "error", title: "Slide generation failed", description: message, message: "Something went wrong" },
      }));
    }
  }, [commit, language]);

  const consumeGenerationStream = useCallback(async (
    stream: (signal: AbortSignal) => Promise<void>,
    controller: AbortController,
  ) => {
    try {
      await stream(controller.signal);
    } catch (requestError) {
      if (isAbortError(requestError)) return;
      const message = requestError instanceof Error
        ? requestError.message
        : language === "vi" ? "Không thể tạo slide lúc này." : "Unable to create slides right now.";
      commit((previous) => ({
        ...previous,
        phase: "error",
        error: message,
        status: language === "vi"
          ? { stage: "error", title: "Không thể tạo slide", description: message, message: "Có lỗi xảy ra" }
          : { stage: "error", title: "Slide generation failed", description: message, message: "Something went wrong" },
      }));
    } finally {
      if (controllerRef.current === controller) controllerRef.current = null;
    }
  }, [commit, language]);

  const restoreActiveGeneration = useCallback(async () => {
    try {
      const snapshot = await loadActiveChatSlideGeneration();
      if (!snapshot || generationRef.current.phase !== "idle") return;

      const restored = stateFromSlideGenerationSnapshot(snapshot);
      notificationArmedRef.current = restored.phase === "running";
      generationRef.current = restored;
      setGeneration(restored);
      setOpenRequest((previous) => previous + 1);

      const controller = new AbortController();
      controllerRef.current = controller;
      await consumeGenerationStream(
        (signal) => streamChatSlideGenerationJob(snapshot.id, handleSlideStreamEvent, signal),
        controller,
      );
    } catch {
      // A missing active job is a valid state after a fast completed run. The
      // persisted chat turn remains the source of truth in that case.
    }
  }, [consumeGenerationStream, handleSlideStreamEvent]);

  useEffect(() => {
    if (authLoading || !token) return;
    void restoreActiveGeneration();
  }, [authLoading, restoreActiveGeneration, token]);

  const beginGeneration = useCallback((
    source: Exclude<SlideGenerationSource, null>,
    sessionId: string,
    slideCount: number | undefined,
    stream: (signal: AbortSignal) => Promise<void>,
  ) => {
    if (generationRef.current.phase === "running") return false;

    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    notificationArmedRef.current = true;
    unlockNotificationSound();
    const firstStatus: ChatSlideStreamStatus = language === "vi"
      ? { stage: "starting", title: "Đang bắt đầu tạo slide", description: "Đang chuẩn bị yêu cầu đã xác nhận...", message: "Đang bắt đầu" }
      : { stage: "starting", title: "Starting slide generation", description: "Preparing the confirmed request...", message: "Starting" };
    const nextState: SlideGenerationState = {
      phase: "running",
      source,
      sessionId,
      panelOpen: true,
      status: firstStatus,
      progress: 0,
      slides: [],
      totalSlides: slideCount ?? null,
      targetSlideCount: slideCount ?? null,
      projectId: null,
      projectName: "",
      error: "",
    };
    generationRef.current = nextState;
    setGeneration(nextState);

    void consumeGenerationStream(
      stream,
      controller,
    );
    return true;
  }, [consumeGenerationStream, language]);

  const startSlideGeneration = useCallback((input: StartSlideGenerationInput) => (
    beginGeneration(
      "chat",
      input.sessionId,
      input.slideCount,
      (signal) => streamChatSlideGeneration(
        input.sessionId,
        input.content,
        input.model,
        input.effort,
        input.slideCount,
        handleSlideStreamEvent,
        signal,
        input.documentIds || [],
      ),
    )
  ), [beginGeneration, handleSlideStreamEvent]);

  const startManualSlideGeneration = useCallback((sessionId: string, slideCount?: number) => (
    beginGeneration(
      "manual",
      sessionId,
      slideCount,
      (signal) => streamManualSlideGeneration(sessionId, handleSlideStreamEvent, signal),
    )
  ), [beginGeneration, handleSlideStreamEvent]);

  const openSlideStream = useCallback(() => {
    commit((previous) => ({ ...previous, panelOpen: true }));
    setOpenRequest((previous) => previous + 1);
  }, [commit]);

  const closeSlideStream = useCallback(() => {
    commit((previous) => ({ ...previous, panelOpen: false }));
  }, [commit]);

  useEffect(() => () => {
    controllerRef.current?.abort();
  }, []);

  const value = useMemo<SlideGenerationContextValue>(() => ({
    generation,
    isGenerating: generation.phase === "running",
    openRequest,
    startSlideGeneration,
    startManualSlideGeneration,
    openSlideStream,
    closeSlideStream,
  }), [closeSlideStream, generation, openRequest, openSlideStream, startManualSlideGeneration, startSlideGeneration]);

  return (
    <SlideGenerationContext.Provider value={value}>
      {children}
      <SlideGenerationIndicator />
    </SlideGenerationContext.Provider>
  );
}

function SlideGenerationIndicator() {
  const { language } = useLanguage();
  const navigate = useNavigate();
  const location = useLocation();
  const { generation, isGenerating, openSlideStream } = useSlideGeneration();
  const isChatRoute = location.pathname === "/home";
  const isManualRoute = location.pathname === "/structure" || location.pathname.startsWith("/structure/");
  const isWorkspaceShellRoute = ["/home", "/manual", "/projects", "/guide", "/settings", "/subscription"]
    .some((path) => location.pathname === path || location.pathname.startsWith(`${path}/`));
  const ownsVisiblePanel = (generation.source === "chat" && isChatRoute)
    || (generation.source === "manual" && (isManualRoute || isWorkspaceShellRoute));
  if ((!isGenerating && generation.phase !== "error") || (generation.panelOpen && ownsVisiblePanel)) return null;

  const isError = generation.phase === "error";
  const count = generation.totalSlides || generation.targetSlideCount;
  const progress = count
    ? `${generation.slides.length}/${count} ${language === "vi" ? "slide" : "slides"}`
    : `${Math.round(generation.progress)}%`;
  const open = () => {
    openSlideStream();
    if (generation.source === "manual" && generation.sessionId) {
      if (!isManualRoute) navigate(`/structure?session=${encodeURIComponent(generation.sessionId)}`);
    } else if (!isChatRoute) {
      navigate("/home");
    }
  };

  return (
    <div className="sgx-global-slide-generation-indicator" role="status" aria-live="polite">
      <button type="button" onClick={open}>
        <span className={`sgx-global-slide-generation-icon ${isError ? "error" : ""}`} aria-hidden="true">
          {isError ? "!" : <span className="sgx-global-slide-generation-spinner" />}
        </span>
        <span className="sgx-global-slide-generation-copy">
          <strong>{isError ? (language === "vi" ? "Tạo slide gặp lỗi" : "Slide generation failed") : (language === "vi" ? "Đang tạo slide" : "Creating slides")}</strong>
          <small>{isError ? generation.error : progress}</small>
        </span>
        <span className="sgx-global-slide-generation-arrow" aria-hidden="true">↗</span>
      </button>
    </div>
  );
}

export function useSlideGeneration() {
  const context = useContext(SlideGenerationContext);
  if (!context) throw new Error("useSlideGeneration must be used within SlideGenerationProvider");
  return context;
}
