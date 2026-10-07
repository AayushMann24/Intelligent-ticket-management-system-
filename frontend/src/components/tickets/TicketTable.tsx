import type { Ticket } from "../../types/ticket";
import { motion } from "framer-motion";
import { Eye, Pencil, Trash2, Bot } from "lucide-react";
import { useReducedMotion } from "../../hooks/useReducedMotion";

interface TicketTableProps {
  tickets: Ticket[];
  onView: (ticket: Ticket) => void;
  onEdit: (ticket: Ticket) => void;
  onDelete: (ticket: Ticket) => void;
}

export default function TicketTable({ tickets, onView, onEdit, onDelete }: TicketTableProps) {
  const reducedMotion = useReducedMotion();

  const priorityColor = (priority: string) => {
    switch (priority) {
      case "High": return "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400";
      case "Medium": return "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400";
      case "Low": return "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400";
      default: return "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300";
    }
  };

  const statusColor = (status: string) => {
    switch (status) {
      case "Open": return "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400";
      case "Assigned": return "bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-400";
      case "Resolved": return "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400";
      default: return "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300";
    }
  };

  const rowVariants = {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 },
    transition: { duration: 0.15, ease: [0, 0, 0.2, 1] },
  };

  const containerVariants = {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { staggerChildren: 0.03, delayChildren: 0.05 } },
    exit: { opacity: 0 },
  };

  return (
    <motion.div
      className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: [0, 0, 0.2, 1] }}
    >
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

        <motion.tbody variants={containerVariants} initial="initial" animate="animate" exit="exit">
          {tickets.length === 0 ? (
            <motion.tr key="empty" variants={rowVariants}>
              <td colSpan={8} className="py-16 text-center text-slate-500 dark:text-slate-400">
                No tickets found.
              </td>
            </motion.tr>
          ) : (
            tickets.map((ticket) => (
              <motion.tr
                key={ticket.id}
                className="border-t border-slate-200 transition-colors hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/40"
                variants={rowVariants}
              >
                <motion.td className="px-6 py-5 font-semibold text-slate-900 dark:text-white" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                  #{ticket.id}
                </motion.td>

                <motion.td className="px-6 py-5 font-medium text-slate-900 dark:text-white" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.02 }}>
                  {ticket.title}
                </motion.td>

                <motion.td className="px-6 py-5" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.04 }}>
                  <motion.span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${priorityColor(ticket.priority)}`}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ type: "spring", stiffness: 400, damping: 25 }}
                  >
                    {ticket.priority}
                  </motion.span>
                </motion.td>

                <motion.td className="px-6 py-5" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.06 }}>
                  {ticket.ai_processed ? (
                    <motion.span
                      className="inline-flex items-center gap-1 rounded-full bg-cyan-100 px-3 py-1 text-xs font-semibold text-cyan-700 dark:bg-cyan-500/20 dark:text-cyan-400"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ type: "spring", stiffness: 400, damping: 25 }}
                    >
                      <Bot size={14} /> AI
                    </motion.span>
                  ) : (
                    <motion.span className="text-slate-400" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>—</motion.span>
                  )}
                </motion.td>

                <motion.td className="px-6 py-5" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.08 }}>
                  <motion.span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${statusColor(ticket.status)}`}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ type: "spring", stiffness: 400, damping: 25 }}
                  >
                    {ticket.status}
                  </motion.span>
                </motion.td>

                <motion.td className="px-6 py-5 text-slate-700 dark:text-slate-300" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
                  {ticket.assigned_name ?? "Unassigned"}
                </motion.td>

                <motion.td className="px-6 py-5 text-slate-600 dark:text-slate-400" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.12 }}>
                  {new Date(ticket.created_at).toLocaleDateString()}
                </motion.td>

                <motion.td className="px-6 py-5" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.14 }}>
                  <div className="flex items-center justify-center gap-2">
                    <motion.button
                      onClick={() => onView(ticket)}
                      className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-200 hover:text-blue-600 dark:hover:bg-slate-700 dark:hover:text-blue-400"
                      whileHover={reducedMotion ? {} : { scale: 1.1 }}
                      whileTap={reducedMotion ? {} : { scale: 0.9 }}
                      aria-label="View ticket"
                    >
                      <Eye size={18} />
                    </motion.button>

                    <motion.button
                      onClick={() => onEdit(ticket)}
                      className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-200 hover:text-green-600 dark:hover:bg-slate-700 dark:hover:text-green-400"
                      whileHover={reducedMotion ? {} : { scale: 1.1 }}
                      whileTap={reducedMotion ? {} : { scale: 0.9 }}
                      aria-label="Edit ticket"
                    >
                      <Pencil size={18} />
                    </motion.button>

                    <motion.button
                      onClick={() => onDelete(ticket)}
                      className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-200 hover:text-red-600 dark:hover:bg-slate-700 dark:hover:text-red-400"
                      whileHover={reducedMotion ? {} : { scale: 1.1 }}
                      whileTap={reducedMotion ? {} : { scale: 0.9 }}
                      aria-label="Delete ticket"
                    >
                      <Trash2 size={18} />
                    </motion.button>
                  </div>
                </motion.td>
              </motion.tr>
            ))
          )}
        </motion.tbody>
      </table>
    </motion.div>
  );
}