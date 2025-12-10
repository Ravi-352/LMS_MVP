// lib/hooks/useCurrentUser.js
"use client";
import useSWR from "swr";
import { apiFetch } from "@/lib/apiClient";

export function useCurrentUser() {
  const { data, error, isLoading, mutate } = useSWR(
    "/auth/me",
    apiFetch,
    { shouldRetryOnError: false }
  );

  return {
    user: data || null,
    isLoading: isLoading,
    mutateUser: mutate,
    error: error,
  };
}
