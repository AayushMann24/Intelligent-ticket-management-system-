import { Search, Filter } from "lucide-react";

interface UserToolbarProps {
  search: string;
  setSearch: (value: string) => void;

  role: string;
  setRole: (value: string) => void;
}

export default function UserToolbar({
  search,
  setSearch,
  role,
  setRole,
}: UserToolbarProps) {
  return (
    <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">

      <div className="relative flex-1">

        <Search
          size={18}
          className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
        />

        <input
          type="text"
          placeholder="Search users..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="
            w-full
            rounded-xl
            border
            border-slate-300
            bg-white
            py-3
            pl-11
            pr-4
            text-slate-900
            outline-none
            transition
            focus:border-blue-500
            dark:border-slate-700
            dark:bg-slate-900
            dark:text-white
          "
        />

      </div>

      <div className="relative w-full lg:w-64">

        <Filter
          size={18}
          className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
        />

        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="
            w-full
            rounded-xl
            border
            border-slate-300
            bg-white
            py-3
            pl-11
            pr-4
            text-slate-900
            outline-none
            transition
            focus:border-blue-500
            dark:border-slate-700
            dark:bg-slate-900
            dark:text-white
          "
        >
          <option value="">All Roles</option>
          <option value="Admin">Admin</option>
          <option value="Technician">Technician</option>
          <option value="Employee">Employee</option>
        </select>

      </div>

    </div>
  );
}