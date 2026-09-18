import {
  api,
  ChatbotConfigResponse,
  ChatMessageResponse,
  ChatSessionResponse,
  ChatDocumentResponse,
  ChatSlideGenerationResponse,
} from "@/lib/api";

export interface WorkspaceProject {
  id: string | number;
  title?: string;
  name?: string;
  slide_count?: number;
  updated_at?: string;
}

export interface WorkspaceSnapshot {
  projects: WorkspaceProject[];
  total: number;
}

export type ChatSession = ChatSessionResponse;
export type ChatMessage = ChatMessageResponse;
export type ChatbotConfig = ChatbotConfigResponse;
export type ChatDocument = ChatDocumentResponse;
export type ChatSlideGeneration = ChatSlideGenerationResponse;

/**
 * Boundary between the new Slidegenius UI and the existing backend client.
 * Keep backend response mapping here so the new UI never depends on legacy
 * page components or their presentation data shape.
 */
export async function loadWorkspaceSnapshot(limit = 3): Promise<WorkspaceSnapshot> {
  const response = await api.getProjects(limit, 0);
  return {
    projects: response.projects as WorkspaceProject[],
    total: response.total,
  };
}

export function renameWorkspaceProject(id: string | number, title: string) {
  return api.renameProject(id, title);
}

export function deleteWorkspaceProject(id: string | number) {
  return api.deleteProject(id);
}

export function loadWorkspaceProject(id: string | number) {
  return api.getProject(id);
}

export function loadChatbotConfig() {
  return api.getChatbotConfig();
}

export function loadActiveChatSlideGeneration() {
  return api.getActiveChatSlideGeneration();
}

export function loadChatSessions() {
  return api.getChatSessions();
}

export function createChatSession(title?: string) {
  return api.createChatSession({ title });
}

export function loadChatMessages(sessionId: string) {
  return api.getChatMessages(sessionId);
}

export function sendChatMessage(
  sessionId: string,
  content: string,
  model: string,
  effort: string,
  slideCount?: number,
  documentIds: string[] = [],
) {
  return api.sendChatMessage(sessionId, {
    content,
    model,
    effort,
    ...(slideCount ? { slide_count: slideCount } : {}),
    ...(documentIds.length ? { document_ids: documentIds } : {}),
  });
}

export interface ChatSlideStreamEvent {
  type: string;
  data: Record<string, unknown>;
}

export type ChatSlideStreamEventHandler = (event: ChatSlideStreamEvent) => void | Promise<void>;

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function streamErrorMessage(value: unknown, fallback: string) {
  if (!isRecord(value)) return fallback;
  if (typeof value.detail === "string" && value.detail.trim()) return value.detail;
  if (typeof value.message === "string" && value.message.trim()) return value.message;
  return fallback;
}

async function consumeChatSlideGenerationStream(
  response: Response,
  onEvent: ChatSlideStreamEventHandler,
) {
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(streamErrorMessage(payload, "Không thể bắt đầu tạo slide."));
  }
  if (!response.body) throw new Error("Luồng tạo slide không khả dụng.");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  const dispatchBlock = async (block: string) => {
    let eventType = "message";
    const dataLines: string[] = [];
    for (const line of block.split(/\r?\n/)) {
      if (line.startsWith("event:")) {
        eventType = line.slice("event:".length).trim() || "message";
      } else if (line.startsWith("data:")) {
        dataLines.push(line.slice("data:".length).trimStart());
      }
    }
    if (!dataLines.length) return;
    let parsed: unknown;
    try {
      parsed = JSON.parse(dataLines.join("\n"));
    } catch {
      throw new Error("Phản hồi streaming của server không hợp lệ.");
    }
    await onEvent({
      type: eventType,
      data: isRecord(parsed) ? parsed : { value: parsed },
    });
  };

  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
    const blocks = buffer.split(/\r?\n\r?\n/);
    buffer = blocks.pop() || "";
    for (const block of blocks) {
      await dispatchBlock(block);
    }
    if (done) break;
  }
  if (buffer.trim()) await dispatchBlock(buffer);
}

/** Consume the POST-backed SSE stream used by the chatbot slide workflow. */
export async function streamChatSlideGeneration(
  sessionId: string,
  content: string,
  model: string,
  effort: string,
  slideCount: number | undefined,
  onEvent: ChatSlideStreamEventHandler,
  signal?: AbortSignal,
  documentIds: string[] = [],
) {
  const response = await api.streamChatSlideGeneration(
    sessionId,
    {
      content,
      model,
      effort,
      ...(slideCount ? { slide_count: slideCount } : {}),
      ...(documentIds.length ? { document_ids: documentIds } : {}),
    },
    signal,
  );
  return consumeChatSlideGenerationStream(response, onEvent);
}

/** Reconnect to an already-running job after a browser reload. */
export async function streamChatSlideGenerationJob(
  generationId: string,
  onEvent: ChatSlideStreamEventHandler,
  signal?: AbortSignal,
) {
  const response = await api.reconnectChatSlideGeneration(generationId, signal);
  return consumeChatSlideGenerationStream(response, onEvent);
}

/** Consume the existing manual workflow through the shared slide-stream UI. */
export async function streamManualSlideGeneration(
  sessionId: string,
  onEvent: ChatSlideStreamEventHandler,
  signal?: AbortSignal,
) {
  const token = localStorage.getItem("token");
  const response = await fetch(api.manualStreamUrl(sessionId), {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    signal,
  });
  return consumeChatSlideGenerationStream(response, onEvent);
}

export async function loadChatSlideContent(path: string) {
  const token = localStorage.getItem("token");
  const response = await fetch(api.getTempFileUrl(path), {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) throw new Error("Không thể tải preview slide.");
  return response.text();
}

export function uploadChatDocument(sessionId: string, file: File) {
  return api.uploadChatDocument(sessionId, file);
}

export function loadChatDocuments(sessionId: string) {
  return api.getChatDocuments(sessionId);
}

export function deleteChatDocument(sessionId: string, documentId: string) {
  return api.deleteChatDocument(sessionId, documentId);
}

export function archiveChatSession(sessionId: string) {
  return api.archiveChatSession(sessionId);
}
