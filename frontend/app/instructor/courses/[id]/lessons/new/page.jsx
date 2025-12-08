"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { apiFetch } from "@/lib/apiClient";
import Layout from "@/components/Layout";

export default function AddLessonPage() {
  const { id: courseId } = useParams();
  const router = useRouter();

  const [form, setForm] = useState({
    title: "",
    type: "video",
    youtube_url: "",
    pdf_url: ""
  });

  async function submit(e) {
    e.preventDefault();
    await apiFetch(`/instructors/courses/${courseId}/lessons`, {
      method: "POST",
      body: JSON.stringify(form),
    });
    router.push(`/instructor/courses/${courseId}`);
  }

  return (
    <Layout>
      <h1 className="text-xl font-semibold mb-4">Add Lesson</h1>
      <form onSubmit={submit} className="space-y-4 max-w-lg">
        <input
          required
          className="input"
          placeholder="Lesson Title"
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
        />

        <select
          className="input"
          value={form.type}
          onChange={(e) => setForm({ ...form, type: e.target.value })}
        >
          <option value="video">YouTube Video</option>
          <option value="pdf">PDF Material</option>
        </select>

        {form.type === "video" && (
          <input
            className="input"
            placeholder="YouTube URL"
            value={form.youtube_url}
            onChange={(e) =>
              setForm({ ...form, youtube_url: e.target.value })
            }
          />
        )}

        {form.type === "pdf" && (
          <input
            className="input"
            placeholder="PDF URL"
            value={form.pdf_url}
            onChange={(e) => setForm({ ...form, pdf_url: e.target.value })}
          />
        )}

        <button className="btn-primary" type="submit">
          Save Lesson
        </button>
      </form>
    </Layout>
  );
}
