interface TicketToolbarProps {
  search: string;
  setSearch: (value: string) => void;

  status: string;
  setStatus: (value: string) => void;

  priority: string;
  setPriority: (value: string) => void;
}

export default function TicketToolbar({
  search,
  setSearch,
  status,
  setStatus,
  priority,
  setPriority,
}: TicketToolbarProps) {
  return (
    <div className="mb-6 flex flex-wrap gap-4">

      <input
        type="text"
        placeholder="Search tickets..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-2 text-white"
      />

      <select
        value={status}
        onChange={(e) => setStatus(e.target.value)}
        className="rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-2 text-white"
      >
        <option value="">All Status</option>
        <option value="Open">Open</option>
        <option value="Assigned">Assigned</option>
        <option value="Resolved">Resolved</option>
      </select>

      <select
        value={priority}
        onChange={(e) => setPriority(e.target.value)}
        className="rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-2 text-white"
      >
        <option value="">All Priority</option>
        <option value="High">High</option>
        <option value="Medium">Medium</option>
        <option value="Low">Low</option>
      </select>

    </div>
  );
}