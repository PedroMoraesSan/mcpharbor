import { TerminalBentoGrid } from "@/features/dashboard/components/TerminalBentoGrid";
import { WelcomeOnboarding } from "@/features/dashboard/components/WelcomeOnboarding";
import { PageHeader } from "@/components/layout/page-header";

export function DashboardPage() {
  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Operational overview of your MCP environment"
      />
      <WelcomeOnboarding />
      <TerminalBentoGrid />
    </div>
  );
}
