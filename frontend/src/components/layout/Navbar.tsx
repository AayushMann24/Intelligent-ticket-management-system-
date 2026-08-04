import { Bell, LogOut, Search } from "lucide-react";

export default function Navbar() {
  return (
    <header className="w-full h-16 bg-slate-900 border-b border-slate-700 flex items-center justify-between px-6">
      {/* Left Section */}
      <div className="flex items-center gap-8">
        {/* Logo */}
        <h1 className="text-2xl font-bold text-cyan-400">
          ITMS
        </h1>

        {/* Search Bar */}
        <div className="relative">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
            size={18}
          />

          <input
            type="text"
            placeholder="Search tickets..."
            className="pl-10 pr-4 py-2 rounded-lg bg-slate-800 text-white placeholder:text-slate-400 border border-slate-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 w-80"
          />
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-6">
        {/* Notifications */}
        <button className="relative text-slate-300 hover:text-white transition">
          <Bell size={22} />

          <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
            3
          </span>
        </button>

        {/* User Info */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-cyan-500 flex items-center justify-center text-white font-bold">
            A
          </div>

          <div>
            <p className="text-white font-medium">Admin</p>
            <p className="text-xs text-slate-400">Administrator</p>
          </div>
        </div>

        {/* Logout */}
        <button className="flex items-center gap-2 bg-red-600 hover:bg-red-700 transition px-4 py-2 rounded-lg text-white">
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </header>
  );
}