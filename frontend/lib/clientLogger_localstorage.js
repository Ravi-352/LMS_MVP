// if using jwt token with locakalStorage
/*const API_BASE = (process.env.NEXT_PUBLIC_API_BASE || "").replace(/\/$/, "");
async function sendLog(level, message) {
  const token = typeof window !== "undefined"
    ? localStorage.getItem("access_token")
    : null;

  try {
    await fetch(`${API_BASE}/logs/client`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` })
      },
      body: JSON.stringify({ message, level }),
    });
  } catch (err) {
    console.error("Client logging failed", err);
  }
}

export const logInfo = (msg) => sendLog("info", msg);
export const logError = (msg) => sendLog("error", msg);
*/