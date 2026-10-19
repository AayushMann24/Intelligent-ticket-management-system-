import { useCallback, useEffect, useState } from "react";
import { isAxiosError } from "axios";
import { AlertCircle, CheckCircle2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

import MainLayout from "../layouts/MainLayout";
import { useTheme } from "../context/useTheme";
import { useAuth } from "../context/useAuth";
import {
  changePassword,
  getMyPreferences,
  updateMyPreferences,
} from "../services/userService";
import type {
  PreferencesUpdate,
  UserPreferences,
} from "../types/preferences";

const MIN_PASSWORD_LENGTH = 8;

type Feedback = { type: "success" | "error"; text: string };

const PREFERENCE_FIELDS: {
  key: keyof PreferencesUpdate;
  label: string;
  description: string;
}[] = [
  {
    key: "email_notifications_enabled",
    label: "Email Notifications",
    description: "Receive escalation and SLA notifications by email.",
  },
  {
    key: "in_app_notifications_enabled",
    label: "In-App Notifications",
    description: "Show alerts inside the ITMS notification center.",
  },
  {
    key: "ai_suggestions_enabled",
    label: "AI Suggestions",
    description: "Allow AI-powered suggestions on your tickets.",
  },
];

function getPasswordErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const status = error.response?.status;
    const detail = error.response?.data?.detail;

    if (status === 400 && typeof detail === "string") {
      // Backend messages here are safe (e.g. "Current password is incorrect").
      return detail;
    }
    if (status === 422) {
      return `New password must be at least ${MIN_PASSWORD_LENGTH} characters.`;
    }
    if (status === 429) {
      return "Too many attempts. Please wait a moment and try again.";
    }
    if (!error.response) {
      return "Unable to reach the server. Please try again.";
    }
  }

  return "Could not change your password. Please try again.";
}

interface PasswordChangeFormProps {
  onSuccess: () => void;
}

function PasswordChangeForm({ onSuccess }: PasswordChangeFormProps) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (submitting) return;

    setError("");

    if (!currentPassword || !newPassword || !confirmPassword) {
      setError("Please fill in all password fields.");
      return;
    }

    if (newPassword.length < MIN_PASSWORD_LENGTH) {
      setError(
        `New password must be at least ${MIN_PASSWORD_LENGTH} characters.`
      );
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("New password and confirmation do not match.");
      return;
    }

    if (newPassword === currentPassword) {
      setError("New password must be different from the current password.");
      return;
    }

    setSubmitting(true);
    try {
      await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });

      // Never keep the typed passwords around after a successful change.
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");

      onSuccess();
    } catch (err) {
      setError(getPasswordErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="mt-6 space-y-4" onSubmit={handleSubmit} noValidate>
      <div>
        <label
          htmlFor="current-password"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          Current Password
        </label>
        <input
          id="current-password"
          name="current-password"
          type="password"
          autoComplete="current-password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          disabled={submitting}
          className="w-full rounded-lg border border-slate-300 bg-white px-4 py-2 text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 disabled:opacity-60 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
        />
      </div>

      <div>
        <label
          htmlFor="new-password"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          New Password
        </label>
        <input
          id="new-password"
          name="new-password"
          type="password"
          autoComplete="new-password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          disabled={submitting}
          className="w-full rounded-lg border border-slate-300 bg-white px-4 py-2 text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 disabled:opacity-60 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
        />
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
          At least {MIN_PASSWORD_LENGTH} characters.
        </p>
      </div>

      <div>
        <label
          htmlFor="confirm-password"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          Confirm New Password
        </label>
        <input
          id="confirm-password"
          name="confirm-password"
          type="password"
          autoComplete="new-password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          disabled={submitting}
          className="w-full rounded-lg border border-slate-300 bg-white px-4 py-2 text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 disabled:opacity-60 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
        />
      </div>

      {error && (
        <p
          role="alert"
          className="flex items-center gap-2 rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-300"
        >
          <AlertCircle size={16} className="flex-shrink-0" />
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={submitting}
        className="rounded-lg bg-slate-700 px-6 py-2 text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-slate-600 dark:hover:bg-slate-500"
      >
        {submitting ? "Updating..." : "Update Password"}
      </button>
    </form>
  );
}

export default function SettingsPage() {
  const { theme, toggleTheme } = useTheme();
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [savedPreferences, setSavedPreferences] =
    useState<UserPreferences | null>(null);
  const [preferencesStatus, setPreferencesStatus] = useState<
    "loading" | "ready" | "error"
  >("loading");
  const [preferencesError, setPreferencesError] = useState("");
  const [savingPreferences, setSavingPreferences] = useState(false);
  const [preferencesFeedback, setPreferencesFeedback] =
    useState<Feedback | null>(null);

  const [showPasswordForm, setShowPasswordForm] = useState(false);

  const loadPreferences = useCallback(async () => {
    setPreferencesStatus("loading");
    setPreferencesError("");

    try {
      const data = await getMyPreferences();
      // Only accept real server data - never fall back to defaults here.
      setPreferences(data);
      setSavedPreferences(data);
      setPreferencesStatus("ready");
    } catch {
      setPreferencesStatus("error");
      setPreferencesError(
        "We couldn't load your notification preferences. Please try again."
      );
    }
  }, []);

  useEffect(() => {
    loadPreferences();
  }, [loadPreferences]);

  const hasPreferenceChanges =
    preferences !== null &&
    savedPreferences !== null &&
    (preferences.email_notifications_enabled !==
      savedPreferences.email_notifications_enabled ||
      preferences.in_app_notifications_enabled !==
        savedPreferences.in_app_notifications_enabled ||
      preferences.ai_suggestions_enabled !==
        savedPreferences.ai_suggestions_enabled);

  const handlePreferenceToggle = (key: keyof PreferencesUpdate) => {
    setPreferencesFeedback(null);
    setPreferences((current) =>
      current ? { ...current, [key]: !current[key] } : current
    );
  };

  const handleSavePreferences = async () => {
    if (!preferences || savingPreferences || !hasPreferenceChanges) return;

    setSavingPreferences(true);
    setPreferencesFeedback(null);

    try {
      const updated = await updateMyPreferences({
        email_notifications_enabled: preferences.email_notifications_enabled,
        in_app_notifications_enabled:
          preferences.in_app_notifications_enabled,
        ai_suggestions_enabled: preferences.ai_suggestions_enabled,
      });

      // Reflect the persisted result exactly as the server returned it.
      setPreferences(updated);
      setSavedPreferences(updated);
      setPreferencesFeedback({
        type: "success",
        text: "Your preferences have been saved.",
      });
    } catch {
      setPreferencesFeedback({
        type: "error",
        text: "We couldn't save your preferences. Please try again.",
      });
    } finally {
      setSavingPreferences(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const handlePasswordChanged = async () => {
    // The backend revokes refresh tokens, so end the session honestly and
    // send the user back to sign in again rather than faking continued auth.
    setShowPasswordForm(false);
    await logout();
    navigate("/login", {
      replace: true,
      state: { passwordChanged: true },
    });
  };

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
              aria-label="Toggle dark mode"
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

          {preferencesStatus === "loading" && (
            <div
              role="status"
              className="mt-6 flex items-center gap-3 text-slate-500 dark:text-slate-400"
            >
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
              Loading your preferences...
            </div>
          )}

          {preferencesStatus === "error" && (
            <div className="mt-6 rounded-xl border border-red-300 bg-red-50 p-4 text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-300">
              <p className="flex items-center gap-2 text-sm">
                <AlertCircle size={16} className="flex-shrink-0" />
                {preferencesError}
              </p>

              <button
                onClick={loadPreferences}
                className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm text-white transition hover:bg-red-700"
              >
                Try again
              </button>
            </div>
          )}

          {preferencesStatus === "ready" && preferences && (
            <>
              <div className="mt-6 space-y-5">
                {PREFERENCE_FIELDS.map((field) => (
                  <label
                    key={field.key}
                    className="flex items-start justify-between gap-4"
                  >
                    <span>
                      <span className="block text-slate-700 dark:text-white">
                        {field.label}
                      </span>
                      <span className="block text-sm text-slate-500 dark:text-slate-400">
                        {field.description}
                      </span>
                    </span>

                    <input
                      type="checkbox"
                      className="mt-1 h-5 w-5 flex-shrink-0"
                      checked={preferences[field.key]}
                      onChange={() => handlePreferenceToggle(field.key)}
                      disabled={savingPreferences}
                    />
                  </label>
                ))}
              </div>

              <div className="mt-6 flex flex-wrap items-center gap-3">
                <button
                  onClick={handleSavePreferences}
                  disabled={!hasPreferenceChanges || savingPreferences}
                  className="rounded-lg bg-blue-600 px-6 py-2 text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {savingPreferences ? "Saving..." : "Save Preferences"}
                </button>

                {preferencesFeedback && (
                  <span
                    role="status"
                    className={`flex items-center gap-2 text-sm ${
                      preferencesFeedback.type === "success"
                        ? "text-emerald-600 dark:text-emerald-400"
                        : "text-red-600 dark:text-red-400"
                    }`}
                  >
                    {preferencesFeedback.type === "success" ? (
                      <CheckCircle2 size={16} className="flex-shrink-0" />
                    ) : (
                      <AlertCircle size={16} className="flex-shrink-0" />
                    )}
                    {preferencesFeedback.text}
                  </span>
                )}
              </div>
            </>
          )}

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
            onClick={handleLogout}
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

          {!showPasswordForm && (
            <button
              onClick={() => setShowPasswordForm(true)}
              className="mt-6 rounded-lg bg-slate-700 px-6 py-2 text-white transition hover:bg-slate-800 dark:bg-slate-600 dark:hover:bg-slate-500"
            >
              Change Password
            </button>
          )}

          {showPasswordForm && (
            <>
              <PasswordChangeForm onSuccess={handlePasswordChanged} />
              <button
                onClick={() => setShowPasswordForm(false)}
                className="mt-3 text-sm text-slate-500 underline transition hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
              >
                Cancel
              </button>
            </>
          )}

        </div>

      </div>

    </MainLayout>
  );
}
