import type { Ticket } from "../../types/ticket";

import {
  Eye,
  Pencil,
  Trash2,
  Bot,
} from "lucide-react";

interface TicketTableProps {
  tickets: Ticket[];

  onView: (ticket: Ticket) => void;
  onEdit: (ticket: Ticket) => void;
  onDelete: (ticket: Ticket) => void;
}

export default function TicketTable({
  tickets,
  onView,
  onEdit,
  onDelete,
}: TicketTableProps) {

  const priorityColor = (priority: string) => {
    switch (priority) {
      case "High":
        return "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400";

      case "Medium":
        return "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400";

      case "Low":
        return "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400";

      default:
        return "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300";
    }
  };

  const statusColor = (status: string) => {
    switch (status) {
      case "Open":
        return "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400";

      case "Assigned":
        return "bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-400";

      case "Resolved":
        return "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400";

      default:
        return "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300";
    }
  };

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">

      <table className="w-full">

        <thead className="bg-slate-100 dark:bg-slate-800">

          <tr className="text-left text-sm font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">

            <th className="px-6 py-4">ID</th>

            <th className="px-6 py-4">Title</th>

            <th className="px-6 py-4">Priority</th>

            <th className="px-6 py-4">AI</th>

            <th className="px-6 py-4">Status</th>

            <th className="px-6 py-4">Assigned</th>

            <th className="px-6 py-4">Created</th>

            <th className="px-6 py-4 text-center">Actions</th>

          </tr>

        </thead>

        <tbody>

          {tickets.length === 0 ? (

            <tr>

              <td
                colSpan={8}
                className="py-16 text-center text-slate-500 dark:text-slate-400"
              >
                No tickets found.
              </td>

            </tr>

          ) : (

            tickets.map((ticket) => (

              <tr
                key={ticket.id}
                className="border-t border-slate-200 transition hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/40"
              >

                <td className="px-6 py-5 font-semibold text-slate-900 dark:text-white">
                  #{ticket.id}
                </td>

                <td className="px-6 py-5 font-medium text-slate-900 dark:text-white">
                  {ticket.title}
                </td>

                <td className="px-6 py-5">

                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${priorityColor(ticket.priority)}`}
                  >
                    {ticket.priority}
                  </span>

                </td>

                <td className="px-6 py-5">

                  {ticket.ai_processed ? (

                    <span className="inline-flex items-center gap-1 rounded-full bg-cyan-100 px-3 py-1 text-xs font-semibold text-cyan-700 dark:bg-cyan-500/20 dark:text-cyan-400">

                      <Bot size={14} />

                      AI

                    </span>

                  ) : (

                    <span className="text-slate-400">
                      —
                    </span>

                  )}

                </td>

                <td className="px-6 py-5">

                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${statusColor(ticket.status)}`}
                  >
                    {ticket.status}
                  </span>

                </td>

                <td className="px-6 py-5 text-slate-700 dark:text-slate-300">
                  {ticket.assigned_name ?? "Unassigned"}
                </td>

                <td className="px-6 py-5 text-slate-600 dark:text-slate-400">
                  {new Date(ticket.created_at).toLocaleDateString()}
                </td>

                <td className="px-6 py-5">

                  <div className="flex items-center justify-center gap-2">

                    <button
                      onClick={() => onView(ticket)}
                      className="rounded-lg p-2 text-slate-500 transition hover:bg-slate-200 hover:text-blue-600 dark:hover:bg-slate-700 dark:hover:text-blue-400"
                    >
                      <Eye size={18} />
                    </button>

                    <button
                      onClick={() => onEdit(ticket)}
                      className="rounded-lg p-2 text-slate-500 transition hover:bg-slate-200 hover:text-green-600 dark:hover:bg-slate-700 dark:hover:text-green-400"
                    >
                      <Pencil size={18} />
                    </button>

                    <button
                      onClick={() => onDelete(ticket)}
                      className="rounded-lg p-2 text-slate-500 transition hover:bg-slate-200 hover:text-red-600 dark:hover:bg-slate-700 dark:hover:text-red-400"
                    >
                      <Trash2 size={18} />
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