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
    const savedToken = localStorage.getItem("access_token");
    if (savedToken) {
      setToken(savedToken);
      fetchUserInfo(savedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUserInfo = async (authToken: string) => {
    try {
      const userData = await fetchApi<User>("/auth/me", { method: "GET" }, authToken);
      setUser(userData);
    } catch (err) {
      logout();
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
      setUser(res.user);
      setIsLoading(false);
    } else {
      await fetchUserInfo(accessToken);
    }
  };

  const logout = () => {
    localStorage.removeItem("access_token");
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
