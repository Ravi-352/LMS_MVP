"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/apiClient";

export default function NewCoursePage() {
  const router = useRouter();

  const [form, setForm] = useState({
    title: "",
    description: "",
    is_udemy: false,
    udemy_url: "",
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleCourseType = (isUdemy) => {
    setForm({
      ...form,
      is_udemy: isUdemy,
      udemy_url: isUdemy ? form.udemy_url : "",
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      title: form.title,
      description: form.description,
      is_udemy: form.is_udemy,
      udemy_url: form.is_udemy ? form.udemy_url : null,
    };

    try {
      await apiFetch("/instructor/courses", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      alert("Course created!");
      router.push("/instructor/dashboard");
    } catch (err) {
      alert("Error creating course");
      console.error(err);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Create New Course</h1>

      {/* Course Type Selection */}
      <div className="flex gap-4 mb-4">
        <button
          className={`px-3 py-2 border rounded ${
            !form.is_udemy ? "bg-primary-500 text-white" : ""
          }`}
          type="button"
          onClick={() => handleCourseType(false)}
        >
          Self-Hosted Course
        </button>

        <button
          className={`px-3 py-2 border rounded ${
            form.is_udemy ? "bg-primary-500 text-white" : ""
          }`}
          type="button"
          onClick={() => handleCourseType(true)}
        >
          Udemy External Course
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">

        {/* Common Fields */}
        <input
          type="text"
          name="title"
          placeholder="Course title"
          className="w-full border p-2 rounded"
          value={form.title}
          onChange={handleChange}
          required
        />

        <textarea
          name="description"
          placeholder="Course description"
          className="w-full border p-2 rounded"
          rows="4"
          value={form.description}
          onChange={handleChange}
        />

        {/* Conditional Fields */}
        {form.is_udemy ? (
          <input
            type="url"
            name="udemy_url"
            placeholder="Udemy Course URL"
            className="w-full border p-2 rounded"
            value={form.udemy_url}
            onChange={handleChange}
            required
          />
        ) : (
          <p className="text-sm text-gray-600">
            After creating the course, you can add lessons, videos, PDFs and quizzes.
          </p>
        )}

        <button className="w-full bg-primary text-white py-2 rounded">
          Create Course
        </button>
      </form>
    </div>
  );
}
