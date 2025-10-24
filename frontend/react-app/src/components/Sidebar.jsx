import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  ShieldCheck,
  TrendingUp,
  History,
  Settings,
  Info,
  User,
  Shield,
} from "lucide-react";

const links = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/verify", icon: ShieldCheck, label: "Verify" },
  { to: "/trending", icon: TrendingUp, label: "Trending" },
  { to: "/history", icon: History, label: "History" },
  { to: "/settings", icon: Settings, label: "Settings" },
  { to: "/account", icon: User, label: "Account" },
  { to: "/about", icon: Info, label: "About" },
];

function Sidebar({ collapsed = false }) {
  return (
    <aside className={`hidden md:flex flex-col ${collapsed ? "w-16" : "w-64"} bg-white dark:bg-gray-800 border-r dark:border-gray-700 shadow-sm text-gray-900 dark:text-gray-100 transition-all duration-200`}>
      <div className={`p-5 border-b dark:border-gray-700 ${collapsed ? "items-center" : ""}`}>
        {!collapsed ? (
          <h2 className="text-2xl font-bold text-blue-600">TruthGuard</h2>
        ) : (
          <div className="w-8 h-8 rounded bg-blue-600 text-white flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
              <path d="M12 2l7 3v6c0 5-3.5 9.74-7 11-3.5-1.26-7-6-7-11V5l7-3z" />
            </svg>
          </div>
        )}
      </div>
      <nav className={`flex-grow ${collapsed ? "px-2" : "px-4"} py-6 space-y-2`}>
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end
            className={({ isActive }) =>
              `group flex items-center ${collapsed ? "justify-center" : "gap-3"} px-3 py-2 rounded-lg font-medium transition-all duration-150 ${
                isActive
                  ? "bg-blue-600 text-white shadow"
                  : "text-gray-700 dark:text-gray-200 hover:bg-blue-50 dark:hover:bg-gray-700/60"
              }`
            }
            title={collapsed ? label : undefined}
          >
            <Icon className="w-5 h-5" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;
