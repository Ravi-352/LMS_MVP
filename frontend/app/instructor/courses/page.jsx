"use client";

import useSWR from "swr";
import Link from "next/link";
import Layout from "@/components/Layout";

export default function InstructorCoursesPage() {
  //const { data: courses, isLoading } = useSWR("/instructor/me/courses");
  const { data: courses, isLoading } = useSWR("/instructor/courses");

  return (
    <section className="p-6 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-xl font-bold">My Courses</h1>
        <Link href="/instructor/courses/new">
          <button className="bg-blue-600 text-white px-4 py-2 rounded">
            + New Course
          </button>
        </Link>
      </div>

      {isLoading && <p>Loading...</p>}

      {courses?.length ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {courses.map(course => (
            <div key={course.id} className="border p-4 rounded shadow">
              <h3 className="text-lg font-semibold">{course.title}</h3>
              <p className="text-sm text-gray-600">{course.description}</p>
              <Link href={`/instructor/courses/${course.id}`}>
                <button className="mt-3 btn-primary hover:underline">
                  Manage
                </button>
              </Link>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-600">
          No courses yet. Click <strong>New Course</strong> to start!
        </p>

      )}
    </section>
  );
}
