import type { Ticket } from "../../types/ticket";

interface TicketTableProps {
  tickets: Ticket[];
}

export default function TicketTable({
  tickets,
}: TicketTableProps) {
  return (
    <div className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900">
      <table className="w-full">

        <thead className="bg-zinc-800 text-left">
          <tr>
            <th className="px-6 py-4">ID</th>
            <th className="px-6 py-4">Title</th>
            <th className="px-6 py-4">Priority</th>
            <th className="px-6 py-4">Status</th>
            <th className="px-6 py-4">Assigned To</th>
            <th className="px-6 py-4">Created</th>
          </tr>
        </thead>

        <tbody>

          {tickets.map((ticket) => (

            <tr
              key={ticket.id}
              className="border-t border-zinc-800 hover:bg-zinc-800/40"
            >
              <td className="px-6 py-4">
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
                {ticket.assigned_to}
              </td>

              <td className="px-6 py-4">
                {new Date(ticket.created_at).toLocaleDateString()}
              </td>

            </tr>

          ))}

        </tbody>

      </table>
    </div>
  );
}