import React, { createContext, useContext, useEffect, useState } from "react";

type Theme = "light" | "dark";

// Fixed schedule: dark 18:00–06:00, light 06:00–18:00
function calcAutoTheme(): Theme {
  const h = new Date().getHours();
  return h >= 18 || h < 6 ? "dark" : "light";
}

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
  autoTheme: boolean;
  setAutoTheme: (v: boolean) => void;
}

const ThemeContext = createContext<ThemeContextType | null>(null);

export const useTheme = () => {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within ThemeProvider");
  return ctx;
};

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [autoTheme, setAutoThemeState] = useState<boolean>(() => {
    return localStorage.getItem("autoTheme") === "true";
  });

  const [theme, setThemeState] = useState<Theme>(() => {
    if (localStorage.getItem("autoTheme") === "true") return calcAutoTheme();
    const stored = localStorage.getItem("theme") as Theme | null;
    if (stored === "light" || stored === "dark") return stored;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);

  // Check every minute when auto mode is on
  useEffect(() => {
    if (!autoTheme) return;
    const apply = () => setThemeState(calcAutoTheme());
    apply();
    const id = setInterval(apply, 60_000);
    return () => clearInterval(id);
  }, [autoTheme]);

  const toggleTheme = () => {
    if (autoTheme) return;
    setThemeState((t) => (t === "dark" ? "light" : "dark"));
  };

  const setTheme = (nextTheme: Theme) => {
    setAutoThemeState(false);
    localStorage.setItem("autoTheme", "false");
    setThemeState(nextTheme);
  };

  const setAutoTheme = (v: boolean) => {
    setAutoThemeState(v);
    localStorage.setItem("autoTheme", String(v));
    if (v) setThemeState(calcAutoTheme());
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme, autoTheme, setAutoTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
