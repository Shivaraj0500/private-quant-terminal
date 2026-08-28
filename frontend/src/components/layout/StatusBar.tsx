import {
  CircleCheck,
  CircleX,
  Database,
  Server,
} from "lucide-react";

import { useUpstoxStatus } from "../../features/broker/hooks/useUpstoxStatus";
import { useHealth } from "../../features/system/hooks/useHealth";

export function StatusBar() {
  const healthQuery = useHealth();
  const upstoxQuery = useUpstoxStatus();

  const backendOnline =
    healthQuery.isSuccess &&
    healthQuery.data?.status.toLowerCase() === "ok";

  const brokerConnected =
    upstoxQuery.isSuccess &&
    upstoxQuery.data?.authenticated === true;

  return (
    <footer className="status-bar">
      <div className="status-bar-left">
        <div className="status-item">
          {backendOnline ? (
            <CircleCheck size={14} />
          ) : (
            <CircleX size={14} />
          )}

          <span
            className={
              backendOnline
                ? "status-indicator status-indicator-online"
                : "status-indicator status-indicator-offline"
            }
          />

          <span>
            {healthQuery.isLoading
              ? "Checking System..."
              : backendOnline
                ? "System Ready"
                : "System Offline"}
          </span>
        </div>

        <div className="status-divider" />

        <div className="status-item">
          <Server size={14} />
          <span>
            Backend: {backendOnline ? "Connected" : "Disconnected"}
          </span>
        </div>

        <div className="status-divider" />

        <div className="status-item">
          <Database size={14} />
          <span>
            Broker: {brokerConnected ? "Connected" : "Not Connected"}
          </span>
        </div>
      </div>

      <div className="status-bar-right">
        <span>PRIVATE QUANT TERMINAL</span>
        <span className="status-version">v0.1.0</span>
      </div>
    </footer>
  );
}
