import api from "./api";
import type {
  Notification,
  NotificationListResponse,
  UnreadCountResponse,
  GetNotificationsParams,
} from "../types/notification";

export type {
  Notification,
  NotificationListResponse,
  UnreadCountResponse,
  GetNotificationsParams,
};

// ======================================
// Notification API
// ======================================

export async function getNotifications(
  params?: GetNotificationsParams
): Promise<NotificationListResponse> {
  const response = await api.get<NotificationListResponse>("/notifications/", {
    params,
  });
  return response.data;
}

export async function getUnreadCount(): Promise<UnreadCountResponse> {
  const response = await api.get<UnreadCountResponse>(
    "/notifications/unread-count"
  );
  return response.data;
}

export async function markAsRead(
  notificationId: number
): Promise<Notification> {
  const response = await api.patch<Notification>(
    `/notifications/${notificationId}/read`
  );
  return response.data;
}

export async function markAllAsRead(): Promise<{ marked_count: number }> {
  const response = await api.post<{ marked_count: number }>(
    "/notifications/mark-all-read"
  );
  return response.data;
}