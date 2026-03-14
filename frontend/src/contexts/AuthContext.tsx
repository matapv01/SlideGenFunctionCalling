import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { api, setGlobalLogout } from "@/lib/api";

interface User {
  id: number;
  username: string;
  email: string;
  avatar_url?: string;
  full_name?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, remember?: boolean) => Promise<void>;
  register: (fullName: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (data: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(() => {
    console.log("Logging out user...");
    setToken(null);
    setUser(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  }, []);

  // Register global logout function with API
  useEffect(() => {
    setGlobalLogout(logout);
  }, [logout]);

  useEffect(() => {
    const validateAndLoadUser = async () => {
      const stored = localStorage.getItem("user");
      if (stored && token) {
        try {
          setUser(JSON.parse(stored));

          // Validate token by fetching profile
          try {
            const profile = await api.getProfile();
            setUser(prev => {
              if (!prev) return prev;
              const updated = { ...prev, full_name: profile.full_name, avatar_url: profile.avatar_url };
              localStorage.setItem("user", JSON.stringify(updated));
              return updated;
            });
          } catch (error) {
            // Token validation failed - logout automatically
            console.warn("Token validation failed during initialization:", error);
            logout();
          }
        } catch {
          // Invalid stored user data - clear it
          logout();
        }
      }
      setIsLoading(false);
    };

    validateAndLoadUser();
  }, [token, logout]);

  const login = useCallback(async (email: string, password: string, remember = false) => {
    const res = await api.login(email, password);
    setToken(res.token);
    setUser(res.user);
    localStorage.setItem("token", res.token);
    localStorage.setItem("user", JSON.stringify(res.user));
  }, []);

  const register = useCallback(async (fullName: string, email: string, password: string) => {
    const res = await api.register(fullName, email, password);
    setToken(res.token);
    setUser(res.user);
    localStorage.setItem("token", res.token);
    localStorage.setItem("user", JSON.stringify(res.user));
  }, []);

  const updateUser = useCallback((data: Partial<User>) => {
    setUser((prev) => {
      if (!prev) return prev;
      const updated = { ...prev, ...data };
      localStorage.setItem("user", JSON.stringify(updated));
      return updated;
    });
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!token && !!user, isLoading, login, register, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
};
