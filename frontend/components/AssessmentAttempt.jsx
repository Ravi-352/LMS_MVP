"use client";
import { useState } from "react";
import { apiFetch } from "@/lib/apiClient";

export default function AssessmentAttempt({ assessment }) {
  const [selected, setSelected] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setLoading(true);
    try {
      const data = await apiFetch(`/students/assessments/${assessment.id}/submit`, { method: "POST", body: JSON.stringify({ answers: [{ choice_id: selected }] }) });
      setResult(data);
    } catch (err) {
      alert(err.message || "Submit failed");
    } finally { setLoading(false); }
  };

  if (result) {
    return (
      <div className="bg-white p-4 rounded shadow">
        <div className="text-lg font-semibold">Result: {result.total_score}</div>
        {result.question_results.map(q => (
          <div key={q.question_id} className="mt-3">
            <div>Selected: {q.selected_choice_id} — {q.is_correct ? "Correct" : "Wrong"}</div>
            <div className="text-sm text-gray-600">Correct: {q.correct_choice_id}</div>
            <div className="text-sm text-gray-700 mt-1">{q.explanation}</div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="bg-white p-4 rounded shadow">
      <div className="prose" dangerouslySetInnerHTML={{ __html: assessment.question_markdown }} />
      <div className="mt-3 space-y-2">
        {assessment.choices.map(c => (
          <label key={c.id} className="block">
            <input type="radio" name="choice" value={c.id} onChange={() => setSelected(c.id)} className="mr-2" />
            {c.text}
          </label>
        ))}
      </div>
      <div className="mt-3">
        <button className="bg-primary-500 text-white px-4 py-2 rounded" onClick={submit} disabled={!selected || loading}>{loading ? "Submitting..." : "Submit"}</button>
      </div>
    </div>
  );
}
