import type { User } from "../../types/user";

import {
  Eye,
  Pencil,
  Shield,
  UserCog,
  UserRound,
} from "lucide-react";

interface UserTableProps {
  users: User[];
  onView: (user: User) => void;
  onEdit: (user: User) => void;
}

function roleBadge(role: string) {
  switch (role) {
    case "Admin":
      return {
        color:
          "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400",
        icon: Shield,
      };

    case "Technician":
      return {
        color:
          "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400",
        icon: UserCog,
      };

    default:
      return {
        color:
          "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400",
        icon: UserRound,
      };
  }
}

export default function UserTable({
  users,
  onView,
  onEdit,
}: UserTableProps) {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">

      <table className="w-full">

        <thead className="border-b border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-800">

          <tr className="text-left text-sm font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">

            <th className="px-6 py-4">ID</th>

            <th className="px-6 py-4">Name</th>

            <th className="px-6 py-4">Email</th>

            <th className="px-6 py-4">Role</th>

            <th className="px-6 py-4 text-center">
              Actions
            </th>

          </tr>

        </thead>

        <tbody>

          {users.length === 0 ? (

            <tr>

              <td
                colSpan={5}
                className="py-12 text-center text-slate-500 dark:text-slate-400"
              >
                No users found.
              </td>

            </tr>

          ) : (

            users.map((user) => {

              const badge = roleBadge(user.role);

              const Icon = badge.icon;

              return (

                <tr
                  key={user.id}
                  className="border-b border-slate-100 transition hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/50"
                >

                  <td className="px-6 py-5 font-semibold text-slate-700 dark:text-white">
                    #{user.id}
                  </td>

                  <td className="px-6 py-5 font-medium text-slate-900 dark:text-white">
                    {user.name}
                  </td>

                  <td className="px-6 py-5 text-slate-600 dark:text-slate-300">
                    {user.email}
                  </td>

                  <td className="px-6 py-5">

                    <span
                      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium ${badge.color}`}
                    >
                      <Icon size={15} />

                      {user.role}

                    </span>

                  </td>

                  <td className="px-6 py-5">

                    <div className="flex justify-center gap-2">

                      <button
                        onClick={() => onView(user)}
                        className="rounded-lg p-2 text-slate-500 transition hover:bg-blue-100 hover:text-blue-600 dark:hover:bg-blue-500/20 dark:hover:text-blue-400"
                      >
                        <Eye size={18} />
                      </button>

                      <button
                        onClick={() => onEdit(user)}
                        className="rounded-lg p-2 text-slate-500 transition hover:bg-green-100 hover:text-green-600 dark:hover:bg-green-500/20 dark:hover:text-green-400"
                      >
                        <Pencil size={18} />
                      </button>

                    </div>

                  </td>

                </tr>

              );

            })

          )}

        </tbody>

      </table>

    </div>
  );
}