export default function SidebarLessons({ course, selectedLessonId, onSelect, isEnrolled }) {
  if (!course) return null;
  const previewId = course.sections?.[0]?.lessons?.[0]?.id;
  return (
    <aside className="hidden md:block w-64 sticky top-24">
      {course.sections.map(sec => (
        <div key={sec.id} className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">{sec.title}</h4>
          <ul className="space-y-1">
            {sec.lessons.map(lesson => {
              const locked = !isEnrolled && lesson.id !== previewId;
              return (
                <li key={lesson.id}>
                  <button
                    onClick={() => { if (!locked) onSelect(lesson); }}
                    className={`w-full text-left px-2 py-2 rounded ${selectedLessonId === lesson.id ? 'bg-gray-100' : 'hover:bg-gray-50'}`}
                  >
                    {lesson.title} {locked ? <span className="text-sm text-gray-400">🔒</span> : null}
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </aside>
  );
}
