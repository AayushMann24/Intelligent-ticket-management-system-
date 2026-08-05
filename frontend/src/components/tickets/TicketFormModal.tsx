import { useEffect, useState } from "react";

import useUsers from "../../hooks/useUsers";

import type { Ticket } from "../../types/ticket";
import type { User } from "../../types/user";

interface TicketFormModalProps {
  open: boolean;
  ticket: Ticket | null;

  onClose: () => void;

  onSubmit: (ticket: {
    title: string;
    description: string;
    priority: string;
    status: string;
    assigned_to: number | null;
  }) => Promise<void>;
}

export default function TicketFormModal({
  open,
  ticket,
  onClose,
  onSubmit,
}: TicketFormModalProps) {
  const { users, loading } = useUsers();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const [priority, setPriority] = useState("Medium");

  const [status, setStatus] = useState("Open");

  const [assignedTo, setAssignedTo] =
    useState<number | null>(null);

  useEffect(() => {
    if (ticket) {
      setTitle(ticket.title);
      setDescription(ticket.description);
      setPriority(ticket.priority);
      setStatus(ticket.status);
      setAssignedTo(ticket.assigned_to);
    } else {
      setTitle("");
      setDescription("");
      setPriority("Medium");
      setStatus("Open");
      setAssignedTo(null);
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
            value={title}
            onChange={(e) =>
              setTitle(e.target.value)
            }
            placeholder="Title"
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 p-3 text-white"
          />

          <textarea
            rows={5}
            value={description}
            onChange={(e) =>
              setDescription(e.target.value)
            }
            placeholder="Description"
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 p-3 text-white"
          />

          <select
            value={priority}
            onChange={(e) =>
              setPriority(e.target.value)
            }
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 p-3 text-white"
          >
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>

          <select
            value={status}
            onChange={(e) =>
              setStatus(e.target.value)
            }
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 p-3 text-white"
          >
            <option value="Open">Open</option>
            <option value="Assigned">Assigned</option>
            <option value="Resolved">Resolved</option>
          </select>

          <select
            value={assignedTo ?? ""}
            onChange={(e) =>
              setAssignedTo(
                e.target.value === ""
                  ? null
                  : Number(e.target.value)
              )
            }
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 p-3 text-white"
          >
            <option value="">
              Unassigned
            </option>

            {!loading &&
              users.map((user: User) => (
                <option
                  key={user.id}
                  value={user.id}
                >
                  {user.name}
                </option>
              ))}
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
                assigned_to: assignedTo,
              })
            }
            className="rounded-lg bg-blue-600 px-5 py-2 text-white hover:bg-blue-700"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}