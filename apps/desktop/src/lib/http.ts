import { isTauri } from "@tauri-apps/api/core";

const DEFAULT_API = "http://127.0.0.1:8741";

export function getApiBaseUrl(): string {
  return import.meta.env.VITE_API_BASE_URL || DEFAULT_API;
}

type FetchInit = RequestInit & { connectTimeout?: number };

export async function httpFetch(
  input: string,
  init?: FetchInit,
): Promise<Response> {
  if (isTauri()) {
    const { fetch: tauriFetch } = await import("@tauri-apps/plugin-http");
    return tauriFetch(input, init);
  }

  return fetch(input, init);
}
