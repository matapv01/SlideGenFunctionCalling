import { ChangeEvent, FormEvent, MouseEvent, useCallback, useEffect, useRef, useState } from "react";
import type { CSSProperties } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import {
  ChatMessage,
  ChatDocument,
  ChatMessageJob,
  ChatSession,
  archiveChatSession,
  createChatSession,
  deleteChatDocument,
  loadChatbotConfig,
  loadActiveChatMessageJob,
  loadChatMessages,
  loadChatDocuments,
  loadChatSessions,
  loadWorkspaceProject,
  streamChatMessage,
  streamChatMessageJob,
  uploadChatDocument,
} from "./data/workspaceApi";
import { ChatSlideStreamPanel } from "./ChatSlideStreamPanel";
import { ChatSlidePlanPanel } from "./ChatSlidePlanPanel";
import { ChatSlideGenerationCard } from "./ChatSlideGenerationCard";
import { truncateProjectName } from "./projectName";
import { useSlideGeneration } from "./SlideGenerationContext";
import ChatMarkdown from "./ChatMarkdown";
import { api, type ChatTurnResponse, type SubscriptionInfoResponse } from "@/lib/api";
import SlidegenConfirmDialog from "@/components/SlidegenConfirmDialog";

const defaultModels = ["genius-1", "genius-2", "genius-3"];
const defaultEfforts = ["low", "medium", "high"] as const;
const sourceSentenceEnd = /[.!?。！？](?:["'”’»)\]}]*)(?=\s|$)/g;

interface SlideFlowOption {
  label: string;
  value: string;
  is_other: boolean;
  action: "answer" | "other" | "upgrade";
}

interface SlideFlowAnswer {
  question: string;
  answer: string;
}

interface SlideFlow {
  state: "clarifying" | "awaiting_confirmation" | "limit_reached";
  question: string | null;
  options: SlideFlowOption[];
  originalPrompt: string;
  brief: string;
  answers: SlideFlowAnswer[];
  targetSlideCount: number | null;
  maxSlideCount: number | null;
  questionKind: "slide_count" | "content" | null;
}

interface SendMessageOptions {
  streamSlides?: boolean;
  slideCount?: number;
  documentIds?: string[];
  messageAttachments?: MessageAttachment[];
  preserveUploadedDocuments?: boolean;
}

interface SlideGenerationLog {
  projectId: number | null;
  projectName: string;
  slideCount: number | null;
}

interface MessageAttachment {
  id: string;
  name: string;
}

interface ChatSource {
  index: number;
  id: string;
  documentId: string;
  title: string;
  section: string;
  excerpt: string;
  role: string;
  similarity: number | null;
}

function sentenceBoundedSourceExcerpt(value: string, limit = 1600) {
  const text = String(value || "").trim();
  if (!text) return "";
  if (text.endsWith("…")) return text;

  const likelyTruncated = text.length > limit || (text.length >= limit - 8 && !/[.!?。！？]$/.test(text));
  if (!likelyTruncated) return text;

  const prefix = text.slice(0, limit);
  const matches = Array.from(prefix.matchAll(sourceSentenceEnd));
  const lastMatch = matches.at(-1);
  if (lastMatch?.index !== undefined) {
    return prefix.slice(0, lastMatch.index + lastMatch[0].length).trimEnd() + " …";
  }

  const wordBoundary = prefix.lastIndexOf(" ");
  const cutoff = wordBoundary >= limit / 2 ? wordBoundary : limit;
  return prefix.slice(0, cutoff).trimEnd() + " …";
}

function getMessageSources(message: ChatMessage): ChatSource[] {
  const metadata = message.metadata;
  if (!metadata || typeof metadata !== "object") return [];

  const retrieval = metadata.retrieval;
  const retrievalCitations = retrieval && typeof retrieval === "object" && !Array.isArray(retrieval)
    ? (retrieval as Record<string, unknown>).citations
    : undefined;
  const candidates = Array.isArray(retrievalCitations)
    ? retrievalCitations
    : Array.isArray(metadata.citations)
      ? metadata.citations
      : [];

  return candidates.flatMap((item, index) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const raw = item as Record<string, unknown>;
    const documentId = typeof raw.document_id === "string" ? raw.document_id.trim() : "";
    const chunkId = raw.chunk_id !== undefined && raw.chunk_id !== null ? String(raw.chunk_id) : "";
    const section = typeof raw.section === "string"
      ? raw.section.trim()
      : typeof raw.section_path === "string"
        ? raw.section_path.trim()
        : "";
    const title = typeof raw.title === "string" ? raw.title.trim() : "";
    const excerptValue = typeof raw.excerpt === "string"
      ? raw.excerpt.trim()
      : typeof raw.snippet === "string"
        ? raw.snippet.trim()
        : typeof raw.content === "string"
          ? raw.content.trim()
          : "";
    const excerpt = sentenceBoundedSourceExcerpt(excerptValue);
    const similarityValue = Number(raw.similarity);
    const similarity = Number.isFinite(similarityValue) ? similarityValue : null;
    const sourceId = documentId || chunkId || `source-${index + 1}`;

    return [{
      index: index + 1,
      id: `${sourceId}:${chunkId || index + 1}`,
      documentId,
      title: title || section || `Source ${index + 1}`,
      section,
      excerpt,
      role: typeof raw.role === "string" ? raw.role.trim() : "",
      similarity,
    }];
  });
}

function sourceKey(messageId: number, source: ChatSource) {
  return `${messageId}:${source.index}:${source.id}`;
}

function getSlideGenerationLog(message: ChatMessage): SlideGenerationLog | null {
  const candidate = message.metadata?.slide_generation;
  if (!candidate || typeof candidate !== "object" || Array.isArray(candidate)) return null;
  const raw = candidate as Record<string, unknown>;
  const projectIdValue = Number(raw.project_id);
  const slideCountValue = Number(raw.slide_count);
  return {
    projectId: Number.isInteger(projectIdValue) && projectIdValue > 0 ? projectIdValue : null,
    projectName: typeof raw.project_name === "string" ? raw.project_name.trim() : "",
    slideCount: Number.isInteger(slideCountValue) && slideCountValue > 0 ? slideCountValue : null,
  };
}

function getMessageAttachments(message: ChatMessage): MessageAttachment[] {
  const candidate = message.metadata?.attachments;
  if (!Array.isArray(candidate)) return [];
  return candidate.flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const raw = item as Record<string, unknown>;
    const id = typeof raw.id === "string" ? raw.id.trim() : "";
    const name = typeof raw.name === "string"
      ? raw.name.trim()
      : typeof raw.title === "string"
        ? raw.title.trim()
        : typeof raw.original_filename === "string"
          ? raw.original_filename.trim()
          : "";
    if (!id || !name) return [];
    return [{ id, name }];
  });
}

function getSentDocumentIds(messages: ChatMessage[]) {
  return new Set(
    messages.flatMap((message) => getMessageAttachments(message).map((item) => item.id)),
  );
}

function isMissingProjectError(value: unknown) {
  if (!value || typeof value !== "object") return false;
  const status = Number((value as { status?: unknown }).status);
  return status === 404 || status === 403;
}

function storedAuthUserId() {
  try {
    const raw = localStorage.getItem("user");
    if (!raw) return null;
    const id = Number((JSON.parse(raw) as { id?: unknown }).id);
    return Number.isInteger(id) && id > 0 ? id : null;
  } catch {
    return null;
  }
}

function chatTurnFromStreamEvent(data: Record<string, unknown>): ChatTurnResponse {
  const result = data.result;
  if (!result || typeof result !== "object" || Array.isArray(result)) {
    throw new Error("Phản hồi streaming của chatbot không hợp lệ.");
  }
  const turn = result as ChatTurnResponse;
  if (!turn.user_message || !turn.assistant_message || !turn.session) {
    throw new Error("Phản hồi streaming của chatbot không đầy đủ.");
  }
  return turn;
}

function getSlideFlow(message: ChatMessage): SlideFlow | null {
  const candidate = message.metadata?.slide_flow;
  if (!candidate || typeof candidate !== "object" || Array.isArray(candidate)) return null;

  const raw = candidate as Record<string, unknown>;
  const state = raw.state;
  if (state !== "clarifying" && state !== "awaiting_confirmation" && state !== "limit_reached") return null;

  const options = (Array.isArray(raw.options) ? raw.options : []).flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const option = item as Record<string, unknown>;
    const label = typeof option.label === "string" ? option.label.trim() : "";
    if (!label) return [];
    const action = option.action === "upgrade" || option.action === "other" ? option.action : "answer";
    return [{
      label,
      value: typeof option.value === "string" && option.value.trim() ? option.value : label,
      is_other: option.is_other === true || action === "other",
      action,
    }];
  });

  const answers = (Array.isArray(raw.answers) ? raw.answers : []).flatMap((item) => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const answer = item as Record<string, unknown>;
    const question = typeof answer.question === "string" ? answer.question.trim() : "";
    const value = typeof answer.answer === "string" ? answer.answer.trim() : "";
    if (!question && !value) return [];
    return [{ question: question || "", answer: value || "" }];
  });

  return {
    state,
    question: typeof raw.question === "string" ? raw.question : null,
    options,
    originalPrompt: typeof raw.original_prompt === "string" ? raw.original_prompt.trim() : "",
    brief: typeof raw.brief === "string" ? raw.brief.trim() : "",
    answers,
    targetSlideCount: Number.isFinite(Number(raw.target_slide_count)) && Number(raw.target_slide_count) > 0
      ? Number(raw.target_slide_count)
      : null,
    maxSlideCount: Number.isFinite(Number(raw.max_slide_count))
      ? Number(raw.max_slide_count)
      : null,
    questionKind: raw.question_kind === "slide_count" || raw.question_kind === "content"
      ? raw.question_kind
      : null,
  };
}

function extractSlideCount(value: string, allowBareNumber = false): number | null {
  const text = String(value || "");
  if (/(?<!\d)\d{1,3}\s*-\s*\d{1,3}\s*(?:slides?|trang|pages?)\b/i.test(text)) {
    return null;
  }
  const match = text.match(/(?:^|\s)(\d{1,3})\s*(?:-\s*)?(?:slides?|trang|pages?)\b/i)
    || text.match(/\b(?:slides?|trang|pages?)\s*(\d{1,3})(?!\d)\b/i);
  if (match) {
    const parsed = Number(match[1]);
    return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
  }
  if (allowBareNumber && /^\s*\d{1,3}\s*$/.test(text)) {
    const parsed = Number(text.trim());
    return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
  }
  return null;
}

function formatSessionDate(value: string, language: "vi" | "en") {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat(language === "vi" ? "vi-VN" : "en-US", {
    day: "2-digit",
    month: "short",
  }).format(date);
}

function messageTime(value: string, language: "vi" | "en") {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return language === "vi" ? "Vừa xong" : "Just now";
  return new Intl.DateTimeFormat(language === "vi" ? "vi-VN" : "en-US", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function formatUsageCountdown(value: string | undefined, now: number, language: "vi" | "en") {
  if (!value) return "—";
  const remaining = Math.max(0, new Date(value).getTime() - now);
  if (!Number.isFinite(remaining) || remaining <= 0) return language === "vi" ? "đang cập nhật" : "refreshing";
  const totalMinutes = Math.ceil(remaining / 60_000);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (language === "vi") return `${hours}g ${String(minutes).padStart(2, "0")}p`;
  return `${hours}h ${String(minutes).padStart(2, "0")}m`;
}

function formatUsageAmount(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(2).replace(/0+$/, "").replace(/\.$/, "");
}

function formatFileSize(bytes: number) {
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${Math.max(0, Math.round(bytes / 1024))} KB`;
}

function usageTone(percent: number | null) {
  if (percent === null) return "unlimited";
  if (percent >= 90) return "critical";
  if (percent >= 70) return "warning";
  return "healthy";
}

function UsageMeter({ label, percent, detail }: { label: string; percent: number | null; detail: string }) {
  const progress = percent === null ? 100 : Math.max(0, Math.min(100, percent));
  const circleStyle = { "--usage-progress": `${progress}%` } as CSSProperties;

  return (
    <div
      className={`composer-usage-meter is-${usageTone(percent)}`}
      data-tooltip={detail}
      tabIndex={0}
      role="img"
      aria-label={detail}
    >
      <span className="composer-usage-circle" style={circleStyle}>
        <span>{percent === null ? "∞" : percent}</span>
      </span>
      <span className="composer-usage-label">{label}</span>
    </div>
  );
}

export default function SlidegeniusChat({ isActive = true }: { isActive?: boolean }) {
  const { user } = useAuth();
  const { language } = useLanguage();
  const navigate = useNavigate();
  const {
    generation,
    isGenerating,
    openRequest,
    startSlideGeneration,
    openSlideStream,
    closeSlideStream,
  } = useSlideGeneration();
  const [message, setMessage] = useState("");
  const [model, setModel] = useState("genius-3");
  const [effort, setEffort] = useState<"low" | "medium" | "high">("medium");
  const [models, setModels] = useState(defaultModels);
  const [efforts, setEfforts] = useState<readonly string[]>(defaultEfforts);
  const [maxSlideCount, setMaxSlideCount] = useState(50);
  const [maxUploadBytes, setMaxUploadBytes] = useState(0);
  const [maxTotalUploadBytes, setMaxTotalUploadBytes] = useState(0);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [activeChatJob, setActiveChatJob] = useState<ChatMessageJob | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [thinkingMode, setThinkingMode] = useState<"conversation" | "document" | null>(null);
  const [documentThinkingStep, setDocumentThinkingStep] = useState(0);
  const [slidePlanOpen, setSlidePlanOpen] = useState(false);
  const [error, setError] = useState("");
  const [toolsOpen, setToolsOpen] = useState(false);
  const [modelOpen, setModelOpen] = useState(false);
  const [searchEnabled, setSearchEnabled] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadingDocument, setUploadingDocument] = useState<string | null>(null);
  const [sessionDocuments, setSessionDocuments] = useState<ChatDocument[]>([]);
  const [uploadedDocuments, setUploadedDocuments] = useState<ChatDocument[]>([]);
  const [removingDocumentId, setRemovingDocumentId] = useState<string | null>(null);
  const [deletingSessionId, setDeletingSessionId] = useState<string | null>(null);
  const [pendingDeleteSession, setPendingDeleteSession] = useState<ChatSession | null>(null);
  const [deletedProjectIds, setDeletedProjectIds] = useState<Set<number>>(() => new Set());
  const [clarificationOtherOpen, setClarificationOtherOpen] = useState(false);
  const [clarificationOther, setClarificationOther] = useState("");
  const [selectedSourceKey, setSelectedSourceKey] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const uploadAbortControllerRef = useRef<AbortController | null>(null);
  const uploadRequestIdRef = useRef(0);
  // Invalidate responses from a previous conversation after every switch.
  // Otherwise a slower document request can populate the new conversation.
  const sessionViewRequestRef = useRef(0);
  const chatMessageJobRef = useRef<string | null>(null);
  const clarificationInputRef = useRef<HTMLInputElement>(null);
  const threadRef = useRef<HTMLDivElement>(null);
  const lastOpenRequestRef = useRef(0);
  const initialChatMountRef = useRef(true);
  const [showScrollToLatest, setShowScrollToLatest] = useState(false);
  const [subscriptionUsage, setSubscriptionUsage] = useState<SubscriptionInfoResponse | null>(null);
  const [usageNow, setUsageNow] = useState(() => Date.now());

  const chatStorageUserId = user?.id ?? storedAuthUserId();
  const activeChatSessionStorageKey = chatStorageUserId
    ? `slidegen.active-chat-session.${chatStorageUserId}`
    : null;
  const chatResumeStorageKey = chatStorageUserId
    ? `slidegen.resume-chat-session.${chatStorageUserId}`
    : null;
  const chatStorageKeysRef = useRef({
    active: activeChatSessionStorageKey,
    resume: chatResumeStorageKey,
  });
  chatStorageKeysRef.current = {
    active: activeChatSessionStorageKey,
    resume: chatResumeStorageKey,
  };

  // Keep the latest lifecycle state available to the unmount cleanup. The
  // workspace routes are separate React trees, so changing from Chat to
  // Projects/Manual unmounts this component instead of toggling isActive.
  const chatLifecycleRef = useRef({
    sessionId: null as string | null,
    messageCount: 0,
    loading: true,
    sending: false,
    uploading: false,
    activeJob: false,
    generating: false,
  });
  const handledDraftSessionRef = useRef<string | null>(null);

  useEffect(() => {
    chatLifecycleRef.current = {
      sessionId: activeSessionId,
      messageCount: messages.length,
      loading,
      sending,
      uploading,
      activeJob: Boolean(activeChatJob),
      generating: isGenerating && generation.sessionId === activeSessionId,
    };
  });

  const preserveRunningChatOrDiscardBlankDraft = useCallback(() => {
    const current = chatLifecycleRef.current;
    const { active: activeStorageKey, resume: resumeStorageKey } = chatStorageKeysRef.current;
    if (!current.sessionId) return;

    const isRunning = current.sending || current.activeJob || current.generating;
    if (isRunning) {
      if (resumeStorageKey) {
        sessionStorage.setItem(resumeStorageKey, current.sessionId);
      }
      return;
    }

    if (
      handledDraftSessionRef.current === current.sessionId
      || current.loading
      || current.messageCount > 0
      || current.uploading
    ) return;

    handledDraftSessionRef.current = current.sessionId;
    if (resumeStorageKey) sessionStorage.removeItem(resumeStorageKey);
    if (
      activeStorageKey
      && localStorage.getItem(activeStorageKey) === current.sessionId
    ) {
      localStorage.removeItem(activeStorageKey);
    }
    // Archiving is the existing soft-delete boundary for chat sessions. The
    // repository also excludes message-less sessions, so a blank draft is
    // neither shown in history nor restored by a later Chat visit.
    void archiveChatSession(current.sessionId).catch(() => undefined);
  }, []);

  useEffect(() => () => {
    preserveRunningChatOrDiscardBlankDraft();
  }, [preserveRunningChatOrDiscardBlankDraft]);

  const isActiveGeneration = generation.sessionId !== null && generation.sessionId === activeSessionId;
  const showSlideStream = isActiveGeneration && generation.panelOpen;

  useEffect(() => {
    setSelectedSourceKey(null);
  }, [activeSessionId]);

  useEffect(() => {
    if (!activeChatSessionStorageKey || !activeSessionId) return;
    localStorage.setItem(activeChatSessionStorageKey, activeSessionId);
  }, [activeChatSessionStorageKey, activeSessionId]);

  const text = language === "vi"
    ? {
        helper: "Hãy để Slidegenius phát triển ý tưởng, lập kế hoạch hoặc biến điều khó thành điều hiển nhiên.",
        placeholder: "Hãy nói điều bạn muốn tạo...",
        prompts: ["Xây dựng câu chuyện ra mắt sản phẩm mới", "Biến ghi chú thành một deck sắc nét", "Tìm hướng hình ảnh cho chiến dịch"],
        newConversation: "Cuộc trò chuyện mới",
        conversations: "CUỘC TRÒ CHUYỆN",
        justNow: "Vừa xong",
        regenerate: "Tạo lại",
        editMessage: "Sửa tin nhắn",
        copyMessage: "Sao chép tin nhắn",
        unavailable: "Không thể tải cuộc trò chuyện.",
        sending: "Đang suy nghĩ...",
        documentThinkingTitle: "Đang phân tích tài liệu",
        documentThinkingSteps: [
          "Đang đọc cấu trúc DOCX",
          "Đang phân tích nội dung tài liệu",
          "Đang chuẩn bị ngữ cảnh liên quan",
        ],
        upload: "Tải tài liệu DOCX",
        uploading: "Đang tải tệp...",
        uploaded: "Đã gắn tài liệu",
        removeAttachment: "Xóa tài liệu",
        cancelUpload: "Hủy tải tài liệu",
        scrollToLatest: "Cuộn đến tin nhắn mới nhất",
        otherPlaceholder: "Nhập hướng bạn muốn...",
        slideCountPlaceholder: "Nhập số slide, ví dụ 12 slide...",
        sendAnswer: "Gửi",
        deleteConversation: "Xóa cuộc trò chuyện",
        deleteConversationConfirm: "Bạn có chắc muốn xóa cuộc trò chuyện này không?",
        slideStreamClose: "Ẩn luồng tạo slide",
        slideStreamOpenProject: "Mở project",
        slideStreamEditProject: "Chỉnh sửa slide",
        slideStreamSlide: "SLIDE",
        slideStreamCompleted: "Đã hoàn thành",
        slideStreamWaiting: "Đang chờ slide đầu tiên...",
        slideStreamError: "Không thể tạo slide lúc này.",
        slideGenerationBusy: "Hiện đang có một deck được tạo. Bạn vẫn có thể trò chuyện, nhưng hãy đợi deck này hoàn tất trước khi tạo deck khác.",
        slideGenerationTitle: "Deck đang được tạo",
        slideGenerationRunning: "Đang tạo",
        slideGenerationOpen: "Xem tiến trình",
        slideGenerated: "Đã tạo slide thành công",
        slideGeneratedProject: "Project đã được lưu",
        projectDeleted: "Project này đã bị xóa nên không thể mở lại.",
        viewSlidePlan: "Xem plan tạo slide",
        slidePlanClose: "Đóng plan tạo slide",
        slidePlanTitle: "Kế hoạch tạo slide",
        slidePlanRequest: "Yêu cầu ban đầu",
        slidePlanBrief: "Brief sẽ dùng để tạo slide",
        slidePlanAnswers: "Các lựa chọn đã chốt",
        slidePlanSource: "Tài liệu tham chiếu",
        slidePlanSettings: "Thiết lập tạo",
        slidePlanNoAnswers: "Chưa có lựa chọn bổ sung.",
        slidePlanNoBrief: "Brief sẽ được hoàn thiện từ yêu cầu này.",
        slideCountLabel: "Số lượng slide",
        slideLimitLabel: "Giới hạn gói hiện tại",
        slideCountNotSet: "Chưa chốt",
        slideCountUnlimited: "Không giới hạn",
        modelLabel: "Model",
        effortLabel: "Effort",
        sources: "Nguồn tham khảo",
        sourceClose: "Đóng nguồn",
        sourceDocument: "Tài liệu",
        sourceSection: "Mục",
        sourceExcerpt: "Đoạn trích",
        sourceNoExcerpt: "Nguồn này chưa có đoạn trích hiển thị.",
        chatUsage: "Chat credit",
        documentUsage: "Tài liệu DOCX",
        chatUsageShort: "CHAT",
        documentUsageShort: "DOCX",
        usageReset: "Reset sau",
      }
    : {
        helper: "Ask Slidegenius to shape an idea, plan a project, or make something impossible feel obvious.",
        placeholder: "Tell me what you want to create...",
        prompts: ["Build a launch story for a new product", "Turn these notes into a sharp deck", "Find a visual direction for our campaign"],
        newConversation: "New conversation",
        conversations: "CONVERSATIONS",
        justNow: "Just now",
        regenerate: "Regenerate",
        editMessage: "Edit message",
        copyMessage: "Copy message",
        unavailable: "Unable to load conversations.",
        sending: "Thinking...",
        documentThinkingTitle: "Analyzing document",
        documentThinkingSteps: [
          "Reading the DOCX structure",
          "Analyzing the document content",
          "Preparing relevant context",
        ],
        upload: "Upload DOCX",
        uploading: "Uploading file...",
        uploaded: "Document attached",
        removeAttachment: "Remove document",
        cancelUpload: "Cancel document upload",
        scrollToLatest: "Scroll to latest message",
        otherPlaceholder: "Add your own direction...",
        slideCountPlaceholder: "Enter a slide count, for example 12 slides...",
        sendAnswer: "Send",
        deleteConversation: "Delete conversation",
        deleteConversationConfirm: "Are you sure you want to delete this conversation?",
        slideStreamClose: "Hide slide stream",
        slideStreamOpenProject: "Open project",
        slideStreamEditProject: "Edit slides",
        slideStreamSlide: "SLIDE",
        slideStreamCompleted: "Completed",
        slideStreamWaiting: "Waiting for the first slide...",
        slideStreamError: "Unable to create slides right now.",
        slideGenerationBusy: "A deck is already being created. You can keep chatting, but wait for it to finish before creating another deck.",
        slideGenerationTitle: "Deck in progress",
        slideGenerationRunning: "Creating",
        slideGenerationOpen: "View progress",
        slideGenerated: "Slides created successfully",
        slideGeneratedProject: "Project saved",
        projectDeleted: "This project was deleted and can no longer be opened.",
        viewSlidePlan: "View slide creation plan",
        slidePlanClose: "Close slide creation plan",
        slidePlanTitle: "Slide creation plan",
        slidePlanRequest: "Original request",
        slidePlanBrief: "Brief used for generation",
        slidePlanAnswers: "Confirmed choices",
        slidePlanSource: "Reference document",
        slidePlanSettings: "Generation settings",
        slidePlanNoAnswers: "No additional choices yet.",
        slidePlanNoBrief: "The brief will be refined from this request.",
        slideCountLabel: "Slide count",
        slideLimitLabel: "Current plan limit",
        slideCountNotSet: "Not chosen",
        slideCountUnlimited: "Unlimited",
        modelLabel: "Model",
        effortLabel: "Effort",
        sources: "Sources",
        sourceClose: "Close source",
        sourceDocument: "Document",
        sourceSection: "Section",
        sourceExcerpt: "Excerpt",
        sourceNoExcerpt: "This source has no excerpt available.",
        chatUsage: "Chat credits",
        documentUsage: "DOCX files",
        chatUsageShort: "CHAT",
        documentUsageShort: "DOCX",
        usageReset: "Resets in",
      };

  const hasUploadedDocuments = uploadedDocuments.length > 0;
  const sessionDocumentNames = sessionDocuments
    .map((document) => document.title || document.original_filename)
    .filter(Boolean);
  const sessionDocumentLabel = sessionDocumentNames.join(", ");
  const usageLimits = subscriptionUsage?.usage_limits || {
    chat_messages: 0,
    docx_upload: 0,
    max_docx_slides: 0,
  };
  const chatUsage = subscriptionUsage?.current_usage.chat_messages
    ?? subscriptionUsage?.current_usage.idea_generation
    ?? 0;
  const chatMessageCount = subscriptionUsage?.current_usage.chat_message_count ?? 0;
  const documentUsage = subscriptionUsage?.current_usage.docx_upload ?? 0;
  const chatUsagePercent = usageLimits.chat_messages === -1
    ? null
    : Math.min(100, Math.round((chatUsage / Math.max(1, usageLimits.chat_messages)) * 100));
  const chatUsageDetail = !subscriptionUsage ? "—" : usageLimits.chat_messages === -1
    ? `${formatUsageAmount(chatUsage)} / ∞ · ${chatMessageCount} ${language === "vi" ? "tin nhắn" : "messages"}`
    : `${formatUsageAmount(chatUsage)} / ${usageLimits.chat_messages} · ${chatMessageCount} ${language === "vi" ? "tin nhắn" : "messages"}`;
  const documentUsagePercent = usageLimits.docx_upload === -1
    ? null
    : Math.min(100, Math.round((documentUsage / Math.max(1, usageLimits.docx_upload)) * 100));
  const documentUsageDetail = !subscriptionUsage ? "—" : usageLimits.docx_upload === -1
    ? `${documentUsage} / ∞`
    : `${documentUsage} / ${usageLimits.docx_upload}`;
  const usageResetText = `${text.usageReset} ${formatUsageCountdown(subscriptionUsage?.usage_reset_at, usageNow, language)}`;
  const chatUsageTooltip = `${text.chatUsage}: ${chatUsageDetail} · ${usageResetText}`;
  const documentUsageTooltip = `${text.documentUsage}: ${documentUsageDetail} · ${usageResetText}`;

  const loadSubscriptionUsage = useCallback(async () => {
    try {
      setSubscriptionUsage(await api.getSubscriptionInfo());
    } catch {
      // Usage is supplemental UI; the backend remains the source of truth.
    }
  }, []);

  const applyChatTurnResult = (optimisticId: number, result: ChatTurnResponse) => {
    const assistantMessage = getMessageSources(result.assistant_message).length || !result.citations.length
      ? result.assistant_message
      : {
          ...result.assistant_message,
          metadata: {
            ...(result.assistant_message.metadata || {}),
            retrieval: { enabled: true, citations: result.citations },
          },
        };
    setMessages((current) => [
      ...current.filter((item) => (
        item.id !== optimisticId
        && item.id !== result.user_message.id
        && item.id !== result.assistant_message.id
      )),
      result.user_message,
      assistantMessage,
    ]);
    setSessions((current) => {
      const exists = current.some((session) => session.id === result.session.id);
      if (!exists) return [result.session, ...current];
      return current.map((session) => (
        session.id === result.session.id ? result.session : session
      ));
    });
  };

  const handleChatStreamEvent = (optimisticId: number, event: { type: string; data: Record<string, unknown> }) => {
    if (event.type === "complete") {
      applyChatTurnResult(optimisticId, chatTurnFromStreamEvent(event.data));
      setActiveChatJob(null);
      void loadSubscriptionUsage();
      return;
    }
    if (event.type === "error_event") {
      const messageValue = event.data.message;
      throw new Error(typeof messageValue === "string" && messageValue.trim()
        ? messageValue
        : text.unavailable);
    }
  };

  useEffect(() => {
    void loadSubscriptionUsage();
    const timer = window.setInterval(() => {
      setUsageNow(Date.now());
      void loadSubscriptionUsage();
    }, 60_000);
    return () => window.clearInterval(timer);
  }, [loadSubscriptionUsage]);

  useEffect(() => {
    if (!sending || thinkingMode !== "document") return;
    const timer = window.setInterval(() => {
      setDocumentThinkingStep((current) => current + 1);
    }, 1600);
    return () => window.clearInterval(timer);
  }, [sending, thinkingMode]);

  useEffect(() => {
    if (!isActive) {
      preserveRunningChatOrDiscardBlankDraft();
      initialChatMountRef.current = false;
      return undefined;
    }

    const restoreOnReload = initialChatMountRef.current && (() => {
      const navigation = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming | undefined;
      return navigation?.type === "reload";
    })();
    initialChatMountRef.current = false;

    let active = true;
    const initialize = async () => {
      const viewRequestId = ++sessionViewRequestRef.current;
      setLoading(true);
      setError("");
      try {
        const [config, existingSessions] = await Promise.all([
          loadChatbotConfig(),
          loadChatSessions(),
        ]);
        // This endpoint is deliberately best-effort so an older API can
        // still load the conversation list while the deployment rolls out.
        let reconnectableJob: ChatMessageJob | null = null;
        try {
          reconnectableJob = await loadActiveChatMessageJob();
        } catch {
          reconnectableJob = null;
        }
        if (!active || viewRequestId !== sessionViewRequestRef.current) return;
        setModels(config.models.map((item) => item.id));
        setEfforts(config.efforts.map((item) => item.id));
        setMaxSlideCount(Number.isFinite(config.max_slide_count) ? config.max_slide_count : 50);
        setMaxUploadBytes(Number.isFinite(config.max_upload_bytes) ? config.max_upload_bytes : 0);
        setMaxTotalUploadBytes(Number.isFinite(config.max_total_upload_bytes) ? config.max_total_upload_bytes : 0);
        setModel(config.default_model);
        setEffort(config.default_effort);

        const generationSession = generation.sessionId
          ? existingSessions.find((session) => session.id === generation.sessionId)
          : undefined;
        const reconnectSession = reconnectableJob
          ? existingSessions.find((session) => session.id === reconnectableJob?.session_id)
          : undefined;
        let storedSessionId: string | null = null;
        if (activeChatSessionStorageKey) {
          storedSessionId = localStorage.getItem(activeChatSessionStorageKey);
        }
        const resumeSessionId = chatResumeStorageKey
          ? sessionStorage.getItem(chatResumeStorageKey)
          : null;
        const resumeSession = resumeSessionId
          ? existingSessions.find((session) => session.id === resumeSessionId)
          : undefined;
        const storedSession = restoreOnReload && storedSessionId
          ? existingSessions.find((session) => session.id === storedSessionId)
          : undefined;
        const nextSession = generationSession
          || reconnectSession
          || resumeSession
          || storedSession
          || await createChatSession();
        if (!active || viewRequestId !== sessionViewRequestRef.current) return;
        setSessions(
          existingSessions.some((session) => session.id === nextSession.id)
            ? existingSessions
            : [nextSession, ...existingSessions],
        );
        setActiveSessionId(nextSession.id);
        setActiveChatJob(
          reconnectableJob?.session_id === nextSession.id ? reconnectableJob : null,
        );
        if (resumeSessionId && chatResumeStorageKey) {
          sessionStorage.removeItem(chatResumeStorageKey);
        }
        const [sessionMessages, sessionDocuments] = await Promise.all([
          loadChatMessages(nextSession.id),
          loadChatDocuments(nextSession.id),
        ]);
        if (!active || viewRequestId !== sessionViewRequestRef.current) return;
        const attachableDocuments = sessionDocuments.filter((item) => item.status !== "failed");
        const sentDocumentIds = getSentDocumentIds(sessionMessages);
        setMessages(sessionMessages);
        setUploadingDocument(null);
        setSessionDocuments(attachableDocuments);
        setUploadedDocuments(attachableDocuments.filter((item) => !sentDocumentIds.has(item.id)));
      } catch {
        if (active && viewRequestId === sessionViewRequestRef.current) setError(text.unavailable);
      } finally {
        if (active && viewRequestId === sessionViewRequestRef.current) setLoading(false);
      }
    };
    void initialize();
    return () => { active = false; };
  }, [isActive, preserveRunningChatOrDiscardBlankDraft]);

  useEffect(() => {
    if (
      !activeChatJob
      || loading
      || !activeSessionId
      || activeChatJob.session_id !== activeSessionId
      || sending
    ) return;

    const job = activeChatJob;
    const optimisticId = -Date.now();
    const pendingDocuments = sessionDocuments.filter((document) => (
      job.document_ids.includes(document.id)
    ));
    const alreadyVisible = messages.some((item) => (
      item.role === "user"
      && item.content === job.query
      && item.metadata?.optimistic === true
    ));

    setActiveChatJob(null);
    if (!alreadyVisible) {
      setMessages((current) => [
        ...current,
        {
          id: optimisticId,
          session_id: job.session_id,
          role: "user",
          content: job.query,
          model: job.model,
          effort: job.effort,
          metadata: {
            optimistic: true,
            ...(job.attachments.length ? { attachments: job.attachments } : {}),
          },
          created_at: new Date().toISOString(),
        },
      ]);
    }
    setUploadedDocuments([]);
    setSending(true);
    setThinkingMode(job.document_ids.length || sessionDocuments.length ? "document" : "conversation");
    setDocumentThinkingStep(0);
    chatMessageJobRef.current = job.id;

    void streamChatMessageJob(
      job.id,
      (event) => handleChatStreamEvent(optimisticId, event),
    )
      .catch((requestError) => {
        setMessages((current) => current.filter((item) => item.id !== optimisticId));
        setMessage(job.query);
        setUploadedDocuments(pendingDocuments);
        setError(requestError instanceof Error ? requestError.message : text.unavailable);
      })
      .finally(() => {
        if (chatMessageJobRef.current === job.id) chatMessageJobRef.current = null;
        setSending(false);
        setThinkingMode(null);
        setDocumentThinkingStep(0);
      });
  }, [activeChatJob, activeSessionId, loading, sending]);

  const loadSessionData = async (sessionId: string) => {
    const viewRequestId = ++sessionViewRequestRef.current;
    const [sessionMessages, sessionDocuments] = await Promise.all([
      loadChatMessages(sessionId),
      loadChatDocuments(sessionId),
    ]);
    if (viewRequestId !== sessionViewRequestRef.current) return;
    const attachableDocuments = sessionDocuments.filter((item) => item.status !== "failed");
    const sentDocumentIds = getSentDocumentIds(sessionMessages);
    setMessages(sessionMessages);
    setUploadingDocument(null);
    setSessionDocuments(attachableDocuments);
    setUploadedDocuments(attachableDocuments.filter((item) => !sentDocumentIds.has(item.id)));
  };

  const invalidatePendingUpload = () => {
    uploadRequestIdRef.current += 1;
    uploadAbortControllerRef.current?.abort();
    uploadAbortControllerRef.current = null;
    setUploading(false);
    setUploadingDocument(null);
  };

  const invalidateSessionView = () => {
    sessionViewRequestRef.current += 1;
  };

  useEffect(() => {
    let active = true;
    const projectIds = Array.from(new Set(
      messages.flatMap((item) => {
        if (item.role !== "assistant") return [];
        const log = getSlideGenerationLog(item);
        return log?.projectId !== null && log?.projectId !== undefined ? [log.projectId] : [];
      }),
    ));

    if (!projectIds.length) {
      setDeletedProjectIds(new Set());
      return () => { active = false; };
    }

    void Promise.all(projectIds.map(async (projectId) => {
      try {
        await loadWorkspaceProject(projectId);
        return null;
      } catch (requestError) {
        return isMissingProjectError(requestError) ? projectId : null;
      }
    })).then((missingProjectIds) => {
      if (!active) return;
      setDeletedProjectIds(new Set(
        missingProjectIds.filter((projectId): projectId is number => projectId !== null),
      ));
    });

    return () => { active = false; };
  }, [messages]);

  const openGeneratedDestination = async (projectId: number, destination: string) => {
    if (deletedProjectIds.has(projectId)) return;
    try {
      await loadWorkspaceProject(projectId);
      navigate(destination);
    } catch (requestError) {
      if (isMissingProjectError(requestError)) {
        setDeletedProjectIds((current) => {
          const next = new Set(current);
          next.add(projectId);
          return next;
        });
        setError(text.projectDeleted);
        return;
      }
      setError(requestError instanceof Error ? requestError.message : text.unavailable);
    }
  };

  const openGeneratedProject = (projectId: number) => openGeneratedDestination(projectId, `/projects/${projectId}`);
  const openGeneratedEditor = (projectId: number) => openGeneratedDestination(projectId, `/editor?project=${encodeURIComponent(projectId)}`);

  useEffect(() => {
    if (!openRequest || openRequest === lastOpenRequestRef.current || !generation.sessionId) return;
    const targetSession = sessions.find((session) => session.id === generation.sessionId);
    if (!targetSession || sending || deletingSessionId) return;

    lastOpenRequestRef.current = openRequest;
    if (targetSession.id === activeSessionId) return;

    invalidateSessionView();
    setError("");
    setActiveSessionId(targetSession.id);
    invalidatePendingUpload();
    setMessages([]);
    setSessionDocuments([]);
    if (!options.preserveUploadedDocuments) setUploadedDocuments([]);
    setSlidePlanOpen(false);
    setClarificationOtherOpen(false);
    setClarificationOther("");
    const loadPromise = loadSessionData(targetSession.id);
    const viewRequestId = sessionViewRequestRef.current;
    void loadPromise.catch(() => {
      if (viewRequestId === sessionViewRequestRef.current) setError(text.unavailable);
    });
  }, [activeSessionId, deletingSessionId, generation.sessionId, openRequest, sending, sessions]);

  useEffect(() => {
    if (!activeSessionId || generation.sessionId !== activeSessionId) return;
    if (generation.phase !== "completed" && generation.phase !== "error") return;

    let active = true;
    const viewRequestId = sessionViewRequestRef.current;
    void Promise.all([
      loadChatMessages(activeSessionId),
      loadChatSessions(),
      loadChatDocuments(activeSessionId),
    ])
      .then(([sessionMessages, freshSessions, sessionDocuments]) => {
        if (!active || viewRequestId !== sessionViewRequestRef.current) return;
        const attachableDocuments = sessionDocuments.filter((item) => item.status !== "failed");
        const sentDocumentIds = getSentDocumentIds(sessionMessages);
        setMessages(sessionMessages);
        setSessions(freshSessions);
        setSessionDocuments(attachableDocuments);
        setUploadedDocuments(attachableDocuments.filter((item) => !sentDocumentIds.has(item.id)));
        if (generation.phase === "error" && generation.error) setError(generation.error);
      })
      .catch(() => {
        if (active && viewRequestId === sessionViewRequestRef.current) setError(text.unavailable);
      });
    return () => { active = false; };
  }, [activeSessionId, generation.error, generation.phase, generation.sessionId]);

  const selectSession = async (session: ChatSession) => {
    if (session.id === activeSessionId || sending || deletingSessionId || removingDocumentId) return;
    const isEmptyDraft = Boolean(
      activeSessionId
      && messages.length === 0
      && !activeChatJob,
    );
    const draftSessionId = activeSessionId;
    invalidatePendingUpload();
    invalidateSessionView();
    setError("");
    if (isEmptyDraft && draftSessionId) {
      void archiveChatSession(draftSessionId).catch(() => undefined);
      setSessions((current) => current.filter((item) => item.id !== draftSessionId));
    }
    setActiveSessionId(session.id);
    setMessages([]);
    setSessionDocuments([]);
    setUploadedDocuments([]);
    setSlidePlanOpen(false);
    setClarificationOtherOpen(false);
    setClarificationOther("");
    const loadPromise = loadSessionData(session.id);
    const viewRequestId = sessionViewRequestRef.current;
    try {
      await loadPromise;
    } catch {
      if (viewRequestId === sessionViewRequestRef.current) setError(text.unavailable);
    }
  };

  const startNewConversation = async () => {
    if (sending || deletingSessionId || removingDocumentId) return;
    const isEmptyDraft = Boolean(
      activeSessionId
      && messages.length === 0
      && !activeChatJob,
    );
    const draftSessionId = activeSessionId;
    invalidatePendingUpload();
    invalidateSessionView();
    setError("");
    try {
      if (isEmptyDraft && draftSessionId) {
        await archiveChatSession(draftSessionId).catch(() => undefined);
      }
      const session = await createChatSession();
      setSessions((current) => [
        session,
        ...current.filter((item) => item.id !== draftSessionId),
      ]);
      setActiveSessionId(session.id);
      setMessages([]);
      setUploadingDocument(null);
      setSessionDocuments([]);
      setUploadedDocuments([]);
      setSlidePlanOpen(false);
      setClarificationOtherOpen(false);
      setClarificationOther("");
    } catch {
      setError(text.unavailable);
    }
  };

  const deleteSession = (event: MouseEvent<HTMLButtonElement>, session: ChatSession) => {
    event.stopPropagation();
    if (sending || deletingSessionId || removingDocumentId) return;
    if (isGenerating && generation.sessionId === session.id) {
      setError(text.slideGenerationBusy);
      return;
    }
    setPendingDeleteSession(session);
  };

  const confirmDeleteSession = async () => {
    const session = pendingDeleteSession;
    setPendingDeleteSession(null);
    if (!session) return;
    if (session.id === activeSessionId) {
      invalidatePendingUpload();
      invalidateSessionView();
    }
    setDeletingSessionId(session.id);
    setError("");
    try {
      await archiveChatSession(session.id);
      const remainingSessions = sessions.filter((item) => item.id !== session.id);
      setSessions(remainingSessions);

      if (session.id !== activeSessionId) return;

      setActiveSessionId(null);
      setMessages([]);
      setSessionDocuments([]);
      setUploadedDocuments([]);
      setSlidePlanOpen(false);
      setClarificationOtherOpen(false);
      setClarificationOther("");

      const nextSession = remainingSessions[0] || await createChatSession();
      setSessions(remainingSessions.length ? remainingSessions : [nextSession]);
      setActiveSessionId(nextSession.id);
      await loadSessionData(nextSession.id);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : text.unavailable);
    } finally {
      setDeletingSessionId(null);
    }
  };

  useEffect(() => {
    const thread = threadRef.current;
    if (!thread) return;

    const frame = window.requestAnimationFrame(() => {
      thread.scrollTo({
        top: thread.scrollHeight,
        behavior: sending ? "smooth" : "auto",
      });
      setShowScrollToLatest(false);
    });
    return () => window.cancelAnimationFrame(frame);
  }, [activeSessionId, loading, messages.length, sending]);

  const handleThreadScroll = () => {
    const thread = threadRef.current;
    if (!thread) return;
    const distanceFromLatest = thread.scrollHeight - thread.scrollTop - thread.clientHeight;
    const shouldShow = distanceFromLatest > 48;
    setShowScrollToLatest((current) => current === shouldShow ? current : shouldShow);
  };

  const scrollThreadToLatest = () => {
    const thread = threadRef.current;
    if (!thread) return;
    thread.scrollTo({ top: thread.scrollHeight, behavior: "smooth" });
    setShowScrollToLatest(false);
  };

  const sendMessageContent = async (
    cleanMessage: string,
    options: SendMessageOptions = {},
  ) => {
    const streamSlides = options.streamSlides === true;
    if (!cleanMessage || !activeSessionId || sending || uploading) return;
    // Keep ordinary chat available while a deck is rendering. The explicit
    // slide-stream action is the only operation that must be blocked here.
    if (streamSlides && isGenerating) {
      setMessage(cleanMessage);
      setError(text.slideGenerationBusy);
      return;
    }
    const sessionId = activeSessionId;
    const pendingDocuments = options.documentIds ? [] : [...uploadedDocuments];
    const documentIds = options.documentIds ?? pendingDocuments.map((document) => document.id);
    const messageAttachments: MessageAttachment[] = options.messageAttachments
      ? [...options.messageAttachments]
      : pendingDocuments.map((document) => ({
          id: document.id,
          name: document.title || document.original_filename,
        }));

    const optimisticMessage: ChatMessage = {
      id: -Date.now(),
      session_id: activeSessionId,
      role: "user",
      content: cleanMessage,
      model,
      effort,
      metadata: {
        optimistic: true,
        ...(messageAttachments.length ? { attachments: messageAttachments } : {}),
      },
      created_at: new Date().toISOString(),
    };

    setMessage("");
    setClarificationOther("");
    setClarificationOtherOpen(false);
    setError("");
    setMessages((current) => [...current, optimisticMessage]);
    // Once submitted, the attachment belongs to this user message. Keep the
    // composer reserved for files that have not been sent yet; restore them
    // below if the request fails.
    setUploadedDocuments([]);

    if (streamSlides) {
      const started = startSlideGeneration({
        sessionId,
        content: cleanMessage,
        model,
        effort,
        slideCount: options.slideCount,
        documentIds,
      });
      if (!started) {
        setMessages((current) => current.filter((item) => item.id !== optimisticMessage.id));
        setMessage(cleanMessage);
        setUploadedDocuments(pendingDocuments);
        setError(text.slideGenerationBusy);
      } else {
        window.setTimeout(() => void loadSubscriptionUsage(), 500);
      }
      return;
    }

    setSending(true);
    setThinkingMode(pendingDocuments.length > 0 || sessionDocuments.length > 0 ? "document" : "conversation");
    setDocumentThinkingStep(0);
    setActiveChatJob(null);
    chatMessageJobRef.current = String(optimisticMessage.id);
    try {
      await streamChatMessage(
        sessionId,
        cleanMessage,
        model,
        effort,
        options.slideCount,
        (event) => handleChatStreamEvent(optimisticMessage.id, event),
        undefined,
        documentIds,
      );
    } catch (requestError) {
      setMessages((current) => current.filter((item) => item.id !== optimisticMessage.id));
      setMessage(cleanMessage);
      setUploadedDocuments(pendingDocuments);
      setError(requestError instanceof Error ? requestError.message : text.unavailable);
    } finally {
      setSending(false);
      setThinkingMode(null);
      setDocumentThinkingStep(0);
      if (chatMessageJobRef.current === String(optimisticMessage.id)) {
        chatMessageJobRef.current = null;
      }
    }
  };

  const submitMessage = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const cleanMessage = message.trim();
    void sendMessageContent(cleanMessage);
  };

  const submitSlideOption = (option: SlideFlowOption, optionIndex: number) => {
    if (sending || isGenerating) return;
    if (option.action === "upgrade") {
      setSlidePlanOpen(false);
      setClarificationOtherOpen(false);
      navigate("/subscription");
      return;
    }
    if (option.is_other || option.action === "other") {
      setSlidePlanOpen(false);
      setClarificationOtherOpen(true);
      window.requestAnimationFrame(() => clarificationInputRef.current?.focus());
      return;
    }
    setSlidePlanOpen(false);
    const latestFlow = [...messages]
      .reverse()
      .map((item) => item.role === "assistant" ? getSlideFlow(item) : null)
      .find((item): item is SlideFlow => Boolean(item));
    const visibleFlow = latestFlow;
    const selectedSlideCount = extractSlideCount(option.value || option.label)
      ?? visibleFlow?.targetSlideCount
      ?? undefined;
    void sendMessageContent(option.value || option.label, {
      streamSlides: visibleFlow?.state === "awaiting_confirmation"
        && optionIndex === 0
        && selectedSlideCount !== undefined,
      slideCount: selectedSlideCount,
    });
  };

  const submitOtherAnswer = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const cleanAnswer = clarificationOther.trim();
    if (!cleanAnswer || sending || isGenerating) return;
    const latestFlow = [...messages]
      .reverse()
      .map((item) => item.role === "assistant" ? getSlideFlow(item) : null)
      .find((item): item is SlideFlow => Boolean(item));
    const isCountQuestion = latestFlow?.questionKind === "slide_count"
      || latestFlow?.state === "limit_reached";
    const slideCount = extractSlideCount(cleanAnswer, isCountQuestion);
    if (isCountQuestion && slideCount === null) {
      setError(language === "vi"
        ? "Hãy nhập số lượng slide, ví dụ: 12 slide."
        : "Enter a slide count, for example: 12 slides.");
      return;
    }
    if (isCountQuestion && slideCount !== null && slideCount < 3) {
      setError(language === "vi"
        ? "Số lượng slide tối thiểu là 3."
        : "The minimum slide count is 3.");
      return;
    }
    setSlidePlanOpen(false);
    void sendMessageContent(cleanAnswer, { slideCount: slideCount ?? undefined });
  };

  const handleDocumentSelected = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file || !activeSessionId || uploading) return;
    if (!file.name.toLowerCase().endsWith(".docx")) {
      setError(language === "vi" ? "Chỉ hỗ trợ file DOCX." : "Only DOCX files are supported.");
      return;
    }
    if (maxUploadBytes <= 0 || maxTotalUploadBytes <= 0) {
      setError(text.unavailable);
      return;
    }
    if (file.size > maxUploadBytes) {
      setError(language === "vi"
        ? `Mỗi file DOCX tối đa ${formatFileSize(maxUploadBytes)}.`
        : `Each DOCX file can be at most ${formatFileSize(maxUploadBytes)}.`);
      return;
    }
    const currentUploadBytes = sessionDocuments.reduce(
      (total, document) => total + Math.max(0, Number(document.size_bytes) || 0),
      0,
    );
    if (currentUploadBytes + file.size > maxTotalUploadBytes) {
      setError(language === "vi"
        ? `Tổng dung lượng DOCX trong cuộc trò chuyện tối đa ${formatFileSize(maxTotalUploadBytes)}. Đã dùng ${formatFileSize(currentUploadBytes)}.`
        : `DOCX files in this conversation can total ${formatFileSize(maxTotalUploadBytes)}. ${formatFileSize(currentUploadBytes)} is already attached.`);
      return;
    }
    const sessionId = activeSessionId;
    const sessionViewRequestId = sessionViewRequestRef.current;
    const controller = new AbortController();
    const requestId = uploadRequestIdRef.current + 1;
    uploadRequestIdRef.current = requestId;
    uploadAbortControllerRef.current = controller;
    setUploading(true);
    setUploadingDocument(file.name);
    setError("");
    try {
      const document = await uploadChatDocument(sessionId, file, controller.signal);
      if (
        requestId !== uploadRequestIdRef.current
        || controller.signal.aborted
        || sessionViewRequestId !== sessionViewRequestRef.current
      ) {
        await deleteChatDocument(sessionId, document.id).catch(() => undefined);
        return;
      }
      setSessionDocuments((current) => [
        ...current.filter((item) => item.id !== document.id),
        document,
      ]);
      setUploadedDocuments((current) => [
        ...current.filter((item) => item.id !== document.id),
        document,
      ]);
      void loadSubscriptionUsage();
    } catch (requestError) {
      if (
        requestId !== uploadRequestIdRef.current
        || controller.signal.aborted
        || sessionViewRequestId !== sessionViewRequestRef.current
        || (requestError instanceof Error && requestError.name === "AbortError")
      ) return;
      setUploadingDocument(null);
      setError(requestError instanceof Error ? requestError.message : text.unavailable);
    } finally {
      if (requestId === uploadRequestIdRef.current) {
        uploadAbortControllerRef.current = null;
        setUploading(false);
        setUploadingDocument(null);
      }
    }
  };

  const cancelDocumentUpload = (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    if (!uploading) return;
    invalidatePendingUpload();
    setError("");
  };

  const removeDocument = async (
    event: MouseEvent<HTMLButtonElement>,
    document: ChatDocument,
  ) => {
    event.stopPropagation();
    if (!activeSessionId || removingDocumentId || uploading) return;
    const sessionId = activeSessionId;
    const sessionViewRequestId = sessionViewRequestRef.current;
    setRemovingDocumentId(document.id);
    setError("");
    try {
      await deleteChatDocument(sessionId, document.id);
      if (sessionViewRequestId !== sessionViewRequestRef.current) return;
      setSessionDocuments((current) => current.filter((item) => item.id !== document.id));
      setUploadedDocuments((current) => current.filter((item) => item.id !== document.id));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : text.unavailable);
    } finally {
      setRemovingDocumentId(null);
    }
  };

  const displayedMessages = messages.filter((item) => item.role === "user" || item.role === "assistant");
  const latestAssistantMessageId = [...displayedMessages]
    .reverse()
    .find((item) => item.role === "assistant")?.id;

  const selectedSourceEntry = selectedSourceKey
    ? displayedMessages.reduce<ChatSource | null>((found, item) => {
        if (found || item.role !== "assistant") return found;
        const source = getMessageSources(item).find((candidate) => sourceKey(item.id, candidate) === selectedSourceKey);
        return source ?? null;
      }, null)
    : null;
  const selectedSource = selectedSourceEntry;
  const selectedSourceDocument = selectedSource
    ? sessionDocuments.find((document) => document.id === selectedSource.documentId)
    : undefined;
  const selectedSourceDocumentName = selectedSourceDocument?.title || selectedSourceDocument?.original_filename || "";

  const regenerateAssistantMessage = (assistantMessage: ChatMessage) => {
    if (
      assistantMessage.id !== latestAssistantMessageId
      || sending
      || uploading
      || !activeSessionId
    ) return;

    const assistantIndex = displayedMessages.findIndex((item) => item.id === assistantMessage.id);
    if (assistantIndex < 0) return;
    const previousUserMessage = [...displayedMessages.slice(0, assistantIndex)]
      .reverse()
      .find((item) => item.role === "user");
    if (!previousUserMessage || !previousUserMessage.content.trim()) {
      setError(text.unavailable);
      return;
    }

    const attachments = getMessageAttachments(previousUserMessage);
    void sendMessageContent(previousUserMessage.content.trim(), {
      documentIds: attachments.map((attachment) => attachment.id),
      messageAttachments: attachments,
      preserveUploadedDocuments: true,
    });
  };
  const latestSlideFlowMessage = [...displayedMessages]
    .reverse()
    .find((item) => item.role === "assistant" && item.metadata && Object.prototype.hasOwnProperty.call(item.metadata, "slide_flow"));
  const latestSlideFlow = latestSlideFlowMessage ? getSlideFlow(latestSlideFlowMessage) : null;
  const latestInteractiveAssistantId = latestSlideFlowMessage && latestSlideFlow
    ? latestSlideFlowMessage.id
    : undefined;
  const hasPersistedGeneration = generation.phase === "completed" && displayedMessages.some((item) => {
    if (item.role !== "assistant") return false;
    const log = getSlideGenerationLog(item);
    if (!log) return false;
    if (generation.projectId !== null) return log.projectId === generation.projectId;
    return Boolean(generation.projectName && log.projectName === generation.projectName);
  });
  const hasActiveGeneration = isActiveGeneration && generation.phase !== "idle" && !hasPersistedGeneration;

  return (
    <section className={`chat-layout ${showSlideStream || slidePlanOpen || Boolean(selectedSource) ? "chat-layout-streaming" : ""}`} onClick={() => { setToolsOpen(false); setModelOpen(false); }}>
      <aside className="chat-history">
        <div className="chat-history-top">
          <span>{text.conversations}</span>
          <button aria-label={text.newConversation} onClick={() => void startNewConversation()} />
        </div>
        <button className="new-chat-button" onClick={() => void startNewConversation()}>{text.newConversation}</button>
        <div className="chat-history-list">
          {sessions.map((session) => (
            <div className="chat-history-row" key={session.id}>
              <button
                className={`chat-history-item ${session.id === activeSessionId ? "active" : ""}`}
                onClick={() => void selectSession(session)}
              >
                <span>{formatSessionDate(session.updated_at, language)}</span>
                {session.title || text.newConversation}
              </button>
              <button
                className="chat-history-delete"
                type="button"
                aria-label={text.deleteConversation}
                title={text.deleteConversation}
                disabled={Boolean(deletingSessionId)}
                onClick={(event) => void deleteSession(event, session)}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      </aside>

      <div className="chat-panel">
        <div className="chat-panel-header">
          <p className="workspace-eyebrow">SLIDEGENIUS / CHAT</p>
        </div>

        {loading ? <div className="chat-empty"><p>{text.sending}</p></div> : messages.length || sending || hasActiveGeneration ? (
          <div className="chat-thread-wrap">
            <div className="chat-thread" ref={threadRef} onScroll={handleThreadScroll} aria-live="polite">
              {displayedMessages.map((item) => {
                const rawFlow = item.role === "assistant" ? getSlideFlow(item) : null;
                const flow = rawFlow;
                const generation = item.role === "assistant" ? getSlideGenerationLog(item) : null;
                const sources = item.role === "assistant" ? getMessageSources(item) : [];
                const activeSource = sources.find((source) => sourceKey(item.id, source) === selectedSourceKey);
                const attachments = item.role === "user" ? getMessageAttachments(item) : [];
                const showFlow = item.id === latestInteractiveAssistantId;
                const visibleContent = item.content;
                return item.role === "assistant" ? (
                  <article className="chat-assistant-message" key={item.id} tabIndex={0}>
                    <span className="chat-assistant-mark" aria-hidden="true">✦</span>
                    <ChatMarkdown
                      content={visibleContent}
                      onCitationClick={sources.length > 0 ? (sourceIndex) => {
                          const source = sources.find((candidate) => candidate.index === sourceIndex);
                          if (!source) return;
                          const nextKey = sourceKey(item.id, source);
                          setSelectedSourceKey((current) => current === nextKey ? null : nextKey);
                        } : undefined}
                    />
                    {sources.length > 0 && (
                      <div className="chat-sources">
                        <div className="chat-sources-heading">
                          <span>{text.sources}</span>
                          <span className="chat-sources-count">{sources.length}</span>
                        </div>
                        <div className="chat-source-list" role="list" aria-label={text.sources}>
                          {sources.map((source) => {
                            const key = sourceKey(item.id, source);
                            const document = sessionDocuments.find((candidate) => candidate.id === source.documentId);
                            const documentName = document?.title || document?.original_filename || "";
                            return (
                              <div className="chat-source-chip-wrap" key={key} role="listitem">
                                <button
                                  className={`chat-source-chip ${activeSource && key === selectedSourceKey ? "active" : ""}`}
                                  type="button"
                                  aria-pressed={key === selectedSourceKey}
                                  title={source.section || source.title}
                                  onClick={() => setSelectedSourceKey((current) => current === key ? null : key)}
                                >
                                  <span className="chat-source-chip-label">Source {source.index}</span>
                                  <span className="chat-source-chip-title">{documentName ? `${documentName} · ` : ""}{source.title}</span>
                                </button>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                    <div className="chat-message-meta">
                      <time>{messageTime(item.created_at, language) || text.justNow}</time>
                      {item.id === latestAssistantMessageId && (
                        <button
                          type="button"
                          aria-label={text.regenerate}
                          title={text.regenerate}
                          disabled={sending || uploading}
                          onClick={(event) => {
                            event.stopPropagation();
                            regenerateAssistantMessage(item);
                          }}
                        >
                          ↻
                        </button>
                      )}
                      <button type="button" aria-label={text.copyMessage} title={text.copyMessage} onClick={() => void navigator.clipboard?.writeText(visibleContent)}>▣</button>
                    </div>
                    {generation && (
                      <div className="chat-slide-generation-log">
                        <span className="chat-slide-generation-mark" aria-hidden="true">✓</span>
                        <div className="chat-slide-generation-copy">
                          <p>{text.slideGenerated}</p>
                          <strong title={generation.projectName || text.slideGeneratedProject}>{truncateProjectName(generation.projectName || text.slideGeneratedProject)}</strong>
                          {generation.slideCount !== null && <span>{generation.slideCount} {text.slideStreamSlide.toLowerCase()}</span>}
                        </div>
                        {generation.projectId !== null && (
                          deletedProjectIds.has(generation.projectId) ? (
                            <span className="chat-slide-generation-deleted">{text.projectDeleted}</span>
                          ) : (
                            <div className="chat-slide-generation-actions">
                              <button className="secondary" type="button" onClick={() => void openGeneratedProject(generation.projectId!)}>{text.slideStreamOpenProject} ↗</button>
                              <button className="primary" type="button" onClick={() => void openGeneratedEditor(generation.projectId!)}>{text.slideStreamEditProject} ↗</button>
                            </div>
                          )
                        )}
                      </div>
                    )}
                    {flow && showFlow && (
                      <div className={`chat-slide-flow ${flow.state === "awaiting_confirmation" ? "confirmation" : ""} ${flow.state === "limit_reached" ? "limit-reached" : ""}`}>
                        {flow.state === "awaiting_confirmation" && (
                          <button
                            className="chat-plan-button"
                            type="button"
                            onClick={(event) => {
                              event.stopPropagation();
                              setSlidePlanOpen(true);
                            }}
                          >
                            <span>{text.viewSlidePlan}</span>
                            <span aria-hidden="true">↗</span>
                          </button>
                        )}
                        <div className="chat-flow-options">
                          {flow.options.map((option, optionIndex) => (
                            <button
                              className={`chat-flow-option ${flow.state === "awaiting_confirmation" && optionIndex === 0 ? "primary" : ""} ${option.action === "upgrade" ? "upgrade" : ""}`}
                              disabled={sending || isGenerating}
                              key={`${item.id}-${option.label}`}
                              type="button"
                              onClick={() => submitSlideOption(option, optionIndex)}
                            >
                              {option.label}
                            </button>
                          ))}
                        </div>
                        {(flow.state === "clarifying" || flow.state === "limit_reached") && clarificationOtherOpen && (
                          <form className="chat-flow-other" onSubmit={submitOtherAnswer}>
                            <input
                              ref={clarificationInputRef}
                              value={clarificationOther}
                              onChange={(event) => setClarificationOther(event.target.value)}
                              disabled={sending || isGenerating}
                              placeholder={flow.questionKind === "slide_count" ? text.slideCountPlaceholder : text.otherPlaceholder}
                              aria-label={flow.questionKind === "slide_count" ? text.slideCountPlaceholder : text.otherPlaceholder}
                            />
                            <button type="submit" disabled={sending || isGenerating || !clarificationOther.trim()}>{text.sendAnswer}</button>
                          </form>
                        )}
                      </div>
                    )}
                  </article>
                ) : (
                  <article className="chat-user-message" key={item.id} tabIndex={0}>
                    <div className="chat-user-bubble"><p style={{ whiteSpace: "pre-wrap" }}>{item.content}</p></div>
                    {attachments.length > 0 && (
                      <div className="chat-message-attachments" role="list" aria-label={text.uploaded}>
                        {attachments.map((attachment) => (
                          <div className="chat-message-attachment" key={attachment.id} role="listitem" title={attachment.name}>
                            <span className="chat-message-attachment-icon" aria-hidden="true">
                              <svg viewBox="0 0 24 24" fill="none">
                                <path d="M7 3.75h7.2L19 8.55v11.7H7z" />
                                <path d="M14 3.75v5h5M9.5 13h7M9.5 16h5" />
                              </svg>
                            </span>
                            <strong>{attachment.name}</strong>
                          </div>
                        ))}
                      </div>
                    )}
                    <div className="chat-message-meta">
                      <time>{messageTime(item.created_at, language) || text.justNow}</time>
                      <button type="button" aria-label={text.editMessage} title={text.editMessage} onClick={() => setMessage(item.content)}>✎</button>
                      <button type="button" aria-label={text.copyMessage} title={text.copyMessage} onClick={() => void navigator.clipboard?.writeText(item.content)}>▣</button>
                    </div>
                  </article>
                );
              })}
              {hasActiveGeneration && (
                <ChatSlideGenerationCard
                  phase={generation.phase}
                  slides={generation.slides}
                  totalSlides={generation.totalSlides}
                  targetSlideCount={generation.targetSlideCount}
                  progress={generation.progress}
                  projectName={generation.projectName}
                  error={generation.error}
                  title={text.slideGenerationTitle}
                  generatingLabel={text.slideGenerationRunning}
                  completedLabel={text.slideStreamCompleted}
                  openStreamLabel={text.slideGenerationOpen}
                  openProjectLabel={text.slideStreamOpenProject}
                  openEditorLabel={text.slideStreamEditProject}
                  slideLabel={text.slideStreamSlide}
                  onOpenStream={openSlideStream}
                  projectId={generation.projectId !== null && !deletedProjectIds.has(generation.projectId) ? generation.projectId : null}
                  onOpenProject={(projectId) => void openGeneratedProject(projectId)}
                  onOpenEditor={(projectId) => void openGeneratedEditor(projectId)}
                />
              )}
              {sending && (
                <div className={`chat-pending-message ${thinkingMode === "document" ? "is-document-thinking" : ""}`} role="status" aria-live="polite">
                  <span className="chat-assistant-mark" aria-hidden="true">✦</span>
                  <div className="chat-pending-copy">
                    <div className="chat-thinking-summary">
                      <span className="chat-pending-loader" aria-hidden="true" />
                      <span>{thinkingMode === "document" ? text.documentThinkingTitle : text.sending}</span>
                    </div>
                    {thinkingMode === "document" && (
                      <div className="chat-thinking-step">
                        <span className="chat-thinking-step-dot" aria-hidden="true" />
                        <span>{text.documentThinkingSteps[documentThinkingStep % text.documentThinkingSteps.length]}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
            {showScrollToLatest && (
              <button
                className="chat-scroll-latest"
                type="button"
                aria-label={text.scrollToLatest}
                title={text.scrollToLatest}
                onClick={(event) => {
                  event.stopPropagation();
                  scrollThreadToLatest();
                }}
              >
                ↓
              </button>
            )}
          </div>
        ) : (
          <div className="chat-empty">
            <div className="genius-orbit" aria-hidden="true"><span /><span /><span /></div>
            <p>{text.helper}</p>
            <div className="chat-suggestions">
              {text.prompts.map((prompt) => <button key={prompt} onClick={() => setMessage(prompt)}>{prompt}<span>↗</span></button>)}
            </div>
          </div>
        )}

        {error && <p className="chat-error" role="alert">{error}</p>}
        <form className="chat-composer" onSubmit={submitMessage}>
          <input
            ref={fileInputRef}
            type="file"
            accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            hidden
            onChange={(event) => void handleDocumentSelected(event)}
          />
          {(uploading || hasUploadedDocuments) && (
            <div
              className="chat-composer-attachments"
              id="chat-composer-attachment"
              role="list"
              aria-label={text.uploaded}
            >
              {uploadingDocument && (
                <div
                  className="chat-composer-attachment is-loading"
                  role="listitem"
                  aria-label={text.uploading + " " + uploadingDocument}
                >
                  <span className="chat-composer-attachment-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" fill="none">
                      <path d="M7 3.75h7.2L19 8.55v11.7H7z" />
                      <path d="M14 3.75v5h5M9.5 13h7M9.5 16h5" />
                    </svg>
                  </span>
                  <strong title={uploadingDocument}>{uploadingDocument}</strong>
                  <span className="chat-composer-attachment-state is-uploading" aria-hidden="true">↑</span>
                  <button
                    className="chat-composer-attachment-remove"
                    type="button"
                    aria-label={text.cancelUpload + " " + uploadingDocument}
                    title={text.cancelUpload}
                    onClick={cancelDocumentUpload}
                  >
                    ×
                  </button>
                </div>
              )}
              {uploadedDocuments.map((document) => {
                const documentName = document.title || document.original_filename;
                return (
                  <div
                    className="chat-composer-attachment is-ready"
                    key={document.id}
                    role="listitem"
                    aria-label={documentName + " — " + text.uploaded}
                  >
                    <span className="chat-composer-attachment-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24" fill="none">
                        <path d="M7 3.75h7.2L19 8.55v11.7H7z" />
                        <path d="M14 3.75v5h5M9.5 13h7M9.5 16h5" />
                      </svg>
                    </span>
                    <strong title={documentName}>{documentName}</strong>
                    <button
                      className="chat-composer-attachment-remove"
                      type="button"
                      aria-label={text.removeAttachment + " " + documentName}
                      title={text.removeAttachment}
                      disabled={removingDocumentId === document.id}
                      onClick={(event) => void removeDocument(event, document)}
                    >
                      ×
                    </button>
                  </div>
                );
              })}
            </div>
          )}
          <textarea
            {...((uploading || hasUploadedDocuments) ? { "aria-describedby": "chat-composer-attachment" } : {})}
            value={message}
            onChange={(event) => {
              setMessage(event.target.value);
              event.currentTarget.style.height = "auto";
              const contentHeight = event.currentTarget.scrollHeight;
              event.currentTarget.style.height = `${Math.min(220, Math.max(44, contentHeight))}px`;
              event.currentTarget.style.overflowY = contentHeight > 220 ? "auto" : "hidden";
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
                event.preventDefault();
                event.currentTarget.form?.requestSubmit();
              }
            }}
            placeholder={text.placeholder}
            aria-label={text.placeholder}
            rows={1}
            disabled={loading || sending || !activeSessionId}
          />
          <div className="composer-controls" onClick={(event) => event.stopPropagation()}>
            <button type="button" className="composer-plus" aria-label="Open tools" aria-expanded={toolsOpen} onClick={() => { setToolsOpen(!toolsOpen); setModelOpen(false); }}>+</button>
            {toolsOpen && <div className="composer-tools-menu"><button type="button" onClick={() => { fileInputRef.current?.click(); setToolsOpen(false); }}>{text.upload}</button><button type="button" className={searchEnabled ? "selected" : ""} onClick={() => { setSearchEnabled(!searchEnabled); setToolsOpen(false); }}>Search</button></div>}
            <div className="composer-spacer" />
            <div className="composer-model">
              <button type="button" className="composer-model-button" aria-expanded={modelOpen} onClick={() => { setModelOpen(!modelOpen); setToolsOpen(false); }}>Genius {model.slice(-1)} <span>{effort[0].toUpperCase() + effort.slice(1)}</span></button>
              {modelOpen && <div className="composer-model-menu"><p className="composer-model-menu-label">Model</p>{models.map((item) => <button type="button" key={item} className={model === item ? "selected" : ""} onClick={() => { setModel(item); setModelOpen(false); }}>Genius {item.slice(-1)}{model === item && <i>✓</i>}</button>)}<div className="composer-model-divider" /><p className="composer-model-menu-label">Effort</p>{efforts.map((item) => <button type="button" key={item} className={effort === item ? "selected" : ""} onClick={() => { if (item === "low" || item === "medium" || item === "high") setEffort(item); setModelOpen(false); }}>{item[0].toUpperCase() + item.slice(1)}{effort === item && <i>✓</i>}</button>)}</div>}
            </div>
            <div className="composer-usage-inline" role="status" aria-live="polite">
              <UsageMeter label={text.chatUsageShort} percent={chatUsagePercent} detail={chatUsageTooltip} />
              <UsageMeter label={text.documentUsageShort} percent={documentUsagePercent} detail={documentUsageTooltip} />
            </div>
            <button className="composer-send" type="submit" aria-label="Send message" disabled={sending || uploading || !message.trim()}>↗</button>
          </div>
        </form>
        <p className="chat-disclaimer">Slidegenius can make mistakes. Review important work before sharing.</p>
      </div>

      {selectedSource && (
        <aside className="chat-slide-stream-panel chat-source-panel" aria-label={text.sources}>
          <div className="chat-slide-stream-header chat-source-panel-header">
            <div>
              <p className="chat-slide-stream-eyebrow">{text.sources} · SOURCE {selectedSource.index}</p>
              <h3>{selectedSource.title}</h3>
            </div>
            <button
              type="button"
              aria-label={text.sourceClose}
              title={text.sourceClose}
              onClick={() => setSelectedSourceKey(null)}
            >
              ×
            </button>
          </div>
          <div className="chat-source-panel-body">
            {selectedSourceDocumentName && <p><span>{text.sourceDocument}</span>{selectedSourceDocumentName}</p>}
            {selectedSource.section && <p><span>{text.sourceSection}</span>{selectedSource.section}</p>}
            <div className="chat-source-panel-excerpt">
              <span>{text.sourceExcerpt}</span>
              <blockquote>{selectedSource.excerpt || text.sourceNoExcerpt}</blockquote>
            </div>
          </div>
        </aside>
      )}

      {showSlideStream && !selectedSource && (
        <ChatSlideStreamPanel
          status={generation.status}
          progress={generation.progress}
          slides={generation.slides}
          totalSlides={generation.totalSlides}
          completed={generation.phase === "completed"}
          projectId={generation.projectId}
          error={generation.error}
          closeLabel={text.slideStreamClose}
          openProjectLabel={text.slideStreamOpenProject}
          slideLabel={text.slideStreamSlide}
          completedLabel={text.slideStreamCompleted}
          waitingLabel={text.slideStreamWaiting}
          onClose={closeSlideStream}
          onOpenProject={(projectId) => navigate(`/projects/${projectId}`)}
        />
      )}
      {slidePlanOpen && !showSlideStream && !selectedSource && latestSlideFlow && (
        <ChatSlidePlanPanel
          originalPrompt={latestSlideFlow.originalPrompt}
          brief={latestSlideFlow.brief}
          answers={latestSlideFlow.answers}
          targetSlideCount={latestSlideFlow.targetSlideCount}
          maxSlideCount={latestSlideFlow.maxSlideCount ?? maxSlideCount}
          model={model}
          effort={effort}
          document={sessionDocumentLabel || null}
          title={text.slidePlanTitle}
          closeLabel={text.slidePlanClose}
          requestLabel={text.slidePlanRequest}
          briefLabel={text.slidePlanBrief}
          answersLabel={text.slidePlanAnswers}
          sourceLabel={text.slidePlanSource}
          settingsLabel={text.slidePlanSettings}
          noAnswersLabel={text.slidePlanNoAnswers}
          noBriefLabel={text.slidePlanNoBrief}
          slideCountLabel={text.slideCountLabel}
          slideLimitLabel={text.slideLimitLabel}
          slideCountNotSet={text.slideCountNotSet}
          slideCountUnlimited={text.slideCountUnlimited}
          modelLabel={text.modelLabel}
          effortLabel={text.effortLabel}
          onClose={() => setSlidePlanOpen(false)}
        />
      )}
      <SlidegenConfirmDialog
        open={Boolean(pendingDeleteSession)}
        onOpenChange={(open) => {
          if (!open) setPendingDeleteSession(null);
        }}
        title={language === "vi" ? "Xóa cuộc trò chuyện?" : "Delete this conversation?"}
        description={text.deleteConversationConfirm}
        confirmLabel={language === "vi" ? "Xóa cuộc trò chuyện" : "Delete conversation"}
        cancelLabel={language === "vi" ? "Hủy" : "Cancel"}
        onConfirm={() => void confirmDeleteSession()}
        destructive
        busy={Boolean(deletingSessionId)}
      />
    </section>
  );
}
