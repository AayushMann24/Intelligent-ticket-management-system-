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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">

      <div className="w-full max-w-md rounded-xl bg-zinc-900 p-6 shadow-2xl">

        {/* Header */}
        <h2 className="mb-4 text-2xl font-bold text-red-500">
          Delete Ticket
        </h2>

        {/* Body */}
        <p className="text-zinc-300">
          Are you sure you want to delete this ticket?
        </p>

        <div className="mt-4 rounded-lg border border-zinc-700 bg-zinc-800 p-4">
          <p className="font-semibold text-white">
            {ticketTitle}
          </p>
        </div>

        <p className="mt-4 text-sm text-zinc-500">
          This action cannot be undone.
        </p>

        {/* Buttons */}
        <div className="mt-8 flex justify-end gap-3">

          <button
            onClick={onClose}
            className="rounded-lg bg-zinc-700 px-5 py-2 text-white transition hover:bg-zinc-600"
          >
            Cancel
          </button>

          <button
            onClick={async () => {
              await onConfirm();
            }}
            className="rounded-lg bg-red-600 px-5 py-2 text-white transition hover:bg-red-700"
          >
            Delete
          </button>

        </div>

      </div>

    </div>
  );
}