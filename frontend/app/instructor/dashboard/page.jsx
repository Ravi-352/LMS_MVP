"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/apiClient";
import Link from "next/link";

export default function InstructorDashboard() {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    apiFetch("/instructors/courses")
      .then(data => setCourses(data))
      .catch(() => {});
  }, []);

  return (
    <section className="p-4 max-w-3xl mx-auto">
      <h1 className="text-xl font-bold mb-4">Instructor Dashboard</h1>
      <Link href="/instructor/courses/new" className="btn-primary">
        ➕ Create New Course
      </Link>

      <div className="mt-6">
        {courses.map(c => (
          <Link 
            key={c.id}
            href={`/instructor/courses/${c.id}`}
            className="block border rounded p-4 mt-2 hover:bg-gray-50"
          >
            <h2 className="font-semibold">{c.title}</h2>
            <p className="text-sm">{c.description}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
