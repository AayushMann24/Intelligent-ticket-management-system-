import { useEffect } from "react";
import type { Ticket } from "../../types/ticket";
import { X } from "lucide-react";

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
      window.removeEventListener("keydown", handleEscape);
    };
  }, [open, onClose]);

  if (!open || !ticket) return null;

  const priorityColor = {
    High: "bg-red-500",
    Medium: "bg-yellow-500",
    Low: "bg-green-500",
  };

  const statusColor = {
    Open: "bg-blue-500",
    Assigned: "bg-purple-500",
    Resolved: "bg-green-600",
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-2xl bg-zinc-900 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}

        <div className="sticky top-0 z-20 flex items-center justify-between border-b border-zinc-800 bg-zinc-900 px-8 py-6">
          <div>
            <h2 className="text-3xl font-bold text-white">
              Ticket Details
            </h2>

            <p className="mt-1 text-zinc-400">
              Complete information about this support ticket
            </p>
          </div>

          <button
            onClick={onClose}
            className="rounded-lg p-2 text-zinc-400 transition hover:bg-zinc-800 hover:text-white"
            title="Close"
          >
            <X size={28} />
          </button>
        </div>

        <div className="space-y-8 p-8">

          {/* Ticket Information */}

          <div>
            <h3 className="mb-4 text-xl font-semibold text-white">
              Ticket Information
            </h3>

            <div className="grid gap-5 md:grid-cols-2">

              <Info
                label="Ticket ID"
                value={`#${ticket.id}`}
              />

              <div>
                <p className="mb-1 text-sm text-zinc-400">
                  Status
                </p>

                <span
                  className={`rounded-full px-3 py-1 text-sm text-white ${
                    statusColor[
                      ticket.status as keyof typeof statusColor
                    ] ?? "bg-zinc-700"
                  }`}
                >
                  {ticket.status}
                </span>
              </div>

              <Info
                label="Title"
                value={ticket.title}
                full
              />

              <div className="md:col-span-2">
                <p className="mb-2 text-sm text-zinc-400">
                  Description
                </p>

                <div className="rounded-xl bg-zinc-800 p-4 text-zinc-200">
                  {ticket.description}
                </div>
              </div>

            </div>
          </div>

          {/* AI Analysis */}

          <div>
            <h3 className="mb-4 text-xl font-semibold text-white">
              AI Analysis
            </h3>

            <div className="grid gap-5 md:grid-cols-2">

              <Info
                label="Category"
                value={ticket.category ?? "N/A"}
              />

              <Info
                label="Subcategory"
                value={ticket.subcategory ?? "N/A"}
              />

              <div className="md:col-span-2">
                <p className="mb-2 text-sm text-zinc-400">
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
                    <span className="text-zinc-400">
                      No keywords
                    </span>
                  )}

                </div>
              </div>

              <Info
                label="AI Confidence"
                value={
                  ticket.confidence != null
                    ? `${Math.round(ticket.confidence * 100)}%`
                    : "N/A"
                }
              />

              <Info
                label="AI Processed"
                value={
                  ticket.ai_processed
                    ? "✅ Yes"
                    : "❌ No"
                }
              />

            </div>
          </div>

          {/* Priority */}

          <div>
            <h3 className="mb-4 text-xl font-semibold text-white">
              Priority
            </h3>

            <div className="grid gap-5 md:grid-cols-2">

              <div>
                <p className="mb-1 text-sm text-zinc-400">
                  Priority
                </p>

                <span
                  className={`rounded-full px-3 py-1 text-sm text-white ${
                    priorityColor[
                      ticket.priority as keyof typeof priorityColor
                    ] ?? "bg-zinc-700"
                  }`}
                >
                  {ticket.priority}
                </span>
              </div>

              <Info
                label="Priority Reason"
                value={
                  ticket.priority_reason ?? "N/A"
                }
              />

            </div>
          </div>

          {/* Assignment */}

          <div>
            <h3 className="mb-4 text-xl font-semibold text-white">
              Assignment
            </h3>

            <div className="grid gap-5 md:grid-cols-2">

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

            </div>
          </div>

          {/* Metadata */}

          <div>
            <h3 className="mb-4 text-xl font-semibold text-white">
              Metadata
            </h3>

            <div className="grid gap-5 md:grid-cols-2">

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

            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

interface InfoProps {
  label: string;
  value: string;
  full?: boolean;
}

function Info({
  label,
  value,
  full = false,
}: InfoProps) {
  return (
    <div className={full ? "md:col-span-2" : ""}>
      <p className="mb-1 text-sm text-zinc-400">
        {label}
      </p>

      <div className="rounded-lg bg-zinc-800 px-4 py-3 text-white">
        {value}
      </div>
    </div>
  );
}