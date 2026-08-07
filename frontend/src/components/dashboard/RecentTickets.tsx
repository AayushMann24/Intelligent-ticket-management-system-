import { ArrowRight, Clock3, User } from "lucide-react";
import { useNavigate } from "react-router-dom";
import type { RecentTicket } from "../../services/dashboardService";

interface RecentTicketsProps {
  tickets: RecentTicket[];
}

function priorityColor(priority: string) {
  switch (priority) {
    case "High":
      return "bg-red-100 text-red-600 dark:bg-red-500/20 dark:text-red-400";

    case "Medium":
      return "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400";

    case "Low":
      return "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400";

    default:
      return "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300";
  }
}

function statusColor(status: string) {
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

  const navigate = useNavigate();

  return (
    <div
      className="
        rounded-2xl
        border
        border-slate-200
        bg-white
        shadow-sm
        transition-colors
        duration-300

        dark:border-slate-800
        dark:bg-slate-900
      "
    >

      {/* Header */}

      <div
        className="
          flex
          items-center
          justify-between
          border-b
          border-slate-200
          px-6
          py-5

          dark:border-slate-800
        "
      >

        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
          Recent Tickets
        </h2>

        <button
          onClick={() => navigate("/tickets")}
          className="flex items-center gap-2 text-sm font-semibold text-blue-600 transition hover:text-blue-700 dark:text-blue-400"
        >
          View All
          <ArrowRight size={18} />
        </button>

      </div>

      {/* Empty */}

      {tickets.length === 0 ? (

        <div className="flex h-60 items-center justify-center text-slate-500 dark:text-slate-400">
          No recent tickets found.
        </div>

      ) : (

        <div>

          {tickets.map((ticket) => (

            <div
              key={ticket.id}
              className="
                cursor-pointer
                border-b
                border-slate-200
                p-5
                transition-all
                duration-200

                hover:bg-slate-50

                dark:border-slate-800
                dark:hover:bg-slate-800/40

                last:border-none
              "
            >

              {/* Top */}

              <div className="mb-3 flex items-center justify-between">

                <h3 className="font-semibold text-slate-900 dark:text-white">
                  #{ticket.id} • {ticket.title}
                </h3>

                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${statusColor(ticket.status)}`}
                >
                  {ticket.status}
                </span>

              </div>

              {/* Priority */}

              <div className="mb-4">

                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${priorityColor(ticket.priority)}`}
                >
                  {ticket.priority}
                </span>

              </div>

              {/* Footer */}

              <div className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">

                <div className="flex items-center gap-2">

                  <User size={16} />

                  <span>
                    {ticket.assigned_to || "Unassigned"}
                  </span>

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