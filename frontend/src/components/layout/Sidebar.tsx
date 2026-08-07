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

export default function Sidebar() {
  const navigate = useNavigate();

  const [collapsed, setCollapsed] =
    useState(false);

  const role =
    localStorage.getItem("role");

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

    ...(role === "Admin"
      ? [
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
            title: "Settings",
            path: "/settings",
            icon: Settings,
          },
        ]
      : []),

    {
      title: "AI Assistant",
      path: "/assistant",
      icon: Bot,
    },
  ];

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
        border-slate-200
        bg-white
        transition-all
        duration-300
        dark:border-slate-800
        dark:bg-slate-950
        ${collapsed ? "w-20" : "w-64"}
      `}
    >
      {/* Logo */}

      <Link
        to="/dashboard"
        className="
          block
          border-b
          border-slate-200
          p-6
          transition
          hover:bg-slate-100
          dark:border-slate-800
          dark:hover:bg-slate-900
        "
      >
        <h1
          className={`
            font-bold
            text-cyan-600
            dark:text-cyan-400
            ${
              collapsed
                ? "text-3xl text-center"
                : "text-2xl"
            }
          `}
        >
          🤖
          {!collapsed && " ITMS"}
        </h1>

        {!collapsed && (
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Intelligent Ticket Management
          </p>
        )}
      </Link>

      {/* Collapse */}

      <div className="p-3">
        <button
          onClick={() =>
            setCollapsed(!collapsed)
          }
          className="
            w-full
            rounded-lg
            p-2
            text-slate-700
            transition
            hover:bg-slate-100
            dark:text-white
            dark:hover:bg-slate-800
          "
        >
          <Menu size={22} />
        </button>
      </div>

      {/* Navigation */}

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

                  ${
                    collapsed
                      ? "justify-center"
                      : "gap-3"
                  }

                  ${
                    isActive
                      ? "bg-blue-600 text-white shadow-lg"
                      : `
                          text-slate-600
                          hover:bg-slate-100
                          hover:text-slate-900

                          dark:text-slate-400
                          dark:hover:bg-slate-900
                          dark:hover:text-white
                        `
                  }
                `
              }
            >
              <Icon size={20} />

              {!collapsed && (
                <span className="font-medium">
                  {item.title}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Logout */}

      <div className="border-t border-slate-200 p-3 dark:border-slate-800">
        <button
          onClick={handleLogout}
          className={`
            flex
            w-full
            items-center
            rounded-xl
            px-4
            py-3
            text-red-500
            transition
            hover:bg-red-50
            dark:hover:bg-red-500/10
            ${
              collapsed
                ? "justify-center"
                : "gap-3"
            }
          `}
        >
          <LogOut size={20} />

          {!collapsed && (
            <span>
              Logout
            </span>
          )}
        </button>
      </div>
    </aside>
  );
}