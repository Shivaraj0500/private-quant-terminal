import {
  CheckCircle2,
  Database,
  Server,
  Wifi,
} from "lucide-react";

const systems = [
  {
    label: "Research Engine",
    value: "Operational",
    icon: CheckCircle2,
    status: "online",
  },
  {
    label: "Backend API",
    value: "Local",
    icon: Server,
    status: "online",
  },
  {
    label: "Market Data",
    value: "Development",
    icon: Database,
    status: "warning",
  },
  {
    label: "Data Connection",
    value: "Connected",
    icon: Wifi,
    status: "online",
  },
];

export function SystemStatusCard() {
  return (
    <section className="dashboard-panel">
      <div className="dashboard-panel-header">
        <div>
          <span className="panel-eyebrow">SYSTEM</span>
          <h3>Infrastructure Status</h3>
        </div>

        <span className="panel-live">
          <span className="live-dot" />
          LIVE
        </span>
      </div>

      <div className="system-status-list">
        {systems.map((system) => {
          const Icon = system.icon;

          return (
            <div className="system-status-item" key={system.label}>
              <div className="system-status-left">
                <span className="system-status-icon">
                  <Icon size={17} />
                </span>

                <span>{system.label}</span>
              </div>

              <div className="system-status-right">
                <span className={`status-dot status-dot-${system.status}`} />
                <span>{system.value}</span>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
