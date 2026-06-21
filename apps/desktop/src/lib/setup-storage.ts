const SETUP_COMPLETE_KEY = "mcpharbour:setup-complete";

export function isSetupComplete(): boolean {
  try {
    return localStorage.getItem(SETUP_COMPLETE_KEY) === "1";
  } catch {
    return false;
  }
}

export function markSetupComplete(): void {
  try {
    localStorage.setItem(SETUP_COMPLETE_KEY, "1");
  } catch {
    // ignore storage failures in restricted environments
  }
}
