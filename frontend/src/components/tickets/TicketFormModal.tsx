import { useEffect, useState } from "react";
import { X, FileText, AlertCircle } from "lucide-react";

import type { Ticket } from "../../types/ticket";

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

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("Medium");
  const [status, setStatus] = useState("Open");

  useEffect(() => {
    if (ticket) {
      setTitle(ticket.title);
      setDescription(ticket.description);
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

  const handleSave = async () => {
    if (!title.trim()) {
      alert("Title is required");
      return;
    }

    if (!description.trim()) {
      alert("Description is required");
      return;
    }

    await onSubmit({
      title,
      description,
      priority,
      status,
      assigned_to: null,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">

      <div className="w-full max-w-2xl rounded-2xl border border-slate-200 bg-white shadow-2xl transition-all duration-300 dark:border-slate-800 dark:bg-slate-900">

        {/* Header */}

        <div className="flex items-center justify-between border-b border-slate-200 px-8 py-6 dark:border-slate-800">

          <div>

            <h2 className="text-3xl font-bold text-slate-900 dark:text-white">
              {ticket ? "Edit Ticket" : "Create Ticket"}
            </h2>

            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              {ticket
                ? "Update the ticket details."
                : "Create a new support ticket."}
            </p>

          </div>

          <button
            onClick={onClose}
            className="rounded-lg p-2 transition hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <X className="text-slate-600 dark:text-white" />
          </button>

        </div>

        {/* Body */}

        <div className="space-y-6 p-8">

          {/* Title */}

          <div>

            <label className="mb-2 flex items-center gap-2 font-medium text-slate-700 dark:text-slate-300">

              <FileText size={18} />

              Ticket Title

            </label>

            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter ticket title..."
              className="w-full rounded-xl border border-slate-300 bg-slate-50 p-3 text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:ring-blue-500/20"
            />

          </div>

          {/* Description */}

          <div>

            <label className="mb-2 flex items-center gap-2 font-medium text-slate-700 dark:text-slate-300">

              <AlertCircle size={18} />

              Description

            </label>

            <textarea
              rows={6}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe your issue in detail..."
              className="w-full rounded-xl border border-slate-300 bg-slate-50 p-3 text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:ring-blue-500/20"
            />

          </div>

          {/* Priority & Status */}

          <div className="grid gap-5 md:grid-cols-2">

            <div>

              <label className="mb-2 block font-medium text-slate-700 dark:text-slate-300">
                Priority
              </label>

              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full rounded-xl border border-slate-300 bg-slate-50 p-3 text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:ring-blue-500/20"
              >
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>

            </div>

            <div>

              <label className="mb-2 block font-medium text-slate-700 dark:text-slate-300">
                Status
              </label>

              <select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className="w-full rounded-xl border border-slate-300 bg-slate-50 p-3 text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:ring-blue-500/20"
              >
                <option value="Open">Open</option>
                <option value="Assigned">Assigned</option>
                <option value="Resolved">Resolved</option>
              </select>

            </div>

          </div>

        </div>

        {/* Footer */}

        <div className="flex justify-end gap-4 border-t border-slate-200 px-8 py-6 dark:border-slate-800">

          <button
            onClick={onClose}
            className="rounded-xl border border-slate-300 bg-white px-6 py-2.5 font-medium text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:hover:bg-slate-700"
          >
            Cancel
          </button>

          <button
            onClick={handleSave}
            className="rounded-xl bg-blue-600 px-6 py-2.5 font-semibold text-white transition-all hover:bg-blue-700 hover:shadow-lg"
          >
            {ticket ? "Update Ticket" : "Create Ticket"}
          </button>

        </div>

      </div>

    </div>
  );
}