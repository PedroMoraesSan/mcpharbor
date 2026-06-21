import { isTauri } from "@tauri-apps/api/core";
import { getVersion } from "@tauri-apps/api/app";

export type UpdateInfo = {
  currentVersion: string;
  nextVersion: string;
  notes?: string;
  date?: string;
};

export async function getAppVersion(): Promise<string | null> {
  if (!isTauri()) {
    return null;
  }
  return getVersion();
}

export async function checkForAppUpdate(): Promise<UpdateInfo | null> {
  if (!isTauri()) {
    return null;
  }

  const { check } = await import("@tauri-apps/plugin-updater");
  const update = await check();

  if (!update) {
    return null;
  }

  return {
    currentVersion: update.currentVersion,
    nextVersion: update.version,
    notes: update.body ?? undefined,
    date: update.date ?? undefined,
  };
}

export async function installAppUpdate(): Promise<void> {
  if (!isTauri()) {
    return;
  }

  const { check } = await import("@tauri-apps/plugin-updater");
  const { relaunch } = await import("@tauri-apps/plugin-process");
  const update = await check();

  if (!update) {
    return;
  }

  await update.downloadAndInstall();
  await relaunch();
}
