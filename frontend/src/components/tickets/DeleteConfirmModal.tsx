interface DeleteConfirmModalProps {
  open: boolean;
  ticketTitle: string;
  onClose: () => void;
  onConfirm: () => void;
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
      <div className="w-full max-w-md rounded-xl bg-zinc-900 p-6">

        <h2 className="mb-4 text-2xl font-bold text-red-500">
          Delete Ticket
        </h2>

        <p className="text-zinc-300">
          Are you sure you want to delete
        </p>

        <p className="mt-2 font-semibold text-white">
          "{ticketTitle}"
        </p>

        <p className="mt-3 text-sm text-zinc-500">
          This action cannot be undone.
        </p>

        <div className="mt-8 flex justify-end gap-3">

          <button
            onClick={onClose}
            className="rounded-lg bg-zinc-700 px-5 py-2 text-white hover:bg-zinc-600"
          >
            Cancel
          </button>

          <button
            onClick={onConfirm}
            className="rounded-lg bg-red-600 px-5 py-2 text-white hover:bg-red-700"
          >
            Delete
          </button>

        </div>

      </div>
    </div>
  );
}