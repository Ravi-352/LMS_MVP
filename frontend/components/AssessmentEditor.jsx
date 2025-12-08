// frontend/components/AssessmentEditor.jsx
"use client";

import { useState } from "react";

/**
 * Props:
 * - assessment (object)
 * - onChange(updatedAssessment)
 * - onDelete()
 */

export default function AssessmentEditor({ assessment = {}, onChange, onDelete }) {
  const [draft, setDraft] = useState({
    id: assessment.id ?? null,
    question_markdown: assessment.question_markdown ?? "",
    image_url: assessment.image_url ?? "",
    max_score: assessment.max_score ?? 1,
    explanation: assessment.explanation ?? "",
    choices: (assessment.choices || []).map(c => ({ id: c.id ?? null, text: c.text, is_correct: !!c.is_correct, explanation: c.explanation })) || []
  });

  function setField(k, v) {
    const next = { ...draft, [k]: v };
    setDraft(next);
    onChange && onChange(next);
  }

  function addChoice() {
    const next = { ...draft, choices: [...draft.choices, { id: null, text: "", is_correct: false, explanation: "" }] };
    setDraft(next);
    onChange && onChange(next);
  }

  function updateChoice(idx, fields) {
    const arr = [...draft.choices];
    arr[idx] = { ...arr[idx], ...fields };
    const next = { ...draft, choices: arr };
    setDraft(next);
    onChange && onChange(next);
  }

  function deleteChoice(idx) {
    const arr = [...draft.choices];
    arr.splice(idx, 1);
    const next = { ...draft, choices: arr };
    setDraft(next);
    onChange && onChange(next);
  }

  return (
    <div className="space-y-2">
      <textarea className="w-full p-2 border rounded" rows="3" placeholder="Question (markdown supported)" value={draft.question_markdown} onChange={e => setField("question_markdown", e.target.value)} />
      <input className="input" placeholder="Image URL (optional)" value={draft.image_url} onChange={e => setField("image_url", e.target.value)} />
      <div className="flex gap-2 items-center">
        <label className="text-sm">Max score</label>
        <input type="number" min="1" value={draft.max_score} onChange={e => setField("max_score", Number(e.target.value))} className="w-20 input" />
      </div>

      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <h4 className="font-medium">Choices</h4>
          <button onClick={addChoice} className="px-2 py-1 bg-green-600 text-white rounded">+ Choice</button>
        </div>

        {draft.choices.map((c, i) => (
          <div key={i} className="flex gap-2 items-start">
            <input type="checkbox" checked={c.is_correct} onChange={(e) => updateChoice(i, { is_correct: e.target.checked })} aria-label="Mark correct" />
            <input className="flex-1 input" placeholder={`Choice ${i + 1}`} value={c.text} onChange={(e) => updateChoice(i, { text: e.target.value })} />
            <button onClick={() => deleteChoice(i)} className="text-red-600">Delete</button>
          </div>
        ))}
      </div>

      <textarea className="w-full p-2 border rounded" rows="2" placeholder="Explanation (optional)" value={draft.explanation} onChange={e => setField("explanation", e.target.value)} />

      <div className="flex justify-end gap-2">
        <button onClick={onDelete} className="text-sm text-red-600">Delete assessment</button>
      </div>
    </div>
  );
}
