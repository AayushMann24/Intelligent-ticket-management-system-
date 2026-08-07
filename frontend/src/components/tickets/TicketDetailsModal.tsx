import { useEffect } from "react";
import type { Ticket } from "../../types/ticket";

import {
  X,
  Ticket as TicketIcon,
  Bot,
  User,
  Calendar,
  Brain,
} from "lucide-react";

interface TicketDetailsModalProps {
  open: boolean;
  ticket: Ticket | null;
  onClose: () => void;
}

export default function TicketDetailsModal({
  open,
  ticket,
  onClose,
}: TicketDetailsModalProps) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };

    if (open) {
      window.addEventListener("keydown", handleEscape);
    }

    return () => {
      window.removeEventListener(
        "keydown",
        handleEscape
      );
    };
  }, [open, onClose]);

  if (!open || !ticket) return null;

  const priorityColor = {
    High:
      "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400",
    Medium:
      "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400",
    Low:
      "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400",
  };

  const statusColor = {
    Open:
      "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400",
    Assigned:
      "bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-400",
    Resolved:
      "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400",
  };

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-5xl max-h-[90vh] overflow-y-auto rounded-2xl border border-slate-200 bg-white shadow-2xl transition-all duration-300 dark:border-slate-800 dark:bg-slate-900"
      >
        {/* Header */}

        <div className="sticky top-0 z-20 flex items-center justify-between border-b border-slate-200 bg-white px-8 py-6 dark:border-slate-800 dark:bg-slate-900">

          <div>

            <h2 className="text-3xl font-bold text-slate-900 dark:text-white">
              Ticket Details
            </h2>

            <p className="mt-1 text-slate-500 dark:text-slate-400">
              Complete AI generated ticket information
            </p>

          </div>

          <button
            onClick={onClose}
            className="rounded-lg p-2 transition hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <X className="text-slate-600 dark:text-white" />
          </button>

        </div>

        <div className="space-y-8 p-8">

          {/* Ticket */}

          <Section title="Ticket Information" icon={<TicketIcon size={20} />}>

            <Info label="Ticket ID" value={`#${ticket.id}`} />

            <BadgeInfo
              label="Status"
              value={ticket.status}
              className={
                statusColor[
                  ticket.status as keyof typeof statusColor
                ] ?? ""
              }
            />

            <Info
              label="Title"
              value={ticket.title}
              full
            />

            <Info
              label="Description"
              value={ticket.description}
              full
            />

          </Section>

          {/* AI */}

          <Section title="AI Analysis" icon={<Bot size={20} />}>

            <Info
              label="Category"
              value={ticket.category ?? "N/A"}
            />

            <Info
              label="Subcategory"
              value={ticket.subcategory ?? "N/A"}
            />

            <Info
              label="Confidence"
              value={
                ticket.confidence != null
                  ? `${Math.round(
                      ticket.confidence * 100
                    )}%`
                  : "N/A"
              }
            />

            <Info
              label="AI Processed"
              value={
                ticket.ai_processed
                  ? "Yes"
                  : "No"
              }
            />

            <div className="md:col-span-2">

              <p className="mb-2 text-sm text-slate-500 dark:text-slate-400">
                Keywords
              </p>

              <div className="flex flex-wrap gap-2">

                {ticket.keywords?.length ? (

                  ticket.keywords.map((word) => (

                    <span
                      key={word}
                      className="rounded-full bg-blue-600 px-3 py-1 text-sm text-white"
                    >
                      {word}
                    </span>

                  ))

                ) : (

                  <span className="text-slate-500">
                    No keywords
                  </span>

                )}

              </div>

            </div>

          </Section>

          {/* Priority */}

          <Section title="Priority" icon={<Brain size={20} />}>

            <BadgeInfo
              label="Priority"
              value={ticket.priority}
              className={
                priorityColor[
                  ticket.priority as keyof typeof priorityColor
                ] ?? ""
              }
            />

            <Info
              label="Priority Reason"
              value={
                ticket.priority_reason ??
                "N/A"
              }
            />

          </Section>

          {/* Assignment */}

          <Section title="Assignment" icon={<User size={20} />}>

            <Info
              label="Assigned To"
              value={
                ticket.assigned_name ??
                "Unassigned"
              }
            />

            <Info
              label="Assignment Reason"
              value={
                ticket.assignment_reason ??
                "N/A"
              }
            />

          </Section>

          {/* Metadata */}

          <Section title="Metadata" icon={<Calendar size={20} />}>

            <Info
              label="Created By"
              value={String(ticket.created_by)}
            />

            <Info
              label="Created At"
              value={new Date(
                ticket.created_at
              ).toLocaleString()}
            />

          </Section>

        </div>

      </div>

    </div>
  );
}

function Section({
  title,
  icon,
  children,
}: {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div>

      <div className="mb-5 flex items-center gap-3">

        <div className="rounded-lg bg-blue-600 p-2 text-white">
          {icon}
        </div>

        <h3 className="text-xl font-semibold text-slate-900 dark:text-white">
          {title}
        </h3>

      </div>

      <div className="grid gap-5 md:grid-cols-2">
        {children}
      </div>

    </div>
  );
}

function Info({
  label,
  value,
  full = false,
}: {
  label: string;
  value: string;
  full?: boolean;
}) {
  return (
    <div className={full ? "md:col-span-2" : ""}>

      <p className="mb-2 text-sm text-slate-500 dark:text-slate-400">
        {label}
      </p>

      <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-white">
        {value}
      </div>

    </div>
  );
}

function BadgeInfo({
  label,
  value,
  className,
}: {
  label: string;
  value: string;
  className: string;
}) {
  return (
    <div>

      <p className="mb-2 text-sm text-slate-500 dark:text-slate-400">
        {label}
      </p>

      <span
        className={`rounded-full px-3 py-1 text-sm font-semibold ${className}`}
      >
        {value}
      </span>

    </div>
  );
}