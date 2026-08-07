import { TriangleAlert, X } from "lucide-react";

interface DeleteConfirmModalProps {
  open: boolean;
  ticketTitle: string;
  onClose: () => void;
  onConfirm: () => Promise<void>;
}

export default function DeleteConfirmModal({
  open,
  ticketTitle,
  onClose,
  onConfirm,
}: DeleteConfirmModalProps) {
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white shadow-2xl transition-all duration-300 dark:border-slate-800 dark:bg-slate-900"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}

        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-5 dark:border-slate-800">

          <div className="flex items-center gap-3">

            <div className="rounded-full bg-red-100 p-3 dark:bg-red-500/20">

              <TriangleAlert
                size={24}
                className="text-red-600 dark:text-red-400"
              />

            </div>

            <div>

              <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
                Delete Ticket
              </h2>

              <p className="text-sm text-slate-500 dark:text-slate-400">
                This action cannot be undone.
              </p>

            </div>

          </div>

          <button
            onClick={onClose}
            className="rounded-lg p-2 transition hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <X className="text-slate-600 dark:text-white" />
          </button>

        </div>

        {/* Body */}

        <div className="space-y-5 p-6">

          <p className="text-slate-700 dark:text-slate-300">
            Are you sure you want to permanently delete this ticket?
          </p>

          <div className="rounded-xl border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-500/10">

            <p className="text-sm text-slate-500 dark:text-slate-400">
              Ticket
            </p>

            <h3 className="mt-1 font-semibold text-slate-900 dark:text-white">
              {ticketTitle}
            </h3>

          </div>

          <div className="rounded-xl border border-yellow-200 bg-yellow-50 p-4 dark:border-yellow-900 dark:bg-yellow-500/10">

            <p className="text-sm text-yellow-700 dark:text-yellow-300">
              ⚠ This ticket and all associated information will be permanently removed.
            </p>

          </div>

        </div>

        {/* Footer */}

        <div className="flex justify-end gap-3 border-t border-slate-200 px-6 py-5 dark:border-slate-800">

          <button
            onClick={onClose}
            className="rounded-xl border border-slate-300 bg-white px-5 py-2.5 font-medium text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:hover:bg-slate-700"
          >
            Cancel
          </button>

          <button
            onClick={async () => {
              await onConfirm();
            }}
            className="rounded-xl bg-red-600 px-5 py-2.5 font-semibold text-white transition-all hover:bg-red-700 hover:shadow-lg"
          >
            Delete Ticket
          </button>

        </div>

      </div>

    </div>
  );
}