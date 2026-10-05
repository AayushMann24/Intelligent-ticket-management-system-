export type NotificationType =
  | "TICKET_ASSIGNED"
  | "TICKET_REASSIGNED"
  | "SLA_RESPONSE_WARNING"
  | "SLA_RESPONSE_BREACHED"
  | "SLA_RESOLUTION_WARNING"
  | "SLA_RESOLUTION_BREACHED"
  | "TICKET_ESCALATED"
  | "SYSTEM";

export interface Notification {
  id: number;
  notification_type: NotificationType;
  title: string;
  message: string;
  ticket_id: number | null;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface NotificationListResponse {
  items: Notification[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface GetNotificationsParams {
  page?: number;
  page_size?: number;
  unread_only?: boolean;
  notification_type?: NotificationType;
  sort_by?: "created_at" | "notification_type" | "is_read";
  sort_order?: "asc" | "desc";
}