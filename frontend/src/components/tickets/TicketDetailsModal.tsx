import { useEffect } from "react";
import { motion } from "framer-motion";
import type { Ticket } from "../../types/ticket";

import { X, Ticket as TicketIcon, Bot, User, Calendar, Brain } from "lucide-react";
import { useReducedMotion } from "../../hooks/useReducedMotion";

interface TicketDetailsModalProps {
  open: boolean;
  ticket: Ticket | null;
  onClose: () => void;
}

export default function TicketDetailsModal({ open, ticket, onClose }: TicketDetailsModalProps) {
  const reducedMotion = useReducedMotion();

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (open) {
      window.addEventListener("keydown", handleEscape);
    }
    return () => window.removeEventListener("keydown", handleEscape);
  }, [open, onClose]);

  if (!open || !ticket) return null;

  const priorityColor = {
    High: "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400",
    Medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400",
    Low: "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400",
  };

  const statusColor = {
    Open: "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400",
    Assigned: "bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-400",
    Resolved: "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400",
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
      onClick={onClose}
      initial={false}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={backdropTransition}
    >
      <motion.div
        className="w-full max-w-5xl max-h-[90vh] overflow-y-auto rounded-2xl border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-900"
        onClick={(e) => e.stopPropagation()}
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        transition={modalTransition}
      >
        {/* Header */}
        <div className="sticky top-0 z-20 flex items-center justify-between border-b border-slate-200 bg-white px-8 py-6 dark:border-slate-800 dark:bg-slate-900">
          <div>
            <motion.h2
              className="text-3xl font-bold text-slate-900 dark:text-white"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
            >
              Ticket Details
            </motion.h2>
            <motion.p
              className="mt-1 text-slate-500 dark:text-slate-400"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.05 }}
            >
              Complete AI generated ticket information
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
        </div>

        <motion.div
          className="space-y-8 p-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1, ease: "easeOut" }}
        >
          {/* Ticket */}
          <Section title="Ticket Information" icon={<TicketIcon size={20} />}>
            <Info label="Ticket ID" value={`#${ticket.id}`} />
            <BadgeInfo label="Status" value={ticket.status} className={statusColor[ticket.status as keyof typeof statusColor] ?? ""} />
            <Info label="Title" value={ticket.title} full />
            <Info label="Description" value={ticket.description} full />
          </Section>

          {/* AI */}
          <Section title="AI Analysis" icon={<Bot size={20} />}>
            <Info label="Category" value={ticket.category ?? "N/A"} />
            <Info label="Subcategory" value={ticket.subcategory ?? "N/A"} />
            <Info label="Confidence" value={ticket.confidence != null ? `${Math.round(ticket.confidence * 100)}%` : "N/A"} />
            <Info label="AI Processed" value={ticket.ai_processed ? "Yes" : "No"} />
            <motion.div className="md:col-span-2" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
              <p className="mb-2 text-sm text-slate-500 dark:text-slate-400">Keywords</p>
              <div className="flex flex-wrap gap-2">
                {ticket.keywords?.length ? (
                  ticket.keywords.map((word) => (
                    <motion.span
                      key={word}
                      className="rounded-full bg-blue-600 px-3 py-1 text-sm text-white"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ type: "spring", stiffness: 400, damping: 25, delay: 0.05 }}
                    >
                      {word}
                    </motion.span>
                  ))
                ) : (
                  <span className="text-slate-500">No keywords</span>
                )}
              </div>
            </motion.div>
          </Section>

          {/* Priority */}
          <Section title="Priority" icon={<Brain size={20} />}>
            <BadgeInfo label="Priority" value={ticket.priority} className={priorityColor[ticket.priority as keyof typeof priorityColor] ?? ""} />
            <Info label="Priority Reason" value={ticket.priority_reason ?? "N/A"} />
          </Section>

          {/* Assignment */}
          <Section title="Assignment" icon={<User size={20} />}>
            <Info label="Assigned To" value={ticket.assigned_name ?? "Unassigned"} />
            <Info label="Assignment Reason" value={ticket.assignment_reason ?? "N/A"} />
          </Section>

          {/* Metadata */}
          <Section title="Metadata" icon={<Calendar size={20} />}>
            <Info label="Created By" value={String(ticket.created_by)} />
            <Info label="Created At" value={new Date(ticket.created_at).toLocaleString()} />
          </Section>

          {/* SLA Information (Phase 2C) */}
          {(ticket.sla_policy_id || ticket.sla_response_deadline || ticket.sla_resolution_deadline) && (
            <Section title="SLA" icon={<Calendar size={20} />}>
              {ticket.sla_policy_id && (
                <BadgeInfo label="SLA Policy" value={`Policy #${ticket.sla_policy_id}`} className="bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400" />
              )}
              {ticket.sla_response_deadline && <Info label="Response Deadline" value={new Date(ticket.sla_response_deadline).toLocaleString()} />}
              {ticket.sla_resolution_deadline && <Info label="Resolution Deadline" value={new Date(ticket.sla_resolution_deadline).toLocaleString()} />}
              {ticket.sla_response_status && <Info label="Response Status" value={ticket.sla_response_status} />}
              {ticket.sla_resolution_status && <Info label="Resolution Status" value={ticket.sla_resolution_status} />}
              {ticket.sla_response_breached && <Info label="Response Breached" value="Yes" />}
              {ticket.sla_resolution_breached && <Info label="Resolution Breached" value="Yes" />}
            </Section>
          )}
        </motion.div>
      </motion.div>
    </motion.div>
  );
}

function Section({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <div className="mb-5 flex items-center gap-3">
        <motion.div
          className="rounded-lg bg-blue-600 p-2 text-white"
          initial={{ opacity: 0, scale: 0.8, rotate: -10 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          transition={{ type: "spring", stiffness: 400, damping: 25 }}
        >
          {icon}
        </motion.div>
        <motion.h3
          className="text-xl font-semibold text-slate-900 dark:text-white"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2 }}
        >
          {title}
        </motion.h3>
      </div>
      <div className="grid gap-5 md:grid-cols-2">{children}</div>
    </motion.div>
  );
}

function Info({ label, value, full = false }: { label: string; value: string; full?: boolean }) {
  return (
    <motion.div className={full ? "md:col-span-2" : ""} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.05 }}>
      <p className="mb-2 text-sm text-slate-500 dark:text-slate-400">{label}</p>
      <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-white">
        {value}
      </div>
    </motion.div>
  );
}

function BadgeInfo({ label, value, className }: { label: string; value: string; className: string }) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.05 }}>
      <p className="mb-2 text-sm text-slate-500 dark:text-slate-400">{label}</p>
      <span className={`rounded-full px-3 py-1 text-sm font-semibold ${className}`}>{value}</span>
    </motion.div>
  );
}