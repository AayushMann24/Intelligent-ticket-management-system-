import type { User } from "../../types/user";

interface UserDetailsModalProps {
  open: boolean;
  user: User | null;
  onClose: () => void;
}

export default function UserDetailsModal({
  open,
  user,
  onClose,
}: UserDetailsModalProps) {
  if (!open || !user) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="w-full max-w-lg rounded-xl bg-zinc-900 p-6 shadow-2xl">

        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-white">
            User Details
          </h2>

          <button
            onClick={onClose}
            className="rounded-lg bg-zinc-700 px-4 py-2 text-white transition hover:bg-zinc-600"
          >
            Close
          </button>
        </div>

        {/* User Information */}
        <div className="space-y-5">

          <div>
            <p className="text-sm text-zinc-400">
              User ID
            </p>

            <p className="text-lg font-semibold text-white">
              #{user.id}
            </p>
          </div>

          <div>
            <p className="text-sm text-zinc-400">
              Name
            </p>

            <p className="text-white">
              {user.name}
            </p>
          </div>

          <div>
            <p className="text-sm text-zinc-400">
              Email
            </p>

            <p className="text-white">
              {user.email}
            </p>
          </div>

          <div>
            <p className="text-sm text-zinc-400">
              Role
            </p>

            <p className="text-white">
              {user.role}
            </p>
          </div>

          {user.created_at && (
            <div>
              <p className="text-sm text-zinc-400">
                Created At
              </p>

              <p className="text-white">
                {new Date(
                  user.created_at
                ).toLocaleString()}
              </p>
            </div>
          )}

        </div>

        {/* Footer */}
        <div className="mt-8 flex justify-end">
          <button
            onClick={onClose}
            className="rounded-lg bg-blue-600 px-5 py-2 text-white transition hover:bg-blue-700"
          >
            Done
          </button>
        </div>

      </div>
    </div>
  );
}