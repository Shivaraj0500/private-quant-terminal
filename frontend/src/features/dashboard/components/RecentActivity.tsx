import {
  BarChart3,
  FlaskConical,
  SearchCheck,
  ShieldCheck,
} from "lucide-react";

const activities = [
  {
    title: "Technical analysis workspace initialized",
    description: "Indicator and signal research environment available.",
    time: "Just now",
    icon: BarChart3,
  },
  {
    title: "Strategy research environment ready",
    description: "Validation and strategy versioning modules prepared.",
    time: "Just now",
    icon: FlaskConical,
  },
  {
    title: "Research evidence framework initialized",
    description: "Evidence-first research workflow is available.",
    time: "Just now",
    icon: SearchCheck,
  },
  {
    title: "System health check completed",
    description: "Frontend infrastructure is operating normally.",
    time: "1 min ago",
    icon: ShieldCheck,
  },
];

export function RecentActivity() {
  return (
    <section className="dashboard-panel">
      <div className="dashboard-panel-header">
        <div>
          <span className="panel-eyebrow">WORKSPACE</span>
          <h3>Recent Activity</h3>
        </div>
      </div>

      <div className="activity-list">
        {activities.map((activity) => {
          const Icon = activity.icon;

          return (
            <div className="activity-item" key={activity.title}>
              <div className="activity-icon">
                <Icon size={17} />
              </div>

              <div className="activity-content">
                <div className="activity-title-row">
                  <h4>{activity.title}</h4>
                  <span>{activity.time}</span>
                </div>

                <p>{activity.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
