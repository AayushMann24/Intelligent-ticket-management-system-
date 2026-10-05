import { vi, describe, it, expect, beforeEach } from 'vitest';

// Mock the api
vi.mock('./api', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
    post: vi.fn(),
  },
}));

import api from './api';
import {
  getNotifications,
  getUnreadCount,
  markAsRead,
  markAllAsRead,
} from './notificationService';
import type {
  Notification,
  NotificationListResponse,
  UnreadCountResponse,
} from '../types/notification';

describe('notificationService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockNotification: Notification = {
    id: 1,
    notification_type: 'TICKET_ASSIGNED',
    title: 'Test Title',
    message: 'Test message',
    ticket_id: 42,
    is_read: false,
    read_at: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  const mockNotificationListResponse: NotificationListResponse = {
    items: [mockNotification],
    total: 1,
    page: 1,
    page_size: 20,
    total_pages: 1,
  };

  const mockUnreadCountResponse: UnreadCountResponse = {
    unread_count: 5,
  };

  describe('getNotifications', () => {
    it('fetches notifications with default params', async () => {
      (api.get as vi.Mock).mockResolvedValueOnce({
        data: mockNotificationListResponse,
      });

      const result = await getNotifications();

      expect(api.get).toHaveBeenCalledWith('/notifications/', {
        params: undefined,
      });
      expect(result).toEqual(mockNotificationListResponse);
    });

    it('fetches notifications with custom params', async () => {
      (api.get as vi.Mock).mockResolvedValueOnce({
        data: mockNotificationListResponse,
      });

      const params = {
        page: 2,
        page_size: 10,
        unread_only: true,
        notification_type: 'TICKET_ASSIGNED' as const,
      };

      const result = await getNotifications(params);

      expect(api.get).toHaveBeenCalledWith('/notifications/', {
        params,
      });
      expect(result).toEqual(mockNotificationListResponse);
    });

    it('handles API errors', async () => {
      (api.get as vi.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect(getNotifications()).rejects.toThrow('Network error');
    });
  });

  describe('getUnreadCount', () => {
    it('fetches unread count', async () => {
      (api.get as vi.Mock).mockResolvedValueOnce({
        data: mockUnreadCountResponse,
      });

      const result = await getUnreadCount();

      expect(api.get).toHaveBeenCalledWith('/notifications/unread-count');
      expect(result).toEqual(mockUnreadCountResponse);
    });

    it('handles API errors', async () => {
      (api.get as vi.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect(getUnreadCount()).rejects.toThrow('Network error');
    });
  });

  describe('markAsRead', () => {
    it('marks a notification as read', async () => {
      const updatedNotification = { ...mockNotification, is_read: true, read_at: '2024-01-01T01:00:00Z' };
      (api.patch as vi.Mock).mockResolvedValueOnce({
        data: updatedNotification,
      });

      const result = await markAsRead(1);

      expect(api.patch).toHaveBeenCalledWith('/notifications/1/read');
      expect(result).toEqual(updatedNotification);
    });

    it('handles API errors', async () => {
      (api.patch as vi.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect(markAsRead(1)).rejects.toThrow('Network error');
    });
  });

  describe('markAllAsRead', () => {
    it('marks all notifications as read', async () => {
      (api.post as vi.Mock).mockResolvedValueOnce({
        data: { marked_count: 5 },
      });

      const result = await markAllAsRead();

      expect(api.post).toHaveBeenCalledWith('/notifications/mark-all-read');
      expect(result).toEqual({ marked_count: 5 });
    });

    it('handles API errors', async () => {
      (api.post as vi.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect(markAllAsRead()).rejects.toThrow('Network error');
    });
  });
});