import type { User } from "../../types/user";
import { Eye, Pencil } from "lucide-react";

interface UserTableProps {
  users: User[];
  onView: (user: User) => void;
  onEdit: (user: User) => void;
}

export default function UserTable({
  users,
  onView,
  onEdit,
}: UserTableProps) {
  return (
    <div className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900">
      <table className="w-full">
        <thead className="bg-zinc-800">
          <tr>
            <th className="px-6 py-4 text-left">ID</th>
            <th className="px-6 py-4 text-left">Name</th>
            <th className="px-6 py-4 text-left">Email</th>
            <th className="px-6 py-4 text-left">Role</th>
            <th className="px-6 py-4 text-center">Actions</th>
          </tr>
        </thead>

        <tbody>
          {users.length === 0 ? (
            <tr>
              <td
                colSpan={5}
                className="py-8 text-center text-zinc-400"
              >
                No users found.
              </td>
            </tr>
          ) : (
            users.map((user) => (
              <tr
                key={user.id}
                className="border-t border-zinc-800 hover:bg-zinc-800/40"
              >
                <td className="px-6 py-4">
                  #{user.id}
                </td>

                <td className="px-6 py-4">
                  {user.name}
                </td>

                <td className="px-6 py-4">
                  {user.email}
                </td>

                <td className="px-6 py-4">
                  {user.role}
                </td>

                <td className="px-6 py-4">
                  <div className="flex justify-center gap-2">
                    <button
                      onClick={() => onView(user)}
                      className="rounded-md p-2 hover:bg-zinc-700"
                    >
                      <Eye size={18} />
                    </button>

                    <button
                      onClick={() => onEdit(user)}
                      className="rounded-md p-2 hover:bg-blue-600"
                    >
                      <Pencil size={18} />
                    </button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}