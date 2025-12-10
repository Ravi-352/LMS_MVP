// frontend/components/SWRProvider.jsx

"use client"; // REQUIRED: This ensures SWR (and React hooks like createContext) runs on the client.

import React from 'react';
import { SWRConfig } from 'swr';
// The path to your apiClient (assuming it contains the exported function apiFetch)
import { swrFetch } from '@/lib/apiClient';

export default function SWRProvider({ children }) {
  return (
    // SWRConfig provides a global context for SWR settings
    <SWRConfig
      value={{
        // Define the default fetcher function here.
        // All useSWR calls without a specific fetcher will use apiFetch.
        fetcher: swrFetch,

        // Optional: Configure common options like automatic refetch behavior
        revalidateOnFocus: true, 
        revalidateOnMount: true,
        
        //Optional: Configure error handling behavior
        onError: (err, key) => {
           console.error('SWR Error for key', key, err);
         }
      }}
    >
      {children}
    </SWRConfig>
  );
}