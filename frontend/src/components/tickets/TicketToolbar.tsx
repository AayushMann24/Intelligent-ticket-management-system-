import { Search, Plus } from "lucide-react";
import { motion } from "framer-motion";
import { useAuth } from "../../context/useAuth";
import { useReducedMotion } from "../../hooks/useReducedMotion";

interface TicketToolbarProps {
  search: string;
  setSearch: (value: string) => void;
  status: string;
  setStatus: (value: string) => void;
  priority: string;
  setPriority: (value: string) => void;
  onCreate: () => void;
}

export default function TicketToolbar({
  search,
  setSearch,
  status,
  setStatus,
  priority,
  setPriority,
  onCreate,
}: TicketToolbarProps) {
  const { user } = useAuth();
  const role = user?.role;
  const reducedMotion = useReducedMotion();

  const itemVariants = {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    transition: { duration: 0.2 },
  };

  const containerVariants = {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { staggerChildren: 0.08, delayChildren: 0.1 } },
  };

  return (
    <motion.div
      className="mb-8 flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all duration-300 dark:border-slate-800 dark:bg-slate-900 lg:flex-row lg:items-center lg:justify-between"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: [0, 0, 0.2, 1] }}
    >
      {/* Left Side */}
      <motion.div
        className="flex flex-1 flex-col gap-4 md:flex-row"
        variants={containerVariants}
        initial="initial"
        animate="animate"
      >
        {/* Search */}
        <motion.div className="relative flex-1" variants={itemVariants}>
          <motion.div
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            <Search size={18} />
          </motion.div>

          <motion.input
            type="text"
            placeholder="Search tickets..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-xl border border-slate-300 bg-slate-50 py-2.5 pl-10 pr-4 text-slate-900 outline-none transition-all placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:placeholder:text-slate-400 dark:focus:ring-blue-500/20"
            whileFocus={reducedMotion ? {} : { scale: 1.01 }}
            initial={{ opacity: 0, width: "50%" }}
            animate={{ opacity: 1, width: "100%" }}
            transition={{ duration: 0.3, delay: 0.15 }}
          />
        </motion.div>

        {/* Status */}
        <motion.select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="rounded-xl border border-slate-300 bg-slate-50 px-4 py-2.5 text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:ring-blue-500/20"
          whileFocus={reducedMotion ? {} : { scale: 1.01 }}
          variants={itemVariants}
        >
          <option value="">All Status</option>
          <option value="Open">Open</option>
          <option value="Assigned">Assigned</option>
          <option value="Resolved">Resolved</option>
        </motion.select>

        {/* Priority */}
        <motion.select
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
          className="rounded-xl border border-slate-300 bg-slate-50 px-4 py-2.5 text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:ring-blue-500/20"
          whileFocus={reducedMotion ? {} : { scale: 1.01 }}
          variants={itemVariants}
        >
          <option value="">All Priority</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </motion.select>
      </motion.div>

      {/* Right Side */}
      {role !== "Technician" && (
        <motion.button
          onClick={onCreate}
          className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-2.5 font-semibold text-white shadow-sm transition-all duration-300 hover:bg-blue-700 hover:shadow-lg"
          whileHover={reducedMotion ? {} : { y: -2, boxShadow: "0 10px 25px -5px rgba(37, 99, 235, 0.4)" }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.3, ease: [0, 0, 0.2, 1] }}
        >
          <Plus size={18} />
          New Ticket
        </motion.button>
      )}
    </motion.div>
  );
}