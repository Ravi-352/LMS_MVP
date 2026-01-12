import { useState } from "react";
import { apiFetch } from "@/lib/apiClient";


export default function FeedbackForm({ courseId, onSubmitted }) {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setLoading(true);
    try {
      const data = await apiFetch(`/students/courses/${courseId}/feedback`, { method: "POST", body: JSON.stringify({ rating, comment_markdown: comment }) });
      alert("Thanks!");
      if (onSubmitted) onSubmitted(data);
    } catch (err) {
      alert(err.message || "Failed");
    } finally { setLoading(false); }
  };

  return (
    <div className="mt-4 bg-white p-4 rounded-md shadow">
      <label className="block text-sm font-medium">Rating</label>
      <select value={rating} onChange={e => setRating(Number(e.target.value))} className="mt-2 p-2 border rounded w-28">
        {[5,4,3,2,1].map(v => <option key={v} value={v}>{v} stars</option>)}
      </select>

      <label className="block text-sm font-medium mt-4">Comment</label>
      <textarea value={comment} onChange={e => setComment(e.target.value)} className="mt-2 w-full p-2 border rounded" rows={4}></textarea>

      <div className="mt-3">
        <button onClick={submit} className="bg-primary-500 text-white px-4 py-2 rounded" disabled={loading}>{loading ? "Submitting..." : "Submit Feedback"}</button>
      </div>
    </div>
  );
}
