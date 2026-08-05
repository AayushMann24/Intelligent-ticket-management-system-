import type { Ticket } from "../../types/ticket";
import {
  Eye,
  Pencil,
  Trash2,
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
  return (
    <div className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900 shadow-lg">
      <table className="w-full">
        <thead className="bg-zinc-800 text-left text-sm uppercase tracking-wide text-zinc-300">
          <tr>
            <th className="px-6 py-4">ID</th>
            <th className="px-6 py-4">Title</th>
            <th className="px-6 py-4">Priority</th>
            <th className="px-6 py-4">Status</th>
            <th className="px-6 py-4">Assigned To</th>
            <th className="px-6 py-4">Created</th>
            <th className="px-6 py-4 text-center">
              Actions
            </th>
          </tr>
        </thead>

        <tbody>
          {tickets.length === 0 ? (
            <tr>
              <td
                colSpan={7}
                className="py-10 text-center text-zinc-500"
              >
                No tickets found.
              </td>
            </tr>
          ) : (
            tickets.map((ticket) => (
              <tr
                key={ticket.id}
                className="border-t border-zinc-800 transition hover:bg-zinc-800/40"
              >
                <td className="px-6 py-4 font-medium">
                  #{ticket.id}
                </td>

                <td className="px-6 py-4">
                  {ticket.title}
                </td>

                <td className="px-6 py-4">
                  {ticket.priority}
                </td>

                <td className="px-6 py-4">
                  {ticket.status}
                </td>

                <td className="px-6 py-4">
                  {ticket.assigned_to || "Unassigned"}
                </td>

                <td className="px-6 py-4">
                  {new Date(
                    ticket.created_at
                  ).toLocaleDateString()}
                </td>

                <td className="px-6 py-4">
                  <div className="flex items-center justify-center gap-2">

                    <button
                      onClick={() => onView(ticket)}
                      className="rounded-md p-2 text-zinc-300 transition hover:bg-zinc-700 hover:text-white"
                      title="View Ticket"
                    >
                      <Eye size={18} />
                    </button>

                    <button
                      onClick={() => onEdit(ticket)}
                      className="rounded-md p-2 text-blue-400 transition hover:bg-blue-600 hover:text-white"
                      title="Edit Ticket"
                    >
                      <Pencil size={18} />
                    </button>

                    <button
                      onClick={() => onDelete(ticket)}
                      className="rounded-md p-2 text-red-400 transition hover:bg-red-600 hover:text-white"
                      title="Delete Ticket"
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