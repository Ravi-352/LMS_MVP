// frontend/lib/apiClient.js

/*
credentials: "include" makes the browser send cookies (HttpOnly access_token + csrf_token).

For state-changing requests we add X-CSRF-Token header from cookie so backend can compare.

We do NOT attach Authorization header anymore (cookie-based flow).
*/


function getCookie(name) {
  if (typeof document === "undefined") return null;
  const token = document.cookie.split("; ").find(row => row.trim().startsWith(name + "="));
  return token ? decodeURIComponent(token.split("=")[1]) : null;
}

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE || "").replace(/\/$/, "");

async function parseJSONSafely(res) {
  const text = await res.text();
  if (!text) return {};
  try { return JSON.parse(text); } catch { return text; }
}

export async function apiFetch(endpoint, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (["POST","PUT","PATCH","DELETE"].includes(method)) {
    const csrf = getCookie("csrf_token");
    if (csrf) headers["X-CSRF-Token"] = csrf;
  }

  const url = endpoint.startsWith("/") ? `${API_BASE}${endpoint}` : `${API_BASE}/${endpoint}`;
  const res = await fetch(url, { ...options, headers, credentials: "include" });

  if (res.status === 401) {
    if (typeof window !== "undefined") window.location.href = "/login";
    throw new Error("Unauthorized");
  }

  const data = await parseJSONSafely(res);
  if (!res.ok) throw new Error(data?.detail || data?.message || data || "API Error");
  return data;
}
