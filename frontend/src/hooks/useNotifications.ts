import { useCallback, useEffect, useRef, useState } from "react";

import {
  getNotifications,
  getUnreadCount,
  markAsRead,
  markAllAsRead,
  type Notification,
  type GetNotificationsParams,
  type NotificationListResponse,
} from "../services/notificationService";

interface UseNotificationsReturn {
  notifications: Notification[];
  unreadCount: number;
  loading: boolean;
  error: Error | null;
  fetchNotifications: (params?: GetNotificationsParams) => Promise<NotificationListResponse | undefined>;
  fetchUnreadCount: () => Promise<void>;
  markAsRead: (id: number) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  setNotifications: React.Dispatch<React.SetStateAction<Notification[]>>;
  setUnreadCount: React.Dispatch<React.SetStateAction<number>>;
}

const POLLING_INTERVAL = 45000; // 45 seconds

export function useNotifications(): UseNotificationsReturn {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isMountedRef = useRef(true);
  const initialLoadRef = useRef(true);

  // Cleanup on unmount
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    };
  }, []);

  const fetchNotifications = useCallback(
    async (params?: GetNotificationsParams): Promise<NotificationListResponse | undefined> => {
      setLoading(true);
      setError(null);
      try {
        const data = await getNotifications(params);
        if (isMountedRef.current) {
          setNotifications(data.items);
        }
        return data;
      } catch (err) {
        if (isMountedRef.current) {
          setError(err instanceof Error ? err : new Error("Failed to fetch notifications"));
        }
        return undefined;
      } finally {
        if (isMountedRef.current) {
          setLoading(false);
        }
      }
    },
    []
  );

  const fetchUnreadCount = useCallback(async () => {
    try {
      const data = await getUnreadCount();
      if (isMountedRef.current) {
        setUnreadCount(data.unread_count);
      }
    } catch {
      // Silently fail for unread count - don't disrupt UX
    }
  }, []);

  const markAsReadFn = useCallback(async (id: number) => {
    try {
      const updated = await markAsRead(id);
      setNotifications((prev) =>
        prev.map((n) =>
          n.id === id ? { ...n, is_read: true, read_at: updated.read_at } : n
        )
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to mark as read"));
    }
  }, []);

  const markAllAsReadFn = useCallback(async () => {
    try {
      await markAllAsRead();
      setNotifications((prev) =>
        prev.map((n) => (n.is_read ? n : { ...n, is_read: true }))
      );
      setUnreadCount(0);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to mark all as read"));
    }
  }, []);

  // Initial fetch and polling for unread count
  useEffect(() => {
    // Initial fetch
    if (initialLoadRef.current) {
      initialLoadRef.current = false;
      fetchUnreadCount();
    }

    // Set up polling
    pollingRef.current = setInterval(() => {
      fetchUnreadCount();
    }, POLLING_INTERVAL);

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    };
  }, [fetchUnreadCount]);

  return {
    notifications,
    unreadCount,
    loading,
    error,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead: markAsReadFn,
    markAllAsRead: markAllAsReadFn,
    setNotifications,
    setUnreadCount,
  };
}