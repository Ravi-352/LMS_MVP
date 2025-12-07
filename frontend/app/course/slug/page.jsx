"use client";
import { useEffect, useState } from "react";
import Layout from "@/components/Layout";
import SidebarLessons from "@/components/SidebarLessons";
import LessonPlayer from "@/components/LessonPlayer";
import EnrollButton from "@/components/EnrollButton";
import FeedbackForm from "@/components/FeedbackForm";
import { apiFetch } from "@/lib/apiClient";

export default function CoursePage({ params }) {
  const { slug } = params;
  const [course, setCourse] = useState(null);
  const [selectedLesson, setSelectedLesson] = useState(null);
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch(`/public/courses/${slug}`);
        setCourse(data);
        const firstLesson = data?.sections?.[0]?.lessons?.[0];
        setSelectedLesson(firstLesson);
        // try to load progress if logged in
        try {
          const p = await apiFetch(`/students/courses/${data.id}/progress`);
          setProgress(p.progress_percent ?? 0);
          setIsEnrolled(p.is_enrolled ?? (p.status === "enrolled"));
        } catch (err) {
          // ignore when not logged in
        }
      } catch (err) {
        console.error(err);
      }
    }
    load();
  }, [slug]);

  if (!course) return <Layout><div>Loading...</div></Layout>;

  return (
    <Layout>
      <div className="grid md:grid-cols-5 gap-6">
        <div className="md:col-span-3">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">{course.title}</h1>
              <div className="text-sm text-gray-600">{course.description}</div>
            </div>
            <div className="text-right">
              {!isEnrolled && <EnrollButton courseId={course.id} onEnrolled={() => setIsEnrolled(true)} />}
              <div className="text-sm mt-2">Progress: {progress}%</div>
            </div>
          </div>

          <LessonPlayer lesson={selectedLesson} courseId={course.id} isEnrolled={isEnrolled} onProgressUpdate={(p) => setProgress(p)} />

          {isEnrolled && progress >= 25 && <FeedbackForm courseId={course.id} onSubmitted={() => { /* refresh list if needed */ }} />}
        </div>

        <div className="md:col-span-2">
          <SidebarLessons course={course} selectedLessonId={selectedLesson?.id} onSelect={setSelectedLesson} isEnrolled={isEnrolled} />
        </div>
      </div>
    </Layout>
  );
}
