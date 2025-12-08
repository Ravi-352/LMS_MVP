// frontend/components/CourseBuilder.jsx
"use client";

import useSWR from "swr";
import { useEffect, useState, useRef } from "react";
import { apiFetch } from "@/lib/apiClient";
import SectionEditor from "./SectionEditor";

/**
 * Props:
 *  - courseId (string|number)
 *
 * Behavior:
 *  - Loads /instructors/courses/{id} (full nested structure expected)
 *  - Maintains local state `courseDraft`
 *  - Autosave (debounced) and manual Save (PUT)
 */

export default function CourseBuilder({ courseId }) {
  const { data: serverCourse, mutate: mutateCourse } = useSWR(`/instructors/courses/${courseId}`);
  const [courseDraft, setCourseDraft] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const autosaveTimer = useRef(null);

  // initialize draft when serverCourse arrives
  useEffect(() => {
    if (serverCourse) {
      // ensure sections array exists
      const initial = {
        title: serverCourse.title || "",
        slug: serverCourse.slug || "",
        description: serverCourse.description || "",
        is_udemy: !!serverCourse.is_udemy,
        udemy_url: serverCourse.udemy_url || null,
        sections: serverCourse.sections?.map(s => ({
          id: s.id,
          title: s.title,
          order: s.order ?? 0,
          lessons: (s.lessons || []).map(l => ({
            id: l.id,
            title: l.title,
            type: l.type,
            youtube_url: l.youtube_url || null,
            pdf_url: l.pdf_url || null,
            order: l.order ?? 0,
            assessments: (l.assessments || []).map(a => ({
              id: a.id,
              question_markdown: a.question_markdown,
              image_url: a.image_url,
              max_score: a.max_score,
              explanation: a.explanation,
              choices: (a.choices || []).map(c => ({
                id: c.id,
                text: c.text,
                is_correct: !!c.is_correct,
                explanation: c.explanation,
              }))
            }))
          }))
        })) || []
      };
      setCourseDraft(initial);
    }
  }, [serverCourse]);

  // local helpers
  function updateDraft(pathUpdater) {
    setCourseDraft(prev => {
      const next = JSON.parse(JSON.stringify(prev || {})); // simple deep clone
      pathUpdater(next);
      scheduleAutosave(next);
      return next;
    });
  }

  function scheduleAutosave(nextDraft) {
    setError(null);
    if (autosaveTimer.current) clearTimeout(autosaveTimer.current);
    autosaveTimer.current = setTimeout(() => {
      handleSave(nextDraft);
    }, 5000); // 5s after last change
  }

  async function handleSave(payload = null) {
    if (!courseDraft && !payload) return;
    setSaving(true);
    setError(null);
    try {
      const body = payload || courseDraft;
      // validate minimal things
      if (!body.title || !body.title.trim()) throw new Error("Course title is required.");
      // call PUT
      await apiFetch(`/instructors/courses/${courseId}`, { method: "PUT", body });
      // refresh server state
      await mutateCourse();
    } catch (err) {
      console.error("Save failed", err);
      setError(err.message || "Save failed");
    } finally {
      setSaving(false);
    }
  }

  function addSection() {
    updateDraft(d => {
      d.sections = d.sections || [];
      d.sections.push({
        id: null,
        title: `Section ${d.sections.length + 1}`,
        order: d.sections.length,
        lessons: []
      });
    });
  }

  function reorderSections(index, dir) {
    updateDraft(d => {
      const s = d.sections.splice(index, 1)[0];
      const newIndex = index + (dir === "up" ? -1 : 1);
      d.sections.splice(newIndex, 0, s);
      d.sections.forEach((sec, i) => (sec.order = i));
    });
  }

  if (!courseDraft) return <p>Loading builder...</p>;

  return (
    <div className="space-y-6">
      <header className="bg-white p-4 rounded shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex-1">
            <input
              className="w-full text-2xl font-semibold border-b p-1"
              value={courseDraft.title}
              onChange={(e) => updateDraft(d => { d.title = e.target.value })}
              placeholder="Course title"
            />
            <input
              className="mt-2 w-full text-sm border p-2 rounded"
              value={courseDraft.slug || ""}
              onChange={(e) => updateDraft(d => { d.slug = e.target.value })}
              placeholder="slug-for-url (optional)"
            />
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => handleSave()}
              className="px-4 py-2 bg-primary-600 text-white rounded"
            >
              {saving ? "Saving..." : "Save changes"}
            </button>
            <button
              onClick={() => { setCourseDraft(serverCourse); }}
              className="px-3 py-2 border rounded"
            >
              Reset
            </button>
          </div>
        </div>

        <textarea
          className="w-full mt-3 p-2 border rounded"
          rows="3"
          placeholder="Course short description"
          value={courseDraft.description || ""}
          onChange={(e) => updateDraft(d => { d.description = e.target.value })}
        />

        <div className="flex flex-col sm:flex-row sm:items-center sm:gap-4 mt-3">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={!!courseDraft.is_udemy}
              onChange={(e) => updateDraft(d => { d.is_udemy = e.target.checked })}
            />
            Udemy (external) course
          </label>
          {courseDraft.is_udemy && (
            <input
              className="mt-2 sm:mt-0 border p-2 rounded w-full sm:w-80"
              placeholder="Udemy URL"
              value={courseDraft.udemy_url || ""}
              onChange={(e) => updateDraft(d => { d.udemy_url = e.target.value })}
            />
          )}
        </div>
      </header>

      {/* Sections list */}
      <section className="bg-white p-4 rounded shadow-sm">
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-lg font-semibold">Sections</h2>
          <div className="flex items-center gap-2">
            <button onClick={addSection} className="px-3 py-1 bg-green-600 text-white rounded">+ Section</button>
          </div>
        </div>

        {courseDraft.sections?.length === 0 && (
          <p className="text-gray-500">No sections yet. Add a section to start adding lessons.</p>
        )}

        <div className="space-y-4">
          {courseDraft.sections?.map((sec, sIdx) => (
            <div key={sIdx} className="border rounded p-3">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <input
                    className="w-full font-semibold text-lg"
                    value={sec.title}
                    onChange={(e) => updateDraft(d => { d.sections[sIdx].title = e.target.value })}
                    placeholder={`Section ${sIdx + 1}`}
                  />
                </div>

                <div className="flex gap-2 items-center">
                  <button
                    disabled={sIdx === 0}
                    onClick={() => reorderSections(sIdx, "up")}
                    className="px-2 py-1 border rounded disabled:opacity-40"
                    aria-label="Move section up"
                  >↑</button>
                  <button
                    disabled={sIdx === courseDraft.sections.length - 1}
                    onClick={() => reorderSections(sIdx, "down")}
                    className="px-2 py-1 border rounded disabled:opacity-40"
                    aria-label="Move section down"
                  >↓</button>
                  <button
                    onClick={() => updateDraft(d => { d.sections.splice(sIdx, 1); })}
                    className="px-2 py-1 text-red-600 border rounded"
                    aria-label="Delete section"
                  >Delete</button>
                </div>
              </div>

              {/* Lessons editor for this section */}
              <div className="mt-3">
                <SectionEditor
                  section={sec}
                  onChange={(newSection) => updateDraft(d => { d.sections[sIdx] = newSection })}
                  onAddLesson={(lesson) => {
                    updateDraft(d => {
                      d.sections[sIdx].lessons = d.sections[sIdx].lessons || [];
                      d.sections[sIdx].lessons.push(lesson);
                    });
                  }}
                  onDeleteLesson={(lessonIndex) => {
                    updateDraft(d => {
                      d.sections[sIdx].lessons.splice(lessonIndex, 1);
                    });
                  }}
                />
              </div>
            </div>
          ))}
        </div>

        {error && <p className="text-red-600 mt-3">{error}</p>}
      </section>

      <footer className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          Changes autosave (5s). Use Save to force immediate PUT.
        </div>
        <div className="flex gap-3">
          <button onClick={() => handleSave()} className="px-4 py-2 bg-primary-600 text-white rounded">
            Save now
          </button>
        </div>
      </footer>
    </div>
  );
}
