import {
  Bell,
  LogOut,
  Search,
  User,
  Sun,
  Moon,
} from "lucide-react";

import { useNavigate } from "react-router-dom";
import { useState, useEffect, useRef } from "react";

import useProfile from "../../hooks/useProfile";
import { useTheme } from "../../context/ThemeContext";

export default function Navbar() {
  const navigate = useNavigate();

  const { user } = useProfile();

  const { theme, toggleTheme } = useTheme();

  const [search, setSearch] = useState("");
  const [profileOpen, setProfileOpen] = useState(false);

  const profileRef = useRef<HTMLDivElement>(null);

  // =====================================
  // Logout
  // =====================================

  const handleLogout = () => {
    localStorage.clear();
    navigate("/");
  };

  // =====================================
  // Search Tickets
  // =====================================

  const handleSearch = () => {
    if (!search.trim()) return;

    navigate(
      `/tickets?search=${encodeURIComponent(search)}`
    );
  };

  // =====================================
  // Close Profile Dropdown
  // =====================================

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        profileRef.current &&
        !profileRef.current.contains(event.target as Node)
      ) {
        setProfileOpen(false);
      }
    }

    document.addEventListener(
      "mousedown",
      handleClickOutside
    );

    return () =>
      document.removeEventListener(
        "mousedown",
        handleClickOutside
      );
  }, []);

  return (
    <header
      className="
      flex
      h-16
      w-full
      items-center
      justify-between
      border-b
      border-slate-300
      bg-white
      px-6
      transition-colors
      dark:border-slate-700
      dark:bg-slate-900
    "
    >
      {/* Left Section */}

      <div className="flex items-center gap-8">
        <h1
          className="
          cursor-pointer
          text-2xl
          font-bold
          text-cyan-600
          dark:text-cyan-400
        "
          onClick={() => navigate("/dashboard")}
        >
          ITMS
        </h1>

        {/* Search */}

        <div className="relative">
          <Search
            size={18}
            onClick={handleSearch}
            className="
            absolute
            left-3
            top-1/2
            -translate-y-1/2
            cursor-pointer
            text-slate-500
            hover:text-cyan-500
            dark:text-slate-400
          "
          />

          <input
            type="text"
            value={search}
            onChange={(e) =>
              setSearch(e.target.value)
            }
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleSearch();
              }
            }}
            placeholder="Search tickets..."
            className="
            w-80
            rounded-lg
            border
            border-slate-300
            bg-white
            py-2
            pl-10
            pr-4
            text-slate-900
            placeholder:text-slate-500
            transition
            focus:outline-none
            focus:ring-2
            focus:ring-cyan-500
            dark:border-slate-700
            dark:bg-slate-800
            dark:text-white
            dark:placeholder:text-slate-400
          "
          />
        </div>
      </div>

      {/* Right Section */}

      <div className="flex items-center gap-6">
        {/* Theme Toggle */}

        <button
          onClick={toggleTheme}
          className="
          rounded-lg
          p-2
          text-slate-600
          transition
          hover:bg-slate-100
          dark:text-slate-300
          dark:hover:bg-slate-800
        "
        >
          {theme === "dark" ? (
            <Sun size={22} />
          ) : (
            <Moon size={22} />
          )}
        </button>

        {/* Notifications */}

        <button
          className="
          relative
          text-slate-600
          transition
          hover:text-black
          dark:text-slate-300
          dark:hover:text-white
        "
        >
          <Bell size={22} />

          <span className="absolute -right-2 -top-2 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs text-white">
            3
          </span>
        </button>

        {/* Profile */}

        <div
          ref={profileRef}
          className="relative"
        >
          <div
            onClick={() =>
              setProfileOpen(!profileOpen)
            }
            className="
            flex
            cursor-pointer
            items-center
            gap-3
            rounded-lg
            px-2
            py-1
            transition
            hover:bg-slate-100
            dark:hover:bg-slate-800
          "
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-cyan-500 text-lg font-bold text-white">
              {user?.name?.charAt(0).toUpperCase() ??
                "U"}
            </div>

            <div>
              <p className="font-medium text-slate-900 dark:text-white">
                {user?.name ?? "Loading..."}
              </p>

              <p className="text-xs text-slate-500 dark:text-slate-400">
                {user?.role ?? ""}
              </p>
            </div>
          </div>

          {/* Dropdown */}

          {profileOpen && (
            <div
              className="
              absolute
              right-0
              mt-3
              w-64
              rounded-xl
              border
              border-slate-300
              bg-white
              shadow-2xl
              dark:border-slate-700
              dark:bg-slate-900
            "
            >
              <div className="p-5">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-cyan-500 text-lg font-bold text-white">
                    {user?.name?.charAt(0).toUpperCase() ??
                      "U"}
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

                <button
                  onClick={() => {
                    navigate("/profile");
                    setProfileOpen(false);
                  }}
                  className="
                  flex
                  w-full
                  items-center
                  gap-2
                  rounded-lg
                  px-3
                  py-2
                  text-left
                  text-slate-900
                  transition
                  hover:bg-slate-100
                  dark:text-white
                  dark:hover:bg-slate-800
                "
                >
                  <User size={18} />
                  My Profile
                </button>

                <button
                  onClick={handleLogout}
                  className="
                  mt-2
                  flex
                  w-full
                  items-center
                  gap-2
                  rounded-lg
                  px-3
                  py-2
                  text-left
                  text-red-500
                  transition
                  hover:bg-slate-100
                  dark:hover:bg-slate-800
                "
                >
                  <LogOut size={18} />
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}