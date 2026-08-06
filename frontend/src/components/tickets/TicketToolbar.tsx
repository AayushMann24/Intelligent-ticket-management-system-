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
    <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
      {/* Left Side */}
      <div className="flex flex-wrap items-center gap-4">

        {/* Search */}
        <div className="relative">
          <Search
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400"
          />

          <input
            type="text"
            placeholder="Search tickets..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-72 rounded-lg border border-zinc-700 bg-zinc-900 py-2 pl-10 pr-4 text-white outline-none focus:border-blue-500"
          />
        </div>

        {/* Status */}
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-2 text-white outline-none focus:border-blue-500"
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
          className="rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-2 text-white outline-none focus:border-blue-500"
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
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2 font-medium text-white transition hover:bg-blue-700"
        >
          <Plus size={18} />
          New Ticket
        </button>
      )}
    </div>
  );
}