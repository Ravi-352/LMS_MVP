"use client";
import { useEffect, useState } from "react";
import Layout from "@/components/Layout";
import SidebarLessons from "@/components/SidebarLessons";
import LessonPlayer from "@/components/LessonPlayer";
import EnrollButton from "@/components/EnrollButton";
import FeedbackForm from "@/components/FeedbackForm";
import { apiFetch, apiFetchPublic } from "@/lib/apiClient";
import PublicFeedback from "@/components/PublicFeedback";

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
        
        
        // set first lesson as selected by default
        const firstLesson = publicCourse?.sections?.[0]?.lessons?.[0] ?? null;
        
        let studentState = null;
        try {
          studentState = await apiFetch(`/students/courses/${publicCourse.id}`);
        } catch (_) { 
          // not logged in or not enrolled
        }

        // MERGE STUDENT PROGRESS INTO LESSONS
        if (studentState?.completed_lesson_ids && studentState.completed_lesson_ids.length > 0) {
          for (const sec of publicCourse.sections) {
            for (const les of sec.lessons) {
              les.is_completed = studentState.completed_lesson_ids.includes(les.id);
              }
          }
        }
        
        setCourse(publicCourse);

        setSelectedLesson(firstLesson);
        setIsEnrolled(studentState?.is_enrolled ?? false);
        setProgress(studentState?.progress_percent ?? 0);


        
        // Try enrollment/progress (only works if logged in)

       /* try {
          const p = await apiFetch(`/students/courses/${publicCourse.id}/progress`);
          setIsEnrolled(p.is_enrolled === true);
          setProgress(p.progress_percent ?? 0);
        } catch (_) {
          // not logged in and not enrolled → public preview
          setIsEnrolled(false);
          setProgress(0);
        } */

      } catch (err) {
        console.error(err);
      }
    }
    load();
  }, [slug]);

  const refreshEnrollment = async () => {
    //const p = await apiFetch(`/students/courses/${course.id}/progress`);
    const p = await apiFetch(`/students/courses/${course.id}`);
    setIsEnrolled(true);
    setProgress(p.progress_percent ?? 0);
  };

  const handleLessonComplete = ({ lessonId, progressPercent }) => {
    setProgress(progressPercent);
  
  // mark lesson as completed in local state
    setCourse((prevCourse) => {
      const updatedCourse = structuredClone(prevCourse);
      for (const sec of updatedCourse.sections) {
        for (const les of sec.lessons) {
          if (les.id === lessonId) {
            les.is_completed = true;
          }
        }
      }
        return updatedCourse;
      });
    
    //auto advance to next lesson
    const allLessons = course.sections.flatMap(sec => sec.lessons);

    const firstIncomplete = allLessons.find(les => !les.is_completed) ?? allLessons[allLessons.length -1] ?? null;
    setSelectedLesson(firstIncomplete);


    /*const currentIndex = allLessons.findIndex(les => les.id === lessonId);
    if (allLessons[currentIndex + 1]) {
      setSelectedLesson(allLessons[currentIndex + 1]);
    }*/
  };

  if (!course) return <div>Loading...</div>;

  return (
    <section className="p-4">
      <div className="grid md:grid-cols-5 gap-6">
        <div className="md:col-span-3">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">{course.title}</h1>
              <div className="text-sm text-gray-600">{course.description}</div>
            </div>
            {/* ACTION AREA */}
            <div className="text-right">
             
             {/* {!isEnrolled && (<EnrollButton courseId={course.id} onEnrolled={refreshEnrollment} />)}
              <div className="text-sm mt-2">Progress: {progress}%</div> */}

              {/* UDEMY COURSE */}
              {course.is_udemy ? (
                <a
                  href={course.udemy_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-purple-600 text-white px-4 py-2 rounded-md inline-block"
                >
                  Go to Udemy
                </a>
              ) : (
                <>
                  {!isEnrolled && (
                    <EnrollButton
                      courseId={course.id}
                      onEnrolled={refreshEnrollment}
                    />
                  )}
                  {isEnrolled && (
                    <div className="text-sm mt-2">
                      Progress: {progress}%
                    </div>
                  )}
                </>
              )}

            

            </div>
          </div>

         {/* <LessonPlayer lesson={selectedLesson} courseId={course.id} isEnrolled={isEnrolled} onProgressUpdate={(p) => setProgress(p)} /> */}
          <LessonPlayer lesson={selectedLesson} courseId={course.id} isEnrolled={isEnrolled} onLessonComplete={handleLessonComplete} />

          {isEnrolled && progress >= 25 && <FeedbackForm courseId={course.id} onSubmitted={() => { /* refresh list if needed */ }} />}
        </div>

        <div className="md:col-span-2">
          <SidebarLessons course={course} selectedLessonId={selectedLesson?.id} onSelect={setSelectedLesson} isEnrolled={isEnrolled} />
        </div>
        {/* to display feedback for non-udemy courses */}
        <div className="md:col-span-5">
          {!course.is_udemy && <PublicFeedback courseId={course.id} />}
        </div>

      </div>
    </section>
  );
}
