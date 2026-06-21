import { createBrowserRouter } from "react-router-dom";
import { AppLayout } from "@/layouts/AppLayout/AppLayout";
import { DashboardPage } from "@/pages/dashboard/DashboardPage";
import { McpsPage } from "@/pages/mcps/McpsPage";
import { McpDetailPage } from "@/pages/mcps/McpDetailPage";
import { CatalogPage } from "@/pages/catalog/CatalogPage";
import { LogsPage } from "@/pages/logs/LogsPage";
import { IntegrationsPage } from "@/pages/integrations/IntegrationsPage";
import { SettingsPage } from "@/pages/settings/SettingsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "mcps", element: <McpsPage /> },
      { path: "mcps/:id", element: <McpDetailPage /> },
      { path: "catalog", element: <CatalogPage /> },
      { path: "logs", element: <LogsPage /> },
      { path: "integrations", element: <IntegrationsPage /> },
      { path: "settings", element: <SettingsPage /> },
    ],
  },
]);
