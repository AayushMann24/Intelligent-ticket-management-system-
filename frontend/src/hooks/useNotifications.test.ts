import { renderHook, act, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

// Mock the notification service BEFORE importing the hook
vi.mock('../services/notificationService', () => ({
  getNotifications: vi.fn(),
  getUnreadCount: vi.fn(),
  markAsRead: vi.fn(),
  markAllAsRead: vi.fn(),
}));

import { useNotifications } from '../hooks/useNotifications';
import { getNotifications, getUnreadCount, markAsRead, markAllAsRead } from '../services/notificationService';

describe('useNotifications', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  const mockNotifications = [
    {
      id: 1,
      notification_type: 'TICKET_ASSIGNED' as const,
      title: 'Test 1',
      message: 'Message 1',
      ticket_id: 42,
      is_read: false,
      read_at: null,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      notification_type: 'SLA_RESPONSE_BREACHED' as const,
      title: 'SLA Breached',
      message: 'SLA breached',
      ticket_id: 43,
      is_read: true,
      read_at: '2024-01-01T01:00:00Z',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
  ];

  const mockListResponse = {
    items: mockNotifications,
    total: 2,
    page: 1,
    page_size: 20,
    total_pages: 1,
  };

  beforeEach(() => {
    (getNotifications as vi.Mock).mockResolvedValue(mockListResponse);
    (getUnreadCount as vi.Mock).mockResolvedValue({ unread_count: 1 });
    (markAsRead as vi.Mock).mockResolvedValue({
      id: 1,
      is_read: true,
      read_at: '2024-01-01T01:00:00Z',
    });
    (markAllAsRead as vi.Mock).mockResolvedValue({ marked_count: 1 });
  });

  describe('initial state', () => {
    it('returns initial empty state', () => {
      const { result } = renderHook(() => useNotifications());

      expect(result.current.notifications).toEqual([]);
      expect(result.current.unreadCount).toBe(0);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });

  describe('fetchNotifications', () => {
    it('fetches notifications and updates state', async () => {
      (getNotifications as vi.Mock).mockResolvedValueOnce({
        items: [],
        total: 0,
        page: 1,
        page_size: 20,
        total_pages: 1,
      });

      const { result } = renderHook(() => useNotifications());

      await act(async () => {
        await result.current.fetchNotifications({ page: 1, page_size: 20 });
      });

      expect(getNotifications).toHaveBeenCalledWith({ page: 1, page_size: 20 });
      expect(result.current.notifications).toEqual([]);
    });

    it('fetches notifications with params', async () => {
      (getNotifications as vi.Mock).mockResolvedValueOnce({
        items: [],
        total: 0,
        page: 2,
        page_size: 10,
        total_pages: 1,
      });

      const { result } = renderHook(() => useNotifications());

      await act(async () => {
        await result.current.fetchNotifications({ page: 2, page_size: 10 });
      });

      expect(getNotifications).toHaveBeenCalledWith({ page: 2, page_size: 10 });
    });

    it('handles fetch errors', async () => {
      (getNotifications as vi.Mock).mockRejectedValueOnce(new Error('Failed to fetch notifications'));

      const { result } = renderHook(() => useNotifications());

      await act(async () => {
        await result.current.fetchNotifications();
      });

      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toBe('Failed to fetch notifications');
      expect(result.current.loading).toBe(false);
    });
  });

  describe('fetchUnreadCount', () => {
    it('fetches unread count and updates state', async () => {
      const { result } = renderHook(() => useNotifications());

      await act(async () => {
        await result.current.fetchUnreadCount();
      });

      expect(getUnreadCount).toHaveBeenCalled();
      expect(result.current.unreadCount).toBe(1);
    });

    it('handles fetch errors gracefully', async () => {
      (getUnreadCount as vi.Mock).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useNotifications());

      await act(async () => {
        await result.current.fetchUnreadCount();
      });

      // Error is silently ignored for unread count
      expect(result.current.unreadCount).toBe(0);
    });
  });

  describe('markAsRead', () => {
    it('marks notification as read and updates state', async () => {
      const { result } = renderHook(() => useNotifications());

      // Set initial notifications
      act(() => {
        result.current.setNotifications([
          { id: 1, is_read: false, notification_type: 'TICKET_ASSIGNED', title: 'Test', message: 'Msg', ticket_id: 1, is_read: false, read_at: null, created_at: '', updated_at: '' },
        ]);
        result.current.setUnreadCount(1);
      });

      await act(async () => {
        await result.current.markAsRead(1);
      });

      expect(markAsRead).toHaveBeenCalledWith(1);
      expect(result.current.unreadCount).toBe(0);
      expect(result.current.notifications[0].is_read).toBe(true);
    });

    it('handles API errors', async () => {
      (markAsRead as vi.Mock).mockRejectedValueOnce(new Error('Failed to mark'));

      const { result } = renderHook(() => useNotifications());

      await act(async () => {
        await result.current.markAsRead(1);
      });

      expect(result.current.error).toBeInstanceOf(Error);
    });
  });

  describe('markAllAsRead', () => {
    it('marks all notifications as read', async () => {
      const { result } = renderHook(() => useNotifications());

      act(() => {
        result.current.setNotifications([
          { id: 1, is_read: false, notification_type: 'TICKET_ASSIGNED', title: 'Test', message: 'Msg', ticket_id: 1, is_read: false, read_at: null, created_at: '', updated_at: '' },
          { id: 2, is_read: false, notification_type: 'SLA_RESPONSE_BREACHED', title: 'Test 2', message: 'Msg 2', ticket_id: 2, is_read: false, read_at: null, created_at: '', updated_at: '' },
        ]);
        result.current.setUnreadCount(2);
      });

      await act(async () => {
        await result.current.markAllAsRead();
      });

      expect(markAllAsRead).toHaveBeenCalled();
      expect(result.current.unreadCount).toBe(0);
      expect(result.current.notifications.every(n => n.is_read)).toBe(true);
    });

    it('handles API errors', async () => {
      (markAllAsRead as vi.Mock).mockRejectedValueOnce(new Error('Failed to mark all'));

      const { result } = renderHook(() => useNotifications());

      await act(async () => {
        await result.current.markAllAsRead();
      });

      expect(result.current.error).toBeInstanceOf(Error);
    });
  });

  describe('polling cleanup', () => {
    it('cleans up interval on unmount', () => {
      const { unmount } = renderHook(() => useNotifications());

      // Verify initial load happened
      expect(getUnreadCount).toHaveBeenCalled();

      unmount();

      // After unmount, no further calls should happen
      vi.advanceTimersByTime(50000);
      expect(getUnreadCount).toHaveBeenCalledTimes(1);
    });

    it('does not create duplicate intervals on re-render', () => {
      const { rerender } = renderHook(() => useNotifications());

      expect(getUnreadCount).toHaveBeenCalledTimes(1);

      rerender();

      // Should not create additional intervals
      expect(getUnreadCount).toHaveBeenCalledTimes(1);
    });

    it('continues polling while mounted', () => {
      const { result } = renderHook(() => useNotifications());

      expect(getUnreadCount).toHaveBeenCalledTimes(1);

      act(() => {
        vi.advanceTimersByTime(50000);
      });

      expect(getUnreadCount).toHaveBeenCalledTimes(2);
    });
  });

  describe('error handling', () => {
    it('sets error state on fetchNotifications failure', async () => {
      (getNotifications as vi.Mock).mockRejectedValueOnce(new Error('Failed to fetch notifications'));

      const { result } = renderHook(() => useNotifications());

      await act(async () => {
        await result.current.fetchNotifications();
      });

      expect(result.current.error).toBeInstanceOf(Error);
      expect(result.current.error?.message).toBe('Failed to fetch notifications');
    });

    it('sets error state on markAsRead failure', async () => {
      (markAsRead as vi.Mock).mockRejectedValueOnce(new Error('Failed to mark'));

      const { result } = renderHook(() => useNotifications());

      await act(async () => {
        await result.current.markAsRead(1);
      });

      expect(result.current.error).toBeInstanceOf(Error);
    });

    it('sets error state on markAllAsRead failure', async () => {
      (markAllAsRead as vi.Mock).mockRejectedValueOnce(new Error('Failed to mark all'));

      const { result } = renderHook(() => useNotifications());

      await act(async () => {
        await result.current.markAllAsRead();
      });

      expect(result.current.error).toBeInstanceOf(Error);
    });
  });
});