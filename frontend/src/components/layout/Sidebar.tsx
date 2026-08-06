import { useState } from "react";

import {
  LayoutDashboard,
  Ticket,
  Users,
  BarChart3,
  Bot,
  Settings,
  LogOut,
  Menu,
} from "lucide-react";

import {
  NavLink,
  Link,
  useNavigate,
} from "react-router-dom";

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
  const navigate = useNavigate();

  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    localStorage.clear();
    navigate("/");
  };

  return (
    <aside
      className={`
        flex
        h-screen
        flex-col
        border-r
        border-zinc-800
        bg-zinc-950
        transition-all
        duration-300
        ${collapsed ? "w-20" : "w-64"}
      `}
    >
      {/* ================= Logo ================= */}

      <Link
        to="/dashboard"
        className="block border-b border-zinc-800 p-6 transition hover:bg-zinc-900"
      >
        <h1
          className={`font-bold text-white ${
            collapsed ? "text-3xl text-center" : "text-2xl"
          }`}
        >
          🤖 {!collapsed && "ITMS"}
        </h1>

        {!collapsed && (
          <p className="mt-1 text-sm text-zinc-400">
            Intelligent Ticket Management
          </p>
        )}
      </Link>

      {/* ================= Collapse Button ================= */}

      <div className="p-3">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full rounded-lg p-2 text-white transition hover:bg-zinc-800"
        >
          <Menu size={22} />
        </button>
      </div>

      {/* ================= Navigation ================= */}

      <nav className="flex-1 space-y-2 p-3">
        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.title}
              to={item.path}
              className={({ isActive }) =>
                `
                flex
                items-center
                rounded-xl
                px-4
                py-3
                transition-all
                duration-200

                ${
                  collapsed
                    ? "justify-center"
                    : "gap-3"
                }

                ${
                  isActive
                    ? "bg-blue-600 text-white shadow-lg"
                    : "text-zinc-400 hover:bg-zinc-900 hover:text-white"
                }
                `
              }
            >
              <Icon size={20} />

              {!collapsed && (
                <span>{item.title}</span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* ================= Logout ================= */}

      <div className="border-t border-zinc-800 p-3">
        <button
          onClick={handleLogout}
          className={`
            flex
            w-full
            items-center
            rounded-xl
            px-4
            py-3
            text-red-400
            transition
            hover:bg-red-500/10
            hover:text-red-300

            ${
              collapsed
                ? "justify-center"
                : "gap-3"
            }
          `}
        >
          <LogOut size={20} />

          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
}