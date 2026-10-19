import { render, screen } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from "vitest";
import { MemoryRouter, Routes, Route } from "react-router-dom";

vi.mock("../context/useAuth", () => ({ useAuth: vi.fn() }));
vi.mock("../hooks/useNotifications", () => ({ useNotifications: vi.fn() }));
vi.mock("../services/userService", () => ({
  getMyPreferences: vi.fn(),
  updateMyPreferences: vi.fn(),
  changePassword: vi.fn(),
}));

import App from "../App";
import { ProtectedRoute } from "../components/auth/ProtectedRoute";
import { ThemeProvider } from "../context/ThemeContext";
import { useAuth } from "../context/useAuth";
import { useNotifications } from "../hooks/useNotifications";
import { getMyPreferences } from "../services/userService";

const employee = {
  id: 2,
  name: "Employee User",
  email: "employee@example.com",
  role: "Employee",
};

describe("Settings access control", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    (useAuth as vi.Mock).mockReturnValue({
      user: employee,
      loading: false,
      logout: vi.fn(),
      login: vi.fn(),
      register: vi.fn(),
      refreshAuth: vi.fn(),
    });

    (useNotifications as vi.Mock).mockReturnValue({
      notifications: [],
      unreadCount: 0,
      loading: false,
      error: null,
      fetchNotifications: vi.fn(),
      fetchUnreadCount: vi.fn(),
      markAsRead: vi.fn(),
      markAllAsRead: vi.fn(),
      setNotifications: vi.fn(),
      setUnreadCount: vi.fn(),
    });

    (getMyPreferences as vi.Mock).mockResolvedValue({
      email_notifications_enabled: true,
      in_app_notifications_enabled: true,
      ai_suggestions_enabled: true,
    });
  });

  it("lets a non-admin reach /settings directly", async () => {
    render(
      <ThemeProvider>
        <MemoryRouter initialEntries={["/settings"]}>
          <App />
        </MemoryRouter>
      </ThemeProvider>
    );

    expect(
      await screen.findByRole("heading", { level: 1, name: /Settings/ })
    ).toBeInTheDocument();
  });

  it("still protects admin-only routes for non-admins", async () => {
    render(
      <MemoryRouter initialEntries={["/admin-only"]}>
        <Routes>
          <Route
            path="/admin-only"
            element={
              <ProtectedRoute allowedRoles={["Admin"]}>
                <div>Secret Admin Area</div>
              </ProtectedRoute>
            }
          />
          <Route path="/dashboard" element={<div>Dashboard Home</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText("Dashboard Home")).toBeInTheDocument();
    expect(screen.queryByText("Secret Admin Area")).not.toBeInTheDocument();
  });
});
