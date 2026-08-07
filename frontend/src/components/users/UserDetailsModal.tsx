import { X, User, Mail, Shield } from "lucide-react";
import type { User as UserType } from "../../types/user";

interface UserDetailsModalProps {
  open: boolean;
  user: UserType | null;
  onClose: () => void;
}

export default function UserDetailsModal({
  open,
  user,
  onClose,
}: UserDetailsModalProps) {

  if (!open || !user) return null;

  return (

    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={onClose}
    >

      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-900"
      >

        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-5 dark:border-slate-800">

          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
            User Details
          </h2>

          <button
            onClick={onClose}
            className="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <X />
          </button>

        </div>

        <div className="space-y-5 p-6">

          <Info icon={<User size={18} />} label="Name" value={user.name} />

          <Info icon={<Mail size={18} />} label="Email" value={user.email} />

          <Info icon={<Shield size={18} />} label="Role" value={user.role} />

          {user.created_at && (
            <Info
              label="Created At"
              value={new Date(user.created_at).toLocaleString()}
            />
          )}

        </div>

        <div className="border-t border-slate-200 px-6 py-5 dark:border-slate-800">

          <button
            onClick={onClose}
            className="w-full rounded-xl bg-blue-600 py-3 font-semibold text-white hover:bg-blue-700"
          >
            Close
          </button>

        </div>

      </div>

    </div>

  );
}

function Info({
  icon,
  label,
  value,
}: {
  icon?: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div>

      <p className="mb-2 flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
        {icon}
        {label}
      </p>

      <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-white">
        {value}
      </div>

    </div>
  );
}