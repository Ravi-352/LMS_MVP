"use client";
import { apiFetch } from "@/lib/apiClient";
import { useState } from "react";

export default function SignupPage() {
  const [form, setForm] = useState({
  full_name: "",
  email: "",
  password: "",
  is_educator: false,
});

  const [loading, setLoading] = useState(false);

  const update = (key, value) => {
    setForm(prev => ({ ...prev, [key]: value }));
  };

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await apiFetch(`${process.env.NEXT_PUBLIC_API_BASE}/auth/signup`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
        full_name: form.full_name,
        email: form.email,
        password: form.password,
        is_educator: form.is_educator,
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "Signup failed");

      alert("Account created! Please login.");
      window.location.href = "/login"; // redirect
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10">
      <h1 className="text-2xl font-bold mb-4">Create your Account</h1>
      <form onSubmit={submit} className="bg-white p-6 rounded-md shadow space-y-4">
        <input
          type="text"
          placeholder="Full Name"
          className="w-full p-2 border rounded"
          value={form.full_name}
          onChange={(e) => update("full_name", e.target.value)}
          required
        />
        <input
          type="email"
          placeholder="Email"
          className="w-full p-2 border rounded"
          value={form.email}
          onChange={(e) => update("email", e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          className="w-full p-2 border rounded"
          value={form.password}
          onChange={(e) => update("password", e.target.value)}
          minLength={6}
          required
        />

        <label className="block text-sm font-medium">Select Role</label>
        <select
          className="w-full border p-2 rounded"
          value={form.is_educator ? "instructor" : "student"}
          onChange={(e) => update("is_educator", e.target.value === "instructor")}
        >
          <option value="student">Student</option>
          <option value="instructor">Instructor</option>
        </select>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary-500 text-white py-2 rounded-md"
        >
          {loading ? "Creating account..." : "Sign up"}
        </button>
      </form>

      <p className="text-center text-sm mt-4">
        Already have an account?{" "}
        <a href="/login" className="text-primary-500 font-medium">
          Login
        </a>
      </p>
    </div>
  );
}
