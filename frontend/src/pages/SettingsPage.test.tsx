import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import type { ReactNode } from "react";

import SettingsPage from "./SettingsPage";

// Keep the page-level test focused on Settings behavior, not the app shell.
vi.mock("../layouts/MainLayout", () => ({
  default: ({ children }: { children: ReactNode }) => <div>{children}</div>,
}));

vi.mock("../context/useAuth", () => ({ useAuth: vi.fn() }));
vi.mock("../context/useTheme", () => ({ useTheme: vi.fn() }));
vi.mock("../services/userService", () => ({
  getMyPreferences: vi.fn(),
  updateMyPreferences: vi.fn(),
  changePassword: vi.fn(),
}));

import { useAuth } from "../context/useAuth";
import { useTheme } from "../context/useTheme";
import {
  getMyPreferences,
  updateMyPreferences,
  changePassword,
} from "../services/userService";

const DEFAULT_PREFERENCES = {
  email_notifications_enabled: true,
  in_app_notifications_enabled: true,
  ai_suggestions_enabled: true,
};

describe("SettingsPage", () => {
  let logoutMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    vi.clearAllMocks();

    logoutMock = vi.fn().mockResolvedValue(undefined);

    (useAuth as vi.Mock).mockReturnValue({
      user: { id: 1, name: "Test", email: "test@example.com", role: "Employee" },
      loading: false,
      logout: logoutMock,
    });
    (useTheme as vi.Mock).mockReturnValue({
      theme: "dark",
      toggleTheme: vi.fn(),
    });

    (getMyPreferences as vi.Mock).mockResolvedValue(DEFAULT_PREFERENCES);
    (updateMyPreferences as vi.Mock).mockImplementation(
      async (updates: Partial<typeof DEFAULT_PREFERENCES>) => ({
        ...DEFAULT_PREFERENCES,
        ...updates,
      })
    );
    (changePassword as vi.Mock).mockResolvedValue({ message: "ok" });
  });

  const renderPage = () =>
    render(
      <MemoryRouter>
        <SettingsPage />
      </MemoryRouter>
    );

  const emailCheckbox = () =>
    screen.getByRole("checkbox", { name: /Email Notifications/ }) as HTMLInputElement;
  const inAppCheckbox = () =>
    screen.getByRole("checkbox", { name: /In-App Notifications/ }) as HTMLInputElement;
  const aiCheckbox = () =>
    screen.getByRole("checkbox", { name: /AI Suggestions/ }) as HTMLInputElement;

  describe("notification preferences", () => {
    it("shows a loading state and no checkboxes until preferences arrive", async () => {
      let resolvePreferences:
        | ((value: typeof DEFAULT_PREFERENCES) => void)
        | undefined;
      (getMyPreferences as vi.Mock).mockReturnValueOnce(
        new Promise((resolve) => {
          resolvePreferences = resolve;
        })
      );

      renderPage();

      expect(
        screen.getByText(/Loading your preferences/i)
      ).toBeInTheDocument();
      expect(screen.queryByRole("checkbox")).not.toBeInTheDocument();

      await act(async () => {
        resolvePreferences?.(DEFAULT_PREFERENCES);
      });

      expect(await emailCheckbox()).toBeInTheDocument();
    });

    it("renders the persisted preference values", async () => {
      (getMyPreferences as vi.Mock).mockResolvedValueOnce({
        email_notifications_enabled: true,
        in_app_notifications_enabled: false,
        ai_suggestions_enabled: true,
      });

      renderPage();

      await waitFor(() => {
        expect(emailCheckbox().checked).toBe(true);
      });
      expect(inAppCheckbox().checked).toBe(false);
      expect(aiCheckbox().checked).toBe(true);
    });

    it("disables save until a change is made", async () => {
      renderPage();

      const saveButton = await screen.findByRole("button", {
        name: /Save Preferences/i,
      });
      expect(saveButton).toBeDisabled();
    });

    it("saves changed preferences and reflects the persisted result", async () => {
      renderPage();

      await waitFor(() => expect(emailCheckbox().checked).toBe(true));

      fireEvent.click(emailCheckbox());

      const saveButton = screen.getByRole("button", {
        name: /Save Preferences/i,
      });
      expect(saveButton).toBeEnabled();

      await act(async () => {
        fireEvent.click(saveButton);
      });

      expect(updateMyPreferences).toHaveBeenCalledWith({
        email_notifications_enabled: false,
        in_app_notifications_enabled: true,
        ai_suggestions_enabled: true,
      });

      expect(
        await screen.findByText(/preferences have been saved/i)
      ).toBeInTheDocument();
      // Saved state matches the response, so there is nothing left to save.
      expect(
        screen.getByRole("button", { name: /Save Preferences/i })
      ).toBeDisabled();
    });

    it("does not issue duplicate save requests while one is in flight", async () => {
      let resolveSave: ((value: typeof DEFAULT_PREFERENCES) => void) | undefined;
      (updateMyPreferences as vi.Mock).mockReturnValueOnce(
        new Promise((resolve) => {
          resolveSave = resolve;
        })
      );

      renderPage();
      await waitFor(() => expect(emailCheckbox().checked).toBe(true));

      fireEvent.click(emailCheckbox());

      const saveButton = screen.getByRole("button", {
        name: /Save Preferences/i,
      });

      fireEvent.click(saveButton);
      fireEvent.click(saveButton);

      expect(updateMyPreferences).toHaveBeenCalledTimes(1);

      await act(async () => {
        resolveSave?.({
          email_notifications_enabled: false,
          in_app_notifications_enabled: true,
          ai_suggestions_enabled: true,
        });
      });
    });

    it("shows an error and no defaults when loading fails", async () => {
      (getMyPreferences as vi.Mock).mockRejectedValueOnce(new Error("boom"));

      renderPage();

      expect(
        await screen.findByText(/couldn't load your notification preferences/i)
      ).toBeInTheDocument();
      // Must not surface default values as if they were saved.
      expect(screen.queryByRole("checkbox")).not.toBeInTheDocument();
    });

    it("retries loading after a failure", async () => {
      (getMyPreferences as vi.Mock)
        .mockRejectedValueOnce(new Error("boom"))
        .mockResolvedValueOnce(DEFAULT_PREFERENCES);

      renderPage();

      const retry = await screen.findByRole("button", { name: /Try again/i });
      await act(async () => {
        fireEvent.click(retry);
      });

      expect(await emailCheckbox()).toBeInTheDocument();
      expect(getMyPreferences).toHaveBeenCalledTimes(2);
    });

    it("reports a save failure without claiming success", async () => {
      (updateMyPreferences as vi.Mock).mockRejectedValueOnce(
        new Error("server down")
      );

      renderPage();
      await waitFor(() => expect(emailCheckbox().checked).toBe(true));

      fireEvent.click(emailCheckbox());
      await act(async () => {
        fireEvent.click(
          screen.getByRole("button", { name: /Save Preferences/i })
        );
      });

      expect(
        await screen.findByText(/couldn't save your preferences/i)
      ).toBeInTheDocument();
      expect(screen.queryByText(/preferences have been saved/i)).not.toBeInTheDocument();
      // Still dirty, so the user can retry.
      expect(
        screen.getByRole("button", { name: /Save Preferences/i })
      ).toBeEnabled();
    });
  });

  describe("change password", () => {
    const openForm = () =>
      fireEvent.click(screen.getByRole("button", { name: "Change Password" }));

    const fill = (current: string, next: string, confirm: string) => {
      fireEvent.change(screen.getByLabelText("Current Password"), {
        target: { value: current },
      });
      fireEvent.change(screen.getByLabelText("New Password"), {
        target: { value: next },
      });
      fireEvent.change(screen.getByLabelText("Confirm New Password"), {
        target: { value: confirm },
      });
    };

    const submit = () =>
      fireEvent.click(screen.getByRole("button", { name: /Update Password/i }));

    it("requires all fields", async () => {
      renderPage();
      openForm();

      await act(async () => {
        submit();
      });

      expect(
        screen.getByText(/fill in all password fields/i)
      ).toBeInTheDocument();
      expect(changePassword).not.toHaveBeenCalled();
    });

    it("rejects a new password shorter than the backend minimum", async () => {
      renderPage();
      openForm();
      fill("oldpassword", "short", "short");

      await act(async () => {
        submit();
      });

      expect(screen.getByRole("alert")).toHaveTextContent(
        /at least 8 characters/i
      );
      expect(changePassword).not.toHaveBeenCalled();
    });

    it("rejects a confirmation mismatch", async () => {
      renderPage();
      openForm();
      fill("oldpassword", "newpassword1", "newpassword2");

      await act(async () => {
        submit();
      });

      expect(
        screen.getByText(/do not match/i)
      ).toBeInTheDocument();
      expect(changePassword).not.toHaveBeenCalled();
    });

    it("rejects reusing the current password", async () => {
      renderPage();
      openForm();
      fill("samepassword", "samepassword", "samepassword");

      await act(async () => {
        submit();
      });

      expect(
        screen.getByText(/different from the current password/i)
      ).toBeInTheDocument();
      expect(changePassword).not.toHaveBeenCalled();
    });

    it("submits the exact backend payload and ends the session on success", async () => {
      renderPage();
      openForm();
      fill("oldpassword", "newpassword1", "newpassword1");

      await act(async () => {
        submit();
      });

      expect(changePassword).toHaveBeenCalledWith({
        current_password: "oldpassword",
        new_password: "newpassword1",
      });
      // Refresh tokens were revoked server-side, so the client signs out.
      expect(logoutMock).toHaveBeenCalled();
    });

    it("shows a safe backend error and does not sign the user out", async () => {
      (changePassword as vi.Mock).mockRejectedValueOnce({
        isAxiosError: true,
        response: {
          status: 400,
          data: { detail: "Current password is incorrect" },
        },
      });

      renderPage();
      openForm();
      fill("wrongpassword", "newpassword1", "newpassword1");

      await act(async () => {
        submit();
      });

      expect(
        screen.getByText("Current password is incorrect")
      ).toBeInTheDocument();
      expect(logoutMock).not.toHaveBeenCalled();
    });

    it("falls back to a generic message for unexpected errors", async () => {
      (changePassword as vi.Mock).mockRejectedValueOnce(new Error("network"));

      renderPage();
      openForm();
      fill("oldpassword", "newpassword1", "newpassword1");

      await act(async () => {
        submit();
      });

      expect(
        screen.getByText(/could not change your password/i)
      ).toBeInTheDocument();
      expect(logoutMock).not.toHaveBeenCalled();
    });
  });
});
