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
      <div className="w-full max-w-2xl rounded-xl bg-zinc-900 p-6">

        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-white">
            Ticket Details
          </h2>

          <button
            onClick={onClose}
            className="rounded-lg bg-zinc-700 px-4 py-2 text-white hover:bg-zinc-600"
          >
            Close
          </button>
        </div>

        <div className="space-y-5">

          <div>
            <p className="text-sm text-zinc-400">Ticket ID</p>
            <p className="text-white font-semibold">
              #{ticket.id}
            </p>
          </div>

          <div>
            <p className="text-sm text-zinc-400">Title</p>
            <p className="text-white">
              {ticket.title}
            </p>
          </div>

          <div>
            <p className="text-sm text-zinc-400">Description</p>
            <p className="text-white">
              {ticket.description}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-6">

            <div>
              <p className="text-sm text-zinc-400">
                Priority
              </p>

              <p className="text-white">
                {ticket.priority}
              </p>
            </div>

            <div>
              <p className="text-sm text-zinc-400">
                Status
              </p>

              <p className="text-white">
                {ticket.status}
              </p>
            </div>

            <div>
              <p className="text-sm text-zinc-400">
                Assigned To
              </p>

              <p className="text-white">
                {ticket.assigned_to}
              </p>
            </div>

            <div>
              <p className="text-sm text-zinc-400">
                Created
              </p>

              <p className="text-white">
                {new Date(ticket.created_at).toLocaleString()}
              </p>
            </div>

          </div>

        </div>

      </div>
    </div>
  );
}