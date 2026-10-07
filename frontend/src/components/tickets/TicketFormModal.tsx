import { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import { X, FileText, AlertCircle } from "lucide-react";

import type { Ticket, TicketType } from "../../types/ticket";
import { useReducedMotion } from "../../hooks/useReducedMotion";

interface TicketFormModalProps {
  open: boolean;
  ticket: Ticket | null;
  onClose: () => void;
  onSubmit: (ticket: {
    title: string;
    description: string;
    priority: string;
    status: string;
    ticket_type: TicketType;
    assigned_to: number | null;
  }) => Promise<void>;
}

export default function TicketFormModal({ open, ticket, onClose, onSubmit }: TicketFormModalProps) {
  const reducedMotion = useReducedMotion();
  const [title, setTitle] = useState(() => ticket?.title ?? "");
  const [description, setDescription] = useState(() => ticket?.description ?? "");
  const [priority, setPriority] = useState(() => ticket?.priority ?? "Medium");
  const [status, setStatus] = useState(() => ticket?.status ?? "Open");
  const [ticketType, setTicketType] = useState<TicketType>(() => ticket?.ticket_type ?? "INCIDENT");

  const isInitialMount = useRef(true);
  /* eslint-disable react-hooks/set-state-in-effect -- Syncing form state with ticket prop is a legitimate controlled/uncontrolled pattern */
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }
    if (ticket) {
      setTitle(ticket.title);
      setDescription(ticket.description);
      setPriority(ticket.priority);
      setStatus(ticket.status);
      setTicketType(ticket.ticket_type);
    } else {
      setTitle("");
      setDescription("");
      setPriority("Medium");
      setStatus("Open");
      setTicketType("INCIDENT");
    }
  }, [ticket]);
  /* eslint-enable react-hooks/set-state-in-effect */

  if (!open) return null;

  const handleSave = async () => {
    if (!title.trim()) {
      alert("Title is required");
      return;
    }
    if (!description.trim()) {
      alert("Description is required");
      return;
    }
    await onSubmit({ title, description, priority, status, ticket_type: ticketType, assigned_to: null });
  };

  const modalTransition = reducedMotion
    ? { duration: 0 }
    : { type: "spring" as const, stiffness: 300, damping: 30 };

  const backdropTransition = reducedMotion
    ? { duration: 0 }
    : { duration: 0.15 };

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      initial={false}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={backdropTransition}
      onClick={onClose}
    >
      <motion.div
        className="w-full max-w-2xl rounded-2xl border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-900"
        onClick={(e) => e.stopPropagation()}
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        transition={modalTransition}
      >
        {/* Header */}
        <motion.div
          className="flex items-center justify-between border-b border-slate-200 px-8 py-6 dark:border-slate-800"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          <div>
            <motion.h2
              className="text-3xl font-bold text-slate-900 dark:text-white"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2 }}
            >
              {ticket ? "Edit Ticket" : "Create Ticket"}
            </motion.h2>
            <motion.p
              className="mt-1 text-sm text-slate-500 dark:text-slate-400"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2, delay: 0.05 }}
            >
              {ticket ? "Update the ticket details." : "Create a new support ticket."}
            </motion.p>
          </div>

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
        <motion.div className="space-y-6 p-8" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.1 }}>
          {/* Title */}
          <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.2, delay: 0.15 }}>
            <label className="mb-2 flex items-center gap-2 font-medium text-slate-700 dark:text-slate-300">
              <FileText size={18} /> Ticket Title
            </label>
            <motion.input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter ticket title..."
              className="w-full rounded-xl border border-slate-300 bg-slate-50 p-3 text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:ring-blue-500/20"
              whileFocus={reducedMotion ? {} : { scale: 1.01 }}
            />
          </motion.div>

          {/* Description */}
          <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.2, delay: 0.2 }}>
            <label className="mb-2 flex items-center gap-2 font-medium text-slate-700 dark:text-slate-300">
              <AlertCircle size={18} /> Description
            </label>
            <motion.textarea
              rows={6}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe your issue in detail..."
              className="w-full rounded-xl border border-slate-300 bg-slate-50 p-3 text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:ring-blue-500/20"
              whileFocus={reducedMotion ? {} : { scale: 1.01 }}
            />
          </motion.div>

          {/* Ticket Type, Priority & Status */}
          <motion.div
            className="grid gap-5 md:grid-cols-3"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: 0.25 }}
          >
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
              <label className="mb-2 block font-medium text-slate-700 dark:text-slate-300">Type</label>
              <motion.select
                value={ticketType}
                onChange={(e) => setTicketType(e.target.value as TicketType)}
                className="w-full rounded-xl border border-slate-300 bg-slate-50 p-3 text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:ring-blue-500/20"
                whileFocus={reducedMotion ? {} : { scale: 1.01 }}
              >
                <option value="INCIDENT">Incident</option>
                <option value="SERVICE_REQUEST">Service Request</option>
              </motion.select>
            </motion.div>

            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.35 }}>
              <label className="mb-2 block font-medium text-slate-700 dark:text-slate-300">Priority</label>
              <motion.select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full rounded-xl border border-slate-300 bg-slate-50 p-3 text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:ring-blue-500/20"
                whileFocus={reducedMotion ? {} : { scale: 1.01 }}
              >
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
                <option value="Critical">Critical</option>
              </motion.select>
            </motion.div>

            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
              <label className="mb-2 block font-medium text-slate-700 dark:text-slate-300">Status</label>
              <motion.select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className="w-full rounded-xl border border-slate-300 bg-slate-50 p-3 text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:ring-blue-500/20"
                whileFocus={reducedMotion ? {} : { scale: 1.01 }}
              >
                <option value="Open">Open</option>
                <option value="Assigned">Assigned</option>
                <option value="In Progress">In Progress</option>
                <option value="Pending">Pending</option>
                <option value="Resolved">Resolved</option>
                <option value="Closed">Closed</option>
              </motion.select>
            </motion.div>
          </motion.div>
        </motion.div>

        {/* Footer */}
        <motion.div
          className="flex justify-end gap-4 border-t border-slate-200 px-8 py-6 dark:border-slate-800"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2, delay: 0.3 }}
        >
          <motion.button
            onClick={onClose}
            className="rounded-xl border border-slate-300 bg-white px-6 py-2.5 font-medium text-slate-700 transition-colors hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:hover:bg-slate-700"
            whileHover={reducedMotion ? {} : { scale: 1.02 }}
            whileTap={reducedMotion ? {} : { scale: 0.98 }}
          >
            Cancel
          </motion.button>

          <motion.button
            onClick={handleSave}
            className="rounded-xl bg-blue-600 px-6 py-2.5 font-semibold text-white transition-all hover:bg-blue-700 hover:shadow-lg"
            whileHover={reducedMotion ? {} : { scale: 1.02, boxShadow: "0 10px 25px -5px rgba(37, 99, 235, 0.4)" }}
            whileTap={reducedMotion ? {} : { scale: 0.98 }}
          >
            {ticket ? "Update Ticket" : "Create Ticket"}
          </motion.button>
        </motion.div>
      </motion.div>
    </motion.div>
  );
}