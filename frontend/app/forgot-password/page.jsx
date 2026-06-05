"use client";
import { useState } from "react";
import { apiFetch } from "@/lib/apiClient";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [done, setDone] = useState(false);

  async function submit(e) {
    e.preventDefault();
    await apiFetch("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
    setDone(true);
  }

  return done ? (
    <p>If the email exists, a reset link was sent.</p>
  ) : (
    <form onSubmit={submit}>
      <input className="w-full p-2 border rounded" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
      <button className="w-full bg-primary-500 text-white py-2 rounded">Send reset link</button>
    </form>
  );
}
