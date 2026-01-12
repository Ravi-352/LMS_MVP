// frontend/app/instructor/courses/[id]/page.jsx
"use client";

import { useParams } from "next/navigation";
import CourseBuilder from "@/components/CourseBuilder";
import Layout from "@/components/Layout";
import { apiFetch } from "@/lib/apiClient";

//import { use, useEffect } from "react";
import { useEffect, useState } from "react";

export default function InstructorCourseEditPage() {
  const { id } = useParams();
  const [feedback, setFeedback] = useState(null);
  
  useEffect(() => {
    async function loadFeedback() {
      try {
        const res = await apiFetch(`/instructor/courses/${id}/feedback`);
        //const data = await res.json();
        //setFeedback(data);
        setFeedback(res);
      } catch (error) {
        console.error("Failed to load feedback:", error);
      }
    }
    loadFeedback();
  }, [id]);


  return (
    <section>
      <div className="max-w-5xl mx-auto px-4 py-6">
        <CourseBuilder courseId={id} />
      </div>
      <div className="max-w-5xl mx-auto px-4 py-6">
        <h2 className="text-xl font-bold mb-4">Student Feedback</h2>
        {!feedback ? (
          <p>Loading feedback...</p>

        ) : (
          <>
            <div className="mb-4">
              <p className= "mb-4 text-lg font-medium text-gray-700">
                ⭐ {feedback.summary.avg_rating} / 5 ·{" "}
                {feedback.summary.total_reviews} reviews </p>

            </div>

            {feedback.reviews.length === 0 ? (
            <p>No feedback available for this course.</p>
          ) : (
            <ul className="space-y-4">
              {feedback.reviews.map((fb) => (
                <li key={fb.id} className="border p-4 rounded">
                  <p className="mb-2">{fb.comment_markdown || "No comment"}</p>
                  <p className="text-sm text-gray-600">Rating: {fb.rating ?? "-"} stars</p>
                  <p className="text-sm text-gray-600">By: {fb.user_name ?? "Anonymous"}</p>
                  <p className="text-sm text-gray-600">On: {new Date(fb.created_at).toLocaleDateString()}</p>

                </li>
              ))}
            </ul>
          )}

          </>
          
        )}
      </div>
    </section>
  );
}
