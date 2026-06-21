import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";

export function useBackendReady() {
  return useQuery({
    queryKey: ["health"],
    queryFn: api.health,
    retry: 30,
    retryDelay: (attempt) => Math.min(1000 * (attempt + 1), 3000),
    refetchOnWindowFocus: false,
  });
}
