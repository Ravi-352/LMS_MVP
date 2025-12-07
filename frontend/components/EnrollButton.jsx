import { useState } from "react";
import { apiFetch } from "@/lib/apiClient";

export default function EnrollButton({ courseId, onEnrolled }) {
  const [loading, setLoading] = useState(false);
  const enroll = async () => {
    setLoading(true);
    try {
      await apiFetch("/students/enroll", { method: "POST", body: JSON.stringify({ course_id: courseId }) });
      alert("Enrolled!");
      if (onEnrolled) onEnrolled();
    } catch (err) {
      alert(err.message || "Failed to enroll");
      console.error("Enrollment error:", err);
      setError("Enrollment failed. Please try again later.");
    } finally { setLoading(false); }
  };
  return <button onClick={enroll} className="bg-primary-500 text-white px-4 py-2 rounded-md" disabled={loading}>{loading ? "Enrolling..." : "Enroll"}</button>;
}
