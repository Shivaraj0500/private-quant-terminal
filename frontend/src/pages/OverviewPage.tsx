import {
  Activity,
  BarChart3,
  BriefcaseBusiness,
  FlaskConical,
} from "lucide-react";

import { MetricCard } from "../features/dashboard/components/MetricCard";
import { RecentActivity } from "../features/dashboard/components/RecentActivity";
import { SystemStatusCard } from "../features/dashboard/components/SystemStatusCard";

export function OverviewPage() {
  return (
    <div className="page dashboard-page">
      <div className="page-header">
        <div>
          <span className="page-eyebrow">PRIVATE QUANT TERMINAL</span>
          <h2>Research Overview</h2>
          <p>
            Monitor your research workspace, strategies, portfolio intelligence,
            and system infrastructure.
          </p>
        </div>
      </div>

      <section className="metrics-grid">
        <MetricCard
          label="Active Strategies"
          value="0"
          change="Ready for research"
          changeType="neutral"
          icon={<FlaskConical size={19} />}
        />

        <MetricCard
          label="Portfolio Positions"
          value="0"
          change="Awaiting portfolio data"
          changeType="neutral"
          icon={<BriefcaseBusiness size={19} />}
        />

        <MetricCard
          label="Research Signals"
          value="0"
          change="No active signals"
          changeType="neutral"
          icon={<Activity size={19} />}
        />

        <MetricCard
          label="Market Instruments"
          value="0"
          change="Data connection pending"
          changeType="neutral"
          icon={<BarChart3 size={19} />}
        />
      </section>

      <section className="dashboard-grid">
        <SystemStatusCard />
        <RecentActivity />
      </section>
    </div>
  );
}
