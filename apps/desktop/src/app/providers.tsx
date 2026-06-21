import { QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "react-router-dom";
import { BackendGate } from "@/components/BackendGate";
import { queryClient } from "@/lib/query-client";
import { router } from "@/app/router";

export function Providers() {
  return (
    <QueryClientProvider client={queryClient}>
      <BackendGate>
        <RouterProvider router={router} />
      </BackendGate>
    </QueryClientProvider>
  );
}
