const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;

async function attemptTokenRefresh(): Promise<string | null> {
  if (typeof window === "undefined") return null;
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) return null;

  if (isRefreshing && refreshPromise) {
    return refreshPromise;
  }

  isRefreshing = true;
  refreshPromise = (async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!res.ok) {
        throw new Error("Refresh token expired");
      }

      const data = await res.json();
      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token);
        if (data.refresh_token) {
          localStorage.setItem("refresh_token", data.refresh_token);
        }
        return data.access_token;
      }
      return null;
    } catch {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user_info");
      return null;
    } finally {
      isRefreshing = false;
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

export async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {},
  token?: string | null,
  idempotencyKey?: string,
  isRetry = false
): Promise<T> {
  let authToken = token;
  if (!authToken && typeof window !== "undefined") {
    authToken = localStorage.getItem("access_token");
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> || {}),
  };

  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }

  const method = (options.method || "GET").toUpperCase();
  if (idempotencyKey) {
    headers["Idempotency-Key"] = idempotencyKey;
  } else if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    headers["Idempotency-Key"] = typeof crypto !== "undefined" && crypto.randomUUID 
      ? crypto.randomUUID() 
      : `idemp-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // If 401 Unauthorized, attempt transparent token refresh once
  if (response.status === 401 && !isRetry && typeof window !== "undefined") {
    const newToken = await attemptTokenRefresh();
    if (newToken) {
      return fetchApi<T>(endpoint, options, newToken, idempotencyKey, true);
    }
  }

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status} Error`;
    try {
      const errorData = await response.json();
      if (errorData?.error?.message) {
        errorMessage = errorData.error.message;
      } else if (errorData?.detail) {
        errorMessage = typeof errorData.detail === "string" ? errorData.detail : JSON.stringify(errorData.detail);
      }
    } catch {
      // Ignore json parse error
    }
    throw new Error(errorMessage);
  }

  return response.json() as Promise<T>;
}
