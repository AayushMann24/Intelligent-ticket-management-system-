import { ArrowRight } from "lucide-react";
import type { Ticket } from "../../types/ticket";

interface RecentTicketsProps {
  tickets: Ticket[];
}

function priorityColor(priority: string) {
  switch (priority) {
    case "High":
      return "bg-red-500/20 text-red-400";

    case "Medium":
      return "bg-yellow-500/20 text-yellow-400";

    case "Low":
      return "bg-green-500/20 text-green-400";

    default:
      return "bg-zinc-700 text-zinc-300";
  }
}

function statusColor(status: string) {
  switch (status) {
    case "Open":
      return "text-blue-400";

    case "Assigned":
      return "text-yellow-400";

    case "Resolved":
      return "text-green-400";

    default:
      return "text-zinc-400";
  }
}

export default function RecentTickets({
  tickets,
}: RecentTicketsProps) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900">

      {/* Header */}

      <div className="flex items-center justify-between border-b border-zinc-800 p-6">

        <h2 className="text-xl font-semibold text-white">
          Recent Tickets
        </h2>

        <button className="flex items-center gap-2 text-blue-400 hover:text-blue-300">
          View All
          <ArrowRight size={18} />
        </button>

      </div>

      {/* Ticket List */}

      <div>

        {tickets.length === 0 ? (

          <div className="p-8 text-center text-zinc-500">
            No recent tickets found.
          </div>

        ) : (

          tickets.map((ticket) => (

            <div
              key={ticket.id}
              className="flex items-center justify-between border-b border-zinc-800 p-5 last:border-none hover:bg-zinc-800/40 transition"
            >

              <div>

                <h3 className="font-semibold text-white">
                  {ticket.title}
                </h3>

                <p className="text-sm text-zinc-400">
                  {ticket.assigned_to ?? "Unassigned"}
                </p>

              </div>

              <div className="flex items-center gap-4">

                <span
                  className={`rounded-full px-3 py-1 text-sm font-medium ${priorityColor(ticket.priority)}`}
                >
                  {ticket.priority}
                </span>

                <span className={statusColor(ticket.status)}>
                  {ticket.status}
                </span>

              </div>

            </div>

          ))

        )}

      </div>

    </div>
  );
}