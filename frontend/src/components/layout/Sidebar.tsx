import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

import {
  LayoutDashboard,
  Ticket,
  Users,
  BarChart3,
  Bot,
  Settings,
  LogOut,
  Menu,
  FileText,
  BookOpen,
} from "lucide-react";

import {
  NavLink,
  Link,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../../context/useAuth";
import { useReducedMotion } from "../../hooks/useReducedMotion";

export default function Sidebar() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const reducedMotion = useReducedMotion();

  const [collapsed, setCollapsed] = useState(false);

  const role = user?.role;

  const menuItems = [
    { title: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { title: "Tickets", path: "/tickets", icon: Ticket },
    { title: "Knowledge Base", path: "/knowledge", icon: BookOpen },
    ...(role === "Admin"
      ? [
          { title: "Users", path: "/users", icon: Users },
          { title: "Analytics", path: "/analytics", icon: BarChart3 },
          { title: "Reports", path: "/reports", icon: FileText },
          { title: "Settings", path: "/settings", icon: Settings },
        ]
      : []),
    { title: "AI Assistant", path: "/assistant", icon: Bot },
  ];

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const sidebarTransition = reducedMotion
    ? { duration: 0 }
    : { type: "spring" as const, stiffness: 300, damping: 30 };

  return (
    <motion.aside
      className={`
        flex h-screen flex-col border-r border-slate-200 bg-white
        dark:border-slate-800 dark:bg-slate-950
      `}
      animate={{ width: collapsed ? "5rem" : "16rem" }}
      transition={sidebarTransition}
    >
      {/* Logo */}
      <Link
        to="/dashboard"
        className="
          block
          border-b border-slate-200 p-6 transition-colors
          hover:bg-slate-100
          dark:border-slate-800 dark:hover:bg-slate-900
        "
      >
        <motion.h1
          className="font-bold text-cyan-600 dark:text-cyan-400 overflow-hidden"
          animate={{ fontSize: collapsed ? "1.875rem" : "1.5rem" }}
          transition={sidebarTransition}
        >
          <span className="flex items-center gap-2">
            <span>🤖</span>
            <AnimatePresence mode="wait">
              {!collapsed && (
                <motion.span
                  key="itms-text"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  transition={{ duration: 0.15, ease: "easeOut" }}
                >
                  ITMS
                </motion.span>
              )}
            </AnimatePresence>
          </span>
        </motion.h1>

        <AnimatePresence mode="wait">
          {!collapsed && (
            <motion.p
              key="subtitle"
              className="mt-1 text-sm text-slate-500 dark:text-slate-400"
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.15, delay: 0.05, ease: "easeOut" }}
            >
              Intelligent Ticket Management
            </motion.p>
          )}
        </AnimatePresence>
      </Link>

      {/* Collapse Button */}
      <div className="p-3">
        <motion.button
          onClick={() => setCollapsed(!collapsed)}
          className="
            w-full rounded-lg p-2 text-slate-700 transition-colors
            hover:bg-slate-100 dark:text-white dark:hover:bg-slate-800
          "
          whileHover={reducedMotion ? {} : { scale: 1.05 }}
          whileTap={reducedMotion ? {} : { scale: 0.95 }}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          <motion.div
            animate={{ rotate: collapsed ? 180 : 0 }}
            transition={sidebarTransition}
          >
            <Menu size={22} />
          </motion.div>
        </motion.button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2 p-3 overflow-hidden">
        <AnimatePresence mode="popLayout">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.title}
                to={item.path}
                className={({ isActive }) => `
                  flex items-center rounded-xl px-4 py-3 transition-all duration-200
                  ${collapsed ? "justify-center" : "gap-3"}
                  ${isActive
                    ? "bg-blue-600 text-white shadow-lg"
                    : `
                        text-slate-600 hover:bg-slate-100 hover:text-slate-900
                        dark:text-slate-400 dark:hover:bg-slate-900 dark:hover:text-white
                      `}
                `}
              >
                <Icon size={20} className="flex-shrink-0" />
                <AnimatePresence mode="wait">
                  {!collapsed && (
                    <motion.span
                      key={item.title}
                      className="font-medium truncate"
                      initial={{ opacity: 0, x: -10, width: 0 }}
                      animate={{ opacity: 1, x: 0, width: "auto" }}
                      exit={{ opacity: 0, x: -10, width: 0 }}
                      transition={{ duration: 0.15, ease: "easeOut" }}
                    >
                      {item.title}
                    </motion.span>
                  )}
                </AnimatePresence>
              </NavLink>
            );
          })}
        </AnimatePresence>
      </nav>

      {/* Logout */}
      <div className="border-t border-slate-200 p-3 dark:border-slate-800">
        <button
          onClick={handleLogout}
          className={`
            flex w-full items-center rounded-xl px-4 py-3 text-red-500 transition-colors
            hover:bg-red-50 dark:hover:bg-red-500/10
            ${collapsed ? "justify-center" : "gap-3"}
          `}
        >
          <LogOut size={20} className="flex-shrink-0" />
          <AnimatePresence mode="wait">
            {!collapsed && (
              <motion.span
                key="logout-text"
                initial={{ opacity: 0, x: -10, width: 0 }}
                animate={{ opacity: 1, x: 0, width: "auto" }}
                exit={{ opacity: 0, x: -10, width: 0 }}
                transition={{ duration: 0.15, ease: "easeOut" }}
              >
                Logout
              </motion.span>
            )}
          </AnimatePresence>
        </button>
      </div>
    </motion.aside>
  );
}