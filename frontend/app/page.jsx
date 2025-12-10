"use client"; // Retain this directive

import useSWR from 'swr'
// NOTE: apiFetch is no longer needed here if it's set as the default
// fetcher in the <SWRProvider> (which is the recommended fix).
import { apiFetchPublic } from '@/lib/apiClient'
import { apiFetch } from '@/lib/apiClient'
//import CourseList from '@/components/CourseList'
import Layout from "@/components/Layout";
import CourseCard from "@/components/CourseCard";


// Home Page
// Must be a synchronous function since it's a Client Component
export default function Home() {
  // Use useSWR for client-side data fetching.
  // It handles the loading, error, and data states automatically.
  const { 
    data: courses, 
    error, 
    isLoading 
  } = useSWR("/public/courses", apiFetchPublic);

  // Handle loading state
  if (isLoading) {
    return (
      
        <div className="text-center py-10">Loading courses...</div>
      
    );
  }

  // Handle error state
  if (error) {
    return (
      
        <div className="text-red-500 py-10">
          Failed to load courses. Please check the backend API.
        </div>
      
    );
  }

  // Use the fetched data (courses will be undefined/null on initial fetch, 
  // so provide a fallback empty array if needed, though SWR is smart)
  const courseList = courses || [];

  if (!courseList.length) {
    return (
      <section className="max-w-5xl mx-auto py-10 text-center">
        <h1 className="text-xl font-bold mb-4">Courses</h1>
        <p>No courses available right now. Please check again later.</p>
      </section>
    );
  }

  return (
    <section>
      <h1 className="text-2xl font-bold mb-4">All Courses</h1>
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
        {courseList.map(c => <CourseCard key={c.id} course={c} />)}
      </div>
    </section>
  );
}


// keep below commented --->

/*
"use client";
import useSWR from 'swr'
//import { apiFetch } from '@/lib/apiClient'
//import { apiFetch } from '@/lib/apiClient'
import CourseList from '@/components/CourseList'
import Layout from "@/components/Layout";
import CourseCard from "@/components/CourseCard";


// Home Page
export default async function Home() {
  let courses = [];
  try {
    courses = await apiFetch("/public/courses");
  } catch (e) {
    console.error("Failed to fetch courses", e);
  }
  return (
    <Layout>
      <h1 className="text-2xl font-bold mb-4">All Courses</h1>
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
        {courses.map(c => <CourseCard key={c.id} course={c} />)}
      </div>
    </Layout>
  );
} */