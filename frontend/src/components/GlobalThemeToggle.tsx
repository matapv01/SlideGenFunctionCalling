import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import { api } from "@/lib/api";
import "./global-theme-toggle.css";

export default function GlobalThemeToggle() {
  const { theme, autoTheme, setTheme } = useTheme();
  const { user } = useAuth();

  const chooseTheme = (nextTheme: "light" | "dark") => {
    if (theme === nextTheme && !autoTheme) return;
    setTheme(nextTheme);
    if (user) {
      void api.updateSettings({ theme: nextTheme }).catch(() => {
        // Keep the local preference when the account settings request fails.
      });
    }
  };

  return (
    <div className="global-theme-toggle" role="group" aria-label="Color theme">
      <button
        type="button"
        className={!autoTheme && theme === "light" ? "active" : ""}
        aria-pressed={!autoTheme && theme === "light"}
        onClick={() => chooseTheme("light")}
        title="Use light mode"
      >
        <span aria-hidden="true">☼</span>
        <small>Light</small>
      </button>
      <button
        type="button"
        className={!autoTheme && theme === "dark" ? "active" : ""}
        aria-pressed={!autoTheme && theme === "dark"}
        onClick={() => chooseTheme("dark")}
        title="Use dark mode"
      >
        <span aria-hidden="true">◐</span>
        <small>Dark</small>
      </button>
    </div>
  );
}
