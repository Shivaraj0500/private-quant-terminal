import {
  Activity,
  AlertTriangle,
  BellRing,
  CheckCircle2,
  Clock3,
  Database,
  Radio,
  Server,
  ShieldCheck,
  TrendingUp,
  Wifi,
} from "lucide-react";

export function MonitoringPage() {
  const systemStatus = [
    {
      label: "Research Engine",
      value: "Operational",
      icon: Activity,
      status: "success",
    },
    {
      label: "Market Data Feed",
      value: "Connected",
      icon: Radio,
      status: "success",
    },
    {
      label: "Execution Engine",
      value: "Operational",
      icon: Server,
      status: "success",
    },
    {
      label: "Broker Connection",
      value: "Development",
      icon: Wifi,
      status: "warning",
    },
  ];

  const alerts = [
    {
      title: "Market data latency within threshold",
      description: "Current feed latency remains below configured limits.",
      time: "Just now",
      type: "success",
    },
    {
      title: "Paper trading session active",
      description: "Strategy execution is running in the simulated environment.",
      time: "2 min ago",
      type: "success",
    },
    {
      title: "Broker integration pending",
      description: "Live broker connectivity has not been enabled.",
      time: "10 min ago",
      type: "warning",
    },
    {
      title: "Production capital protection enabled",
      description: "Live deployment remains protected by risk controls.",
      time: "Today",
      type: "success",
    },
  ];

  const metrics = [
    {
      label: "System Uptime",
      value: "99.98%",
      description: "Development environment",
      icon: TrendingUp,
      tone: "success",
    },
    {
      label: "Active Alerts",
      value: "1",
      description: "Requires attention",
      icon: BellRing,
      tone: "warning",
    },
    {
      label: "Data Latency",
      value: "42 ms",
      description: "Within threshold",
      icon: Clock3,
      tone: "success",
    },
    {
      label: "Audit Events",
      value: "128",
      description: "Recorded today",
      icon: ShieldCheck,
      tone: "success",
    },
  ];

  return (
    <section className="monitoring-page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">SYSTEM OBSERVABILITY</span>
          <h1>Monitoring Workspace</h1>
          <p>
            Monitor infrastructure, market data, strategy execution, alerts,
            and operational health.
          </p>
        </div>

        <div className="monitoring-live-status">
          <span className="status-dot" />
          <div>
            <span>System Status</span>
            <strong>Operational</strong>
          </div>
        </div>
      </div>

      <div className="monitoring-metric-grid">
        {metrics.map((metric) => {
          const Icon = metric.icon;

          return (
            <article className="monitoring-metric-card" key={metric.label}>
              <div
                className={`monitoring-icon monitoring-icon--${metric.tone}`}
              >
                <Icon size={21} />
              </div>

              <span className="monitoring-metric-label">{metric.label}</span>
              <strong className="monitoring-metric-value">
                {metric.value}
              </strong>
              <span className="monitoring-metric-description">
                {metric.description}
              </span>
            </article>
          );
        })}
      </div>

      <div className="monitoring-main-grid">
        <article className="monitoring-panel">
          <div className="monitoring-panel-header">
            <div>
              <span className="eyebrow">INFRASTRUCTURE</span>
              <h2>System Health</h2>
            </div>

            <span className="monitoring-badge monitoring-badge--success">
              <span className="status-dot" />
              LIVE
            </span>
          </div>

          <div className="monitoring-status-list">
            {systemStatus.map((item) => {
              const Icon = item.icon;

              return (
                <div className="monitoring-status-row" key={item.label}>
                  <div className="monitoring-status-left">
                    <div
                      className={`monitoring-status-icon monitoring-status-icon--${item.status}`}
                    >
                      <Icon size={18} />
                    </div>

                    <span>{item.label}</span>
                  </div>

                  <div
                    className={`monitoring-state monitoring-state--${item.status}`}
                  >
                    <span className="status-dot" />
                    {item.value}
                  </div>
                </div>
              );
            })}
          </div>
        </article>

        <article className="monitoring-panel">
          <div className="monitoring-panel-header">
            <div>
              <span className="eyebrow">ALERT CENTER</span>
              <h2>Recent Alerts</h2>
            </div>

            <span className="monitoring-badge">1 ACTIVE</span>
          </div>

          <div className="monitoring-alert-list">
            {alerts.map((alert) => (
              <div className="monitoring-alert-row" key={alert.title}>
                <div
                  className={`monitoring-alert-icon monitoring-alert-icon--${alert.type}`}
                >
                  {alert.type === "warning" ? (
                    <AlertTriangle size={18} />
                  ) : (
                    <CheckCircle2 size={18} />
                  )}
                </div>

                <div className="monitoring-alert-content">
                  <strong>{alert.title}</strong>
                  <p>{alert.description}</p>
                </div>

                <span className="monitoring-alert-time">{alert.time}</span>
              </div>
            ))}
          </div>
        </article>
      </div>

      <div className="monitoring-bottom-grid">
        <article className="monitoring-panel">
          <div className="monitoring-panel-header">
            <div>
              <span className="eyebrow">DATA OBSERVABILITY</span>
              <h2>Data Feed Monitoring</h2>
            </div>
          </div>

          <div className="monitoring-feed-summary">
            <div className="monitoring-feed-item">
              <div>
                <span>Primary Market Feed</span>
                <strong>Connected</strong>
              </div>
              <span className="monitoring-state monitoring-state--success">
                <span className="status-dot" />
                Healthy
              </span>
            </div>

            <div className="monitoring-feed-item">
              <div>
                <span>Data Processing</span>
                <strong>42 ms latency</strong>
              </div>
              <span className="monitoring-state monitoring-state--success">
                <span className="status-dot" />
                Normal
              </span>
            </div>

            <div className="monitoring-feed-item">
              <div>
                <span>Historical Database</span>
                <strong>Development Data</strong>
              </div>
              <span className="monitoring-state monitoring-state--warning">
                <span className="status-dot" />
                Simulated
              </span>
            </div>
          </div>

          <div className="monitoring-info-box">
            <Database size={18} />
            <p>
              Live market-data monitoring will connect to the backend data
              pipeline when production feeds are configured.
            </p>
          </div>
        </article>

        <article className="monitoring-panel">
          <div className="monitoring-panel-header">
            <div>
              <span className="eyebrow">RISK & DRIFT</span>
              <h2>Strategy Monitoring</h2>
            </div>
          </div>

          <div className="strategy-monitor-grid">
            <div className="strategy-monitor-item">
              <span>Active Strategies</span>
              <strong>3</strong>
              <small>Research pipeline monitored</small>
            </div>

            <div className="strategy-monitor-item">
              <span>Paper Sessions</span>
              <strong>1</strong>
              <small>Execution currently active</small>
            </div>

            <div className="strategy-monitor-item">
              <span>Drift Events</span>
              <strong>0</strong>
              <small>No abnormal model behaviour</small>
            </div>

            <div className="strategy-monitor-item">
              <span>Risk Breaches</span>
              <strong>0</strong>
              <small>All configured limits respected</small>
            </div>
          </div>
        </article>
      </div>

      <article className="monitoring-panel monitoring-audit-panel">
        <div className="monitoring-panel-header">
          <div>
            <span className="eyebrow">AUDIT TRAIL</span>
            <h2>Operational Activity</h2>
          </div>
        </div>

        <div className="monitoring-audit-list">
          <div className="monitoring-audit-row">
            <span className="status-dot" />
            <div>
              <strong>System health verification completed</strong>
              <p>All core Quant Terminal services are responding normally.</p>
            </div>
            <time>Just now</time>
          </div>

          <div className="monitoring-audit-row">
            <span className="status-dot" />
            <div>
              <strong>Paper trading environment checked</strong>
              <p>Execution controls and deployment safety gates remain active.</p>
            </div>
            <time>5 min ago</time>
          </div>

          <div className="monitoring-audit-row">
            <span className="status-dot status-dot--warning" />
            <div>
              <strong>Broker connectivity remains in development mode</strong>
              <p>Live order execution is not enabled.</p>
            </div>
            <time>Today</time>
          </div>
        </div>
      </article>
    </section>
  );
}