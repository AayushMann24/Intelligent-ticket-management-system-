import {
  Bell,
  LogOut,
  Search,
  User,
  Sun,
  Moon,
  ChevronDown,
} from "lucide-react";

import { useNavigate } from "react-router-dom";
import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

import { useAuth } from "../../context/useAuth";
import { useTheme } from "../../context/useTheme";
import NotificationDropdown from "./NotificationDropdown";
import { useNotifications } from "../../hooks/useNotifications";
import { useReducedMotion } from "../../hooks/useReducedMotion";

export default function Navbar() {
  const navigate = useNavigate();
  const reducedMotion = useReducedMotion();

  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { unreadCount } = useNotifications();

  const [search, setSearch] = useState("");
  const [profileOpen, setProfileOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  const profileRef = useRef<HTMLDivElement>(null);
  const notificationsRef = useRef<HTMLDivElement>(null);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const handleSearch = () => {
    if (!search.trim()) return;
    navigate(`/tickets?search=${encodeURIComponent(search)}`);
  };

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setProfileOpen(false);
      }
      if (notificationsRef.current && !notificationsRef.current.contains(event.target as Node)) {
        setNotificationsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="flex h-16 w-full items-center justify-between border-b border-slate-300 bg-white px-6 transition-colors dark:border-slate-700 dark:bg-slate-900">
      {/* Left Section */}
      <div className="flex items-center gap-8">
        <motion.h1
          onClick={() => navigate("/dashboard")}
          className="cursor-pointer text-2xl font-bold text-cyan-600 dark:text-cyan-400"
          whileHover={reducedMotion ? {} : { scale: 1.05 }}
          whileTap={reducedMotion ? {} : { scale: 0.95 }}
        >
          ITMS
        </motion.h1>

        {/* Search */}
        <motion.div
          className="relative"
          initial={{ opacity: 0, width: 0 }}
          animate={{ opacity: 1, width: "20rem" }}
          transition={{ duration: 0.3, delay: 0.2, ease: [0, 0, 0.2, 1] }}
        >
          <motion.button
            onClick={handleSearch}
            className="absolute left-3 top-1/2 -translate-y-1/2 cursor-pointer text-slate-500 hover:text-cyan-500 dark:text-slate-400"
            whileHover={reducedMotion ? {} : { scale: 1.1 }}
            whileTap={reducedMotion ? {} : { scale: 0.9 }}
            aria-label="Search"
          >
            <Search size={18} />
          </motion.button>

          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSearch();
            }}
            placeholder="Search tickets..."
            className="
              w-80 rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-4 text-slate-900
              placeholder:text-slate-500 transition-all focus:outline-none focus:ring-2
              focus:ring-cyan-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white
              dark:placeholder:text-slate-400
            "
          />
        </motion.div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-6">
        {/* Theme Toggle */}
        <motion.button
          onClick={toggleTheme}
          className="rounded-lg p-2 text-slate-600 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
          whileHover={reducedMotion ? {} : { scale: 1.1, rotate: 15 }}
          whileTap={reducedMotion ? {} : { scale: 0.9 }}
          aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
        >
          <motion.span
            animate={{ rotate: theme === "dark" ? 180 : 0, scale: [1, 1.2, 1] }}
            transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
          >
            {theme === "dark" ? <Sun size={22} /> : <Moon size={22} />}
          </motion.span>
        </motion.button>

        {/* Notifications */}
        <div ref={notificationsRef} className="relative">
          <motion.button
            onClick={() => setNotificationsOpen(!notificationsOpen)}
            className="relative p-2 rounded-lg text-slate-600 transition-colors hover:bg-slate-100 hover:text-black dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white"
            whileHover={reducedMotion ? {} : { scale: 1.1 }}
            whileTap={reducedMotion ? {} : { scale: 0.9 }}
            aria-label="Notifications"
          >
            <Bell size={22} />
            <AnimatePresence>
              {unreadCount > 0 && (
                <motion.span
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0, opacity: 0 }}
                  transition={{ type: "spring", stiffness: 400, damping: 20 }}
                  className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs font-medium text-white"
                >
                  {unreadCount > 9 ? "9+" : unreadCount}
                </motion.span>
              )}
            </AnimatePresence>
          </motion.button>

          <AnimatePresence>
            {notificationsOpen && (
              <NotificationDropdown
                isOpen={notificationsOpen}
                onClose={() => setNotificationsOpen(false)}
              />
            )}
          </AnimatePresence>
        </div>

        {/* Profile */}
        <div ref={profileRef} className="relative">
          <motion.div
            onClick={() => setProfileOpen(!profileOpen)}
            className="flex cursor-pointer items-center gap-3 rounded-lg px-2 py-1 transition-colors hover:bg-slate-100 dark:hover:bg-slate-800"
            whileHover={reducedMotion ? {} : { scale: 1.02 }}
            whileTap={reducedMotion ? {} : { scale: 0.98 }}
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-cyan-500 text-lg font-bold text-white">
              {user?.name?.charAt(0).toUpperCase() ?? "U"}
            </div>

            <AnimatePresence mode="wait">
              {(!reducedMotion || profileOpen) && (
                <motion.div
                  key="profile-info"
                  initial={{ opacity: 0, width: 0, x: -10 }}
                  animate={{ opacity: 1, width: "auto", x: 0 }}
                  exit={{ opacity: 0, width: 0, x: -10 }}
                  transition={{ duration: 0.15, ease: [0.4, 0, 1, 1] }}
                >
                  <p className="font-medium text-slate-900 dark:text-white truncate max-w-[150px]">
                    {user?.name ?? "Loading..."}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400 truncate max-w-[150px]">
                    {user?.role ?? ""}
                  </p>
                </motion.div>
              )}
            </AnimatePresence>

            <motion.div
              animate={{ rotate: profileOpen ? 180 : 0 }}
              transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
              className="text-slate-500 dark:text-slate-400"
            >
              <ChevronDown size={16} />
            </motion.div>
          </motion.div>

          {/* Dropdown */}
          <AnimatePresence>
            {profileOpen && (
              <motion.div
                initial={{ opacity: 0, y: -8, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -8, scale: 0.98 }}
                transition={{ duration: 0.15, ease: [0.4, 0, 1, 1] }}
                className="absolute right-0 mt-3 w-64 rounded-xl border border-slate-300 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900"
              >
                <div className="p-5">
                  <div className="flex items-center gap-3">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-cyan-500 text-lg font-bold text-white">
                      {user?.name?.charAt(0).toUpperCase() ?? "U"}
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-900 dark:text-white">
                        {user?.name ?? "Loading..."}
                      </h3>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        {user?.role ?? ""}
                      </p>
                    </div>
                  </div>

                  <hr className="my-4 border-slate-300 dark:border-slate-700" />

                  <motion.button
                    onClick={() => {
                      navigate("/profile");
                      setProfileOpen(false);
                    }}
                    className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-slate-900 transition-colors hover:bg-slate-100 dark:text-white dark:hover:bg-slate-800"
                    whileHover={reducedMotion ? {} : { x: 4 }}
                    whileTap={reducedMotion ? {} : { scale: 0.98 }}
                  >
                    <User size={18} />
                    My Profile
                  </motion.button>

                  <motion.button
                    onClick={handleLogout}
                    className="mt-2 flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-red-500 transition-colors hover:bg-slate-100 dark:hover:bg-slate-800"
                    whileHover={reducedMotion ? {} : { x: 4 }}
                    whileTap={reducedMotion ? {} : { scale: 0.98 }}
                  >
                    <LogOut size={18} />
                    Logout
                  </motion.button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
}