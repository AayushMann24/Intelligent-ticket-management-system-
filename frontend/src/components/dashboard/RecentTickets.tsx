import { ArrowRight, Clock3, User } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import type { RecentTicket } from "../../services/dashboardService";
import { useReducedMotion } from "../../hooks/useReducedMotion";

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
  if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} hr ago`;
  return `${Math.floor(diff / 86400)} day ago`;
}

const itemVariants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
  transition: { duration: 0.15, ease: [0, 0, 0.2, 1] },
};

const containerVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { staggerChildren: 0.05, delayChildren: 0.1 } },
  exit: { opacity: 0 },
};

export default function RecentTickets({ tickets }: RecentTicketsProps) {
  const navigate = useNavigate();
  const reducedMotion = useReducedMotion();

  return (
    <motion.div
      className="rounded-2xl border border-slate-200 bg-white shadow-sm transition-colors duration-300 dark:border-slate-800 dark:bg-slate-900"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: [0, 0, 0.2, 1] }}
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 px-6 py-5 dark:border-slate-800">
        <motion.h2
          className="text-xl font-semibold text-slate-900 dark:text-white"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2 }}
        >
          Recent Tickets
        </motion.h2>

        <motion.button
          onClick={() => navigate("/tickets")}
          className="flex items-center gap-2 text-sm font-semibold text-blue-600 transition-colors hover:text-blue-700 dark:text-blue-400"
          whileHover={reducedMotion ? {} : { x: 4 }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2, delay: 0.1 }}
        >
          View All
          <ArrowRight size={18} />
        </motion.button>
      </div>

      {/* Empty */}
      {tickets.length === 0 ? (
        <motion.div
          className="flex h-60 items-center justify-center text-slate-500 dark:text-slate-400"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          No recent tickets found.
        </motion.div>
      ) : (
        <motion.div variants={containerVariants} initial="initial" animate="animate" exit="exit">
          {tickets.map((ticket) => (
            <motion.div
              key={ticket.id}
              className="cursor-pointer border-b border-slate-200 p-5 transition-colors dark:border-slate-800 last:border-none"
              variants={itemVariants}
              whileHover={reducedMotion ? {} : { backgroundColor: "rgba(0, 0, 0, 0.02)" }}
            >
              {/* Top */}
              <div className="mb-3 flex items-center justify-between">
                <motion.h3
                  className="font-semibold text-slate-900 dark:text-white"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  #{ticket.id} • {ticket.title}
                </motion.h3>

                <motion.span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${statusColor(ticket.status)}`}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ type: "spring", stiffness: 400, damping: 25 }}
                >
                  {ticket.status}
                </motion.span>
              </div>

              {/* Priority */}
              <motion.div
                className="mb-4"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.05 }}
              >
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${priorityColor(ticket.priority)}`}>
                  {ticket.priority}
                </span>
              </motion.div>

              {/* Footer */}
              <motion.div
                className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400"
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <div className="flex items-center gap-2">
                  <User size={16} />
                  <span>{ticket.assigned_to || "Unassigned"}</span>
                </div>

                <div className="flex items-center gap-2">
                  <Clock3 size={16} />
                  <span>{getRelativeTime(ticket.created_at)}</span>
                </div>
              </motion.div>
            </motion.div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
}