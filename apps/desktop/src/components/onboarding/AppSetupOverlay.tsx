import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  CheckCircle2,
  Circle,
  ExternalLink,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { HarborLogo } from "@/components/brand/harbor-logo";
import { AppIcon } from "@/components/icons/app-icon";
import { Button } from "@/components/ui/button";
import { StatusIndicator } from "@/components/status/StatusIndicator";
import { useDockerStatus } from "@/hooks/use-docker-status";
import { isSetupComplete, markSetupComplete } from "@/lib/setup-storage";
import { cn } from "@/lib/utils";

const STEPS = [
  { id: "welcome", label: "Welcome" },
  { id: "docker", label: "Docker" },
  { id: "install", label: "Install" },
  { id: "verify", label: "Verify" },
  { id: "ready", label: "Ready" },
] as const;

type StepId = (typeof STEPS)[number]["id"];

const DOCKER_DOWNLOAD_URL = "https://docs.docker.com/desktop/setup/install/mac-install/";

/* ── slide direction based on navigation ─────────────────────────── */
const SLIDE = {
  enter: (dir: number) => ({ x: dir * 32, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit: (dir: number) => ({ x: dir * -32, opacity: 0 }),
};

export function AppSetupOverlay() {
  const [visible, setVisible] = useState(() => !isSetupComplete());
  const [stepIndex, setStepIndex] = useState(0);
  const [direction, setDirection] = useState(1);
  const [isAdvancing, setIsAdvancing] = useState(false);
  const { data: docker, refetch, isFetching } = useDockerStatus();
  const dockerReady = docker?.running === true;

  /* refs for animated connector lines */
  const prevIndex = useRef(stepIndex);

  useEffect(() => {
    if (!visible || stepIndex !== 2 || !dockerReady) return;
    prevIndex.current = stepIndex;
    setDirection(1);
    setStepIndex(3);
  }, [visible, stepIndex, dockerReady]);

  if (!visible) return null;

  const step = STEPS[stepIndex];
  const isLastStep = stepIndex === STEPS.length - 1;
  const canAdvance =
    step.id === "welcome" ||
    step.id === "docker" ||
    step.id === "install" ||
    (step.id === "verify" && dockerReady) ||
    step.id === "ready";

  const finish = () => {
    setIsAdvancing(true);
    markSetupComplete();
    window.setTimeout(() => {
      setVisible(false);
      setIsAdvancing(false);
    }, 650);
  };

  const goNext = () => {
    if (isLastStep) {
      finish();
      return;
    }
    if (step.id === "verify" && !dockerReady) return;
    prevIndex.current = stepIndex;
    setDirection(1);
    setStepIndex((i) => Math.min(i + 1, STEPS.length - 1));
  };

  const goBack = () => {
    if (stepIndex === 0 || isAdvancing) return;
    prevIndex.current = stepIndex;
    setDirection(-1);
    setStepIndex((i) => Math.max(i - 1, 0));
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-background/90 p-4 backdrop-blur-md">
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 12 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.25, 0.46, 0.45, 0.94] }}
        className="console-floating-surface w-full max-w-2xl rounded-3xl border border-border/60 p-6 shadow-2xl sm:p-8"
      >
        {/* ── Stepper header ─────────────────────────────────────── */}
        <div className="mb-8 flex items-center justify-center gap-1 sm:gap-2">
          {STEPS.map((item, index) => {
            const done = index < stepIndex || (index === 3 && dockerReady && stepIndex > 3);
            const active = index === stepIndex;

            return (
              <div key={item.id} className="flex items-center gap-1 sm:gap-2">
                <div className="flex flex-col items-center gap-1">
                  {/* Step circle */}
                  <motion.div
                    animate={
                      done
                        ? { scale: [1, 1.15, 1], backgroundColor: "var(--primary)" }
                        : active
                          ? { scale: [1, 1.05, 1] }
                          : { scale: 1 }
                    }
                    transition={{ duration: 0.4, ease: "easeOut" }}
                    className={cn(
                      "flex h-8 w-8 items-center justify-center rounded-full border text-xs font-mono transition-colors duration-300",
                      done &&
                        "border-primary bg-primary text-primary-foreground",
                      active &&
                        !done &&
                        "border-primary text-primary ring-2 ring-primary/25",
                      !done && !active && "border-border text-muted-foreground",
                    )}
                  >
                    <AnimatePresence mode="wait" initial={false}>
                      {done ? (
                        <motion.span
                          key="check"
                          initial={{ scale: 0, rotate: -45 }}
                          animate={{ scale: 1, rotate: 0 }}
                          exit={{ scale: 0 }}
                          transition={{ duration: 0.25 }}
                        >
                          <CheckCircle2 className="h-4 w-4" />
                        </motion.span>
                      ) : (
                        <motion.span
                          key="num"
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          exit={{ scale: 0 }}
                          transition={{ duration: 0.2 }}
                        >
                          {index + 1}
                        </motion.span>
                      )}
                    </AnimatePresence>
                  </motion.div>

                  {/* Step label */}
                  <span
                    className={cn(
                      "hidden text-[10px] uppercase tracking-wider transition-colors duration-300 sm:block",
                      active ? "text-primary" : "text-muted-foreground",
                    )}
                  >
                    {item.label}
                  </span>
                </div>

                {/* Connector line */}
                {index < STEPS.length - 1 ? (
                  <div className="relative mb-4 h-px w-6 overflow-hidden rounded-full bg-border sm:w-10">
                    <motion.div
                      className="absolute inset-y-0 left-0 bg-primary"
                      initial={{ width: "0%" }}
                      animate={{ width: index < stepIndex ? "100%" : "0%" }}
                      transition={{ duration: 0.4, ease: "easeInOut" }}
                    />
                  </div>
                ) : null}
              </div>
            );
          })}
        </div>

        {/* ── Step content (animated slide) ──────────────────────── */}
        <div className="relative overflow-hidden" style={{ minHeight: 260 }}>
          <AnimatePresence mode="wait" custom={direction} initial={false}>
            <motion.div
              key={step.id}
              custom={direction}
              variants={SLIDE}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.28, ease: [0.25, 0.46, 0.45, 0.94] }}
            >
              <StepContent
                stepId={step.id}
                dockerReady={dockerReady}
                docker={docker}
                isFetching={isFetching}
                onRefetch={refetch}
                onFinish={finish}
              />
            </motion.div>
          </AnimatePresence>
        </div>

        <div className="mt-6 space-y-2">
          <div className="h-1 overflow-hidden rounded-full bg-border">
            <motion.div
              className="h-full bg-primary"
              initial={{ width: "0%" }}
              animate={{ width: `${((stepIndex + 1) / STEPS.length) * 100}%` }}
              transition={{ duration: 0.45, ease: "easeOut" }}
            />
          </div>
          <p className="text-center text-xs text-muted-foreground">
            Step {stepIndex + 1} of {STEPS.length} · {step.label}
          </p>
        </div>

        {/* ── Navigation buttons ──────────────────────────────────── */}
        <div className="mt-8 flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-between">
          <Button
            type="button"
            variant="ghost"
            onClick={goBack}
            disabled={stepIndex === 0 || isAdvancing}
            className="gap-2.5 px-5 sm:w-auto"
          >
            Back
          </Button>

          <div className="flex flex-col gap-2 sm:flex-row">
            {isLastStep ? (
              <>
                <Button asChild variant="secondary" disabled={isAdvancing} className="gap-2.5 px-5">
                  <Link to="/catalog" onClick={finish}>
                    Open Catalog
                  </Link>
                </Button>
                <Button
                  type="button"
                  onClick={finish}
                  disabled={isAdvancing}
                  className="gap-2.5 px-5"
                >
                  {isAdvancing ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Entering Harbor…
                    </>
                  ) : (
                    <>
                      Enter Harbor
                      <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </Button>
              </>
            ) : (
              <Button type="button" onClick={goNext} disabled={!canAdvance || isAdvancing} className="gap-2.5 px-5">
                {isAdvancing ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Loading…
                  </>
                ) : step.id === "verify" && !dockerReady ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Waiting for Docker…
                  </>
                ) : (
                  <>
                    Continue
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   Step content panels
══════════════════════════════════════════════════════════════════ */

type DockerData = { running?: boolean; message?: string; socket?: string | null } | undefined;

function StepContent({
  stepId,
  dockerReady,
  docker,
  isFetching,
  onRefetch,
  onFinish,
}: {
  stepId: StepId;
  dockerReady: boolean;
  docker: DockerData;
  isFetching: boolean;
  onRefetch: () => void;
  onFinish: () => void;
}) {
  switch (stepId) {
    case "welcome":
      return <WelcomeStep />;
    case "docker":
      return <DockerWhyStep />;
    case "install":
      return <InstallStep />;
    case "verify":
      return (
        <VerifyStep
          dockerReady={dockerReady}
          docker={docker}
          isFetching={isFetching}
          onRefetch={onRefetch}
        />
      );
    case "ready":
      return <ReadyStep onFinish={onFinish} />;
  }
}

function WelcomeStep() {
  return (
    <div className="space-y-5 text-center">
      <motion.div
        initial={{ scale: 0.7, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.05, duration: 0.4, type: "spring", stiffness: 260, damping: 20 }}
        className="mx-auto flex h-20 w-20 items-center justify-center rounded-2xl border border-primary/30 bg-primary/10"
      >
        <HarborLogo size={48} className="text-primary" />
      </motion.div>
      <div>
        <h2 className="font-display text-2xl uppercase tracking-wider">Welcome to MCP Harbor</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Your control plane for MCP servers — install, configure credentials, and connect to AI
          clients without touching the terminal.
        </p>
      </div>
      <div className="grid gap-3 text-left sm:grid-cols-3">
        {[
          { title: "Catalog", body: "Pick MCP servers to install" },
          { title: "Credentials", body: "Store secrets in the OS keyring" },
          { title: "Integrations", body: "Wire MCPs into Cursor & Claude" },
        ].map((item, i) => (
          <motion.div
            key={item.title}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.07, duration: 0.3 }}
            className="rounded-xl border border-border/50 bg-secondary/20 px-3 py-3 text-sm"
          >
            <div className="font-medium">{item.title}</div>
            <div className="mt-1 text-muted-foreground">{item.body}</div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function DockerWhyStep() {
  return (
    <div className="space-y-5">
      <div className="flex items-start gap-4">
        <motion.div
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.05, type: "spring", stiffness: 300, damping: 22 }}
        >
          <AppIcon kind="docker" size={40} branded className="text-[#2496ED]" />
        </motion.div>
        <div>
          <h2 className="font-display text-xl uppercase tracking-wider">Docker is required</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            MCP Harbor runs each server inside a Docker container. You need Docker Desktop installed
            and running before installing MCPs from the catalog.
          </p>
        </div>
      </div>
      <ul className="space-y-2 text-sm text-muted-foreground">
        {[
          "Pulls container images when you install an MCP",
          "Starts and stops MCP runtimes on demand",
          "Keeps credentials out of containers via the Harbor wrapper",
        ].map((text, i) => (
          <motion.li
            key={text}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 + i * 0.07, duration: 0.3 }}
            className="flex items-start gap-2"
          >
            <Circle className="mt-1 h-3 w-3 shrink-0 text-primary" />
            {text}
          </motion.li>
        ))}
      </ul>
    </div>
  );
}

function InstallStep() {
  const steps = [
    "Download Docker Desktop for Mac (Apple Silicon or Intel).",
    "Open the .dmg and drag Docker to Applications.",
    "Launch Docker Desktop from Applications.",
    "Wait until the whale icon in the menu bar shows Docker is running.",
  ];

  return (
    <div className="space-y-5">
      <div className="flex items-start gap-4">
        <motion.div
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.05, type: "spring", stiffness: 300, damping: 22 }}
        >
          <AppIcon kind="docker" size={40} branded />
        </motion.div>
        <div>
          <h2 className="font-display text-xl uppercase tracking-wider">Install Docker Desktop</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            If Docker is not installed yet, follow these steps on macOS. Already installed? Open
            Docker Desktop and continue to verification.
          </p>
        </div>
      </div>
      <ol className="space-y-3 text-sm">
        {steps.map((text, i) => (
          <motion.li
            key={text}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08 + i * 0.07, duration: 0.3 }}
            className="flex gap-3 rounded-xl border border-border/50 bg-secondary/20 px-3 py-3"
          >
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/15 font-mono text-xs text-primary">
              {i + 1}
            </span>
            <span className="text-muted-foreground">{text}</span>
          </motion.li>
        ))}
      </ol>
      <Button asChild variant="secondary" className="w-full gap-2.5 px-5 sm:w-auto">
        <a href={DOCKER_DOWNLOAD_URL} target="_blank" rel="noreferrer">
          Download Docker Desktop
          <ExternalLink className="h-4 w-4" />
        </a>
      </Button>
    </div>
  );
}

function VerifyStep({
  dockerReady,
  docker,
  isFetching,
  onRefetch,
}: {
  dockerReady: boolean;
  docker: DockerData;
  isFetching: boolean;
  onRefetch: () => void;
}) {
  return (
    <div className="space-y-5">
      <div className="flex items-start gap-4">
        <motion.div
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.05, type: "spring", stiffness: 300, damping: 22 }}
        >
          <AppIcon kind="docker" size={40} branded />
        </motion.div>
        <div>
          <h2 className="font-display text-xl uppercase tracking-wider">
            Verify Docker is running
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            We check the Docker engine automatically. When the status below is green, you can
            continue.
          </p>
        </div>
      </div>

      <motion.div
        animate={dockerReady ? { borderColor: "var(--primary)" } : {}}
        transition={{ duration: 0.4 }}
        className={cn(
          "rounded-2xl border px-4 py-4",
          dockerReady ? "border-primary/30 bg-primary/5" : "border-warning/30 bg-warning/5",
        )}
      >
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-sm font-medium">
              {dockerReady ? "Docker is ready" : "Waiting for Docker"}
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              {docker?.message ??
                "Open Docker Desktop and wait until the engine finishes starting."}
            </p>
            {docker?.socket ? (
              <p className="mt-2 font-mono text-xs text-muted-foreground">{docker.socket}</p>
            ) : null}
          </div>
          <StatusIndicator status={dockerReady ? "running" : "stopped"} />
        </div>
      </motion.div>

      <Button
        type="button"
        variant="outline"
        onClick={onRefetch}
        disabled={isFetching}
        className="w-full gap-2.5 px-5 sm:w-auto"
      >
        {isFetching ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <RefreshCw className="h-4 w-4" />
        )}
        Check again
      </Button>
    </div>
  );
}

function ReadyStep({ onFinish: _onFinish }: { onFinish: () => void }) {
  return (
    <div className="space-y-5 text-center">
      <motion.div
        initial={{ scale: 0, rotate: -30 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ delay: 0.05, type: "spring", stiffness: 280, damping: 18 }}
        className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/15"
      >
        <CheckCircle2 className="h-8 w-8 text-primary" />
      </motion.div>
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.18, duration: 0.35 }}
      >
        <h2 className="font-display text-2xl uppercase tracking-wider">You are all set</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Docker is running. Head to the catalog to install your first MCP — GitHub MCP is a great
          place to start.
        </p>
      </motion.div>
    </div>
  );
}
