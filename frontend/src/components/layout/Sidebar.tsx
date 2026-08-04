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
    path: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Tickets",
    path: "/tickets",
    icon: Ticket,
  },
  {
    title: "Users",
    path: "/users",
    icon: Users,
  },
  {
    title: "Analytics",
    path: "/analytics",
    icon: BarChart3,
  },
  {
    title: "AI Assistant",
    path: "/assistant",
    icon: Bot,
  },
  {
    title: "Settings",
    path: "/settings",
    icon: Settings,
  },
];

export default function Sidebar() {
  return (
    <aside className="flex h-screen w-64 flex-col border-r border-zinc-800 bg-zinc-950">

      {/* Logo */}

      <div className="border-b border-zinc-800 p-6">

        <h1 className="text-2xl font-bold text-white">
          🤖 ITMS
        </h1>

        <p className="mt-1 text-sm text-zinc-400">
          Intelligent Ticket Management
        </p>

      </div>

      {/* Navigation */}

      <nav className="flex-1 space-y-2 p-4">

        {menuItems.map((item) => {

          const Icon = item.icon;

          return (
            <NavLink
              key={item.title}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-4 py-3 transition-all duration-200

                ${
                  isActive
                    ? "bg-blue-600 text-white shadow-lg"
                    : "text-zinc-400 hover:bg-zinc-900 hover:text-white"
                }`
              }
            >
              <Icon size={20} />

              <span>{item.title}</span>
            </NavLink>
          );
        })}

      </nav>

      {/* Bottom Section */}

      <div className="border-t border-zinc-800 p-4">

        <button
          className="
            flex
            w-full
            items-center
            gap-3
            rounded-xl
            px-4
            py-3
            text-red-400
            transition
            hover:bg-red-500/10
          "
        >
          <LogOut size={20} />

          Logout
        </button>

      </div>

    </aside>
  );
}