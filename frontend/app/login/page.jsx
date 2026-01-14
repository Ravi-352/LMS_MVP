"use client";
import { apiFetch, loginWithPassword } from "@/lib/apiClient";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/AuthProvider";
//import { mutate } from "swr";



export default function LoginPage() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    setErrorMessage("");
    try {
      //const res = await apiFetch(`${process.env.NEXT_PUBLIC_API_BASE}/auth/token`, {
      /*const res = await apiFetch(`/auth/token`, {
        method: "POST",
        credentials: "include", // allow cookies to be set by backend
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
        //body: new URLSearchParams({ email, password })
      });*/
      const res = await loginWithPassword(email, password);
      //const data = await res.json();
      const data = res;
      const user = await refreshUser();

      // If we reach here → login succeeded (apiFetch throws on error)
      console.log("Login success:", data);
      //if (!res.ok) throw new Error(data?.detail || "Login failed");
      //if (res.ok) {
      const profile = await apiFetch("/auth/me");
      console.log("Logged in user profile:", profile);
      
      // role-based redirection
      router.replace(
        user.is_educator ? "/instructor/dashboard" : "/student/dashboard"
      );

      // sync SWR cache for current user
      //await mutate("/auth/me", profile, false);
      // Redirect based on role

      //window.location.href = profile.is_educator
      //  ? "/instructor/dashboard"
      //  : "/student/dashboard";
      /*if (profile.is_educator) {
        //router.push("/instructor/dashboard");
        router.replace("/instructor/dashboard");
        router.refresh();
      } else {
        //router.push("/student/dashboard");
        router.replace("/student/dashboard");
        router.refresh();
      }
      //} */
      // backend set cookies (access_token HttpOnly + csrf_token)
      //window.location.href = "/";
    } catch (err) {
      console.error("Login error:", err);
      setErrorMessage(err.message || "Login failed");
      alert(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-2xl font-semibold mb-4">Login</h1>
      <form onSubmit={submit} className="space-y-3 bg-white p-4 rounded shadow">
        <input className="w-full p-2 border rounded" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required/>
        <input type="password" className="w-full p-2 border rounded" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} required />
        {errorMessage && <p className="text-red-500">{errorMessage}</p>}
        <div><button className="w-full bg-primary-500 text-white py-2 rounded">{loading ? "Signing in..." : "Sign in"}</button></div>
      </form>
    </div>
  );
}
