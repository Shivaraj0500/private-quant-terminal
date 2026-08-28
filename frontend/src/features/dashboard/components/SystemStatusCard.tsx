import {
  CheckCircle2,
  Database,
  Server,
  Wifi,
  XCircle,
} from "lucide-react";

import { useUpstoxStatus } from "../../broker/hooks/useUpstoxStatus";
import { useHealth } from "../../system/hooks/useHealth";

export function SystemStatusCard() {
  const healthQuery = useHealth();
  const upstoxQuery = useUpstoxStatus();

  const backendOnline =
    healthQuery.isSuccess &&
    healthQuery.data?.status.toLowerCase() === "ok";

  const brokerConnected =
    upstoxQuery.isSuccess &&
    upstoxQuery.data?.authenticated === true;

  const systems = [
    {
      label: "Research Engine",
      value: backendOnline ? "Operational" : "Waiting",
      icon: CheckCircle2,
      status: backendOnline ? "online" : "warning",
    },
    {
      label: "Backend API",
      value: backendOnline ? "Connected" : "Disconnected",
      icon: Server,
      status: backendOnline ? "online" : "offline",
    },
    {
      label: "Market Data",
      value: brokerConnected ? "Broker Connected" : "Development",
      icon: Database,
      status: brokerConnected ? "online" : "warning",
    },
    {
      label: "Upstox Broker",
      value: upstoxQuery.isLoading
        ? "Checking..."
        : brokerConnected
          ? upstoxQuery.data?.user_name || "Connected"
          : "Not Connected",
      icon: Wifi,
      status: brokerConnected
        ? "online"
        : upstoxQuery.isLoading
          ? "warning"
          : "offline",
    },
  ];

  const live = backendOnline;

  return (
    <section className="dashboard-panel">
      <div className="dashboard-panel-header">
        <div>
          <span className="panel-eyebrow">SYSTEM</span>
          <h3>Infrastructure Status</h3>
        </div>

        <span className="panel-live">
          {live ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
          <span className={live ? "live-dot" : "status-dot status-dot-offline"} />
          {live ? "LIVE" : "OFFLINE"}
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
