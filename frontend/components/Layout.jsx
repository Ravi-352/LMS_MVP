"use client";
import Link from "next/link";
import React, { useState } from "react";
import { useCurrentUser } from "@/lib/hooks/useCurrentUser";

export default function Layout({ children }) {
  const [open, setOpen] = useState(false);
  const { user, isLoading } = useCurrentUser();
  return (
    <div>
      <header className="bg-white border-b shadow-sm sticky top-0 z-50">
        <div className="container flex items-center justify-between py-3">
          <Link href="/" className="text-xl font-bold text-primary-500">EduTech</Link>
            
          <div className="md:hidden">
            <button className="p-2" onClick={() => setOpen(!open)} aria-label="Open menu">☰</button>
          </div>

          <nav className="hidden md:flex gap-6 items-center">
            <Link href="/" className="text-sm">Courses</Link>
            {user ? (
              <>
                {user.is_educator ? (
                  <Link href="/instructor/dashboard" className="text-sm">Instructor</Link>
                ) : (
                  <Link href="/student/dashboard" className="text-sm">Student</Link>
                )}

                <Link href="/logout" className="text-sm text-primary-500 font-medium">Logout</Link>
              </>
            ) : (
              <>
                <Link href="/login" className="text-sm text-primary-500 font-medium">Login</Link>
                <Link href="/signup" className="text-sm text-primary-500 font-medium">Sign Up</Link>
              </>
            )}
           
          </nav>
        </div>

        {open && (
          <div className="md:hidden bg-white border-t p-4 space-y-3">
            <Link href="/">Courses</Link>
            {user ? (
              <>
                {user.is_educator ? (
                  <Link href="/instructor/dashboard" className="text-sm">Instructor</Link>
                ) : (
                  <Link href="/student/dashboard" className="text-sm">Student</Link>
                )}

                <Link href="/logout">Logout</Link>
              </>
            ) : (
              <>
                <Link href="/login">Login</Link>
                <Link href="/signup">Sign Up</Link>
              </>
            )}
            
          </div>
        )}
      </header>

      <main className="container py-6">{children}</main>

      <footer className="container text-center text-sm text-gray-500 py-6">
        © {new Date().getFullYear()} EduTech — Built with ❤️
      </footer>
    </div>
  );
}
