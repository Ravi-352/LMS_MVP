"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useState } from "react";
import { apiFetch } from "@/lib/apiClient";

export default function ResetPassword() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const token = searchParams.get("token");
  const email = searchParams.get("email");
  

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState("");

  const MIN_PASSWORD_LENGTH = 8;
  const isPasswordTooShort = password.length > 0 && password.length < MIN_PASSWORD_LENGTH;
  const isFormValid = loading || !password || !confirm || password != confirm|| isPasswordTooShort;
  const isPasswordsMismatch = password && confirm && password != confirm;

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setMessage("");

    if (!token) {
      setError("Invalid or missing reset link");
      return;
    }

    if (password !== confirm) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);

    try {
      await apiFetch("/auth/reset-password", {
        method: "POST",
        body: JSON.stringify({
          token,
          new_password: password,
        }),
      });

      setMessage("Password reset Successful; Redirecting to Login...")

      
      //  Redirect to login after success

      setTimeout(() => {
        router.replace("/login");
      }, 2000);

    } catch (err) {
      setError("Reset link is invalid or expired");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto mt-10 card">
      <h1 className="text-xl font-bold mb-4">Reset Password</h1>

      {error && (
        <p className="mb-3 text-red-600 text-sm">{error}</p>
      )}

      {message && (
        <p className="mb-3 text-green-600 text-sm">{message}</p>
      )}

      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          type="password"
          placeholder="New password"
          className="input w-full"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />

        {isPasswordTooShort && (
          <p className="text-sm text-red-600">
            Password must be at least {MIN_PASSWORD_LENGTH} characters long.
          </p>
        )}

        <input
          type="password"
          placeholder="Confirm password"
          className="input w-full"
          value={confirm}
          onChange={e => setConfirm(e.target.value)}
          required
        />

        {isPasswordsMismatch && (
          <p className="text-sm text-red-600">
            Passwords do not match.
          </p>
        )}

        <button
          className="btn-primary w-full"
          disabled={isFormValid}
        >
          {loading ? "Resetting..." : "Reset Password"}
        </button>
      </form>
    </div>
  );
}
