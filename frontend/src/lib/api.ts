const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL?.trim() || new URL("../api/v1", document.baseURI).pathname
).replace(/\/$/, "");

// Global logout function - will be set by AuthContext
let globalLogout: (() => void) | null = null;

export const setGlobalLogout = (logoutFn: () => void) => {
  globalLogout = logoutFn;
};

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("token");
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
  if (!res.ok) {
    // First try to get error message from backend
    const err = await res.json().catch(() => ({ message: res.statusText }));
    const backendErrorMsg = typeof err.detail === "string"
      ? err.detail
      : Array.isArray(err.detail)
        ? err.detail
          .map((item: unknown) => {
            if (!item || typeof item !== "object") return String(item);
            const detail = item as { msg?: unknown };
            return typeof detail.msg === "string" ? detail.msg : JSON.stringify(item);
          })
          .filter(Boolean)
          .join("; ")
        : (err.detail ? JSON.stringify(err.detail) : (err.message || null));

    // Handle 401 Unauthorized
    if (res.status === 401) {
      const authRequired = res.headers.get("X-Auth-Required");
      const authExpired = res.headers.get("X-Auth-Expired");

      if (authRequired) {
        // User needs to login, don't auto logout - use backend message if available
        const errorMsg = backendErrorMsg || "Vui lòng đăng nhập để sử dụng tính năng này";
        throw new Error(errorMsg);
      } else if (authExpired && globalLogout) {
        // Token expired, auto logout
        console.warn("Token expired, logging out user automatically");
        globalLogout();
        const errorMsg = backendErrorMsg || "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.";
        throw new Error(errorMsg);
      } else if (globalLogout) {
        // Default 401 behavior
        console.warn("Authentication failed, logging out user automatically");
        globalLogout();
        const errorMsg = backendErrorMsg || "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.";
        throw new Error(errorMsg);
      } else {
        // No globalLogout function available
        const errorMsg = backendErrorMsg || "Vui lòng đăng nhập để sử dụng tính năng này";
        throw new Error(errorMsg);
      }
    }

    // For non-401 errors, use backend message
    const finalErrorMsg = backendErrorMsg || res.statusText;
    const error = new Error(finalErrorMsg) as any;
    error.status = res.status;
    throw error;
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Types based on backend models
interface Token {
  access_token: string;
  token_type: string;
}

export interface EmailVerificationChallenge {
  challenge_id: string;
  email: string;
  expires_in: number;
  message: string;
}

interface UserResponse {
  id: number;
  email: string;
  username: string;
  created_at: string;
  is_active: boolean;
  is_admin?: boolean;
}

interface ProjectsResponse {
  projects: any[];
  total: number;
}

interface SlidesResponse {
  slides: any[];
  total: number;
}

export type ProjectRole = "owner" | "editor" | "viewer";
export interface ProjectCollaborator {
  id?: number | null;
  project_id: number;
  user_id: number;
  email: string;
  name: string;
  role: ProjectRole;
  owner?: boolean;
  created_at?: string;
}
export interface ProjectVersion {
  id: number;
  project_id: number;
  label?: string;
  created_at?: string;
  created_by?: { id?: number; email?: string; name?: string };
  snapshot?: { xml?: string; slides?: any[]; [key: string]: any };
}
export interface ProjectComment {
  id: number;
  project_id: number;
  user_id: number;
  author: { id?: number; email?: string; name?: string };
  body: string;
  slide_index?: number | null;
  element_id?: string | null;
  resolved: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ChatSessionResponse {
  id: string;
  project_id?: number | null;
  title?: string | null;
  history_summary?: string | null;
  max_turns: number;
  created_at: string;
  updated_at: string;
  archived: boolean;
}

export interface ChatMessageResponse {
  id: number;
  session_id: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  standalone_query?: string | null;
  model?: string | null;
  effort?: string | null;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface ChatTurnResponse {
  session: ChatSessionResponse;
  user_message: ChatMessageResponse;
  assistant_message: ChatMessageResponse;
  standalone_query: string;
  citations: Array<Record<string, unknown>>;
  project_id?: number | null;
}

export interface ChatDocumentResponse {
  id: string;
  original_filename: string;
  title?: string | null;
  status: "processing" | "ready" | "failed";
  content_hash: string;
  size_bytes?: number;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatbotConfigResponse {
  default_model: string;
  default_effort: "low" | "medium" | "high";
  models: Array<{ id: string; temperature: number; top_p: number; usage_multiplier: number }>;
  efforts: Array<{ id: "low" | "medium" | "high"; max_tokens: number; temperature_delta: number; usage_multiplier: number }>;
  max_slide_count: number;
  max_upload_bytes: number;
  max_total_upload_bytes: number;
}

export interface ChatSlideGenerationResponse {
  id: string;
  session_id: string;
  phase: "running" | "completed" | "error";
  status: {
    stage?: string;
    title?: string;
    description?: string;
    message?: string;
  };
  progress: number;
  slides: Array<{
    index: number;
    title: string;
    content_path?: string;
    xml_path?: string;
  }>;
  total_slides?: number | null;
  target_slide_count?: number | null;
  project_id?: number | null;
  project_name: string;
  error: string;
}

export interface ChatMessageJobResponse {
  id: string;
  session_id: string;
  phase: "running" | "completed" | "error";
  status: {
    stage?: string;
    title?: string;
    description?: string;
    message?: string;
  };
  query: string;
  model?: string | null;
  effort?: string | null;
  slide_count?: number | null;
  document_ids: string[];
  attachments: Array<{ id: string; name: string; original_filename?: string }>;
  error: string;
}

export interface SubscriptionInfoResponse {
  tier: string;
  is_active: boolean;
  expires_at?: string;
  cancel_at_period_end: boolean;
  usage_limits: {
    chat_messages: number;
    docx_upload: number;
    max_docx_slides: number;
  };
  current_usage: {
    chat_messages?: number;
    chat_message_count?: number;
    idea_generation?: number;
    docx_upload: number;
  };
  usage_window_hours: number;
  usage_window_started_at: string;
  usage_reset_at: string;
  daily_limits?: Record<string, number>;
  usage_reset_date?: string;
}

export interface UserSettingsResponse {
  user_id: number;
  theme: "light" | "dark" | "system";
  language: "vi" | "en";
  notifications_enabled: boolean;
}

export interface AdminUsageWeight {
  id: string;
  percentage: number;
  multiplier: number;
}

export interface AdminPlanLimit {
  chat_credits: number;
  docx_upload: number;
  max_docx_slides: number;
  max_docx_file_mb: number;
  max_docx_total_mb: number;
}

export interface AdminUsageConfigResponse {
  usage_window_hours: number;
  model_weights: AdminUsageWeight[];
  effort_weights: AdminUsageWeight[];
  plan_limits: Record<string, AdminPlanLimit>;
}

export interface AdminUser {
  id: number;
  email: string;
  full_name?: string | null;
  username: string;
  subscription_tier: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  chat_usage: number;
  chat_message_count: number;
  docx_usage: number;
  usage_window_started_at: string;
  usage_reset_at: string;
}
export interface ImageSearchResult {
  url: string;
}
export type OutputFormat = "xml";

// Auth
export const api = {
  // Auth endpoints - match backend /api/auth/*
  login: async (email: string, password: string) => {
    return request<EmailVerificationChallenge>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },

  register: async (fullName: string, email: string, password: string) => {
    await request<UserResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, full_name: fullName, password }),
    });
    return api.login(email, password);
  },

  verifyEmailCode: async (challengeId: string, code: string) => {
    const tokenResponse = await request<Token>("/auth/verify-email-code", {
      method: "POST",
      body: JSON.stringify({ challenge_id: challengeId, code }),
    });
    localStorage.setItem("token", tokenResponse.access_token);
    const user = await request<UserResponse>("/auth/me");
    return { token: tokenResponse.access_token, user };
  },

  resendEmailCode: (challengeId: string) =>
    request<EmailVerificationChallenge>("/auth/resend-email-code", {
      method: "POST",
      body: JSON.stringify({ challenge_id: challengeId }),
    }),

  me: () => request<UserResponse>("/auth/me"),

  // Chatbot endpoints - /api/chat/*
  getChatbotConfig: () => request<ChatbotConfigResponse>("/chat/config"),

  getChatSessions: () => request<ChatSessionResponse[]>("/chat/sessions"),

  createChatSession: (data: { project_id?: number; title?: string }) =>
    request<ChatSessionResponse>("/chat/sessions", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getChatMessages: (sessionId: string) =>
    request<ChatMessageResponse[]>(`/chat/sessions/${encodeURIComponent(sessionId)}/messages`),

  sendChatMessage: (sessionId: string, data: { content: string; model?: string; effort?: string; slide_count?: number; document_ids?: string[] }) =>
    request<ChatTurnResponse>(`/chat/sessions/${encodeURIComponent(sessionId)}/messages`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getActiveChatSlideGeneration: () =>
    request<ChatSlideGenerationResponse | null>("/chat/slide-generations/active"),

  getActiveChatMessageJob: () =>
    request<ChatMessageJobResponse | null>("/chat/message-jobs/active"),

  streamChatMessage: (
    sessionId: string,
    data: { content: string; model?: string; effort?: string; slide_count?: number; document_ids?: string[] },
    signal?: AbortSignal,
  ) => {
    const token = localStorage.getItem("token");
    return fetch(`${API_BASE_URL}/chat/sessions/${encodeURIComponent(sessionId)}/message-stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(data),
      signal,
    });
  },

  reconnectChatMessageJob: (jobId: string, signal?: AbortSignal) => {
    const token = localStorage.getItem("token");
    return fetch(`${API_BASE_URL}/chat/message-jobs/${encodeURIComponent(jobId)}/stream`, {
      method: "GET",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      signal,
    });
  },

  // The slide stream is consumed as SSE by the new chatbot workspace, so it
  // intentionally returns the raw response instead of passing through the
  // JSON request helper.
  streamChatSlideGeneration: (
    sessionId: string,
    data: { content: string; model?: string; effort?: string; slide_count?: number; document_ids?: string[] },
    signal?: AbortSignal,
  ) => {
    const token = localStorage.getItem("token");
    return fetch(`${API_BASE_URL}/chat/sessions/${encodeURIComponent(sessionId)}/slide-stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(data),
      signal,
    });
  },

  reconnectChatSlideGeneration: (generationId: string, signal?: AbortSignal) => {
    const token = localStorage.getItem("token");
    return fetch(`${API_BASE_URL}/chat/slide-generations/${encodeURIComponent(generationId)}/stream`, {
      method: "GET",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      signal,
    });
  },

  uploadChatDocument: (sessionId: string, file: File, signal?: AbortSignal) => {
    const body = new FormData();
    body.append("file", file);
    return request<ChatDocumentResponse>(
      `/chat/sessions/${encodeURIComponent(sessionId)}/documents`,
      { method: "POST", body, signal },
    );
  },

  getChatDocuments: (sessionId: string) =>
    request<ChatDocumentResponse[]>(
      `/chat/sessions/${encodeURIComponent(sessionId)}/documents`,
    ),

  deleteChatDocument: (sessionId: string, documentId: string) =>
    request<void>(
      `/chat/sessions/${encodeURIComponent(sessionId)}/documents/${encodeURIComponent(documentId)}`,
      { method: "DELETE" },
    ),

  archiveChatSession: (sessionId: string) =>
    request<void>(`/chat/sessions/${encodeURIComponent(sessionId)}/archive`, { method: "POST" }),

  googleLoginUrl: () => `${API_BASE_URL}/auth/google/login`,

  logout: () => request<{ message: string }>("/auth/logout", { method: "POST" }),

  changePassword: (currentPassword: string, newPassword: string) =>
    request<{ message: string }>("/auth/change-password", {
      method: "PUT",
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    }),

  // Profile endpoints - /api/profile
  getProfile: () => request<any>("/profile"),

  updateProfile: (profile: { full_name?: string; avatar_url?: string; bio?: string }) =>
    request<{ message: string }>("/profile", {
      method: "PUT",
      body: JSON.stringify(profile),
    }),

  // Settings endpoints - /api/profile/settings
  getSettings: () => request<UserSettingsResponse>("/profile/settings"),

  updateSettings: (settings: any) =>
    request<{ message: string }>("/profile/settings", {
      method: "PUT",
      body: JSON.stringify(settings),
    }),

  // Projects endpoints - /api/projects/*
  getProjects: (limit = 50, offset = 0) =>
    request<ProjectsResponse>(`/projects?limit=${limit}&offset=${offset}`),

  createProject: (data: { title: string; description?: string; source_type?: string; source_data?: any }) =>
    request<{ project_id: number; message: string }>("/projects", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getProject: (id: string | number) => request<any>(`/projects/${id}`),

  updateProject: (id: string | number, data: { title?: string; description?: string; status?: string; slide_count?: number }) =>
    request<{ message: string }>(`/projects/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  // Renamed from renameProject to match backend
  renameProject: (id: string | number, name: string) =>
    request<{ message: string }>(`/projects/${id}`, {
      method: "PUT",
      body: JSON.stringify({ title: name }),
    }),

  deleteProject: (id: string | number) =>
    request<{ message: string }>(`/projects/${id}`, { method: "DELETE" }),

  // Collaboration, project history and review comments
  getProjectCollaborators: (projectId: string | number) =>
    request<{ collaborators: ProjectCollaborator[] }>(`/projects/${projectId}/collaborators`),

  inviteProjectCollaborator: (projectId: string | number, email: string, role: "viewer" | "editor") =>
    request<ProjectCollaborator>(`/projects/${projectId}/collaborators`, {
      method: "POST",
      body: JSON.stringify({ email, role }),
    }),

  updateProjectCollaborator: (projectId: string | number, userId: string | number, role: "viewer" | "editor") =>
    request<ProjectCollaborator>(`/projects/${projectId}/collaborators/${userId}`, {
      method: "PATCH",
      body: JSON.stringify({ role }),
    }),

  removeProjectCollaborator: (projectId: string | number, userId: string | number) =>
    request<{ message: string }>(`/projects/${projectId}/collaborators/${userId}`, { method: "DELETE" }),

  getProjectVersions: (projectId: string | number) =>
    request<{ versions: ProjectVersion[] }>(`/projects/${projectId}/versions`),

  getProjectVersion: (projectId: string | number, versionId: string | number) =>
    request<ProjectVersion>(`/projects/${projectId}/versions/${versionId}`),

  createProjectVersion: (projectId: string | number, data: { snapshot: ProjectVersion["snapshot"]; label?: string }) =>
    request<ProjectVersion>(`/projects/${projectId}/versions`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  restoreProjectVersion: (projectId: string | number, versionId: string | number) =>
    request<{ restored: boolean; version_id: number }>(`/projects/${projectId}/versions/${versionId}/restore`, { method: "POST" }),

  getProjectComments: (projectId: string | number, includeResolved = true) =>
    request<{ comments: ProjectComment[] }>(`/projects/${projectId}/comments?include_resolved=${includeResolved}`),

  createProjectComment: (projectId: string | number, data: { body: string; slide_index?: number; element_id?: string }) =>
    request<ProjectComment>(`/projects/${projectId}/comments`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateProjectComment: (projectId: string | number, commentId: string | number, data: { body?: string; resolved?: boolean }) =>
    request<ProjectComment>(`/projects/${projectId}/comments/${commentId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteProjectComment: (projectId: string | number, commentId: string | number) =>
    request<{ message: string }>(`/projects/${projectId}/comments/${commentId}`, { method: "DELETE" }),

  // Upload endpoints - /api/generate/docx*
  uploadDocx: (file: File, options: { outputFormat?: OutputFormat } = {}) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("output_format", options.outputFormat ?? "xml");
    return request<any>("/generate/docx", { method: "POST", body: formData });
  },

  // Upload for streaming workflow
  uploadDocxForStream: (file: File, options: {
    workflow_mode?: string;
    outputFormat?: OutputFormat;
  } = {}) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("workflow_mode", options.workflow_mode ?? "auto_no_heading");
    formData.append("output_format", options.outputFormat ?? "xml");
    return request<{ filename: string }>("/generate/docx/prepare-stream", { method: "POST", body: formData });
  },

  // Upload for manual structure editing workflow
  uploadDocxForManual: (file: File, options: { outputFormat?: OutputFormat } = {}) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("output_format", options.outputFormat ?? "xml");
    return request<{
      success: boolean;
      session_id: string;
      document_title: string;
      output_format?: OutputFormat;
    }>("/generate/docx/manual-session", { method: "POST", body: formData });
  },

  // Structure Editor endpoints - /api/structure/*
  getStructure: (sessionId: string) =>
    request<{
      document_title: string;
      document_text: string;
      document_structure: any[];
      can_edit: boolean;
      output_format?: OutputFormat;
    }>(`/structure/current?session_id=${sessionId}`),

  updateStructure: (sessionId: string, documentStructure: any[], introSlide?: any, outputFormat: OutputFormat = "xml") =>
    request<{ success: boolean }>("/structure/update", {
      method: "PUT",
      body: JSON.stringify({
        session_id: sessionId,
        document_structure: documentStructure,
        intro_slide: introSlide,
        output_format: outputFormat,
      }),
    }),

  approveStructure: (sessionId: string, outputFormat: OutputFormat = "xml") =>
    request<{
      success: boolean;
      session_id: string;
      document_title: string;
      document_outline: any[];
      slide_chunks: any[];
      slide_positions: any[];
      slide_context_maps: string[];
      slide_types: string[];
      output_format?: OutputFormat;
    }>("/structure/approve", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, output_format: outputFormat }),
    }),

  // Markdown Parser endpoints - /api/generate/markdown/*
  parseMarkdown: (data: { markdown: string; default_title?: string }) =>
    request<{
      success: boolean;
      document_title: string;
      structure: any[];
      validation_warnings: string[];
      node_count: number;
    }>("/generate/markdown/parse", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Slides endpoints - /api/projects/{project_id}/slides and /api/slides/{slide_id}
  getSlides: (projectId: string | number, limit?: number) =>
    request<SlidesResponse>(`/projects/${projectId}/slides${limit ? `?limit=${limit}` : ''}`),

  getSlidesByProjectName: (projectName: string) =>
    request<{ project_name: string; project_id: number; slides: any[]; count: number }>(
      `/projects/by-name/${encodeURIComponent(projectName)}/slides`
    ),

  createSlide: (projectId: string | number, data: {
    slide_index?: number;
    slide_type?: string;
    title?: string;
    content_text?: string;
    html_content?: string;
    design_settings?: any;
  }) =>
    request<{ id?: number; project_id?: number; message: string }>(`/projects/${projectId}/slides`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getSlide: (slideId: string | number) => request<any>(`/slides/${slideId}`),

  updateSlide: (slideId: string | number, data: {
    title?: string;
    slide_index?: number;
    content_text?: string;
    html_content?: string;
    design_settings?: any;
  }) =>
    request<{ message: string }>(`/slides/${slideId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  deleteSlide: (slideId: string | number) =>
    request<{ message: string }>(`/slides/${slideId}`, { method: "DELETE" }),

  exportXmlToPptx: (xmlContent: string, fileName: string = "presentation") =>
    request<{
      success: boolean;
      download_url?: string;
      filename?: string;
      message: string;
      error?: string;
    }>("/export/xml-pptx", {
      method: "POST",
      body: JSON.stringify({ xml_content: xmlContent, file_name: fileName }),
    }),

  // Capture/Export endpoints - /api/capture/* and /api/export/*
  captureSlidesBatch: (slides: Array<{ html_content: string; slide_name?: string }>) =>
    request<{ success: boolean; download_url?: string; message: string }>("/capture/capture-slides-batch", {
      method: "POST",
      body: JSON.stringify({ slides }),
    }),

  exportSlidePdf: (htmlContent: string, slideName: string = "slide") =>
    request<{ success: boolean; download_url?: string; message: string }>("/export/slide-pdf", {
      method: "POST",
      body: JSON.stringify({ html_content: htmlContent, slide_name: slideName }),
    }),

  exportSlidesPdf: (slides: Array<{ html_content: string; slide_name?: string }>) =>
    request<{ success: boolean; download_url?: string; filename?: string; message: string; error?: string }>("/export/slides-pdf", {
      method: "POST",
      body: JSON.stringify({ slides }),
    }),

  // Download URLs
  downloadCaptureUrl: (filename: string) =>
    `${API_BASE_URL}/capture/download-capture/${encodeURIComponent(filename)}`,

  // Health check endpoints
  health: () => request<{ status: string; services: any }>("/health"),

  // Temp file serving - /api/temp/*
  getTempFileUrl: (path: string) =>
    `${API_BASE_URL}/temp/file?path=${encodeURIComponent(path)}`,

  // Cleanup temp directory
  cleanupTemp: (tempDir: string) =>
    request<{ success: boolean }>("/temp/cleanup", {
      method: "POST",
      body: JSON.stringify({ temp_dir: tempDir }),
    }),

  // SSE streaming URLs - requires token in query param for EventSource
  streamUrl: (filename: string) => {
    const token = localStorage.getItem("token");
    return `${API_BASE_URL}/generate/docx/stream?filename=${encodeURIComponent(filename)}&token=${encodeURIComponent(token || "")}`;
  },

  // SSE streaming for manual structure workflow
  manualStreamUrl: (sessionId: string) => {
    const token = localStorage.getItem("token");
    return `${API_BASE_URL}/generate/manual/stream?session_id=${encodeURIComponent(sessionId)}&token=${encodeURIComponent(token || "")}`;
  },

  // Image URL - /api/image-serve/*
  imageUrl: (imageName: string) => `${API_BASE_URL}/image-serve/${encodeURIComponent(imageName)}`,

  imageProxyUrl: (imageUrl: string) => `${API_BASE_URL}/image-serve/remote-proxy?url=${encodeURIComponent(imageUrl)}`,

  searchImages: (
    query: string,
    options: { layout?: "Wide" | "Tall" | "Square"; size?: "Large" | "Medium" | "Small"; maxResults?: number } = {},
  ) => {
    const params = new URLSearchParams({ query });
    if (options.layout) params.set("layout", options.layout);
    if (options.size) params.set("size", options.size);
    if (options.maxResults) params.set("max_results", String(options.maxResults));
    return request<{ query: string; images: ImageSearchResult[] }>(`/image-search?${params.toString()}`);
  },

  // Subscription endpoints - /api/subscription/*
  getSubscriptionInfo: () => request<SubscriptionInfoResponse>("/subscription/info"),

  redeemCode: (code: string) => request<{
    success: boolean;
    message: string;
    new_tier: string;
    expires_at?: string;
  }>("/subscription/redeem", {
    method: "POST",
    body: JSON.stringify({ code })
  }),

  getPricingInfo: () => request<{
    tiers: Array<{
      name: string;
      display_name: string;
      price: number;
      currency: string;
      period: string;
      features: Record<string, any>;
    }>;
  }>("/subscription/pricing"),

  getAdminUsageConfig: () => request<AdminUsageConfigResponse>("/admin/usage/config"),

  updateAdminUsageConfig: (data: {
    model_percentages: Record<string, number>;
    effort_percentages: Record<string, number>;
    plan_limits: Record<string, AdminPlanLimit>;
  }) =>
    request<AdminUsageConfigResponse>("/admin/usage/config", {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  resetAllUsage: () => request<{ reset_users: number; usage_window_hours: number }>("/admin/usage/reset", {
    method: "POST",
  }),

  getAdminUsers: () => request<AdminUser[]>("/admin/users"),

  updateAdminRole: (userId: number, isAdmin: boolean) =>
    request<AdminUser>(`/admin/users/${userId}/admin`, {
      method: "PATCH",
      body: JSON.stringify({ is_admin: isAdmin }),
    }),

  resetAdminUserPassword: (userId: number, password: string) =>
    request<{ user_id: number; message: string }>(`/admin/users/${userId}/password-reset`, {
      method: "POST",
      body: JSON.stringify({ password }),
    }),

  resetAdminUserUsage: (userId: number) =>
    request<AdminUser>(`/admin/users/${userId}/usage-reset`, {
      method: "POST",
    }),

  upgradeSubscription: (tier: string) => request<{ message: string }>("/subscription/upgrade", {
    method: "POST",
    body: JSON.stringify({ tier })
  }),

  cancelSubscription: (immediate: boolean) => request<{ success: boolean; immediate: boolean; expires_at?: string }>(
    `/subscription/cancel?immediate=${immediate}`,
    { method: "POST" }
  )
};
