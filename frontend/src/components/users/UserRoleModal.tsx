import { useEffect, useState } from "react";
import { X, Shield } from "lucide-react";

import type { User } from "../../types/user";

interface UserRoleModalProps {
  open: boolean;
  user: User | null;
  onClose: () => void;
  onSave: (role: string) => Promise<void>;
}

export default function UserRoleModal({
  open,
  user,
  onClose,
  onSave,
}: UserRoleModalProps) {

  const [role, setRole] = useState("Employee");

  useEffect(() => {
    if (user) {
      setRole(user.role);
    }
  }, [user]);

  if (!open || !user) return null;

  return (

    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={onClose}
    >

      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-md rounded-2xl border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-900"
      >

        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-5 dark:border-slate-800">

          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
            Change Role
          </h2>

          <button
            onClick={onClose}
            className="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <X />
          </button>

        </div>

        <div className="space-y-5 p-6">

          <div>

            <p className="text-sm text-slate-500 dark:text-slate-400">
              User
            </p>

            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
              {user.name}
            </h3>

            <p className="text-slate-500">
              {user.email}
            </p>

          </div>

          <div>

            <label className="mb-2 flex items-center gap-2 font-medium text-slate-700 dark:text-slate-300">

              <Shield size={18} />

              Role

            </label>

            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="
                w-full
                rounded-xl
                border
                border-slate-300
                bg-slate-50
                p-3
                text-slate-900
                dark:border-slate-700
                dark:bg-slate-800
                dark:text-white
              "
            >
              <option value="Admin">Admin</option>
              <option value="Technician">Technician</option>
              <option value="Employee">Employee</option>
            </select>

          </div>

        </div>

        <div className="flex justify-end gap-3 border-t border-slate-200 px-6 py-5 dark:border-slate-800">

          <button
            onClick={onClose}
            className="rounded-xl border border-slate-300 px-5 py-2.5 dark:border-slate-700"
          >
            Cancel
          </button>

          <button
            onClick={async () => {
              await onSave(role);
            }}
            className="rounded-xl bg-blue-600 px-5 py-2.5 font-semibold text-white hover:bg-blue-700"
          >
            Save Changes
          </button>

        </div>

      </div>

    </div>

  );
}