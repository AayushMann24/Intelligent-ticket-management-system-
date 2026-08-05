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
    <div className="mb-6 flex flex-col gap-4 md:flex-row">
      {/* Search */}
      <input
        type="text"
        placeholder="Search users..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="flex-1 rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-3 text-white outline-none transition focus:border-blue-500"
      />

      {/* Role Filter */}
      <select
        value={role}
        onChange={(e) => setRole(e.target.value)}
        className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-3 text-white outline-none transition focus:border-blue-500 md:w-60"
      >
        <option value="">All Roles</option>
        <option value="Admin">Admin</option>
        <option value="Technician">Technician</option>
        <option value="Employee">Employee</option>
      </select>
    </div>
  );
}