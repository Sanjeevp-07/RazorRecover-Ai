"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { fetchApi } from "@/lib/api/client";
import { supabase } from "@/lib/supabase";

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
  loginWithGoogle: () => Promise<void>;
  register: (merchantName: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    async function initAuth() {
      try {
        const savedToken = localStorage.getItem("access_token");
        const savedUser = localStorage.getItem("user_info");

        if (savedUser) {
          try {
            setUser(JSON.parse(savedUser));
          } catch {
            // ignore parse error
          }
        }

        // Check active Supabase session
        const { data: sessionData } = await supabase.auth.getSession();
        if (sessionData?.session) {
          const spToken = sessionData.session.access_token;
          setToken(spToken);
          localStorage.setItem("access_token", spToken);
          await fetchUserInfo(spToken);
          return;
        }

        if (savedToken) {
          setToken(savedToken);
          await fetchUserInfo(savedToken);
        } else {
          setIsLoading(false);
        }
      } catch {
        setIsLoading(false);
      }
    }

    initAuth();

    // Listen for Supabase Auth state changes (including Google OAuth redirects)
    const { data: authListener } = supabase.auth.onAuthStateChange(async (event, session) => {
      if ((event === "SIGNED_IN" || event === "TOKEN_REFRESHED") && session) {
        const spToken = session.access_token;
        setToken(spToken);
        localStorage.setItem("access_token", spToken);
        if (session.refresh_token) {
          localStorage.setItem("refresh_token", session.refresh_token);
        }
        await fetchUserInfo(spToken);
      } else if (event === "SIGNED_OUT") {
        setToken(null);
        setUser(null);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user_info");
      }
    });

    return () => {
      authListener.subscription.unsubscribe();
    };
  }, []);

  const fetchUserInfo = async (authToken: string) => {
    try {
      const userData = await fetchApi<User>("/auth/me", { method: "GET" }, authToken);
      if (userData && userData.email) {
        setUser(userData);
        localStorage.setItem("user_info", JSON.stringify(userData));
      }
    } catch (err: any) {
      // If access token failed, try refreshing using refresh_token before logging out
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        try {
          const refreshRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/auth/refresh`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token: refreshToken }),
          });

          if (refreshRes.ok) {
            const data = await refreshRes.json();
            if (data.access_token) {
              localStorage.setItem("access_token", data.access_token);
              setToken(data.access_token);
              if (data.refresh_token) {
                localStorage.setItem("refresh_token", data.refresh_token);
              }
              const retryUser = await fetchApi<User>("/auth/me", { method: "GET" }, data.access_token);
              if (retryUser) {
                setUser(retryUser);
                localStorage.setItem("user_info", JSON.stringify(retryUser));
              }
              return;
            }
          }
        } catch {
          // Refresh failed
        }
      }

      const msg = err?.message || "";
      if (msg.includes("inactive") || msg.includes("credentials")) {
        logout();
      }
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    let accessToken: string | null = null;
    let userInfo: User | null = null;

    // 1. Try Supabase Auth first
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      if (data?.session && !error) {
        accessToken = data.session.access_token;
        if (data.session.refresh_token) {
          localStorage.setItem("refresh_token", data.session.refresh_token);
        }
      }
    } catch {
      // Supabase Auth fallback
    }

    // 2. Fallback or Sync with Backend API
    try {
      const res = await fetchApi<{ access_token: string; refresh_token?: string; user?: User }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      if (!accessToken) {
        accessToken = res.access_token;
      }
      if (res.refresh_token) {
        localStorage.setItem("refresh_token", res.refresh_token);
      }
      if (res.user) {
        userInfo = res.user;
      }
    } catch (err) {
      if (!accessToken) {
        setIsLoading(false);
        throw err;
      }
    }

    if (accessToken) {
      localStorage.setItem("access_token", accessToken);
      setToken(accessToken);

      if (userInfo) {
        localStorage.setItem("user_info", JSON.stringify(userInfo));
        setUser(userInfo);
        setIsLoading(false);
      } else {
        await fetchUserInfo(accessToken);
      }
    }
  };

  const loginWithGoogle = async () => {
    setIsLoading(true);
    const origin = typeof window !== "undefined" ? window.location.origin : "http://localhost:3000";
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${origin}/login/callback`,
        queryParams: {
          access_type: "offline",
          prompt: "consent",
        },
      },
    });

    if (error) {
      setIsLoading(false);
      throw error;
    }
  };

  const register = async (merchantName: string, email: string, password: string) => {
    setIsLoading(true);
    let accessToken: string | null = null;

    // 1. Sign up with Supabase Auth
    try {
      const { data } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { merchant_name: merchantName }
        }
      });
      if (data?.session) {
        accessToken = data.session.access_token;
      }
    } catch {
      // Supabase auth fallback
    }

    // 2. Register with Backend API
    try {
      const res = await fetchApi<{ access_token: string; refresh_token?: string; user?: User }>("/auth/register", {
        method: "POST",
        body: JSON.stringify({ merchant_name: merchantName, email, password }),
      });

      if (!accessToken) {
        accessToken = res.access_token;
      }
      if (res.user) {
        setUser(res.user);
        localStorage.setItem("user_info", JSON.stringify(res.user));
      }
    } catch (err) {
      if (!accessToken) {
        setIsLoading(false);
        throw err;
      }
    }

    if (accessToken) {
      localStorage.setItem("access_token", accessToken);
      setToken(accessToken);
      await fetchUserInfo(accessToken);
    }
  };

  const logout = async () => {
    try {
      await supabase.auth.signOut();
    } catch {
      // ignore
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_info");
    setToken(null);
    setUser(null);
    setIsLoading(false);
  };

  return (
    <AuthContext.Provider value={{ token, user, isLoading, login, loginWithGoogle, register, logout }}>
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
