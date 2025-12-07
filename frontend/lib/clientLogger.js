
// frontend/lib/clientLogger.js
// Sends client logs to the backend using the same secure cookie/CSRF flow
const API_BASE = (process.env.NEXT_PUBLIC_API_BASE || "").replace(/\/$/, "");

function getCookie(name) {
  if (typeof document === "undefined") return null;
  const match = document.cookie.split("; ").find(row => row.trim().startsWith(name + "="));
  return match ? decodeURIComponent(match.split("=")[1]) : null;
}

export async function logClient(level, message) {
  try {
    const csrf = getCookie("csrf_token");
    await fetch(`${API_BASE}/logs/client`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(csrf && { "X-CSRF-Token": csrf }),
      },
      body: JSON.stringify({ level, message }),
    });
  } catch (err) {
    console.error("Client logging failed", err);
  }
}
