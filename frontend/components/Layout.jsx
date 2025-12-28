"use client";
import Link from "next/link";
import React, { useEffect, useState, useRef } from "react";
import { useCurrentUser } from "@/lib/hooks/useCurrentUser";
import { usePathname, useRouter } from "next/navigation";


// inside component:




export default function Layout({ children }) {
  const pathname = usePathname();
  const router = useRouter();
  const isProtected =
    pathname.startsWith("/student") ||
    pathname.startsWith("/instructor");

  // Always call hooks FIRST
  //const { user, isLoading } = isProtected ? useCurrentUser() : { user: null, isLoading: false };
  const { user, isLoading } = useCurrentUser();

  const [open, setOpen] = useState(false); // MUST stay above any condition return

  // Handle Loading States
  // While checking for a user on a protected page, show a loader
  if (isProtected && isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
        <span className="ml-3">Verifying session...</span>
      </div>
    );
  }

  // Redirect unauthenticated users on protected routes
  useEffect(() => {
    if (!isLoading && isProtected && !user) {
      router.replace("/login");
    }
  }, [user, isLoading, isProtected, router]);

  // Avoid rendering protected content briefly
  if (isProtected && !user) {
    return null;
  }

  //if (isProtected && !isLoading && !user && pathname !== "/login") {
  //if (isProtected && !isLoading && !user) {
  // redirect to login
  //  if (typeof window !== "undefined") {
  //    window.location.href = "/login";
  //    }
  //  return null;
  //}


  
  //const finalUser = isProtected ? user : null;
  

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
                <Link
                  href={
                    user.is_educator
                      ? "/instructor/dashboard"
                      : "/student/dashboard"
                  }
                  className="text-sm"
                >
                  {user.is_educator ? "Instructor" : "Student"}
                </Link>


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
                <Link
                  href={
                    user.is_educator
                      ? "/instructor/dashboard"
                      : "/student/dashboard"
                  }
                >
                  {user.is_educator ? "Instructor" : "Student"}
                </Link>

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
        © {new Date().getFullYear()} All Rights Reserved. EduTech — Built with ❤️
      </footer>
    </div>
  );
}
