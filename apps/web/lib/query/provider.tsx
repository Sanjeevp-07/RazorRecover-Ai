"use client";

import { ReactNode, useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

export function QueryProvider({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 0, // Real-time: always fresh on navigation
            gcTime: 10 * 60 * 1000, // 10 minutes memory retention
            refetchOnWindowFocus: true, // Auto-update when returning to tab
            refetchOnMount: true, // Auto-update every time page is visited
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
