// frontend/app/instructor/courses/[id]/page.jsx
"use client";

import { useParams } from "next/navigation";
import CourseBuilder from "@/components/CourseBuilder";
import Layout from "@/components/Layout";

export default function InstructorCourseEditPage() {
  const { id } = useParams();

  return (
    <section>
      <div className="max-w-5xl mx-auto px-4 py-6">
        <CourseBuilder courseId={id} />
      </div>
    </section>
  );
}
