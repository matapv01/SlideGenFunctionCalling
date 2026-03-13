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

  const [theme, setTheme] = useState<Theme>(() => {
    if (localStorage.getItem("autoTheme") === "true") return calcAutoTheme();
    const stored = localStorage.getItem("theme") as Theme | null;
    if (stored) return stored;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem("theme", theme);
  }, [theme]);

  // Check every minute when auto mode is on
  useEffect(() => {
    if (!autoTheme) return;
    const apply = () => setTheme(calcAutoTheme());
    apply();
    const id = setInterval(apply, 60_000);
    return () => clearInterval(id);
  }, [autoTheme]);

  const toggleTheme = () => {
    if (autoTheme) return;
    setTheme((t) => (t === "dark" ? "light" : "dark"));
  };

  const setAutoTheme = (v: boolean) => {
    setAutoThemeState(v);
    localStorage.setItem("autoTheme", String(v));
    if (v) setTheme(calcAutoTheme());
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, autoTheme, setAutoTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
