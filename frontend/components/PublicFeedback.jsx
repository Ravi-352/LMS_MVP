"use client";
import { useEffect, useState } from "react";
import { apiFetchPublic } from "@/lib/apiClient";

export default function PublicFeedback({ courseId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetchPublic(`/public/courses/${courseId}/feedback`);
        setData(res);
      } catch (e) {
        console.error("Failed to load feedback for public", e);
      }
    }
    load();
  }, [courseId]);

  if (!data) return <p className="text-sm text-gray-500">Loading reviews…</p>;

  return (
    <div className="mt-8 border-t pt-6">
      <h2 className="text-xl font-semibold mb-2">Student Reviews</h2>

      <div className="mb-4 text-sm text-gray-700">
        ⭐ {data.avg_rating} / 5 · {data.total_reviews} reviews
      </div>

      {data.reviews.length === 0 ? (
        <p className="text-sm text-gray-500">No reviews yet.</p>
      ) : (
        <ul className="space-y-4">
          {data.reviews.map((fb) => (
            <li key={fb.id} className="border p-4 rounded-md">
              <div className="flex justify-between items-center mb-1">
                <span className="font-medium">
                  {fb.user_name || "Anonymous"}
                </span>
                <span className="text-sm text-gray-600">
                  ⭐ {fb.rating ?? "-"}
                </span>
              </div>

              {fb.comment_markdown && (
                <p className="text-sm text-gray-700">{fb.comment_markdown}</p>
              )}

              <p className="text-xs text-gray-400 mt-1">
                {new Date(fb.created_at).toLocaleDateString()}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
