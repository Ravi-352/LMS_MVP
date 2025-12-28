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


export async function swrFetch(endpoint, options = {}) {
  const url = endpoint.startsWith("/")
    ? `${API_BASE}${endpoint}`
    : `${API_BASE}/${endpoint}`;

  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    credentials: "include",
  });

   // SWR *expects a thrown error* on non-OK
  if (!res.ok) {
    const text = await res.text();
    let detail;
    try { detail = JSON.parse(text); }
    catch { detail = text; }

    const error = new Error(detail?.detail || detail || "API Error");
    error.status = res.status;
    throw error;
  }

  return res.json();
}



export async function apiFetchPublic(endpoint, options = {}) {
  const url = endpoint.startsWith("/")
    ? `${API_BASE}${endpoint}`
    : `${API_BASE}/${endpoint}`;

  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    credentials: "include",
  });

  //const data = await parseJSONSafely(res);
  //if (!res.ok) throw new Error(data?.detail || data?.message || data || "API Error");
  //return data; // ← do NOT redirect on 401
  return await res.json();
}


export async function apiFetch(endpoint, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const headers = {
    "Content-Type": "application/json", 
    ...(options.headers || {}),
  };

  /* const fetchOptions = {
  method: options.method || "GET",
  headers,
  credentials: "include"
  };
  
   if (options.body) {
    fetchOptions.body = JSON.stringify(options.body);   // <-- REQUIRED
  }
  */

  if (["POST","PUT","PATCH","DELETE"].includes(method)) {
    const csrf = getCookie("csrf_token");
    if (csrf) headers["X-CSRF-Token"] = csrf;
  }

  const url = endpoint.startsWith("/") ? `${API_BASE}${endpoint}` : `${API_BASE}/${endpoint}`;
  // const res = await fetch(url, { ...options, headers, credentials: "include", fetchOptions });
  const res = await fetch(url, { ...options, headers, credentials: "include"});
  const PUBLIC_PATHS = ["/login", "/signup", "/public/courses"];

  
  if (res.status === 401) {
  /*  if (typeof window !== "undefined" && !PUBLIC_PATHS.includes(window.location.pathname)) {
      window.location.href = "/login";
    }*/
    throw new Error("Unauthorized");
  }

  const data = await parseJSONSafely(res);
  if (!res.ok) throw new Error(data?.detail || data?.message || data || "API Error");
  return data;
}

export async function logout() {
  const res = await fetch(`${API_BASE}/auth/logout`, {
    method: "POST",
    credentials: "include",  // send cookies
  });

  if (!res.ok) {
    throw new Error("Logout failed");
  }

  return true;
}