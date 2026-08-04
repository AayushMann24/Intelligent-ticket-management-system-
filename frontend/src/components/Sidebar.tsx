import {
  LayoutDashboard,
  Ticket,
  Users,
  BarChart3,
  Bot,
  Settings,
  LogOut,
} from "lucide-react";

import { NavLink } from "react-router-dom";

const menuItems = [
  {
    title: "Dashboard",
    icon: LayoutDashboard,
    path: "/dashboard",
  },
  {
    title: "Tickets",
    icon: Ticket,
    path: "/tickets",
  },
  {
    title: "Users",
    icon: Users,
    path: "/users",
  },
  {
    title: "Analytics",
    icon: BarChart3,
    path: "/analytics",
  },
  {
    title: "AI Assistant",
    icon: Bot,
    path: "/assistant",
  },
  {
    title: "Settings",
    icon: Settings,
    path: "/settings",
  },
];

export default function Sidebar() {
  return (
    <aside className="w-64 h-screen bg-zinc-950 border-r border-zinc-800 flex flex-col">

      {/* Logo */}

      <div className="p-6 border-b border-zinc-800">

        <h1 className="text-2xl font-bold text-white">
          🤖 ITMS
        </h1>

        <p className="text-sm text-zinc-400">
          AI Powered
        </p>

      </div>

      {/* Menu */}

      <nav className="flex-1 p-4 space-y-2">

        {menuItems.map((item) => {

          const Icon = item.icon;

          return (
            <NavLink
              key={item.title}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-4 py-3 transition-all

                ${
                  isActive
                    ? "bg-blue-600 text-white"
                    : "text-zinc-400 hover:bg-zinc-900 hover:text-white"
                }`
              }
            >
              <Icon size={20} />

              {item.title}
            </NavLink>
          );
        })}
      </nav>

      {/* Logout */}

      <div className="p-4 border-t border-zinc-800">

        <button className="w-full flex items-center gap-3 rounded-xl px-4 py-3 text-red-400 hover:bg-red-500/10 transition-all">

          <LogOut size={20} />

          Logout

        </button>

      </div>
    </aside>
  );
}