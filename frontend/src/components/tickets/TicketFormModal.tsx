import { useEffect, useState } from "react";
import type { Ticket } from "../../types/ticket";

interface TicketFormModalProps {
  open: boolean;
  ticket: Ticket | null;
  onClose: () => void;
  onSubmit: (data: {
    title: string;
    description: string;
    priority: string;
    status: string;
    assigned_to: number | null;
  }) => void;
}

export default function TicketFormModal({
  open,
  ticket,
  onClose,
  onSubmit,
}: TicketFormModalProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("Medium");
  const [status, setStatus] = useState("Open");

  useEffect(() => {
    if (ticket) {
      setTitle(ticket.title);
      setDescription(ticket.description ?? "");
      setPriority(ticket.priority);
      setStatus(ticket.status);
    } else {
      setTitle("");
      setDescription("");
      setPriority("Medium");
      setStatus("Open");
    }
  }, [ticket]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">

      <div className="w-full max-w-xl rounded-xl bg-zinc-900 p-6">

        <h2 className="mb-6 text-2xl font-bold text-white">
          {ticket ? "Edit Ticket" : "Create Ticket"}
        </h2>

        <div className="space-y-4">

          <input
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 p-3 text-white"
            placeholder="Ticket Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />

          <textarea
            rows={5}
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 p-3 text-white"
            placeholder="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          <select
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 p-3 text-white"
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
          >
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>

          <select
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 p-3 text-white"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option>Open</option>
            <option>Assigned</option>
            <option>Resolved</option>
          </select>

        </div>

        <div className="mt-8 flex justify-end gap-3">

          <button
            onClick={onClose}
            className="rounded-lg bg-zinc-700 px-5 py-2 text-white hover:bg-zinc-600"
          >
            Cancel
          </button>

          <button
            onClick={() =>
              onSubmit({
                title,
                description,
                priority,
                status,
                assigned_to: null,
              })
            }
            className="rounded-lg bg-blue-600 px-5 py-2 text-white hover:bg-blue-700"
          >
            {ticket ? "Save Changes" : "Create Ticket"}
          </button>

        </div>

      </div>

    </div>
  );
}