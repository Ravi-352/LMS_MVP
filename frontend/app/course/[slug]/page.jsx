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
        //const data = await apiFetch(`/public/courses/${slug}`);
        // loading public course data
        const publicCourse = await apiFetch(`/public/courses/${slug}`);
        setCourse(publicCourse);
        
        // set first lesson as selected by default
        const firstLesson = publicCourse?.sections?.[0]?.lessons?.[0] ?? null;
        setSelectedLesson(firstLesson);
        
        // Try enrollment/progress (only works if logged in)

        try {
          const p = await apiFetch(`/students/courses/${publicCourse.id}/progress`);
          setIsEnrolled(p.is_enrolled === true);
          setProgress(p.progress_percent ?? 0);
        } catch (_) {
          // not logged in and not enrolled → public preview
          setIsEnrolled(false);
          setProgress(0);
        }

      } catch (err) {
        console.error(err);
      }
    }
    load();
  }, [slug]);

  const refreshEnrollment = async () => {
    const p = await apiFetch(`/students/courses/${course.id}/progress`);
    setIsEnrolled(true);
    setProgress(p.progress_percent ?? 0);
  };


  if (!course) return <div>Loading...</div>;

  return (
    <section>
      <div className="grid md:grid-cols-5 gap-6">
        <div className="md:col-span-3">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">{course.title}</h1>
              <div className="text-sm text-gray-600">{course.description}</div>
            </div>
            <div className="text-right">
             {/* {!isEnrolled && <EnrollButton courseId={course.id} onEnrolled={() => setIsEnrolled(true)} />} */}
             {!isEnrolled && <EnrollButton courseId={course.id} onEnrolled={refreshEnrollment} />}
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
    </section>
  );
}
