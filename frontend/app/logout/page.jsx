"use client";
import { useEffect } from "react";
import { logout } from "@/lib/apiClient";
import { useRouter } from "next/navigation";
import { mutate } from "swr";
import { useAuth } from "@/lib/auth/AuthProvider";

export default function LogoutPage() {
  const router = useRouter();
  const { refreshUser } = useAuth();

  useEffect(() => {
    async function doLogout() {
      try {

        await logout();
        //invalidate current user cache
        //await mutate("/auth/me", null, { revalidate: false });

        //redirect to home page
        //router.push("/");
        await refreshUser();
        router.replace("/");
        //router.refresh();
      } catch (err) {
        console.error("Logout failed:", err);
        router.replace("/");
      }
    }
    doLogout();
  }, [router]);

  return <p>Logging out...</p>;
}
