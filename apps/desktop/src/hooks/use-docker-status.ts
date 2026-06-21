import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";

export function useDockerStatus() {
  return useQuery({
    queryKey: ["settings"],
    queryFn: api.settings,
    refetchInterval: 10_000,
    select: (settings) => ({
      running: settings.docker_running,
      message: settings.docker_message,
      socket: settings.docker_socket,
    }),
  });
}
