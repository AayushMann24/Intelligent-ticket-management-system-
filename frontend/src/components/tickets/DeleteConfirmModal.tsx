import { motion } from "framer-motion";
import { TriangleAlert, X } from "lucide-react";
import { useReducedMotion } from "../../hooks/useReducedMotion";

interface DeleteConfirmModalProps {
  open: boolean;
  ticketTitle: string;
  onClose: () => void;
  onConfirm: () => Promise<void>;
}

export default function DeleteConfirmModal({ open, ticketTitle, onClose, onConfirm }: DeleteConfirmModalProps) {
  const reducedMotion = useReducedMotion();

  if (!open) return null;

  const modalTransition = reducedMotion
    ? { duration: 0 }
    : { type: "spring" as const, stiffness: 300, damping: 30 };

  const backdropTransition = reducedMotion
    ? { duration: 0 }
    : { duration: 0.15 };

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={onClose}
      initial={false}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={backdropTransition}
    >
      <motion.div
        className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-900"
        onClick={(e) => e.stopPropagation()}
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        transition={modalTransition}
      >
        {/* Header */}
        <motion.div
          className="flex items-center justify-between border-b border-slate-200 px-6 py-5 dark:border-slate-800"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          <motion.div
            className="flex items-center gap-3"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2, delay: 0.05 }}
          >
            <motion.div
              className="rounded-full bg-red-100 p-3 dark:bg-red-500/20"
              initial={{ opacity: 0, scale: 0.8, rotate: -10 }}
              animate={{ opacity: 1, scale: 1, rotate: 0 }}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
            >
              <TriangleAlert size={24} className="text-red-600 dark:text-red-400" />
            </motion.div>

            <div>
              <motion.h2
                className="text-2xl font-bold text-slate-900 dark:text-white"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
              >
                Delete Ticket
              </motion.h2>
              <motion.p
                className="text-sm text-slate-500 dark:text-slate-400"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: 0.05 }}
              >
                This action cannot be undone.
              </motion.p>
            </div>
          </motion.div>

          <motion.button
            onClick={onClose}
            className="rounded-lg p-2 transition-colors hover:bg-slate-100 dark:hover:bg-slate-800"
            whileHover={reducedMotion ? {} : { scale: 1.1 }}
            whileTap={reducedMotion ? {} : { scale: 0.9 }}
            initial={{ opacity: 0, rotate: -90 }}
            animate={{ opacity: 1, rotate: 0 }}
            transition={{ duration: 0.2, delay: 0.1 }}
          >
            <X className="text-slate-600 dark:text-white" />
          </motion.button>
        </motion.div>

        {/* Body */}
        <motion.div className="space-y-5 p-6" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.1 }}>
          <motion.p
            className="text-slate-700 dark:text-slate-300"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15 }}
          >
            Are you sure you want to permanently delete this ticket?
          </motion.p>

          <motion.div
            className="rounded-xl border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-500/10"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 25, delay: 0.2 }}
          >
            <motion.p className="text-sm text-slate-500 dark:text-slate-400" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.25 }}>
              Ticket
            </motion.p>
            <motion.h3
              className="mt-1 font-semibold text-slate-900 dark:text-white"
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.3 }}
            >
              {ticketTitle}
            </motion.h3>
          </motion.div>

          <motion.div
            className="rounded-xl border border-yellow-200 bg-yellow-50 p-4 dark:border-yellow-900 dark:bg-yellow-500/10"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 25, delay: 0.25 }}
          >
            <motion.p
              className="text-sm text-yellow-700 dark:text-yellow-300"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              ⚠ This ticket and all associated information will be permanently removed.
            </motion.p>
          </motion.div>
        </motion.div>

        {/* Footer */}
        <motion.div
          className="flex justify-end gap-3 border-t border-slate-200 px-6 py-5 dark:border-slate-800"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2, delay: 0.3 }}
        >
          <motion.button
            onClick={onClose}
            className="rounded-xl border border-slate-300 bg-white px-5 py-2.5 font-medium text-slate-700 transition-colors hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:hover:bg-slate-700"
            whileHover={reducedMotion ? {} : { scale: 1.02 }}
            whileTap={reducedMotion ? {} : { scale: 0.98 }}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            Cancel
          </motion.button>

          <motion.button
            onClick={async () => await onConfirm()}
            className="rounded-xl bg-red-600 px-5 py-2.5 font-semibold text-white transition-all hover:bg-red-700 hover:shadow-lg"
            whileHover={reducedMotion ? {} : { scale: 1.02, boxShadow: "0 10px 25px -5px rgba(239, 68, 68, 0.4)" }}
            whileTap={reducedMotion ? {} : { scale: 0.98 }}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: 0.05 }}
          >
            Delete Ticket
          </motion.button>
        </motion.div>
      </motion.div>
    </motion.div>
  );
}