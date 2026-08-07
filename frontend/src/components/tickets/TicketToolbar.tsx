import { Search, Plus } from "lucide-react";

interface TicketToolbarProps {
  search: string;
  setSearch: (value: string) => void;

  status: string;
  setStatus: (value: string) => void;

  priority: string;
  setPriority: (value: string) => void;

  onCreate: () => void;
}

export default function TicketToolbar({
  search,
  setSearch,
  status,
  setStatus,
  priority,
  setPriority,
  onCreate,
}: TicketToolbarProps) {
  const role = localStorage.getItem("role");

  return (
    <div className="mb-8 flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all duration-300 dark:border-slate-800 dark:bg-slate-900 lg:flex-row lg:items-center lg:justify-between">

      {/* Left Side */}

      <div className="flex flex-1 flex-col gap-4 md:flex-row">

        {/* Search */}

        <div className="relative flex-1">

          <Search
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          />

          <input
            type="text"
            placeholder="Search tickets..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="
              w-full
              rounded-xl
              border
              border-slate-300
              bg-slate-50
              py-2.5
              pl-10
              pr-4
              text-slate-900
              outline-none
              transition-all

              placeholder:text-slate-400

              focus:border-blue-500
              focus:ring-2
              focus:ring-blue-200

              dark:border-slate-700
              dark:bg-slate-800
              dark:text-white
              dark:placeholder:text-slate-400
              dark:focus:ring-blue-500/20
            "
          />

        </div>

        {/* Status */}

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="
            rounded-xl
            border
            border-slate-300
            bg-slate-50
            px-4
            py-2.5
            text-slate-900
            outline-none
            transition-all

            focus:border-blue-500
            focus:ring-2
            focus:ring-blue-200

            dark:border-slate-700
            dark:bg-slate-800
            dark:text-white
            dark:focus:ring-blue-500/20
          "
        >
          <option value="">All Status</option>
          <option value="Open">Open</option>
          <option value="Assigned">Assigned</option>
          <option value="Resolved">Resolved</option>
        </select>

        {/* Priority */}

        <select
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
          className="
            rounded-xl
            border
            border-slate-300
            bg-slate-50
            px-4
            py-2.5
            text-slate-900
            outline-none
            transition-all

            focus:border-blue-500
            focus:ring-2
            focus:ring-blue-200

            dark:border-slate-700
            dark:bg-slate-800
            dark:text-white
            dark:focus:ring-blue-500/20
          "
        >
          <option value="">All Priority</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>

      </div>

      {/* Right Side */}

      {role !== "Technician" && (

        <button
          onClick={onCreate}
          className="
            flex
            items-center
            justify-center
            gap-2
            rounded-xl
            bg-blue-600
            px-6
            py-2.5
            font-semibold
            text-white
            shadow-sm
            transition-all
            duration-300

            hover:-translate-y-0.5
            hover:bg-blue-700
            hover:shadow-lg
          "
        >
          <Plus size={18} />
          New Ticket
        </button>

      )}

    </div>
  );
}