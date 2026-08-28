import { createBrowserRouter } from "react-router-dom";

import { AppLayout } from "../components/layout/AppLayout";
import DeploymentPage from "../pages/DeploymentPage";
import { MarketPage } from "../pages/MarketPage";
import { MonitoringPage } from "../pages/MonitoringPage";
import { OverviewPage } from "../pages/OverviewPage";
import { PortfolioPage } from "../pages/PortfolioPage";
import { ResearchPage } from "../pages/ResearchPage";
import { StrategiesPage } from "../pages/StrategiesPage";
import { TechnicalAnalysisPage } from "../pages/TechnicalAnalysisPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: <OverviewPage />,
      },
      {
        path: "market",
        element: <MarketPage />,
      },
      {
        path: "technical-analysis",
        element: <TechnicalAnalysisPage />,
      },
      {
        path: "portfolio",
        element: <PortfolioPage />,
      },
      {
        path: "strategies",
        element: <StrategiesPage />,
      },
      {
        path: "research",
        element: <ResearchPage />,
      },
      {
        path: "deployment",
        element: <DeploymentPage />,
      },
      {
        path: "monitoring",
        element: <MonitoringPage />,
      },
    ],
  },
]);
