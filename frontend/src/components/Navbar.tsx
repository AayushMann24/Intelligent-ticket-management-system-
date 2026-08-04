import {
  Bell,
  Search,
  Moon,
  UserCircle,
} from "lucide-react";

export default function Navbar() {
  return (
    <header className="h-20 border-b border-zinc-800 bg-zinc-950 px-8">

      <div className="flex h-full items-center justify-between">

        {/* Search */}

        <div className="relative w-96">

          <Search
            size={18}
            className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500"
          />

          <input
            type="text"
            placeholder="Search tickets..."
            className="
              w-full
              rounded-xl
              border
              border-zinc-700
              bg-zinc-900
              py-3
              pl-11
              pr-4
              text-white
              outline-none
              focus:border-blue-500
            "
          />

        </div>

        {/* Right Side */}

        <div className="flex items-center gap-6">

          <button className="text-zinc-400 hover:text-white">
            <Bell size={22} />
          </button>

          <button className="text-zinc-400 hover:text-white">
            <Moon size={22} />
          </button>

          <div className="flex items-center gap-3">

            <UserCircle
              size={42}
              className="text-blue-500"
            />

            <div>

              <h3 className="font-semibold text-white">
                Aayush
              </h3>

              <p className="text-sm text-zinc-400">
                Administrator
              </p>

            </div>

          </div>

        </div>

      </div>

    </header>
  );
}