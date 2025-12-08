"use client";
import { useEffect } from "react";
import { logout } from "@/lib/apiClient";
import { useRouter } from "next/navigation";

export default function LogoutPage() {
  const router = useRouter();

  useEffect(() => {
    async function doLogout() {
      await logout();
      router.push("/");
    }
    doLogout();
  }, [router]);

  return <p>Logging out...</p>;
}
