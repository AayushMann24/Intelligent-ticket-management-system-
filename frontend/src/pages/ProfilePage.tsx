import MainLayout from "../layouts/MainLayout";
import { User, Mail, Shield } from "lucide-react";

export default function ProfilePage() {
  return (
    <MainLayout>
      <div className="mx-auto max-w-4xl">

        <h1 className="mb-8 text-4xl font-bold text-white">
          My Profile
        </h1>

        <div className="rounded-2xl bg-slate-900 p-8 shadow-lg">

          <div className="flex items-center gap-6">

            <div className="flex h-24 w-24 items-center justify-center rounded-full bg-cyan-500 text-4xl font-bold text-white">
              A
            </div>

            <div>
              <h2 className="text-3xl font-bold text-white">
                Administrator
              </h2>

              <p className="text-slate-400">
                admin@gmail.com
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
                  Admin
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
                  admin@gmail.com
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
                  Administrator
                </p>
              </div>
            </div>

          </div>

        </div>

      </div>
    </MainLayout>
  );
}