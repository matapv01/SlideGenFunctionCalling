const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL?.trim() || "http://localhost:12008/api/v1"
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
    console.log(`API Error for ${endpoint}:`, {
      status: res.status,
      statusText: res.statusText,
      headers: Object.fromEntries(res.headers.entries())
    });

    // First try to get error message from backend
    const err = await res.json().catch(() => ({ message: res.statusText }));
    const backendErrorMsg = typeof err.detail === 'string'
      ? err.detail
      : (err.detail ? JSON.stringify(err.detail) : (err.message || null));

    console.log('Backend error message:', backendErrorMsg);

    // Handle 401 Unauthorized
    if (res.status === 401) {
      const authRequired = res.headers.get("X-Auth-Required");
      const authExpired = res.headers.get("X-Auth-Expired");

      console.log('Auth headers:', { authRequired, authExpired });

      if (authRequired) {
        // User needs to login, don't auto logout - use backend message if available
        const errorMsg = backendErrorMsg || "Vui lòng đăng nhập để sử dụng tính năng này";
        console.log('Throwing auth required error:', errorMsg);
        throw new Error(errorMsg);
      } else if (authExpired && globalLogout) {
        // Token expired, auto logout
        console.warn("Token expired, logging out user automatically");
        globalLogout();
        const errorMsg = backendErrorMsg || "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.";
        console.log('Throwing token expired error:', errorMsg);
        throw new Error(errorMsg);
      } else if (globalLogout) {
        // Default 401 behavior
        console.warn("Authentication failed, logging out user automatically");
        globalLogout();
        const errorMsg = backendErrorMsg || "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.";
        console.log('Throwing generic auth error:', errorMsg);
        throw new Error(errorMsg);
      } else {
        // No globalLogout function available
        const errorMsg = backendErrorMsg || "Vui lòng đăng nhập để sử dụng tính năng này";
        console.log('Throwing no-logout auth error:', errorMsg);
        throw new Error(errorMsg);
      }
    }

    // For non-401 errors, use backend message
    const finalErrorMsg = backendErrorMsg || res.statusText;
    console.log('Throwing non-401 error:', finalErrorMsg);
    const error = new Error(finalErrorMsg) as any;
    error.status = res.status;
    throw error;
  }
  return res.json();
}

// Types based on backend models
interface Token {
  access_token: string;
  token_type: string;
}

interface UserResponse {
  id: number;
  email: string;
  username: string;
  created_at: string;
  is_active: boolean;
}

interface ProjectsResponse {
  projects: any[];
  total: number;
}

interface SlidesResponse {
  slides: any[];
  total: number;
}

// Auth
export const api = {
  // Auth endpoints - match backend /api/auth/*
  login: async (email: string, password: string) => {
    const tokenResponse = await request<Token>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    // Store token and fetch user info
    localStorage.setItem("token", tokenResponse.access_token);
    const user = await request<UserResponse>("/auth/me");
    return { token: tokenResponse.access_token, user };
  },

  register: async (fullName: string, email: string, password: string) => {
    // Register returns UserResponse (no token), need to login after
    await request<UserResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, full_name: fullName, password }),
    });
    // Auto-login after registration
    return api.login(email, password);
  },

  me: () => request<UserResponse>("/auth/me"),

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
  getSettings: () => request<any>("/profile/settings"),

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

  updateProject: (id: string | number, data: { title?: string; description?: string; status?: string }) =>
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

  // Upload endpoints - /api/generate/docx*
  uploadDocx: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<any>("/generate/docx", { method: "POST", body: formData });
  },

  // Upload for streaming workflow
  uploadDocxForStream: (file: File, options: {
    enable_transition_slides?: boolean;
    enable_thank_you_slide?: boolean;
  } = {}) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("enable_transition_slides", String(options.enable_transition_slides ?? true));
    formData.append("enable_thank_you_slide", String(options.enable_thank_you_slide ?? true));
    return request<{ filename: string }>("/generate/docx/prepare-stream", { method: "POST", body: formData });
  },

  // Upload for manual structure editing workflow
  uploadDocxForManual: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<{
      success: boolean;
      session_id: string;
      document_title: string;
    }>("/generate/docx/manual-session", { method: "POST", body: formData });
  },

  // Structure Editor endpoints - /api/structure/*
  getStructure: (sessionId: string) =>
    request<{
      document_title: string;
      document_text: string;
      document_structure: any[];
      can_edit: boolean;
    }>(`/structure/current?session_id=${sessionId}`),

  updateStructure: (sessionId: string, documentStructure: any[], introSlide?: any) =>
    request<{ success: boolean }>("/structure/update", {
      method: "PUT",
      body: JSON.stringify({
        session_id: sessionId,
        document_structure: documentStructure,
        intro_slide: introSlide,
      }),
    }),

  approveStructure: (sessionId: string) =>
    request<{
      success: boolean;
      message: string;
      session_id: string;
      document_title: string;
      document_outline: any[];
      slide_chunks: any[];
      slide_positions: any[];
      slide_context_maps: string[];
      slide_types: string[];
    }>("/structure/approve", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId }),
    }),

  createTestSession: () =>
    request<{ success: boolean; session_id: string; redirect_url: string }>("/structure/test-session", {
      method: "POST",
    }),

  // Slides endpoints - /api/projects/{project_id}/slides and /api/slides/{slide_id}
  getSlides: (projectId: string | number) =>
    request<SlidesResponse>(`/projects/${projectId}/slides`),

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
    request<{ id: number; message: string }>(`/projects/${projectId}/slides`, {
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

  // Conversion endpoints - /api/convert/*
  convertSlides: (projectName: string) =>
    request<{ success: boolean; conversion_result: any; message: string }>("/convert/", {
      method: "POST",
      body: JSON.stringify({ project_name: projectName }),
    }),

  getConversionStatus: (projectName: string) =>
    request<{ project_name: string; status: any; has_converted: boolean }>(
      `/convert/status/${encodeURIComponent(projectName)}`
    ),

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
    request<{ success: boolean; download_url?: string; message: string }>("/export/slides-pdf", {
      method: "POST",
      body: JSON.stringify({ slides }),
    }),

  // Download URLs
  downloadCaptureUrl: (filename: string) =>
    `${API_BASE_URL}/capture/download-capture/${encodeURIComponent(filename)}`,

  // Health check endpoints
  health: () => request<{ status: string; services: any }>("/health"),

  converterHealth: () => request<{ healthy: boolean; message: string; details?: any }>("/convert/health"),

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

  // SSE streaming for idea workflow
  ideaStreamUrl: (sessionId: string) => {
    const token = localStorage.getItem("token");
    return `${API_BASE_URL}/generate/idea/stream?session_id=${encodeURIComponent(sessionId)}&token=${encodeURIComponent(token || "")}`;
  },

  // Generate idea structure
  generateIdeaStructure: (data: {
    title?: string;
    prompt: string;
    content_length?: string;
    enable_transition_slides?: boolean;
    enable_thank_you_slide?: boolean;
  }) =>
    request<{
      session_id: string;
      filename: string;
      slide_count: number;
      is_from_idea: boolean;
    }>("/generate/idea/structure", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Get idea structure details
  getIdeaStructure: (sessionId: string) =>
    request<{
      session_id: string;
      title: string;
      slide_chunks: any[];
      enable_transition_slides: boolean;
      enable_thank_you_slide: boolean;
      metadata?: any;
    }>(`/generate/idea/structure/${encodeURIComponent(sessionId)}`),

  // Update idea structure
  updateIdeaStructure: (sessionId: string, data: {
    title: string;
    slide_chunks: any[];
    enable_transition_slides: boolean;
    enable_thank_you_slide: boolean;
  }) =>
    request<{
      session_id: string;
      title: string;
      slide_chunks: any[];
      enable_transition_slides: boolean;
      enable_thank_you_slide: boolean;
      metadata?: any;
    }>(`/generate/idea/structure/${encodeURIComponent(sessionId)}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  // Image URL - /api/image-serve/*
  imageUrl: (imageName: string) => `${API_BASE_URL}/image-serve/${encodeURIComponent(imageName)}`,

  // Subscription endpoints - /api/subscription/*
  getSubscriptionInfo: () => request<{
    tier: string;
    is_active: boolean;
    expires_at?: string;
    daily_limits: {
      idea_generation: number;
      docx_upload: number;
      max_docx_slides: number;
    };
    current_usage: {
      idea_generation: number;
      docx_upload: number;
    };
    usage_reset_date: string;
  }>("/subscription/info"),

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

  upgradeSubscription: (tier: string) => request<{ message: string }>("/subscription/upgrade", {
    method: "POST",
    body: JSON.stringify({ tier })
  }),

  cancelSubscription: (immediate: boolean) => request<{ success: boolean; immediate: boolean; expires_at?: string }>(
    `/subscription/cancel?immediate=${immediate}`,
    { method: "POST" }
  )
};
