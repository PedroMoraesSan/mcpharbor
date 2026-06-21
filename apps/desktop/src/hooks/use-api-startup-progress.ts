import { useEffect, useState } from "react";

const STEP_MS = 700;
const HOLD_MS = 550;

export function useApiStartupProgress(
  isLoading: boolean,
  isSuccess: boolean,
  stepCount = 3,
) {
  const [activeStep, setActiveStep] = useState(0);
  const [progress, setProgress] = useState(8);
  const [holding, setHolding] = useState(false);
  const maxStep = Math.max(stepCount - 1, 0);

  useEffect(() => {
    if (!isLoading) return;

    setActiveStep(0);
    setProgress(8);
    setHolding(false);

    const stepTimer = window.setInterval(() => {
      setActiveStep((current) => Math.min(current + 1, maxStep));
    }, STEP_MS);

    const progressTimer = window.setInterval(() => {
      setProgress((current) => Math.min(current + 10, 90));
    }, STEP_MS / 2);

    return () => {
      window.clearInterval(stepTimer);
      window.clearInterval(progressTimer);
    };
  }, [isLoading, maxStep]);

  useEffect(() => {
    if (isLoading || !isSuccess) return;

    setActiveStep(maxStep);
    setProgress(100);
    setHolding(true);
    const timer = window.setTimeout(() => setHolding(false), HOLD_MS);
    return () => window.clearTimeout(timer);
  }, [isLoading, isSuccess, maxStep]);

  const visible = isLoading || holding;

  return { visible, activeStep, progress };
}
