import {
  CircleCheck,
  Database,
  Server,
} from "lucide-react";

export function StatusBar() {
  return (
    <footer className="status-bar">
      <div className="status-bar-left">
        <div className="status-item">
          <CircleCheck size={14} />
          <span className="status-indicator status-indicator-online" />
          <span>System Ready</span>
        </div>

        <div className="status-divider" />

        <div className="status-item">
          <Server size={14} />
          <span>Backend: Local</span>
        </div>

        <div className="status-divider" />

        <div className="status-item">
          <Database size={14} />
          <span>Data: Development</span>
        </div>
      </div>

      <div className="status-bar-right">
        <span>PRIVATE QUANT TERMINAL</span>
        <span className="status-version">v0.1.0</span>
      </div>
    </footer>
  );
}
