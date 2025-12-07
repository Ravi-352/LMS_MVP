"use client";
import { apiFetch } from "@/lib/apiClient";
import { logClient } from "@/lib/clientLogger";
import { useState } from "react";

export default function LessonPlayer({ lesson, courseId, isEnrolled, onProgressUpdate }) {
  const [loading, setLoading] = useState(false);
  if (!lesson) return <div>Select a lesson</div>;

  const markComplete = async () => {
    if (!isEnrolled) { alert("Please enroll"); return; }
    setLoading(true);
    try {
      const data = await apiFetch(`/students/courses/${courseId}/lessons/${lesson.id}/complete`, { method: "POST" });
      await logClient("info", `Completed lesson ${lesson.id}`);
      if (onProgressUpdate) onProgressUpdate(data.progress);
    } catch (err) {
      alert(err.message || "Failed");
    } finally { setLoading(false); }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">{lesson.title}</h2>

      {lesson.type === "video" && lesson.youtube_url && (
        <div className="w-full aspect-video mb-4">
          <iframe className="w-full h-full rounded-md" src={lesson.youtube_url.replace("watch?v=", "embed/")} title={lesson.title} frameBorder="0" allowFullScreen></iframe>
        </div>
      )}

      {lesson.type === "pdf" && lesson.pdf_url && (
        <div className="mb-4">
          <iframe src={lesson.pdf_url} className="w-full h-[60vh] rounded-md border" />
        </div>
      )}

      <div className="mt-3">
        <button onClick={markComplete} disabled={!isEnrolled || loading} className="bg-primary-500 text-white px-4 py-2 rounded-md">
          {isEnrolled ? (loading ? "Marking..." : "Mark Complete & Continue") : "Enroll to Continue"}
        </button>
      </div>
    </div>
  );
}
