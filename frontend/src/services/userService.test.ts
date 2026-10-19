import { vi, describe, it, expect, beforeEach } from "vitest";

// Mock the api client
vi.mock("./api", () => ({
  default: {
    get: vi.fn(),
    put: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}));

import api from "./api";
import {
  getMyPreferences,
  updateMyPreferences,
  changePassword,
} from "./userService";
import type { UserPreferences } from "../types/preferences";

describe("userService - settings endpoints", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const preferences: UserPreferences = {
    email_notifications_enabled: true,
    in_app_notifications_enabled: false,
    ai_suggestions_enabled: true,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  };

  describe("getMyPreferences", () => {
    it("calls GET /users/me/preferences", async () => {
      (api.get as vi.Mock).mockResolvedValueOnce({ data: preferences });

      const result = await getMyPreferences();

      expect(api.get).toHaveBeenCalledWith("/users/me/preferences");
      expect(result).toEqual(preferences);
    });

    it("propagates API errors", async () => {
      (api.get as vi.Mock).mockRejectedValueOnce(new Error("Network error"));

      await expect(getMyPreferences()).rejects.toThrow("Network error");
    });
  });

  describe("updateMyPreferences", () => {
    it("PUTs the exact payload to /users/me/preferences", async () => {
      const payload = { email_notifications_enabled: false };
      (api.put as vi.Mock).mockResolvedValueOnce({
        data: { ...preferences, ...payload },
      });

      const result = await updateMyPreferences(payload);

      expect(api.put).toHaveBeenCalledWith(
        "/users/me/preferences",
        payload
      );
      expect(result.email_notifications_enabled).toBe(false);
    });

    it("propagates API errors", async () => {
      (api.put as vi.Mock).mockRejectedValueOnce(new Error("Server error"));

      await expect(
        updateMyPreferences({ in_app_notifications_enabled: false })
      ).rejects.toThrow("Server error");
    });
  });

  describe("changePassword", () => {
    it("PUTs current_password and new_password to /users/me/password", async () => {
      (api.put as vi.Mock).mockResolvedValueOnce({
        data: { message: "Password changed successfully." },
      });

      const payload = {
        current_password: "oldpassword1",
        new_password: "newpassword1",
      };

      const result = await changePassword(payload);

      expect(api.put).toHaveBeenCalledWith("/users/me/password", payload);
      expect(result).toEqual({ message: "Password changed successfully." });
    });

    it("propagates API errors", async () => {
      (api.put as vi.Mock).mockRejectedValueOnce(new Error("Bad request"));

      await expect(
        changePassword({
          current_password: "oldpassword1",
          new_password: "newpassword1",
        })
      ).rejects.toThrow("Bad request");
    });
  });
});
