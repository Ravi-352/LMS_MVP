"use client";
import { apiFetch } from "@/lib/apiClient";
import { logClient } from "@/lib/clientLogger";
import { useState } from "react";

//export default function LessonPlayer({ lesson, courseId, isEnrolled, onProgressUpdate }) {
export default function LessonPlayer({ lesson, courseId, isEnrolled, onLessonComplete }) {
  const [loading, setLoading] = useState(false);
  if (!lesson) return <div>Select a lesson</div>;

  const markComplete = async () => {
    if (!isEnrolled) { alert("Please enroll"); return; }
    setLoading(true);
    try {
      const data = await apiFetch(`/students/courses/${courseId}/lessons/${lesson.id}/complete`, { method: "POST" });
      //await logClient("info", `Completed lesson ${lesson.id}`);
      //if (onProgressUpdate) onProgressUpdate(data.progress);
      if (onLessonComplete) onLessonComplete({
        lesson_id: lesson.id,
        progress_percent: data.progress_percent
      });
    } catch (err) {
      alert(err.message || "Failed");
    } finally { setLoading(false); }
  };
  const getEmbedUrl = (url) => {
    try {
      const u = new URL(url);
      const videoId = u.searchParams.get("v");
      return videoId ? `https://www.youtube.com/embed/${videoId}` : url;
    } catch {
      return url;
    }
  };


  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">
        {lesson.title}
        {lesson.is_completed && (<span className="text-green-500 ml-2">✔ (Completed)</span>)}
      </h2>

      {lesson.type === "video" && lesson.youtube_url && (
        <div className="w-full aspect-video mb-4">
          <iframe className="w-full h-full rounded-md" src={getEmbedUrl(lesson.youtube_url)} title={lesson.title} frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen></iframe>
        </div>
      )}

      {lesson.type === "pdf" && lesson.pdf_url && (
        <div className="mb-4">
          <iframe src={lesson.pdf_url} className="w-full h-[60vh] rounded-md border" />
        </div>
      )}

      <div className="mt-3">
        <button onClick={markComplete} disabled={!isEnrolled || loading || lesson.is_completed} className="bg-primary-500 text-white px-4 py-2 rounded-md">
         {/* {isEnrolled ? (loading ? "Marking..." : "Mark Complete & Continue") : "Enroll to Continue"} */}
          {lesson.is_completed ? "Completed" : loading ? "Marking..." : "Mark Complete & Continue"}
        </button>
      </div>
    </div>
  );
}
