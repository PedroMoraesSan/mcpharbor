import { useEffect, useRef } from "react";
import { checkForAppUpdate, installAppUpdate } from "@/lib/updater";

/**
 * Silently checks for updates once after the desktop app loads.
 * Prompts via native confirm before downloading (minimal UX, no extra dialog plugin).
 */
export function useStartupUpdateCheck() {
  const checked = useRef(false);

  useEffect(() => {
    if (checked.current) {
      return;
    }
    checked.current = true;

    void (async () => {
      const update = await checkForAppUpdate();
      if (!update) {
        return;
      }

      const message = [
        `MCP Harbor ${update.nextVersion} is available.`,
        update.notes ? `\n\n${update.notes}` : "",
        "\n\nInstall now? The app will restart.",
      ].join("");

      if (window.confirm(message)) {
        await installAppUpdate();
      }
    })();
  }, []);
}
