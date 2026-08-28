import {
  Bell,
  CircleUserRound,
  Command,
  Search,
} from "lucide-react";

import { useUpstoxStatus } from "../../features/broker/hooks/useUpstoxStatus";

export function Topbar() {
  const upstoxQuery = useUpstoxStatus();

  const userName =
    upstoxQuery.isSuccess &&
    upstoxQuery.data?.authenticated &&
    upstoxQuery.data.user_name
      ? upstoxQuery.data.user_name
      : "Researcher";

  return (
    <header className="topbar">
      <div className="topbar-left">
        <div className="topbar-title-group">
          <span className="topbar-eyebrow">PRIVATE QUANT TERMINAL</span>
          <h1 className="topbar-title">Research Workspace</h1>
        </div>
      </div>

      <div className="topbar-right">
        <button
          className="topbar-search"
          type="button"
          aria-label="Search"
        >
          <Search size={17} />
          <span>Search workspace...</span>
          <kbd>
            <Command size={13} />
            K
          </kbd>
        </button>

        <button
          className="topbar-icon-button"
          type="button"
          aria-label="Notifications"
        >
          <Bell size={19} />
        </button>

        <button
          className="topbar-profile"
          type="button"
          aria-label="User profile"
          title={
            upstoxQuery.data?.authenticated
              ? "Upstox connected"
              : "No broker connected"
          }
        >
          <CircleUserRound size={22} />
          <span>{userName}</span>
        </button>
      </div>
    </header>
  );
}
