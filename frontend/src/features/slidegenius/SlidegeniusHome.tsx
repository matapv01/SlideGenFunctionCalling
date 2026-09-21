import { useCallback, useEffect, useState, type FormEvent, type MouseEvent } from "react";
import { useNavigate } from "react-router-dom";
import { FilePenLine } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { api, type SubscriptionInfoResponse } from "@/lib/api";
import { deleteWorkspaceProject, loadWorkspaceSnapshot, renameWorkspaceProject, WorkspaceProject } from "./data/workspaceApi";
import SlidegeniusChat from "./SlidegeniusChat";
import SlidegeniusSettings from "./SlidegeniusSettings";
import SlidegeniusWorkspaceShell, { workspacePlanLabel } from "./SlidegeniusWorkspaceShell";
import SlidegeniusManual from "./SlidegeniusManual";
import { ProjectSlidePreview } from "@/components/ProjectSlidePreview";
import { resolveSlideBackground } from "@/lib/slideBackground";
import { PROJECT_NAME_MAX_LENGTH, projectNameForInput, truncateProjectName } from "./projectName";
import SlidegenConfirmDialog from "@/components/SlidegenConfirmDialog";

type Tab = "slidegenius" | "projects" | "manual" | "guide" | "settings" | "subscription";

interface PricingTier {
  name: string;
  display_name: string;
  price: number;
  currency: string;
  period: string;
  features: Record<string, unknown>;
}

interface ProjectPreviewSlide {
  id?: string | number;
  title?: string;
  html_content?: string;
  content?: string;
  html?: string;
  design_settings?: unknown;
}

const copy = {
  en: {
    tabs: { slidegenius: "Slidegenius", projects: "Project Manager", manual: "Manual", guide: "Guide", settings: "Settings" },
    projectsTitle: "Your projects", projectsSub: "Keep every idea moving forward.", newProject: "New project", loading: "Loading projects...", emptyTitle: "No projects yet", emptyDescription: "Create your first deck in Slidegenius and it will appear here.", createFirstProject: "Create your first project", deleteProject: "Delete project", renameProject: "Rename project", saveProjectName: "Save project name", cancelRename: "Cancel rename", projectNamePlaceholder: "Project name", projectRenamed: "Project renamed.", projectRenameFailed: "Unable to rename project.", invalidProjectName: "Enter a project name.", deleteProjectConfirm: "The slides will be permanently removed, while the generation record will remain in chat.", deleteProjectTitle: "Delete this project?", projectDeleted: "Project deleted.", projectDeleteFailed: "Unable to delete project.", cancelPlanTitle: "Cancel this plan?", cancelPlanConfirm: "Your workspace will return to the Free plan. Existing projects will remain available.", confirm: "Confirm", cancel: "Cancel",
    guideTitle: "A faster way to make better work.", guideSub: "Start with a thought. Slidegenius helps you turn it into a clear, compelling direction.",
    settingsTitle: "Workspace settings", settingsSub: "Shape your Slidegen experience.", language: "Language", theme: "Theme", dark: "Dark canvas", notifications: "Notifications", save: "Save changes",
    collapse: "Collapse sidebar", expand: "Expand sidebar", openSettings: "Open settings", upgrade: "Upgrade", currentPlan: "CURRENT PLAN", free: "Free plan", help: "Need a hand?",
    subscriptionTitle: "Make room for better work.", subscriptionSub: "Start free, then scale when the work calls for it.", currentFree: "CURRENT PLAN / FREE", choose: "Use upgrade code", loadingPlan: "Loading plan...", planUnavailable: "Plan information is temporarily unavailable.", retry: "Try again", active: "Active", expired: "Expired", noExpiry: "No expiration", usage: "5-HOUR USAGE", chatUsage: "Chat credits", uploads: "File usage", slideLimit: "Slide limit", resetUsage: "Resets every 5 hours", currentUsage: "Current usage", redeemCode: "Redeem upgrade code", codePlaceholder: "Enter your upgrade code", redeem: "Redeem", cancelPlan: "Cancel plan", cancelConfirm: "Cancel this plan now?", current: "Current", updated: "Updated",
  },
  vi: {
    tabs: { slidegenius: "Slidegenius", projects: "Quản lý dự án", manual: "Manual", guide: "Hướng dẫn", settings: "Cài đặt" },
    projectsTitle: "Dự án của bạn", projectsSub: "Giữ mọi ý tưởng luôn tiến về phía trước.", newProject: "Dự án mới", loading: "Đang tải dự án...", emptyTitle: "Bạn chưa có project nào", emptyDescription: "Hãy bắt đầu tạo bộ slide đầu tiên trong Slidegenius. Project của bạn sẽ xuất hiện ở đây.", createFirstProject: "Tạo project đầu tiên", deleteProject: "Xóa project", renameProject: "Đổi tên project", saveProjectName: "Lưu tên project", cancelRename: "Hủy đổi tên", projectNamePlaceholder: "Tên project", projectRenamed: "Đã đổi tên project.", projectRenameFailed: "Không thể đổi tên project.", invalidProjectName: "Vui lòng nhập tên project.", deleteProjectConfirm: "Toàn bộ slide sẽ bị xóa vĩnh viễn, còn lịch sử tạo vẫn được giữ trong chatbot.", deleteProjectTitle: "Xóa project này?", projectDeleted: "Đã xóa project.", projectDeleteFailed: "Không thể xóa project.", cancelPlanTitle: "Hủy gói này?", cancelPlanConfirm: "Workspace sẽ chuyển về gói Free. Các project hiện có vẫn được giữ nguyên.", confirm: "Xác nhận", cancel: "Hủy",
    guideTitle: "Cách nhanh hơn để tạo ra điều tốt hơn.", guideSub: "Bắt đầu từ một suy nghĩ. Slidegenius giúp bạn biến nó thành một hướng đi rõ ràng và thuyết phục.",
    settingsTitle: "Cài đặt không gian", settingsSub: "Định hình trải nghiệm Slidegenius của bạn.", language: "Ngôn ngữ", theme: "Giao diện", dark: "Nền tối", notifications: "Thông báo", save: "Lưu thay đổi",
    collapse: "Thu gọn thanh bên", expand: "Mở rộng thanh bên", openSettings: "Mở cài đặt", upgrade: "Nâng cấp", currentPlan: "GÓI HIỆN TẠI", free: "Gói miễn phí", help: "Cần trợ giúp?",
    subscriptionTitle: "Mở rộng không gian cho công việc tốt hơn.", subscriptionSub: "Bắt đầu miễn phí, nâng cấp khi công việc cần thêm sức mạnh.", currentFree: "GÓI HIỆN TẠI / FREE", choose: "Dùng mã nâng cấp", loadingPlan: "Đang tải gói...", planUnavailable: "Tạm thời không thể tải thông tin gói.", retry: "Thử lại", active: "Đang hoạt động", expired: "Đã hết hạn", noExpiry: "Không giới hạn thời gian", usage: "SỬ DỤNG 5 GIỜ", chatUsage: "Chat credit", uploads: "File đã tải", slideLimit: "Giới hạn slide", resetUsage: "Reset sau mỗi 5 giờ", currentUsage: "Đang sử dụng", redeemCode: "Nhập mã nâng cấp", codePlaceholder: "Nhập mã nâng cấp", redeem: "Kích hoạt", cancelPlan: "Hủy gói", cancelConfirm: "Hủy gói này ngay bây giờ?", current: "Đang dùng", updated: "Cập nhật",
  },
} as const;

function projectTitle(project: WorkspaceProject) {
  return project.title || project.name || "Untitled project";
}

function projectUpdated(value: string | undefined, language: "vi" | "en") {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat(language === "vi" ? "vi-VN" : "en-US", { day: "2-digit", month: "short" }).format(date);
}

function formatPlanDate(value: string | undefined, language: "vi" | "en") {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat(language === "vi" ? "vi-VN" : "en-US", { day: "2-digit", month: "short", year: "numeric" }).format(date);
}

function formatPlanLimit(value: number | undefined, language: "vi" | "en") {
  if (value === -1) return language === "vi" ? "Không giới hạn" : "Unlimited";
  return String(value ?? "—");
}

function usagePercent(used: number | undefined, limit: number | undefined) {
  if (!limit || limit < 0) return 0;
  return Math.min(100, Math.round(((used || 0) / limit) * 100));
}

function formatUsageAmount(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(2).replace(/0+$/, "").replace(/\.$/, "");
}

function planFeature(tier: PricingTier, key: string, fallback = "") {
  return String(tier.features[key] ?? tier.features[fallback] ?? "");
}

export default function SlidegeniusHome({ initialTab = "slidegenius" }: { initialTab?: Tab }) {
  const navigate = useNavigate();
  const { language } = useLanguage();
  const t = copy[language];
  const [tab, setTab] = useState<Tab>(initialTab);
  const [projects, setProjects] = useState<WorkspaceProject[]>([]);
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [projectsError, setProjectsError] = useState(false);
  const [projectActionMessage, setProjectActionMessage] = useState("");
  const [deletingProjectId, setDeletingProjectId] = useState<string | number | null>(null);
  const [renamingProjectId, setRenamingProjectId] = useState<string | number | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const [renamingProject, setRenamingProject] = useState(false);
  const [projectPreviews, setProjectPreviews] = useState<Record<string, ProjectPreviewSlide | null>>({});
  const [subscriptionInfo, setSubscriptionInfo] = useState<SubscriptionInfoResponse | null>(null);
  const [pricingTiers, setPricingTiers] = useState<PricingTier[]>([]);
  const [subscriptionLoading, setSubscriptionLoading] = useState(true);
  const [subscriptionError, setSubscriptionError] = useState(false);
  const [redeemCode, setRedeemCode] = useState("");
  const [redeemingCode, setRedeemingCode] = useState(false);
  const [subscriptionMessage, setSubscriptionMessage] = useState("");
  const [confirmation, setConfirmation] = useState<"cancel-plan" | "delete-project" | null>(null);
  const [pendingDeleteProject, setPendingDeleteProject] = useState<WorkspaceProject | null>(null);
  // /home, /projects, /manual, /guide, /settings and /subscription reuse this
  // component. Sync the visible panel when React Router changes the route
  // without remounting the component.
  useEffect(() => {
    setTab(initialTab);
  }, [initialTab]);

  const loadSubscription = useCallback(async () => {
    setSubscriptionLoading(true);
    setSubscriptionError(false);
    try {
      const [info, pricing] = await Promise.all([api.getSubscriptionInfo(), api.getPricingInfo()]);
      setSubscriptionInfo(info);
      setPricingTiers(pricing.tiers);
    } catch {
      setSubscriptionError(true);
    } finally {
      setSubscriptionLoading(false);
    }
  }, []);

  useEffect(() => {
    let active = true;
    loadWorkspaceSnapshot(50).then((snapshot) => {
      if (active) setProjects(snapshot.projects);
    }).catch(() => {
      if (active) setProjectsError(true);
    }).finally(() => {
      if (active) setProjectsLoading(false);
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    let active = true;
    if (!projects.length) {
      setProjectPreviews({});
      return () => { active = false; };
    }
    Promise.all(projects.map(async (project) => {
      try {
        const response = await api.getSlides(project.id, 1);
        return [String(project.id), (response.slides?.[0] as ProjectPreviewSlide | undefined) ?? null] as const;
      } catch {
        return [String(project.id), null] as const;
      }
    })).then((entries) => {
      if (active) setProjectPreviews(Object.fromEntries(entries));
    });
    return () => { active = false; };
  }, [projects]);

  useEffect(() => {
    void loadSubscription();
  }, [loadSubscription]);

  const handleRedeemCode = async () => {
    if (!redeemCode.trim()) return;
    setRedeemingCode(true);
    setSubscriptionMessage("");
    try {
      const result = await api.redeemCode(redeemCode.trim());
      setRedeemCode("");
      setSubscriptionMessage(result.message);
      await loadSubscription();
    } catch (error) {
      setSubscriptionMessage(error instanceof Error ? error.message : (language === "vi" ? "Không thể kích hoạt mã." : "Unable to redeem this code."));
    } finally {
      setRedeemingCode(false);
    }
  };

  const handleCancelPlan = () => {
    setConfirmation("cancel-plan");
  };

  const confirmCancelPlan = async () => {
    setConfirmation(null);
    setSubscriptionMessage("");
    try {
      await api.cancelSubscription(true);
      setSubscriptionMessage(language === "vi" ? "Đã chuyển về gói miễn phí." : "Your plan is now Free.");
      await loadSubscription();
    } catch (error) {
      setSubscriptionMessage(error instanceof Error ? error.message : (language === "vi" ? "Không thể hủy gói." : "Unable to cancel this plan."));
    }
  };

  const handleDeleteProject = (
    event: MouseEvent<HTMLButtonElement>,
    project: WorkspaceProject,
  ) => {
    event.stopPropagation();
    if (deletingProjectId !== null) return;
    setPendingDeleteProject(project);
    setConfirmation("delete-project");
  };

  const confirmDeleteProject = async () => {
    const project = pendingDeleteProject;
    setConfirmation(null);
    setPendingDeleteProject(null);
    if (!project) return;
    setDeletingProjectId(project.id);
    setProjectActionMessage("");
    try {
      await deleteWorkspaceProject(project.id);
      setProjects((current) => current.filter((item) => String(item.id) !== String(project.id)));
      setProjectPreviews((current) => {
        const next = { ...current };
        delete next[String(project.id)];
        return next;
      });
      setProjectActionMessage(t.projectDeleted);
    } catch (error) {
      setProjectActionMessage(error instanceof Error ? error.message : t.projectDeleteFailed);
    } finally {
      setDeletingProjectId(null);
    }
  };

  const beginRenameProject = (event: MouseEvent<HTMLButtonElement>, project: WorkspaceProject) => {
    event.stopPropagation();
    setProjectActionMessage("");
    setRenamingProjectId(project.id);
    setRenameValue(projectNameForInput(projectTitle(project)));
  };

  const cancelRenameProject = (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    if (renamingProject) return;
    setRenamingProjectId(null);
    setRenameValue("");
  };

  const handleRenameProject = async (
    event: FormEvent<HTMLFormElement>,
    project: WorkspaceProject,
  ) => {
    event.preventDefault();
    event.stopPropagation();
    if (renamingProject) return;

    const title = renameValue.trim().slice(0, PROJECT_NAME_MAX_LENGTH);
    if (!title) {
      setProjectActionMessage(t.invalidProjectName);
      return;
    }

    setRenamingProject(true);
    setProjectActionMessage("");
    try {
      await renameWorkspaceProject(project.id, title);
      setProjects((current) => current.map((item) => (
        String(item.id) === String(project.id) ? { ...item, title } : item
      )));
      setRenamingProjectId(null);
      setRenameValue("");
      setProjectActionMessage(t.projectRenamed);
    } catch (error) {
      setProjectActionMessage(error instanceof Error ? error.message : t.projectRenameFailed);
    } finally {
      setRenamingProject(false);
    }
  };

  const currentPlan = workspacePlanLabel(subscriptionInfo?.tier, language);
  const usageLimits = subscriptionInfo?.usage_limits || {
    chat_messages: 0,
    docx_upload: 0,
    max_docx_slides: 0,
  };
  const chatUsage = subscriptionInfo?.current_usage.chat_messages
    ?? subscriptionInfo?.current_usage.idea_generation
    ?? 0;
  const documentUsage = subscriptionInfo?.current_usage.docx_upload ?? 0;
  const chatLimit = usageLimits.chat_messages;
  const documentLimit = usageLimits.docx_upload;
  const chatUsageText = chatLimit === -1
    ? (language === "vi" ? "Không giới hạn" : "Unlimited")
    : `${usagePercent(chatUsage, chatLimit)}% (${formatUsageAmount(chatUsage)}/${chatLimit})`;
  const documentUsageText = documentLimit === -1
    ? `${documentUsage} / ${language === "vi" ? "Không giới hạn" : "Unlimited"}`
    : `${documentUsage} / ${documentLimit}`;

  return (
    <SlidegeniusWorkspaceShell activeTab={tab}>
        <div className="workspace-chat-keepalive" hidden={tab !== "slidegenius"}>
          <SlidegeniusChat isActive={tab === "slidegenius"} />
        </div>

        {tab === "manual" && <SlidegeniusManual />}

        {tab === "projects" && (
          <section className="workspace-panel">
            <div className="panel-heading">
              <div>
                <p className="workspace-eyebrow">PROJECTS / {String(projects.length).padStart(2, "0")}</p>
                <h2>{t.projectsTitle}</h2>
                <p>{t.projectsSub}</p>
              </div>
              <button className="panel-primary" onClick={() => navigate("/home")}>+ {t.newProject}</button>
            </div>
            {projectActionMessage && <p className="project-action-message" role="status">{projectActionMessage}</p>}
            {projectsLoading ? (
              <div className="project-grid project-grid-state">{t.loading}</div>
            ) : projectsError ? (
              <div className="project-grid project-grid-state">{language === "en" ? "Projects are temporarily unavailable." : "Không thể tải dự án lúc này."}</div>
            ) : projects.length === 0 ? (
              <div className="project-empty-state" role="status">
                <span className="project-empty-mark" aria-hidden="true">＋</span>
                <h3>{t.emptyTitle}</h3>
                <p>{t.emptyDescription}</p>
                <button type="button" className="project-empty-action" onClick={() => navigate("/home")}>
                  {t.createFirstProject} <span>↗</span>
                </button>
              </div>
            ) : (
              <div className="project-grid">
                {projects.map((project, index) => {
                  const preview = projectPreviews[String(project.id)];
                  const content = preview?.html_content || preview?.html || preview?.content || "";
                  const background = content ? resolveSlideBackground(preview?.design_settings, content) : {};
                  const isDeleting = String(deletingProjectId) === String(project.id);
                  const isRenaming = String(renamingProjectId) === String(project.id);
                  return (
                    <article className="project-card" key={project.id} onClick={() => navigate(`/projects/${project.id}`)}>
                      <button
                        className="project-card-rename"
                        type="button"
                        aria-label={`${t.renameProject}: ${projectTitle(project)}`}
                        title={t.renameProject}
                        disabled={deletingProjectId !== null || renamingProject}
                        onClick={(event) => beginRenameProject(event, project)}
                      >
                        {isRenaming && renamingProject ? "…" : "✎"}
                      </button>
                      <button
                        className="project-card-delete"
                        type="button"
                        aria-label={`${t.deleteProject}: ${projectTitle(project)}`}
                        title={t.deleteProject}
                        disabled={deletingProjectId !== null}
                        onClick={(event) => void handleDeleteProject(event, project)}
                      >
                        {isDeleting ? "…" : "×"}
                      </button>
                      <div className={`project-art project-art-${index % 3}`}>
                        {content && <ProjectSlidePreview slideId={`project-manager-${project.id}`} content={content} backgroundColor={background.backgroundColor} backgroundImage={background.backgroundImage} className="project-slide-preview absolute inset-0" />}
                      </div>
                      <p>0{index + 1} / PROJECT</p>
                      {isRenaming ? (
                        <form
                          className="project-card-rename-form"
                          onSubmit={(event) => void handleRenameProject(event, project)}
                          onClick={(event) => event.stopPropagation()}
                        >
                          <input
                            className="project-card-rename-input"
                            value={renameValue}
                            maxLength={PROJECT_NAME_MAX_LENGTH}
                            autoFocus
                            placeholder={t.projectNamePlaceholder}
                            aria-label={t.projectNamePlaceholder}
                            onChange={(event) => setRenameValue(event.target.value.slice(0, PROJECT_NAME_MAX_LENGTH))}
                          />
                          <button className="project-card-rename-save" type="submit" aria-label={t.saveProjectName} title={t.saveProjectName} disabled={renamingProject}>✓</button>
                          <button className="project-card-rename-cancel" type="button" aria-label={t.cancelRename} title={t.cancelRename} disabled={renamingProject} onClick={cancelRenameProject}>×</button>
                        </form>
                      ) : (
                        <h3 title={projectTitle(project)}>{truncateProjectName(projectTitle(project))}</h3>
                      )}
                      <div className="project-card-footer">
                        <span>{project.slide_count ?? 0} slides · {t.updated} {projectUpdated(project.updated_at, language)} ↗</span>
                        <button
                          className="project-card-edit"
                          type="button"
                          aria-label={language === "vi" ? "Chỉnh sửa slide" : "Edit slides"}
                          title={language === "vi" ? "Chỉnh sửa slide" : "Edit slides"}
                          onClick={(event) => {
                            event.stopPropagation();
                            navigate(`/editor?project=${project.id}&slide=0`);
                          }}
                        >
                          <FilePenLine aria-hidden="true" />
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            )}
          </section>
        )}

        {tab === "guide" && <section className="workspace-panel guide-panel"><p className="workspace-eyebrow">GUIDE / START HERE</p><h2>{t.guideTitle}</h2><p className="guide-lead">{t.guideSub}</p><div className="guide-steps">{["Bring a brief", "Shape the direction", "Make it unmistakable"].map((step, index) => <article key={step}><span>0{index + 1}</span><h3>{step}</h3><p>{language === "en" ? ["Give Slidegenius the rough idea.", "Explore a few strong routes.", "Polish the story until it lands."][index] : ["Đưa ý tưởng thô cho Slidegenius.", "Khám phá vài hướng đi mạnh.", "Tinh chỉnh câu chuyện đến khi thuyết phục."][index]}</p></article>)}</div></section>}

        {tab === "subscription" && (
          <section className="workspace-panel subscription-panel">
            <div className="panel-heading">
              <div>
                <p className="workspace-eyebrow">PRICING / PLANS</p>
                <h2>{t.subscriptionTitle}</h2>
                <p>{t.subscriptionSub}</p>
              </div>
              {(!subscriptionInfo || subscriptionInfo.tier === "free") && (
                <span className="subscription-current">{subscriptionInfo ? `${t.currentPlan} / ${subscriptionInfo.tier.toUpperCase()}` : t.loadingPlan}</span>
              )}
            </div>
            {subscriptionLoading ? <div className="subscription-state">{t.loadingPlan}</div> : subscriptionError || !subscriptionInfo ? (
              <div className="subscription-state">
                <p>{t.planUnavailable}</p>
                <button className="panel-primary" type="button" onClick={() => void loadSubscription()}>{t.retry}</button>
              </div>
            ) : (
              <>
                <div className="subscription-overview">
                  <div>
                    <span className="subscription-label">{t.currentPlan}</span>
                    <strong>{currentPlan}</strong>
                    <small>{subscriptionInfo.is_active ? t.active : t.expired}{subscriptionInfo.expires_at ? ` · ${subscriptionInfo.cancel_at_period_end ? (language === "vi" ? "hết hạn" : "ends") : (language === "vi" ? "gia hạn" : "renews")} ${formatPlanDate(subscriptionInfo.expires_at, language)}` : ` · ${t.noExpiry}`}</small>
                  </div>
                  <div>
                    <span className="subscription-label">{t.usage}</span>
                    <div className="subscription-usage">
                      <span><strong>{chatUsageText}</strong><small>{t.chatUsage}</small></span>
                      <span><strong>{documentUsageText}</strong><small>{t.uploads}</small></span>
                      <span><strong>{formatPlanLimit(usageLimits.max_docx_slides, language)}</strong><small>{t.slideLimit}</small></span>
                    </div>
                    <small className="subscription-reset-note">{t.resetUsage}</small>
                  </div>
                </div>
                <div className="subscription-actions">
                  <input value={redeemCode} onChange={(event) => setRedeemCode(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") void handleRedeemCode(); }} placeholder={t.codePlaceholder} aria-label={t.redeemCode} />
                  <button className="subscription-button" type="button" onClick={() => void handleRedeemCode()} disabled={redeemingCode || !redeemCode.trim()}>{redeemingCode ? "..." : t.redeem}</button>
                  {subscriptionInfo.tier !== "free" && subscriptionInfo.is_active && <button className="subscription-button secondary" type="button" onClick={() => void handleCancelPlan()}>{t.cancelPlan}</button>}
                </div>
                {subscriptionMessage && <p className="subscription-message" role="status">{subscriptionMessage}</p>}
                <div className="subscription-grid">
                  {pricingTiers.map((tier, index) => {
                    const isCurrentPlan = subscriptionInfo.tier === tier.name;
                    return (
                      <article className={`subscription-card ${isCurrentPlan ? "featured" : ""}`} key={tier.name}>
                        <p className="subscription-label">0{index + 1} / {tier.name.toUpperCase()}</p>
                        <h3>{tier.display_name}</h3>
                        <div className="subscription-price">{tier.price === 0 ? "$0" : `$${tier.price}`} <small>{tier.period === "forever" ? "" : ` / ${tier.period}`}</small></div>
                        <p className="subscription-description">{planFeature(tier, "content_length")}</p>
                        <div className="subscription-features">
                          <span>{planFeature(tier, "chat_messages", "idea_generation")}</span>
                          <span>{planFeature(tier, "docx_upload")}</span>
                          <span>{planFeature(tier, "max_slides")}</span>
                          <span>{planFeature(tier, "usage_reset") || t.resetUsage}</span>
                        </div>
                        {isCurrentPlan && <div className="subscription-card-current-usage"><small>{t.currentUsage}</small><strong>{chatUsageText} · {documentUsageText}</strong></div>}
                        <button className={`subscription-button ${isCurrentPlan ? "secondary" : ""}`} type="button" onClick={() => { setRedeemCode(""); document.querySelector<HTMLInputElement>(".subscription-actions input")?.focus(); }} disabled={isCurrentPlan}>{isCurrentPlan ? t.current : t.choose} {!isCurrentPlan && <span>↗</span>}</button>
                      </article>
                    );
                  })}
                </div>
              </>
            )}
          </section>
        )}

        {tab === "settings" && <SlidegeniusSettings />}

        <SlidegenConfirmDialog
          open={confirmation === "delete-project"}
          onOpenChange={(open) => {
            if (!open) {
              setConfirmation(null);
              setPendingDeleteProject(null);
            }
          }}
          title={t.deleteProjectTitle}
          description={`${t.deleteProjectConfirm} ${pendingDeleteProject ? `(${projectTitle(pendingDeleteProject)})` : ""}`}
          confirmLabel={t.deleteProject}
          cancelLabel={t.cancel}
          onConfirm={() => void confirmDeleteProject()}
          destructive
          busy={deletingProjectId !== null}
        />
        <SlidegenConfirmDialog
          open={confirmation === "cancel-plan"}
          onOpenChange={(open) => {
            if (!open) setConfirmation(null);
          }}
          title={t.cancelPlanTitle}
          description={t.cancelPlanConfirm}
          confirmLabel={t.confirm}
          cancelLabel={t.cancel}
          onConfirm={() => void confirmCancelPlan()}
          destructive
        />
    </SlidegeniusWorkspaceShell>
  );
}
