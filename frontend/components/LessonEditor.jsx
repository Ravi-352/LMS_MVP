// frontend/components/LessonEditor.jsx
"use client";

import { useState } from "react";
import AssessmentEditor from "./AssessmentEditor";

export default function LessonEditor({ lesson = {}, onSave, onCancel }) {
  const [draft, setDraft] = useState({
    id: lesson.id ?? null,
    title: lesson.title ?? "",
    type: lesson.type ?? "video",
    youtube_url: lesson.youtube_url ?? "",
    pdf_url: lesson.pdf_url ?? "",
    order: lesson.order ?? 0,
    assessments: lesson.assessments ? [...lesson.assessments] : []
  });

  function setField(k, v) {
    setDraft(prev => ({ ...prev, [k]: v }));
  }

  function addAssessment() {
    setDraft(prev => ({
      ...prev,
      assessments: [
        ...(prev.assessments || []),
        {
          id: null,
          question_markdown: "",
          image_url: null,
          max_score: 1,
          explanation: "",
          choices: []
        }
      ]
    }));
  }

  function updateAssessment(index, newAss) {
    const arr = [...(draft.assessments || [])];
    arr[index] = newAss;
    setDraft(prev => ({ ...prev, assessments: arr }));
  }

  function deleteAssessment(index) {
    const arr = [...(draft.assessments || [])];
    arr.splice(index, 1);
    setDraft(prev => ({ ...prev, assessments: arr }));
  }

  function save() {
    // basic validation
    if (!draft.title || !draft.title.trim()) {
      alert("Lesson title is required");
      return;
    }
    if (draft.type === "video" && !draft.youtube_url) {
      alert("YouTube URL required for video lessons");
      return;
    }
    if (draft.type === "pdf" && !draft.pdf_url) return alert("PDF URL required");
    onSave && onSave(draft);
  }

  return (
    <div className="bg-gray-50 p-3 rounded">
      <div className="space-y-2">
        <input className="input" value={draft.title} onChange={(e) => setField("title", e.target.value)} placeholder="Lesson title" />
        <div className="flex gap-3 items-center">
          <label className="flex items-center gap-2">
            <input type="radio" checked={draft.type === "video"} onChange={() => setField("type", "video")} /> Video
          </label>
          <label className="flex items-center gap-2">
            <input type="radio" checked={draft.type === "pdf"} onChange={() => setField("type", "pdf")} /> PDF
          </label>
        </div>

        {draft.type === "video" && (
          <>
            <input className="input" value={draft.youtube_url} onChange={(e) => setField("youtube_url", e.target.value)} placeholder="YouTube watch URL (https://www.youtube.com/watch?v=...)" />
            {/* preview */}
            {draft.youtube_url && (
              <div className="mt-2 w-full aspect-video">
                <iframe
                  src={draft.youtube_url.replace("watch?v=", "embed/")}
                  title={draft.title}
                  className="w-full h-full rounded"
                  frameBorder="0"
                  allowFullScreen
                />
              </div>
            )}
          </>
        )}

        {draft.type === "pdf" && (
          <>
            <input className="input" value={draft.pdf_url} onChange={(e) => setField("pdf_url", e.target.value)} placeholder="PDF public URL" />
            {draft.pdf_url && (
              <div className="mt-2">
                <iframe src={draft.pdf_url} className="w-full h-96" title="PDF preview" />
              </div>
            )}
          </>
        )}

        {/* Assessments */}
        <div className="mt-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Assessments</h3>
            <button onClick={addAssessment} className="px-2 py-1 bg-indigo-600 text-white rounded">+ Add</button>
          </div>

          <div className="mt-2 space-y-2">
            {(draft.assessments || []).map((a, i) => (
              <div key={i} className="border p-2 rounded">
                <AssessmentEditor
                  assessment={a}
                  onChange={(updated) => updateAssessment(i, updated)}
                  onDelete={() => deleteAssessment(i)}
                />
              </div>
            ))}
            {!draft.assessments?.length && <p className="text-sm text-gray-500">No assessments yet for this lesson.</p>}
          </div>
        </div>

        <div className="flex gap-2 justify-end mt-3">
          <button onClick={onCancel} className="px-3 py-1 border rounded">Cancel</button>
          <button onClick={save} className="px-3 py-1 bg-green-600 text-white rounded">Save lesson</button>
        </div>
      </div>
    </div>
  );
}
