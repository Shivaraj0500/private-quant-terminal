import type { ReactNode } from "react";

interface MetricCardProps {
  label: string;
  value: string;
  change?: string;
  changeType?: "positive" | "negative" | "neutral";
  icon?: ReactNode;
}

export function MetricCard({
  label,
  value,
  change,
  changeType = "neutral",
  icon,
}: MetricCardProps) {
  return (
    <article className="metric-card">
      <div className="metric-card-header">
        <span className="metric-card-label">{label}</span>

        {icon ? (
          <span className="metric-card-icon">{icon}</span>
        ) : null}
      </div>

      <div className="metric-card-value">{value}</div>

      {change ? (
        <span className={`metric-card-change metric-card-change-${changeType}`}>
          {change}
        </span>
      ) : null}
    </article>
  );
}
