// frontend/components/CourseBuilder.jsx
"use client";

import useSWR from "swr";
import { useEffect, useState, useRef } from "react";
import { apiFetch } from "@/lib/apiClient";
import SectionEditor from "./SectionEditor";
import { toast } from "react-hot-toast";


/**
 * Props:
 *  - courseId (string|number)
 *
 * Behavior:
 *  - Loads /instructor/courses/{id} (full nested structure expected)
 *  - Maintains local state `courseDraft`
 *  - Autosave (debounced) and manual Save (PUT)
 */

export default function CourseBuilder({ courseId }) {
  const { data: serverCourse, mutate: mutateCourse } = useSWR(courseId ? `/instructor/courses/${courseId}` : null);

  /** ---------------------------
   * State separation (CRITICAL)
   * --------------------------*/
  const [courseMeta, setCourseMeta] = useState(null); // safe to save
  const [sections, setSections] = useState([]); // UI only
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const autosaveTimer = useRef(null);

  // const [courseDraft, setCourseDraft] = useState(null);
  
  /** ---------------------------
   * Initialize from server
   * --------------------------*/
  useEffect(() => {
    if (!serverCourse) return;

    setCourseMeta({
      title: serverCourse.title || "",
      slug: serverCourse.slug || "",
      description: serverCourse.description || "",
      is_udemy: !!serverCourse.is_udemy,
      udemy_url: serverCourse.udemy_url || "",
    });

    setSections(
      (serverCourse.sections || []).map((s) => ({
        id: s.id,
        title: s.title,
        order: s.order ?? 0,
        lessons: s.lessons || [],
      }))
    );
  }, [serverCourse]);


  /** ---------------------------
   * Autosave (meta only)
   * --------------------------*/
  function scheduleAutosave(nextMeta) {
    if (autosaveTimer.current) clearTimeout(autosaveTimer.current);

    autosaveTimer.current = setTimeout(() => {
      saveCourseMeta(nextMeta);
    }, 5000);
  }

  function updateMeta(updater) {
    setCourseMeta((prev) => {
      const next = { ...prev };
      updater(next);
      scheduleAutosave(next);
      return next;
    });
  }



  /** ---------------------------
   * SAVE (SAFE)
   * --------------------------*/
  async function saveCourseMeta(payload = courseMeta) {
    if (!payload?.title?.trim()) {
      setError("Course title is required.");
      return;
    }

    setSaving(true);
    setError(null);


    try {
      await apiFetch(`/instructor/courses/${courseId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });

      await mutate(); // refresh server copy
    } catch (err) {
      console.error(err);
      setError(err.message || "Save failed");
    } finally {
      setSaving(false);
    }
  }

  /** ---------------------------
   * Section UI helpers
   * --------------------------*/
  function addSection() {
    setSections((prev) => [
      ...prev,
      {
        title: `Section ${prev.length + 1}`,
        order: prev.length,
        lessons: [],
      },
    ]);
  }

  function reorderSections(index, dir) {
    setSections((prev) => {
      const next = [...prev];
      const [item] = next.splice(index, 1);
      const newIndex = dir === "up" ? index - 1 : index + 1;
      next.splice(newIndex, 0, item);
      return next.map((s, i) => ({ ...s, order: i }));
    });

  }

  async function saveSections() {
  try {
    const res = await apiFetch(`/instructor/courses/${courseId}/structure`, {
      method: "PUT",
      body: JSON.stringify({ sections }),
    });
    
    //alert("Sections saved");
    if (res.ok) {
      toast.success("Sections saved");
    }

  } catch (err) {
    console.error(err);
    alert("Failed to save sections");
    toast.error(err.message || "Failed to save sections");
  }
}


  if (!courseMeta) return <p>Loading builder...</p>;

  /** ---------------------------
   * RENDER
   * --------------------------*/
  return (
    <div className="space-y-6">
      {/* Header */}
      <header className="bg-white p-4 rounded shadow-sm">
        <input
          className="w-full text-2xl font-semibold border-b p-1"
          value={courseMeta.title}
          onChange={(e) =>
            updateMeta((m) => {
              m.title = e.target.value;
            })
          }
          placeholder="Course title"
        />

        <textarea
          className="w-full mt-3 p-2 border rounded"
          rows="3"
          value={courseMeta.description}
          onChange={(e) =>
            updateMeta((m) => {
              m.description = e.target.value;
            })
          }
          placeholder="Course description"
        />

        <div className="flex gap-3 mt-3">
          <button
            onClick={() => saveCourseMeta()}
            className="px-4 py-2 bg-primary-600 text-white rounded"
          >
            {saving ? "Saving..." : "Save"}
          </button>
        </div>
      </header>

      {/* Sections */}
      <section className="bg-white p-4 rounded shadow-sm">
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-lg font-semibold">Sections</h2>
          <button
            onClick={addSection}
            className="px-3 py-1 bg-green-600 text-white rounded"
          >
            + Section
          </button>
        </div>

        {sections.length === 0 && (
          <p className="text-gray-500">No sections yet.</p>
        )}

        <div className="space-y-4">
          {sections.map((sec, idx) => (
            <div key={idx} className="border rounded p-3">
              <div className="flex justify-between gap-3">
                <input
                  className="flex-1 font-semibold text-lg"
                  value={sec.title}
                  onChange={(e) =>
                    setSections((prev) => {
                      const next = [...prev];
                      next[idx].title = e.target.value;
                      return next;
                    })
                  }
                />

                <div className="flex gap-2">
                  <button
                    disabled={idx === 0}
                    onClick={() => reorderSections(idx, "up")}
                  >
                    ↑
                  </button>
                  <button
                    disabled={idx === sections.length - 1}
                    onClick={() => reorderSections(idx, "down")}
                  >
                    ↓
                  </button>
                  <button
                    onClick={() =>
                      setSections((prev) => prev.filter((_, i) => i !== idx))
                    }
                    className="text-red-600"
                  >
                    Delete
                  </button>
                </div>
              </div>

              <SectionEditor
                section={sec}
                onChange={(updated) =>
                  setSections((prev) => {
                    const next = [...prev];
                    next[idx] = updated;
                    return next;
                  })
                }
                onLessonAdd={(lesson) =>
                  setSections((prev) => {
                    const next = [...prev];
                    next[idx].lessons = [...next[idx].lessons, lesson];
                    return next;
                  })
                }
                onLessonDelete={(lessonIdx) =>
                  setSections((prev) => {
                    const next = [...prev];
                    next[idx].lessons = next[idx].lessons.filter((_, i) => i !== lessonIdx);
                    return next;
                  })
                }
              />
            </div>
          ))}
        </div>

        {error && <p className="text-red-600 mt-3">{error}</p>}
      </section>
      
      <button
        onClick={saveSections}
        className="px-4 py-2 bg-blue-600 text-white rounded"
      >
        Save Sections & Lessons
      </button>

      
      <footer className="text-sm text-gray-600">
        Autosave applies to course info only. Sections are saved via APIs later.
      </footer>


    </div>
  );
}
