import MainLayout from "../layouts/MainLayout";
import { useTheme } from "../context/ThemeContext";

export default function SettingsPage() {
  const { theme, toggleTheme } = useTheme();

  return (
    <MainLayout>
      {/* Header */}

      <div className="mb-10">
        <h1 className="text-4xl font-bold text-slate-900 dark:text-white">
          ⚙️ Settings
        </h1>

        <p className="mt-2 text-slate-500 dark:text-slate-400">
          Manage your application preferences, account and system settings.
        </p>
      </div>

      {/* Settings Grid */}

      <div className="grid gap-6 lg:grid-cols-2">

        {/* ================= Appearance ================= */}

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition dark:border-slate-700 dark:bg-slate-900">

          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            🎨 Appearance
          </h2>

          <p className="mt-2 text-slate-500 dark:text-slate-400">
            Customize the appearance of your dashboard.
          </p>

          <p className="mt-4 font-medium text-blue-600 dark:text-blue-400">
            Current Theme :
            {theme === "dark" ? " 🌙 Dark" : " ☀️ Light"}
          </p>

          {/* Theme Toggle */}

          <div className="mt-6 flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800">

            <div>

              <p className="font-semibold text-slate-900 dark:text-white">
                Dark Mode
              </p>

              <p className="text-sm text-slate-500 dark:text-slate-400">
                Switch between light and dark appearance
              </p>

            </div>

            <button
              onClick={toggleTheme}
              className={`relative h-8 w-16 rounded-full transition-all duration-300 ${
                theme === "dark"
                  ? "bg-blue-600"
                  : "bg-slate-300"
              }`}
            >
              <span
                className={`absolute top-1 h-6 w-6 rounded-full bg-white shadow transition-all duration-300 ${
                  theme === "dark"
                    ? "left-9"
                    : "left-1"
                }`}
              />
            </button>

          </div>

        </div>

        {/* ================= Notifications ================= */}

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition dark:border-slate-700 dark:bg-slate-900">

          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            🔔 Notifications
          </h2>

          <p className="mt-2 text-slate-500 dark:text-slate-400">
            Choose how you receive alerts.
          </p>

          <div className="mt-6 space-y-5">

            <label className="flex items-center justify-between">
              <span className="text-slate-700 dark:text-white">
                Email Notifications
              </span>

              <input
                type="checkbox"
                defaultChecked
              />
            </label>

            <label className="flex items-center justify-between">
              <span className="text-slate-700 dark:text-white">
                Browser Notifications
              </span>

              <input
                type="checkbox"
                defaultChecked
              />
            </label>

            <label className="flex items-center justify-between">
              <span className="text-slate-700 dark:text-white">
                AI Suggestions
              </span>

              <input
                type="checkbox"
                defaultChecked
              />
            </label>

          </div>

        </div>

        {/* ================= Account ================= */}

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition dark:border-slate-700 dark:bg-slate-900">

          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            👤 Account
          </h2>

          <p className="mt-2 text-slate-500 dark:text-slate-400">
            Manage your account settings.
          </p>

          <button
            onClick={() => {
              localStorage.removeItem("token");
              window.location.href = "/";
            }}
            className="mt-6 rounded-lg bg-red-600 px-6 py-2 text-white transition hover:bg-red-700"
          >
            Logout
          </button>

        </div>

        {/* ================= Security ================= */}

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition dark:border-slate-700 dark:bg-slate-900">

          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            🔒 Security
          </h2>

          <p className="mt-2 text-slate-500 dark:text-slate-400">
            Manage your security preferences.
          </p>

          <button className="mt-6 rounded-lg bg-slate-700 px-6 py-2 text-white transition hover:bg-slate-800 dark:bg-slate-600 dark:hover:bg-slate-500">
            Change Password
          </button>

        </div>

      </div>

    </MainLayout>
  );
}