/* import Link from 'next/link'

export default function CourseList({ courses }) {
  return (
    <div>
      {courses.map(c => (
        <div key={c.id} style={{border:'1px solid #ddd', padding:12, marginBottom:8}}>
          <h3>{c.title}</h3>
          <p>{c.description}</p>
          {c.is_udemy ? (
            <a href={c.udemy_url} target="_blank" rel="noreferrer">Open on Udemy</a>
          ) : (
            <Link href={`/course/${c.slug}`}>View Course</Link>
          )}
        </div>
      ))}
    </div>
  )
}
*/