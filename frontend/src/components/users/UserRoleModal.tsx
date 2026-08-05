import { useEffect, useState } from "react";

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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">

      <div className="w-full max-w-md rounded-xl bg-zinc-900 p-6 shadow-2xl">

        {/* Header */}
        <h2 className="mb-6 text-2xl font-bold text-white">
          Change User Role
        </h2>

        {/* User Information */}
        <div className="mb-6 space-y-2">

          <div>
            <p className="text-sm text-zinc-400">
              Name
            </p>

            <p className="text-white font-medium">
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

        </div>

        {/* Role Selection */}
        <div className="mb-8">

          <label className="mb-2 block text-sm text-zinc-400">
            Role
          </label>

          <select
            value={role}
            onChange={(e) =>
              setRole(e.target.value)
            }
            className="w-full rounded-lg border border-zinc-700 bg-zinc-800 p-3 text-white"
          >
            <option value="Admin">
              Admin
            </option>

            <option value="Technician">
              Technician
            </option>

            <option value="Employee">
              Employee
            </option>

          </select>

        </div>

        {/* Buttons */}
        <div className="flex justify-end gap-3">

          <button
            onClick={onClose}
            className="rounded-lg bg-zinc-700 px-5 py-2 text-white hover:bg-zinc-600"
          >
            Cancel
          </button>

          <button
            onClick={async () => {
              await onSave(role);
            }}
            className="rounded-lg bg-blue-600 px-5 py-2 text-white hover:bg-blue-700"
          >
            Save
          </button>

        </div>

      </div>

    </div>
  );
}