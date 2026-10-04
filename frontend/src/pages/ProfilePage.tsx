import MainLayout from "../layouts/MainLayout";
import { User, Mail, Shield } from "lucide-react";
import { useAuth } from "../context/useAuth";

export default function ProfilePage() {
  const { user } = useAuth();

  return (
    <MainLayout>
      <div className="mx-auto max-w-4xl">

        <h1 className="mb-8 text-4xl font-bold text-white">
          My Profile
        </h1>

        <div className="rounded-2xl bg-slate-900 p-8 shadow-lg">

          <div className="flex items-center gap-6">

            <div className="flex h-24 w-24 items-center justify-center rounded-full bg-cyan-500 text-4xl font-bold text-white">
              {user?.name?.charAt(0).toUpperCase() ?? "U"}
            </div>

            <div>
              <h2 className="text-3xl font-bold text-white">
                {user?.name ?? "User"}
              </h2>

              <p className="text-slate-400">
                {user?.email ?? ""}
              </p>
            </div>

          </div>

          <div className="mt-10 space-y-6">

            <div className="flex items-center gap-4 rounded-xl bg-slate-800 p-4">
              <User className="text-cyan-400" />
              <div>
                <p className="text-sm text-slate-400">
                  Username
                </p>

                <p className="text-white">
                  {user?.name ?? ""}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4 rounded-xl bg-slate-800 p-4">
              <Mail className="text-cyan-400" />
              <div>
                <p className="text-sm text-slate-400">
                  Email
                </p>

                <p className="text-white">
                  {user?.email ?? ""}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4 rounded-xl bg-slate-800 p-4">
              <Shield className="text-cyan-400" />
              <div>
                <p className="text-sm text-slate-400">
                  Role
                </p>

                <p className="text-white">
                  {user?.role ?? ""}
                </p>
              </div>
            </div>

          </div>

        </div>

      </div>
    </MainLayout>
  );
}