import { useCallback, useEffect, useState, type FormEvent, type MouseEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "@/contexts/LanguageContext";
import { api } from "@/lib/api";
import { deleteWorkspaceProject, loadWorkspaceSnapshot, renameWorkspaceProject, WorkspaceProject } from "./data/workspaceApi";
import SlidegeniusChat from "./SlidegeniusChat";
import SlidegeniusSettings from "./SlidegeniusSettings";
import SlidegeniusWorkspaceShell, { workspacePlanLabel } from "./SlidegeniusWorkspaceShell";
import SlidegeniusManual from "./SlidegeniusManual";
import { ProjectSlidePreview } from "@/components/ProjectSlidePreview";
import { resolveSlideBackground } from "@/lib/slideBackground";

type Tab = "slidegenius" | "projects" | "manual" | "guide" | "settings" | "subscription";

interface SubscriptionInfo {
  tier: string;
  is_active: boolean;
  expires_at?: string;
  cancel_at_period_end: boolean;
  daily_limits: { idea_generation: number; docx_upload: number; max_docx_slides: number };
  current_usage: { idea_generation: number; docx_upload: number };
  usage_reset_date: string;
}

interface PricingTier {
  name: string;
  display_name: string;
  price: number;
  currency: string;
  period: string;
  features: Record<string, string | boolean>;
}

interface ProjectPreviewSlide {
  id?: string | number;
  title?: string;
  html_content?: string;
  content?: string;
  html?: string;
  design_settings?: unknown;
}

const MAX_PROJECT_TITLE_LENGTH = 60;

const copy = {
  en: {
    tabs: { slidegenius: "Slidegenius", projects: "Project Manager", manual: "Manual", guide: "Guide", settings: "Settings" },
    projectsTitle: "Your projects", projectsSub: "Keep every idea moving forward.", newProject: "New project", loading: "Loading projects...", empty: "Your saved projects will appear here.", deleteProject: "Delete project", renameProject: "Rename project", saveProjectName: "Save project name", cancelRename: "Cancel rename", projectNamePlaceholder: "Project name", projectRenamed: "Project renamed.", projectRenameFailed: "Unable to rename project.", invalidProjectName: "Enter a project name.", deleteProjectConfirm: "Delete this project? Its slides will be permanently removed, while the generation record will remain in chat.", projectDeleted: "Project deleted.", projectDeleteFailed: "Unable to delete project.",
    guideTitle: "A faster way to make better work.", guideSub: "Start with a thought. Slidegenius helps you turn it into a clear, compelling direction.",
    settingsTitle: "Workspace settings", settingsSub: "Shape your Slidegen experience.", language: "Language", theme: "Theme", dark: "Dark canvas", notifications: "Notifications", save: "Save changes",
    collapse: "Collapse sidebar", expand: "Expand sidebar", openSettings: "Open settings", upgrade: "Upgrade", currentPlan: "CURRENT PLAN", free: "Free plan", help: "Need a hand?",
    subscriptionTitle: "Make room for better work.", subscriptionSub: "Start free, then scale when the work calls for it.", currentFree: "CURRENT PLAN / FREE", choose: "Use upgrade code", loadingPlan: "Loading plan...", planUnavailable: "Plan information is temporarily unavailable.", retry: "Try again", active: "Active", expired: "Expired", noExpiry: "No expiration", usage: "TODAY'S USAGE", ideas: "Idea generations", uploads: "DOCX uploads", slideLimit: "Slide limit", redeemCode: "Redeem upgrade code", codePlaceholder: "Enter your upgrade code", redeem: "Redeem", cancelPlan: "Cancel plan", cancelConfirm: "Cancel this plan now?", current: "Current", updated: "Updated",
  },
  vi: {
    tabs: { slidegenius: "Slidegenius", projects: "Quản lý dự án", manual: "Manual", guide: "Hướng dẫn", settings: "Cài đặt" },
    projectsTitle: "Dự án của bạn", projectsSub: "Giữ mọi ý tưởng luôn tiến về phía trước.", newProject: "Dự án mới", loading: "Đang tải dự án...", empty: "Các dự án đã lưu sẽ xuất hiện ở đây.", deleteProject: "Xóa project", renameProject: "Đổi tên project", saveProjectName: "Lưu tên project", cancelRename: "Hủy đổi tên", projectNamePlaceholder: "Tên project", projectRenamed: "Đã đổi tên project.", projectRenameFailed: "Không thể đổi tên project.", invalidProjectName: "Vui lòng nhập tên project.", deleteProjectConfirm: "Xóa project này? Toàn bộ slide sẽ bị xóa vĩnh viễn, còn lịch sử tạo vẫn được giữ trong chatbot.", projectDeleted: "Đã xóa project.", projectDeleteFailed: "Không thể xóa project.",
    guideTitle: "Cách nhanh hơn để tạo ra điều tốt hơn.", guideSub: "Bắt đầu từ một suy nghĩ. Slidegenius giúp bạn biến nó thành một hướng đi rõ ràng và thuyết phục.",
    settingsTitle: "Cài đặt không gian", settingsSub: "Định hình trải nghiệm Slidegenius của bạn.", language: "Ngôn ngữ", theme: "Giao diện", dark: "Nền tối", notifications: "Thông báo", save: "Lưu thay đổi",
    collapse: "Thu gọn thanh bên", expand: "Mở rộng thanh bên", openSettings: "Mở cài đặt", upgrade: "Nâng cấp", currentPlan: "GÓI HIỆN TẠI", free: "Gói miễn phí", help: "Cần trợ giúp?",
    subscriptionTitle: "Mở rộng không gian cho công việc tốt hơn.", subscriptionSub: "Bắt đầu miễn phí, nâng cấp khi công việc cần thêm sức mạnh.", currentFree: "GÓI HIỆN TẠI / FREE", choose: "Dùng mã nâng cấp", loadingPlan: "Đang tải gói...", planUnavailable: "Tạm thời không thể tải thông tin gói.", retry: "Thử lại", active: "Đang hoạt động", expired: "Đã hết hạn", noExpiry: "Không giới hạn thời gian", usage: "SỬ DỤNG HÔM NAY", ideas: "Lượt tạo ý tưởng", uploads: "Lượt tải DOCX", slideLimit: "Giới hạn slide", redeemCode: "Nhập mã nâng cấp", codePlaceholder: "Nhập mã nâng cấp", redeem: "Kích hoạt", cancelPlan: "Hủy gói", cancelConfirm: "Hủy gói này ngay bây giờ?", current: "Đang dùng", updated: "Cập nhật",
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
  const [subscriptionInfo, setSubscriptionInfo] = useState<SubscriptionInfo | null>(null);
  const [pricingTiers, setPricingTiers] = useState<PricingTier[]>([]);
  const [subscriptionLoading, setSubscriptionLoading] = useState(true);
  const [subscriptionError, setSubscriptionError] = useState(false);
  const [redeemCode, setRedeemCode] = useState("");
  const [redeemingCode, setRedeemingCode] = useState(false);
  const [subscriptionMessage, setSubscriptionMessage] = useState("");
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

  const handleCancelPlan = async () => {
    if (!window.confirm(t.cancelConfirm)) return;
    setSubscriptionMessage("");
    try {
      await api.cancelSubscription(true);
      setSubscriptionMessage(language === "vi" ? "Đã chuyển về gói miễn phí." : "Your plan is now Free.");
      await loadSubscription();
    } catch (error) {
      setSubscriptionMessage(error instanceof Error ? error.message : (language === "vi" ? "Không thể hủy gói." : "Unable to cancel this plan."));
    }
  };

  const handleDeleteProject = async (
    event: MouseEvent<HTMLButtonElement>,
    project: WorkspaceProject,
  ) => {
    event.stopPropagation();
    if (deletingProjectId !== null) return;
    if (!window.confirm(`${t.deleteProjectConfirm}\n\n${projectTitle(project)}`)) return;

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
    setRenameValue(projectTitle(project).slice(0, MAX_PROJECT_TITLE_LENGTH));
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

    const title = renameValue.trim().slice(0, MAX_PROJECT_TITLE_LENGTH);
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

  return (
    <SlidegeniusWorkspaceShell activeTab={tab}>
        {tab === "slidegenius" && <SlidegeniusChat />}

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
              <div className="project-grid project-grid-state">{t.empty}</div>
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
                            maxLength={MAX_PROJECT_TITLE_LENGTH}
                            autoFocus
                            placeholder={t.projectNamePlaceholder}
                            aria-label={t.projectNamePlaceholder}
                            onChange={(event) => setRenameValue(event.target.value.slice(0, MAX_PROJECT_TITLE_LENGTH))}
                          />
                          <button className="project-card-rename-save" type="submit" aria-label={t.saveProjectName} title={t.saveProjectName} disabled={renamingProject}>✓</button>
                          <button className="project-card-rename-cancel" type="button" aria-label={t.cancelRename} title={t.cancelRename} disabled={renamingProject} onClick={cancelRenameProject}>×</button>
                        </form>
                      ) : (
                        <h3 title={projectTitle(project)}>{projectTitle(project)}</h3>
                      )}
                      <span>{project.slide_count ?? 0} slides · {t.updated} {projectUpdated(project.updated_at, language)} ↗</span>
                    </article>
                  );
                })}
              </div>
            )}
          </section>
        )}

        {tab === "guide" && <section className="workspace-panel guide-panel"><p className="workspace-eyebrow">GUIDE / START HERE</p><h2>{t.guideTitle}</h2><p className="guide-lead">{t.guideSub}</p><div className="guide-steps">{["Bring a brief", "Shape the direction", "Make it unmistakable"].map((step, index) => <article key={step}><span>0{index + 1}</span><h3>{step}</h3><p>{language === "en" ? ["Give Slidegenius the rough idea.", "Explore a few strong routes.", "Polish the story until it lands."][index] : ["Đưa ý tưởng thô cho Slidegenius.", "Khám phá vài hướng đi mạnh.", "Tinh chỉnh câu chuyện đến khi thuyết phục."][index]}</p></article>)}</div></section>}

        {tab === "subscription" && <section className="workspace-panel subscription-panel"><div className="panel-heading"><div><p className="workspace-eyebrow">PRICING / PLANS</p><h2>{t.subscriptionTitle}</h2><p>{t.subscriptionSub}</p></div><span className="subscription-current">{subscriptionInfo ? `${t.currentPlan} / ${subscriptionInfo.tier.toUpperCase()}` : t.loadingPlan}</span></div>{subscriptionLoading ? <div className="subscription-state">{t.loadingPlan}</div> : subscriptionError || !subscriptionInfo ? <div className="subscription-state"><p>{t.planUnavailable}</p><button className="panel-primary" type="button" onClick={() => void loadSubscription()}>{t.retry}</button></div> : <><div className="subscription-overview"><div><span className="subscription-label">{t.currentPlan}</span><strong>{currentPlan}</strong><small>{subscriptionInfo.is_active ? t.active : t.expired}{subscriptionInfo.expires_at ? ` · ${subscriptionInfo.cancel_at_period_end ? (language === "vi" ? "hết hạn" : "ends") : (language === "vi" ? "gia hạn" : "renews")} ${formatPlanDate(subscriptionInfo.expires_at, language)}` : ` · ${t.noExpiry}`}</small></div><div><span className="subscription-label">{t.usage}</span><div className="subscription-usage"><span>{subscriptionInfo.current_usage.idea_generation} / {formatPlanLimit(subscriptionInfo.daily_limits.idea_generation, language)}<small>{t.ideas}</small></span><span>{subscriptionInfo.current_usage.docx_upload} / {formatPlanLimit(subscriptionInfo.daily_limits.docx_upload, language)}<small>{t.uploads}</small></span><span>{formatPlanLimit(subscriptionInfo.daily_limits.max_docx_slides, language)}<small>{t.slideLimit}</small></span></div></div></div><div className="subscription-actions"><input value={redeemCode} onChange={(event) => setRedeemCode(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") void handleRedeemCode(); }} placeholder={t.codePlaceholder} aria-label={t.redeemCode} /><button className="subscription-button" type="button" onClick={() => void handleRedeemCode()} disabled={redeemingCode || !redeemCode.trim()}>{redeemingCode ? "..." : t.redeem}</button>{subscriptionInfo.tier !== "free" && subscriptionInfo.is_active && <button className="subscription-button secondary" type="button" onClick={() => void handleCancelPlan()}>{t.cancelPlan}</button>}</div>{subscriptionMessage && <p className="subscription-message" role="status">{subscriptionMessage}</p>}<div className="subscription-grid">{pricingTiers.map((tier, index) => <article className={`subscription-card ${subscriptionInfo.tier === tier.name ? "featured" : ""}`} key={tier.name}><p className="subscription-label">0{index + 1} / {tier.name.toUpperCase()}</p><h3>{tier.display_name}</h3><div className="subscription-price">{tier.price === 0 ? "$0" : `$${tier.price}`} <small>{tier.period === "forever" ? "" : ` / ${tier.period}`}</small></div><p className="subscription-description">{String(tier.features.content_length || "")}</p><div className="subscription-features"><span>{String(tier.features.idea_generation)} {t.ideas.toLowerCase()}</span><span>{String(tier.features.docx_upload)} {t.uploads.toLowerCase()}</span><span>{String(tier.features.max_slides)} {t.slideLimit.toLowerCase()}</span></div><button className={`subscription-button ${subscriptionInfo.tier === tier.name ? "secondary" : ""}`} type="button" onClick={() => { setRedeemCode(""); document.querySelector<HTMLInputElement>(".subscription-actions input")?.focus(); }} disabled={subscriptionInfo.tier === tier.name}>{subscriptionInfo.tier === tier.name ? t.current : t.choose} {!subscriptionInfo.tier || subscriptionInfo.tier === tier.name ? null : <span>↗</span>}</button></article>)}</div></>}</section>}

        {tab === "settings" && <SlidegeniusSettings />}
    </SlidegeniusWorkspaceShell>
  );
}
