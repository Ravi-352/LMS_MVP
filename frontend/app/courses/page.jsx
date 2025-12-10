"use client";
import useSWR from "swr";
import Link from "next/link";
import { apiFetchPublic } from "@/lib/apiClient";

export default function CoursesPage() {
  const { data: courses, error } = useSWR("/public/courses", apiFetchPublic);

  if (!courses && !error) return <p className="p-4">Loading...</p>;
  if (error) return <p className="p-4 text-red-500">Failed to load courses</p>;

  return (
    <section className="max-w-4xl mx-auto p-4">
      <h1 className="text-xl font-bold mb-4">Available Courses</h1>

      <div className="grid sm:grid-cols-2 gap-4">
        {courses.map((c) => (
          <Link
            key={c.slug}
            href={`/course/${c.slug}`}
            className="border rounded-lg shadow-sm p-4 hover:shadow-md transition"
          >
            <h2 className="font-semibold">{c.title}</h2>
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
              {c.description}
            </p>
          </Link>
        ))}
      </div>
    </section>
  );
}
