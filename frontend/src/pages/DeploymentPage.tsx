import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  CircleDot,
  Clock3,
  Database,
  Play,
  Rocket,
  Server,
  ShieldCheck,
  Wifi,
} from "lucide-react";

const deploymentStages = [
  {
    name: "Research Validation",
    description: "Evidence and robustness requirements completed.",
    status: "Completed",
    tone: "success",
  },
  {
    name: "Paper Trading",
    description: "Strategy execution running in simulated conditions.",
    status: "Active",
    tone: "active",
  },
  {
    name: "Risk Approval",
    description: "Final deployment controls awaiting approval.",
    status: "Pending",
    tone: "warning",
  },
  {
    name: "Live Deployment",
    description: "Production capital execution remains disabled.",
    status: "Locked",
    tone: "muted",
  },
];

const deploymentQueue = [
  {
    strategy: "NIFTY Momentum Breakout",
    version: "v1.0.0",
    environment: "Paper Trading",
    status: "Ready",
    return: "+18.42%",
    tone: "success",
  },
  {
    strategy: "EMA Trend Following",
    version: "v0.8.2",
    environment: "Validation",
    status: "Testing",
    return: "+9.86%",
    tone: "warning",
  },
  {
    strategy: "Mean Reversion Engine",
    version: "v0.4.1",
    environment: "Research",
    status: "Blocked",
    return: "-2.14%",
    tone: "danger",
  },
];

const activity = [
  {
    title: "Paper trading environment initialized",
    description: "Execution engine connected to the simulated market environment.",
    time: "Just now",
    icon: Play,
  },
  {
    title: "Deployment controls verified",
    description: "Risk limits, validation gates, and environment permissions checked.",
    time: "12 min ago",
    icon: ShieldCheck,
  },
  {
    title: "Strategy version registered",
    description: "NIFTY Momentum Breakout v1.0.0 added to the deployment queue.",
    time: "28 min ago",
    icon: Database,
  },
];

function StatusBadge({
  children,
  tone,
}: {
  children: string;
  tone: string;
}) {
  return <span className={`deployment-badge ${tone}`}>{children}</span>;
}

export default function DeploymentPage() {
  return (
    <div className="page deployment-page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">EXECUTION ENVIRONMENT</div>
          <h1>Deployment Workspace</h1>
          <p>
            Control strategy deployment from validated research through paper
            trading and production execution.
          </p>
        </div>

        <div className="deployment-mode-card">
          <div className="icon-box">
            <Rocket size={20} />
          </div>
          <div>
            <span>Execution Mode</span>
            <strong>Paper Trading</strong>
          </div>
        </div>
      </div>

      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-card-top">
            <span>Deployment Ready</span>
            <div className="icon-box">
              <Rocket size={19} />
            </div>
          </div>
          <strong className="stat-value">1</strong>
          <p className="positive">Paper trading eligible</p>
        </div>

        <div className="stat-card">
          <div className="stat-card-top">
            <span>Active Sessions</span>
            <div className="icon-box">
              <Activity size={19} />
            </div>
          </div>
          <strong className="stat-value">1</strong>
          <p className="positive">Execution engine running</p>
        </div>

        <div className="stat-card">
          <div className="stat-card-top">
            <span>Risk Gates</span>
            <div className="icon-box">
              <ShieldCheck size={19} />
            </div>
          </div>
          <strong className="stat-value">6 / 7</strong>
          <p className="warning-text">Final approval pending</p>
        </div>

        <div className="stat-card">
          <div className="stat-card-top">
            <span>Live Capital</span>
            <div className="icon-box warning-icon">
              <AlertTriangle size={19} />
            </div>
          </div>
          <strong className="stat-value">₹0</strong>
          <p>Production execution disabled</p>
        </div>
      </section>

      <section className="deployment-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <div className="eyebrow">DEPLOYMENT PIPELINE</div>
              <h2>Execution Workflow</h2>
            </div>
            <StatusBadge tone="active">PAPER MODE</StatusBadge>
          </div>

          <div className="pipeline-list">
            {deploymentStages.map((stage, index) => (
              <div className="pipeline-item" key={stage.name}>
                <div className={`pipeline-icon ${stage.tone}`}>
                  {stage.tone === "success" ? (
                    <CheckCircle2 size={19} />
                  ) : stage.tone === "warning" ? (
                    <Clock3 size={19} />
                  ) : stage.tone === "muted" ? (
                    <CircleDot size={19} />
                  ) : (
                    <Activity size={19} />
                  )}
                </div>

                <div className="pipeline-content">
                  <strong>{stage.name}</strong>
                  <span>{stage.description}</span>
                </div>

                <StatusBadge tone={stage.tone}>
                  {stage.status}
                </StatusBadge>

                {index < deploymentStages.length - 1 && (
                  <div className="pipeline-line" />
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="panel environment-panel">
          <div className="panel-header">
            <div>
              <div className="eyebrow">SYSTEM STATUS</div>
              <h2>Execution Environment</h2>
            </div>
          </div>

          <div className="environment-list">
            <div className="environment-row">
              <div className="environment-label">
                <Server size={18} />
                <span>Execution Engine</span>
              </div>
              <span className="status-value online">Operational</span>
            </div>

            <div className="environment-row">
              <div className="environment-label">
                <Wifi size={18} />
                <span>Broker Connection</span>
              </div>
              <span className="status-value local">Development</span>
            </div>

            <div className="environment-row">
              <div className="environment-label">
                <Database size={18} />
                <span>Market Data</span>
              </div>
              <span className="status-value warning">Simulated</span>
            </div>

            <div className="environment-row">
              <div className="environment-label">
                <ShieldCheck size={18} />
                <span>Risk Controls</span>
              </div>
              <span className="status-value online">Enabled</span>
            </div>
          </div>

          <div className="deployment-safety">
            <div className="icon-box">
              <ShieldCheck size={20} />
            </div>
            <div>
              <strong>Production Safety Enabled</strong>
              <p>
                Live order execution requires explicit approval and a validated
                production environment.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="deployment-grid deployment-grid-bottom">
        <div className="panel queue-panel">
          <div className="panel-header">
            <div>
              <div className="eyebrow">STRATEGY REGISTRY</div>
              <h2>Deployment Queue</h2>
            </div>
            <StatusBadge tone="success">3 REGISTERED</StatusBadge>
          </div>

          <div className="deployment-table">
            <div className="deployment-table-head">
              <span>STRATEGY</span>
              <span>ENVIRONMENT</span>
              <span>STATUS</span>
              <span>RETURN</span>
            </div>

            {deploymentQueue.map((item) => (
              <div className="deployment-table-row" key={item.strategy}>
                <div className="strategy-name">
                  <strong>{item.strategy}</strong>
                  <span>{item.version}</span>
                </div>

                <span>{item.environment}</span>

                <div>
                  <StatusBadge tone={item.tone}>{item.status}</StatusBadge>
                </div>

                <strong
                  className={
                    item.return.startsWith("-") ? "negative" : "positive"
                  }
                >
                  {item.return}
                </strong>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <div className="eyebrow">EXECUTION LOG</div>
              <h2>Recent Activity</h2>
            </div>
          </div>

          <div className="deployment-activity">
            {activity.map((item) => {
              const Icon = item.icon;

              return (
                <div className="activity-row" key={item.title}>
                  <div className="activity-icon">
                    <Icon size={18} />
                  </div>

                  <div className="activity-content">
                    <strong>{item.title}</strong>
                    <span>{item.description}</span>
                  </div>

                  <time>{item.time}</time>
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </div>
  );
}
