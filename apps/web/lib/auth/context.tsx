"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { fetchApi } from "@/lib/api/client";

interface User {
  id: string;
  merchant_id: string;
  email: string;
  role: string;
  is_active: boolean;
}

interface AuthContextType {
  token: string | null;
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (merchantName: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    try {
      const savedToken = localStorage.getItem("access_token");
      const savedUser = localStorage.getItem("user_info");

      if (savedUser) {
        try {
          setUser(JSON.parse(savedUser));
        } catch (e) {
          // ignore parse error
        }
      }

      if (savedToken) {
        setToken(savedToken);
        fetchUserInfo(savedToken);
      } else {
        setIsLoading(false);
      }
    } catch (e) {
      setIsLoading(false);
    }
  }, []);

  const fetchUserInfo = async (authToken: string) => {
    try {
      const userData = await fetchApi<User>("/auth/me", { method: "GET" }, authToken);
      if (userData && userData.email) {
        setUser(userData);
        localStorage.setItem("user_info", JSON.stringify(userData));
      }
    } catch (err: any) {
      // Only logout if error is strictly a 401 Unauthorized / credentials error
      const msg = err?.message || "";
      if (msg.includes("401") || msg.includes("credentials") || msg.includes("inactive")) {
        logout();
      }
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const res = await fetchApi<{ access_token: string; refresh_token?: string; user?: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    const accessToken = res.access_token;
    localStorage.setItem("access_token", accessToken);
    setToken(accessToken);

    if (res.user) {
      localStorage.setItem("user_info", JSON.stringify(res.user));
      setUser(res.user);
      setIsLoading(false);
    } else {
      await fetchUserInfo(accessToken);
    }
  };

  const register = async (merchantName: string, email: string, password: string) => {
    const res = await fetchApi<{ access_token: string; refresh_token?: string; user?: User }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ merchant_name: merchantName, email, password }),
    });

    const accessToken = res.access_token;
    localStorage.setItem("access_token", accessToken);
    setToken(accessToken);

    if (res.user) {
      localStorage.setItem("user_info", JSON.stringify(res.user));
      setUser(res.user);
      setIsLoading(false);
    } else {
      await fetchUserInfo(accessToken);
    }
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_info");
    setToken(null);
    setUser(null);
    setIsLoading(false);
  };

  return (
    <AuthContext.Provider value={{ token, user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
