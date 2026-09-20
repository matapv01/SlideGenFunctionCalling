import { useEffect, useMemo, useState, type ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import SlidegenLogo from "@/components/SlidegenLogo";
import { api } from "@/lib/api";
import { ChatSlideStreamPanel } from "./ChatSlideStreamPanel";
import { useSlideGeneration } from "./SlideGenerationContext";
import WorkspaceTour from "./WorkspaceTour";
import "./slidegenius.css";
import "./slidegenius-sidebar.css";

export type WorkspaceShellTab = "slidegenius" | "projects" | "manual" | "guide" | "settings" | "subscription" | "admin";

const tabRoutes: Record<WorkspaceShellTab, string> = {
  slidegenius: "/home",
  projects: "/projects",
  manual: "/manual",
  guide: "/guide",
  settings: "/settings",
  subscription: "/subscription",
  admin: "/admin",
};

const shellCopy = {
  en: {
    tabs: { slidegenius: "Slidegenius", projects: "Project Manager", manual: "Manual", guide: "Guide", settings: "Settings", admin: "Admin" },
    collapse: "Collapse sidebar",
    expand: "Expand sidebar",
    openSettings: "Open settings",
    yourPlan: "Your plan",
    upgrade: "Upgrade",
    currentPlan: "CURRENT PLAN",
    logout: "Log out",
  },
  vi: {
    tabs: { slidegenius: "Slidegenius", projects: "Quản lý dự án", manual: "Manual", guide: "Hướng dẫn", settings: "Cài đặt", admin: "Admin" },
    collapse: "Thu gọn thanh bên",
    expand: "Mở rộng thanh bên",
    openSettings: "Mở cài đặt",
    yourPlan: "Gói của bạn",
    upgrade: "Nâng cấp",
    currentPlan: "GÓI HIỆN TẠI",
    logout: "Đăng xuất",
  },
} as const;

export function workspacePlanLabel(tier: string | undefined, language: "vi" | "en") {
  const normalized = tier?.toLowerCase();
  if (normalized === "plus") return language === "vi" ? "Gói Plus" : "Plus plan";
  if (normalized === "ultra") return language === "vi" ? "Gói Ultra" : "Ultra plan";
  if (normalized === "free") return language === "vi" ? "Gói miễn phí" : "Free plan";
  return language === "vi" ? "Đang tải gói" : "Loading plan";
}

interface SlidegeniusWorkspaceShellProps {
  activeTab: WorkspaceShellTab;
  children: ReactNode;
  className?: string;
}

function WorkspaceManualSlideStream() {
  const navigate = useNavigate();
  const { language } = useLanguage();
  const { generation, closeSlideStream } = useSlideGeneration();

  if (generation.source !== "manual" || !generation.panelOpen || generation.phase === "idle") return null;

  const text = language === "vi"
    ? {
        close: "Ẩn tiến trình",
        openProject: "Mở project",
        slide: "Slide",
        completed: "Deck đã hoàn thành",
        waiting: "Đang chờ slide đầu tiên...",
      }
    : {
        close: "Hide progress",
        openProject: "Open project",
        slide: "Slide",
        completed: "Deck completed",
        waiting: "Waiting for the first slide...",
      };

  return (
    <div className="workspace-slide-stream-drawer">
      <ChatSlideStreamPanel
        status={generation.status}
        progress={generation.progress}
        slides={generation.slides}
        totalSlides={generation.totalSlides}
        completed={generation.phase === "completed"}
        projectId={generation.projectId}
        error={generation.error}
        closeLabel={text.close}
        openProjectLabel={text.openProject}
        slideLabel={text.slide}
        completedLabel={text.completed}
        waitingLabel={text.waiting}
        onClose={closeSlideStream}
        onOpenProject={(projectId) => navigate(`/projects/${projectId}`)}
      />
    </div>
  );
}

export function SlidegeniusWorkspaceShell({ activeTab, children, className = "" }: SlidegeniusWorkspaceShellProps) {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { language } = useLanguage();
  const text = shellCopy[language];
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [subscriptionTier, setSubscriptionTier] = useState("free");

  const userName = user?.full_name || user?.username || user?.email || "Slidegen user";
  const initials = useMemo(() => userName.slice(0, 2).toUpperCase(), [userName]);
  const currentPlan = workspacePlanLabel(subscriptionTier, language);
  const isUltraPlan = subscriptionTier.toLowerCase() === "ultra";

  useEffect(() => {
    if (!user) return;
    api.getSubscriptionInfo().then((info: any) => {
      setSubscriptionTier(info.tier || "free");
    }).catch(() => {
      // Keep the shell usable while subscription data is temporarily unavailable.
    });
  }, [user]);

  const goToTab = (tab: WorkspaceShellTab) => navigate(tabRoutes[tab]);

  return (
    <main
      className={`sgx-home workspace-page ${sidebarCollapsed ? "sidebar-collapsed" : ""} ${className}`.trim()}
      data-tab={activeTab}
      onClick={() => setUserMenuOpen(false)}
    >
      <aside className="workspace-sidebar">
        <div className="workspace-brand-row">
          <Link className="workspace-brand" to="/" aria-label="Slidegen home">
            <SlidegenLogo />
          </Link>
          <button
            className="workspace-collapse"
            type="button"
            onClick={() => setSidebarCollapsed((value) => !value)}
            aria-label={sidebarCollapsed ? text.expand : text.collapse}
            title={sidebarCollapsed ? text.expand : text.collapse}
          >
            <span aria-hidden="true" />
          </button>
        </div>

        <div className="workspace-sidebar-label">WORKSPACE</div>
        <nav className="workspace-nav" aria-label="Workspace navigation" data-tour="workspace-nav">
          {(["slidegenius", "projects", "manual", "guide"] as const).map((item) => (
            <button
              key={item}
              className={activeTab === item ? "active" : ""}
              data-tour={item === "projects" ? "projects-nav" : undefined}
              onClick={() => goToTab(item)}
              title={text.tabs[item]}
              aria-label={text.tabs[item]}
            >
              <span className={`workspace-icon icon-${item}`} aria-hidden="true" />
              <span className="workspace-nav-label">{text.tabs[item]}</span>
            </button>
          ))}
          {user?.is_admin && (
            <button
              className={activeTab === "admin" ? "active" : ""}
              onClick={() => goToTab("admin")}
              title={text.tabs.admin}
              aria-label={text.tabs.admin}
            >
              <span className="workspace-icon icon-admin" aria-hidden="true" />
              <span className="workspace-nav-label">{text.tabs.admin}</span>
            </button>
          )}
        </nav>

        <div className="workspace-sidebar-bottom">
          {!sidebarCollapsed && (
            <>
              <div className="workspace-plan-card">
                <div>
                  <span className="workspace-plan-label">{text.currentPlan}</span>
                  <strong>{currentPlan}</strong>
                </div>
                {!isUltraPlan && (
                  <button type="button" onClick={() => goToTab("subscription")}>{text.upgrade} <span>↗</span></button>
                )}
              </div>
            </>
          )}

          <div className="workspace-user-wrap">
            <button
              className="workspace-user"
              type="button"
              onClick={(event) => {
                event.stopPropagation();
                setUserMenuOpen((value) => !value);
              }}
              aria-label={text.openSettings}
              aria-expanded={userMenuOpen}
              title={text.tabs.settings}
              style={{ width: sidebarCollapsed ? 30 : "100%", minWidth: sidebarCollapsed ? 30 : 0, gap: sidebarCollapsed ? 0 : 9, overflow: "hidden" }}
            >
              <span>{initials}</span>
              <div style={{ display: sidebarCollapsed ? "none" : "grid" }}>
                <strong>{userName}</strong>
                <small>{currentPlan}</small>
              </div>
            </button>
            {userMenuOpen && (
              <div className="workspace-user-menu" onClick={(event) => event.stopPropagation()}>
                <button type="button" onClick={() => { setUserMenuOpen(false); goToTab("subscription"); }}>{text.yourPlan}<span>↗</span></button>
                <button type="button" onClick={() => { setUserMenuOpen(false); goToTab("settings"); }}>{text.tabs.settings}<span>↗</span></button>
                <button type="button" onClick={() => { setUserMenuOpen(false); logout(); navigate("/"); }}>{text.logout}<span>↗</span></button>
              </div>
            )}
          </div>
        </div>
      </aside>

      <section className="workspace-main">
        {children}
      </section>
      <WorkspaceManualSlideStream />
      {activeTab === "slidegenius" && <WorkspaceTour />}
    </main>
  );
}

export default SlidegeniusWorkspaceShell;
