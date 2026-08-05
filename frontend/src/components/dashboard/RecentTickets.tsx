import { ArrowRight, Clock3, User } from "lucide-react";
import type { RecentTicket } from "../../services/dashboardService";

interface RecentTicketsProps {
  tickets: RecentTicket[];
}
function priorityColor(priority: string) {
  switch (priority) {
    case "High":
      return "bg-red-500/20 text-red-400 border border-red-500/30";

    case "Medium":
      return "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30";

    case "Low":
      return "bg-green-500/20 text-green-400 border border-green-500/30";

    default:
      return "bg-zinc-700 text-zinc-300";
  }
}

function statusColor(status: string) {
  switch (status) {
    case "Open":
      return "bg-blue-500/20 text-blue-400";

    case "Assigned":
      return "bg-yellow-500/20 text-yellow-400";

    case "Resolved":
      return "bg-green-500/20 text-green-400";

    default:
      return "bg-zinc-700 text-zinc-300";
  }
}

function getRelativeTime(date: string) {
  const now = new Date().getTime();
  const created = new Date(date).getTime();

  const diff = Math.floor((now - created) / 1000);

  if (diff < 60) return "Just now";

  if (diff < 3600)
    return `${Math.floor(diff / 60)} min ago`;

  if (diff < 86400)
    return `${Math.floor(diff / 3600)} hr ago`;

  return `${Math.floor(diff / 86400)} day ago`;
}

export default function RecentTickets({
  tickets,
}: RecentTicketsProps) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900 shadow-lg">

      {/* Header */}

      <div className="flex items-center justify-between border-b border-zinc-800 px-6 py-5">

        <h2 className="text-xl font-semibold text-white">
          Recent Tickets
        </h2>

        <button className="flex items-center gap-2 text-sm font-medium text-blue-400 transition hover:text-blue-300">
          View All
          <ArrowRight size={18} />
        </button>

      </div>

      {/* Empty State */}

      {tickets.length === 0 ? (
        <div className="flex h-60 items-center justify-center text-zinc-500">
          No recent tickets found.
        </div>
      ) : (

        <div>

          {tickets.map((ticket) => (

            <div
              key={ticket.id}
              className="cursor-pointer border-b border-zinc-800 p-5 transition hover:bg-zinc-800/40 last:border-none"
            >

              {/* First Row */}

              <div className="mb-3 flex items-center justify-between">

                <h3 className="font-semibold text-white">
                  #{ticket.id} • {ticket.title}
                </h3>

                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${statusColor(ticket.status)}`}
                >
                  {ticket.status}
                </span>

              </div>

              {/* Second Row */}

              <div className="mb-3 flex items-center gap-3">

                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${priorityColor(ticket.priority)}`}
                >
                  {ticket.priority}
                </span>

              </div>

              {/* Third Row */}

              <div className="flex items-center justify-between text-sm text-zinc-400">

                <div className="flex items-center gap-2">

                  <User size={16} />

                  <span>{ticket.assigned_to}</span>

                </div>

                <div className="flex items-center gap-2">

                  <Clock3 size={16} />

                  <span>
                    {getRelativeTime(ticket.created_at)}
                  </span>

                </div>

              </div>

            </div>

          ))}

        </div>

      )}

    </div>
  );
}
