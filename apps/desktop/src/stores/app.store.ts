import { create } from "zustand";

interface InstallWizardState {
  catalogId: string | null;
  steps: { label: string; done: boolean }[];
  progress: number;
  isOpen: boolean;
  setCatalogId: (id: string | null) => void;
  setSteps: (steps: { label: string; done: boolean }[]) => void;
  setProgress: (progress: number) => void;
  setOpen: (open: boolean) => void;
  reset: () => void;
}

export const useInstallWizard = create<InstallWizardState>((set) => ({
  catalogId: null,
  steps: [],
  progress: 0,
  isOpen: false,
  setCatalogId: (catalogId) => set({ catalogId }),
  setSteps: (steps) => set({ steps }),
  setProgress: (progress) => set({ progress }),
  setOpen: (isOpen) => set({ isOpen }),
  reset: () =>
    set({ catalogId: null, steps: [], progress: 0, isOpen: false }),
}));

interface AppState {
  searchQuery: string;
  setSearchQuery: (q: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  searchQuery: "",
  setSearchQuery: (searchQuery) => set({ searchQuery }),
}));
