import React, { useState, useCallback, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Home, FolderOpen, Settings, BookOpen, LogOut, Menu, X, ChevronDown, User, PanelLeftClose, PanelLeft, Crown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LanguageToggle } from "@/components/LanguageToggle";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { api } from "@/lib/api";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

const SIDEBAR_COLLAPSED_KEY = "sidebar-collapsed";

const navItemDefs = [
  { labelKey: "sidebar_slidegen" as const, path: "/home", icon: Home },
  { labelKey: "sidebar_projects" as const, path: "/projects", icon: FolderOpen },
  { labelKey: "sidebar_guide" as const, path: "/guide", icon: BookOpen },
];

export const AppLayout: React.FC<{ children: React.ReactNode; headerContent?: React.ReactNode }> = ({ children, headerContent }) => {
  const { t } = useLanguage();
  const navItems = navItemDefs.map((item) => ({ ...item, label: t[item.labelKey] || item.labelKey }));
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    const stored = localStorage.getItem(SIDEBAR_COLLAPSED_KEY);
    return stored === "true";
  });

  const toggleSidebarCollapsed = useCallback(() => {
    setSidebarCollapsed((prev) => {
      const newValue = !prev;
      localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(newValue));
      return newValue;
    });
  }, []);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout, isAuthenticated } = useAuth();
  const [subscriptionTier, setSubscriptionTier] = useState<string>("free");

  useEffect(() => {
    if (isAuthenticated) {
      api.getSubscriptionInfo().then((info: any) => {
        setSubscriptionTier(info.tier || "free");
      }).catch(() => { });
    }
  }, [isAuthenticated]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex min-h-screen">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex flex-col border-r border-border bg-sidebar transition-all duration-300 lg:sticky lg:top-0 lg:h-screen lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full",
          sidebarCollapsed ? "lg:w-16" : "w-64"
        )}
      >
        <div className={cn(
          "flex h-16 items-center border-b border-sidebar-border px-4",
          sidebarCollapsed ? "justify-center" : "justify-between"
        )}>
          <Link to="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg gradient-primary flex-shrink-0">
              <span className="text-sm font-bold text-primary-foreground">S</span>
            </div>
            {!sidebarCollapsed && <span className="text-lg font-bold gradient-text">SlideGen</span>}
          </Link>
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setSidebarOpen(false)}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        <nav className={cn("flex-1 space-y-1 p-3", sidebarCollapsed && "px-2")}>
          <TooltipProvider delayDuration={0}>
            {navItems.map((item) => {
              // Check if current path matches or is a related sub-route
              const isActive = location.pathname === item.path ||
                (item.path === "/projects" && (
                  location.pathname.startsWith("/projects/") ||
                  location.pathname.startsWith("/editor/") ||
                  location.pathname.startsWith("/streaming/")
                ));
              const linkContent = (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-sidebar-accent text-sidebar-accent-foreground"
                      : "text-sidebar-foreground hover:bg-sidebar-accent/50",
                    sidebarCollapsed && "justify-center px-2"
                  )}
                >
                  <item.icon className="h-4 w-4 flex-shrink-0" />
                  {!sidebarCollapsed && item.label}
                </Link>
              );

              if (sidebarCollapsed) {
                return (
                  <Tooltip key={item.path}>
                    <TooltipTrigger asChild>{linkContent}</TooltipTrigger>
                    <TooltipContent side="right">{item.label}</TooltipContent>
                  </Tooltip>
                );
              }
              return linkContent;
            })}
          </TooltipProvider>
        </nav>

        {/* Collapse toggle button - desktop only */}
        <div className="hidden lg:block border-t border-sidebar-border p-3">
          <TooltipProvider delayDuration={0}>
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  onClick={toggleSidebarCollapsed}
                  className={cn(
                    "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-sidebar-foreground hover:bg-sidebar-accent/50 transition-colors",
                    sidebarCollapsed && "justify-center px-2"
                  )}
                >
                  {sidebarCollapsed ? (
                    <PanelLeft className="h-4 w-4 flex-shrink-0" />
                  ) : (
                    <>
                      <PanelLeftClose className="h-4 w-4 flex-shrink-0" />
                      <span>{t.sidebar_collapse}</span>
                    </>
                  )}
                </button>
              </TooltipTrigger>
              {sidebarCollapsed && <TooltipContent side="right">{t.sidebar_expand}</TooltipContent>}
            </Tooltip>
          </TooltipProvider>
        </div>

        {isAuthenticated && (
          <div className={cn("border-t border-sidebar-border p-3", sidebarCollapsed && "px-2")}>
            <TooltipProvider delayDuration={0}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    onClick={handleLogout}
                    className={cn(
                      "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-sidebar-foreground hover:bg-sidebar-accent/50 transition-colors",
                      sidebarCollapsed && "justify-center px-2"
                    )}
                  >
                    <LogOut className="h-4 w-4 flex-shrink-0" />
                    {!sidebarCollapsed && t.sidebar_logout}
                  </button>
                </TooltipTrigger>
                {sidebarCollapsed && <TooltipContent side="right">{t.sidebar_logout}</TooltipContent>}
              </Tooltip>
            </TooltipProvider>
          </div>
        )}
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Header */}
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-background/80 backdrop-blur-xl px-4 lg:px-6">
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setSidebarOpen(true)}>
            <Menu className="h-5 w-5" />
          </Button>
          {headerContent ? (
            <div className="hidden min-w-0 flex-1 pr-3 lg:flex lg:items-center">{headerContent}</div>
          ) : (
            <div className="hidden lg:block" />
          )}
          <div className="flex items-center gap-2">
            {/* Language and Theme toggles for all users */}
            <LanguageToggle />
            <ThemeToggle />

            {isAuthenticated && user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-2 px-2">
                    <Avatar className="h-8 w-8 flex-shrink-0">
                      <AvatarImage src={user.avatar_url || undefined} />
                      <AvatarFallback className="gradient-primary text-primary-foreground text-xs font-bold">
                        {user.username?.charAt(0).toUpperCase() || "U"}
                      </AvatarFallback>
                    </Avatar>
                    <div className="hidden sm:block text-left min-w-0">
                      <div className="text-sm font-medium leading-tight truncate max-w-[120px]">
                        {user.full_name || user.username || user.email}
                      </div>
                      <div className={cn(
                        "text-xs leading-tight font-medium capitalize",
                        subscriptionTier === "ultra" && "text-yellow-600 dark:text-yellow-400",
                        subscriptionTier === "plus" && "text-blue-600 dark:text-blue-400",
                        subscriptionTier === "free" && "text-muted-foreground"
                      )}>
                        {subscriptionTier === "ultra" ? "👑 ultra" : subscriptionTier}
                      </div>
                    </div>
                    <ChevronDown className="h-4 w-4 flex-shrink-0" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => navigate("/subscription")}>
                    <Crown className="mr-2 h-4 w-4" /> {t.nav_subscription}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate("/settings")}>
                    <Settings className="mr-2 h-4 w-4" /> {t.nav_settings}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" /> {t.sidebar_logout}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Button variant="outline" size="sm" onClick={() => navigate("/login")}>
                <User className="mr-2 h-4 w-4" /> {t.nav_login}
              </Button>
            )}
          </div>
        </header>

        <main
          key={location.pathname}
          className="flex-1 overflow-y-auto animate-in fade-in slide-in-from-bottom-4 duration-500 ease-out fill-mode-both"
        >
          {children}
        </main>
      </div>
    </div>
  );
};
