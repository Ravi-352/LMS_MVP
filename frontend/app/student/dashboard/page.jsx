"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/apiClient";
import Link from "next/link";

export default function StudentDashboard() {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    apiFetch("/students/courses")
      .then(data => setCourses(data))
      .catch(() => {});
  }, []);

  return (
    <section className="p-4 max-w-3xl mx-auto">
      <h1 className="text-xl font-bold mb-4">My Learning</h1>

      {courses.length === 0 ? (
        <p>No enrollments yet. Browse courses!</p>
      ) : (
        courses.map(c => (
          <Link
            key={c.course_id}
            href={`/course/${c.course_slug}`}
            className="block border rounded p-4 mt-2 hover:bg-gray-50"
          >
            <h2 className="font-semibold">{c.course_title}</h2>
            <p className="text-sm">
              Progress: {c.progress_percent}% — {c.status}
            </p>
          </Link>
        ))
      )}
    </section>
  );
}
