import type { Ticket } from "../../types/ticket";

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
  if (!open || !ticket) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">

      <div className="w-full max-w-2xl rounded-xl bg-zinc-900 p-6 shadow-2xl">

        {/* Header */}
        <div className="mb-6 flex items-center justify-between">

          <h2 className="text-2xl font-bold text-white">
            Ticket Details
          </h2>

          <button
            onClick={onClose}
            className="rounded-lg bg-zinc-700 px-4 py-2 text-white transition hover:bg-zinc-600"
          >
            Close
          </button>

        </div>

        {/* Content */}

        <div className="grid gap-6 md:grid-cols-2">

          <div>
            <p className="mb-1 text-sm text-zinc-400">
              Ticket ID
            </p>

            <p className="text-lg font-semibold text-white">
              #{ticket.id}
            </p>
          </div>

          <div>
            <p className="mb-1 text-sm text-zinc-400">
              Status
            </p>

            <p className="text-white">
              {ticket.status}
            </p>
          </div>

          <div className="md:col-span-2">
            <p className="mb-1 text-sm text-zinc-400">
              Title
            </p>

            <p className="text-white">
              {ticket.title}
            </p>
          </div>

          <div className="md:col-span-2">
            <p className="mb-1 text-sm text-zinc-400">
              Description
            </p>

            <div className="rounded-lg bg-zinc-800 p-4 text-zinc-200">
              {ticket.description}
            </div>
          </div>

          <div>
            <p className="mb-1 text-sm text-zinc-400">
              Priority
            </p>

            <p className="text-white">
              {ticket.priority}
            </p>
          </div>

          <div>
            <p className="mb-1 text-sm text-zinc-400">
              Assigned To
            </p>

            <p className="text-white">
              {ticket.assigned_to ?? "Unassigned"}
            </p>
          </div>

          <div>
            <p className="mb-1 text-sm text-zinc-400">
              Created By
            </p>

            <p className="text-white">
              {ticket.created_by}
            </p>
          </div>

          <div>
            <p className="mb-1 text-sm text-zinc-400">
              Created At
            </p>

            <p className="text-white">
              {new Date(
                ticket.created_at
              ).toLocaleString()}
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}