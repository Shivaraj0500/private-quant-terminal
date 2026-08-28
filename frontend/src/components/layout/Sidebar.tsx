import {
  Activity,
  BarChart3,
  BriefcaseBusiness,
  Database,
  FlaskConical,
  LayoutDashboard,
  Radar,
  Rocket,
  SearchCheck,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const navigationItems = [
  {
    label: "Overview",
    path: "/",
    icon: LayoutDashboard,
  },
  {
    label: "Market",
    path: "/market",
    icon: Database,
  },
  {
    label: "Technical Analysis",
    path: "/technical-analysis",
    icon: Activity,
  },
  {
    label: "Portfolio",
    path: "/portfolio",
    icon: BriefcaseBusiness,
  },
  {
    label: "Strategies",
    path: "/strategies",
    icon: FlaskConical,
  },
  {
    label: "Research",
    path: "/research",
    icon: SearchCheck,
  },
  {
    label: "Deployment",
    path: "/deployment",
    icon: Rocket,
  },
  {
    label: "Monitoring",
    path: "/monitoring",
    icon: Radar,
  },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <BarChart3 size={22} />
        <span>PRIVATE QUANT</span>
      </div>

      <nav className="sidebar-nav">
        {navigationItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) =>
                `sidebar-link${isActive ? " sidebar-link-active" : ""}`
              }
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <span className="sidebar-status-dot" />
        <span>Research System</span>
      </div>
    </aside>
  );
}
