// frontend/components/SectionEditor.jsx
"use client";

import { useState } from "react";
import LessonEditor from "./LessonEditor";

export default function SectionEditor({ section, onChange, onLessonAdd, onLessonDelete }) {
  const [editingIndex, setEditingIndex] = useState(null);

  function addLessonTemplate() {
    return {
      id: null,
      title: "New lesson",
      type: "video",
      youtube_url: "",
      pdf_url: "",
      order: (section.lessons?.length || 0),
      assessments: []
    };
  }

  function handleAddLesson() {
    const newLesson = addLessonTemplate();
    onLessonAdd(newLesson);
    // open editor for the newly added lesson (last index)
    setEditingIndex((section.lessons?.length || 0));
  }

  function moveLesson(idx, dir) {
    onChange(prev => {
      // prev is section object? We accept onChange to set entire section externally.
    });
    // simpler: we emit change via onChange with re-ordered lessons
    const lessons = [...(section.lessons || [])];
    const [item] = lessons.splice(idx, 1);
    lessons.splice(idx + (dir === "up" ? -1 : 1), 0, item);
    lessons.forEach((l, i) => (l.order = i));
    onChange({ ...section, lessons });
  }

  function updateLesson(idx, updatedLesson) {
    const lessons = [...(section.lessons || [])];
    lessons[idx] = updatedLesson;
    onChange({ ...section, lessons });
  }

  function deleteLesson(idx) {
    if (!confirm("Delete this lesson? This will remove all related assessments and student progress.")) return;
    onDeleteLesson(idx);
  }

  return (
    <div className="space-y-3">
      {(section.lessons || []).map((l, idx) => (
        <div key={idx} className="border p-3 rounded flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <div className="font-medium">{l.title || "Untitled lesson"}</div>
            <div className="text-sm text-gray-600">{l.type} • {l.youtube_url ? "YouTube" : l.pdf_url ? "PDF" : "—"}</div>
          </div>

          <div className="flex items-center gap-2">
            <button disabled={idx === 0} onClick={() => moveLesson(idx, "up")} className="px-2 py-1 border rounded">↑</button>
            <button disabled={idx === (section.lessons.length - 1)} onClick={() => moveLesson(idx, "down")} className="px-2 py-1 border rounded">↓</button>

            <button onClick={() => setEditingIndex(idx)} className="px-3 py-1 bg-blue-600 text-white rounded">Edit</button>
            <button onClick={() => deleteLesson(idx)} className="px-2 py-1 border text-red-600 rounded">Delete</button>
          </div>

          {editingIndex === idx && (
            //<div className="mt-3 w-full">
              <LessonEditor
                lesson={l}
                onCancel={() => setEditingIndex(null)}
                onSave={(updated) => { updateLesson(idx, updated); setEditingIndex(null); }}
              />
            //</div>
          )}
        </div>
      ))}

      <div>
        <button onClick={handleAddLesson} className="px-3 py-2 bg-green-600 text-white rounded">+ Add lesson</button>
      </div>
    </div>
  );
}
