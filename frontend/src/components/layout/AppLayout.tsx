import { Outlet } from "react-router-dom";

import { Sidebar } from "./Sidebar";
import { StatusBar } from "./StatusBar";
import { Topbar } from "./Topbar";

export function AppLayout() {
  return (
    <div className="app-shell">
      <Topbar />

      <div className="app-body">
        <Sidebar />

        <main className="app-main">
          <Outlet />
        </main>
      </div>

      <StatusBar />
    </div>
  );
}
