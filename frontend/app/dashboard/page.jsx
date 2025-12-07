"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

/**
 * Student Dashboard Page
 * - Shows enrolled courses and progress
 * - More data will be integrated once backend APIs are connected
 */

export default function DashboardPage() {
  const [enrolledCourses, setEnrolledCourses] = useState([]);

  useEffect(() => {
    // TODO: Replace with real API call: /api/enrollments/me
    setEnrolledCourses([
      {
        id: 1,
        title: "Intro to Python",
        progress: 40,
      },
      {
        id: 2,
        title: "Cloud Fundamentals",
        progress: 10,
      },
    ]);
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-6">My Learning</h1>

      {enrolledCourses.length === 0 ? (
        <p className="text-gray-500">You are not enrolled in any course yet.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {enrolledCourses.map(course => (
            <Link
              key={course.id}
              href={`/courses/${course.id}`}
              className="border rounded-xl p-4 hover:shadow-lg transition"
            >
              <h2 className="text-lg font-semibold mb-2">
                {course.title}
              </h2>

              <div className="w-full bg-gray-200 h-2 rounded">
                <div
                  className="bg-blue-600 h-2 rounded"
                  style={{ width: `${course.progress}%` }}
                ></div>
              </div>

              <p className="text-sm text-gray-600 mt-2">
                Progress: {course.progress}%
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
