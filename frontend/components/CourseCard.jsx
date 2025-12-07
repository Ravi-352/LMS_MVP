import Link from "next/link";

export default function CourseCard({ course }) {
  return (
    <div className="card hover:shadow-md transition">
      <div className="flex items-start gap-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold">{course.title}</h3>
          <p className="text-gray-600 mt-2 line-clamp-2">{course.description}</p>
          <div className="mt-4">
            <Link href={`/course/${course.slug}`} className="inline-block bg-primary-500 text-white px-4 py-2 rounded-md">View course</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
