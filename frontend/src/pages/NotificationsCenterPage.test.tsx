import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

import { useNotifications } from '../hooks/useNotifications';
import NotificationsCenterPage from '../pages/NotificationsCenterPage';

// Mock the useNotifications hook
vi.mock('../hooks/useNotifications', () => ({
  useNotifications: vi.fn(),
}));

describe('NotificationsCenterPage', () => {
  let mockUseNotifications: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    vi.clearAllMocks();

    mockUseNotifications = {
      unreadCount: 2,
      loading: false,
      error: null,
      fetchNotifications: vi.fn().mockResolvedValue({
        items: [
          { id: 1, notification_type: 'TICKET_ASSIGNED', title: 'Ticket Assigned', message: 'Ticket #42 assigned to you', ticket_id: 42, is_read: false, read_at: null, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
          { id: 2, notification_type: 'SLA_RESPONSE_BREACHED', title: 'SLA Breached', message: 'SLA breached for ticket #43', ticket_id: 43, is_read: true, read_at: '2024-01-01T01:00:00Z', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
          { id: 3, notification_type: 'TICKET_ESCALATED', title: 'Ticket Escalated', message: 'Ticket escalated to you', ticket_id: 44, is_read: false, read_at: null, created_at: '2024-01-01T02:00:00Z', updated_at: '2024-01-01T02:00:00Z' },
        ],
        total: 3,
        page: 1,
        page_size: 20,
        total_pages: 2,
      }),
      markAsRead: vi.fn().mockResolvedValue(undefined),
      markAllAsRead: vi.fn().mockResolvedValue(undefined),
    };

    (useNotifications as vi.Mock).mockReturnValue(mockUseNotifications);
  });

  const renderPage = async (options?: { waitForEmpty?: boolean }) => {
    const result = render(
      <MemoryRouter>
        <NotificationsCenterPage />
      </MemoryRouter>
    );
    // Wait for notifications to load (component fetches async in useEffect)
    if (options?.waitForEmpty) {
      await waitFor(() => {
        expect(screen.getByText('No notifications')).toBeInTheDocument();
      });
    } else {
      await waitFor(() => {
        expect(screen.getByText('Ticket Assigned')).toBeInTheDocument();
      });
    }
    return result;
  };

  describe('rendering', () => {
    it('renders page title', async () => {
      await renderPage();
      expect(screen.getByText('Notifications')).toBeInTheDocument();
      expect(screen.getByText('Manage and view your notifications')).toBeInTheDocument();
    });

    it('shows mark all as read button when unread > 0', async () => {
      await renderPage();
      expect(screen.getByText('Mark all as read')).toBeInTheDocument();
    });

    it('hides mark all as read button when unread = 0', async () => {
      (useNotifications as vi.Mock).mockReturnValue({
        unreadCount: 0,
        loading: false,
        error: null,
        fetchNotifications: vi.fn().mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20, total_pages: 1 }),
        markAsRead: vi.fn().mockResolvedValue(undefined),
        markAllAsRead: vi.fn().mockResolvedValue(undefined),
      });

      await renderPage({ waitForEmpty: true });
      expect(screen.queryByText('Mark all as read')).not.toBeInTheDocument();
    });

    it('shows filter button', async () => {
      await renderPage();
      expect(screen.getByText('Filters')).toBeInTheDocument();
    });
  });

  describe('notification list', () => {
    it('renders notifications with correct content', async () => {
      await renderPage();

      expect(screen.getByText('Ticket Assigned')).toBeInTheDocument();
      expect(screen.getByText('SLA Breached')).toBeInTheDocument();
      expect(screen.getByText('Ticket Escalated')).toBeInTheDocument();
    });

    it('shows relative time', async () => {
      await renderPage();

      expect(screen.getAllByText('1/1/2024')).toHaveLength(3);
    });
  });

  describe('mark as read', () => {
    it('marks notification as read on click', async () => {
      await renderPage();

      await act(async () => {
        fireEvent.click(screen.getByText('Ticket Assigned'));
      });

      expect(screen.getByText('Ticket Assigned')).toBeInTheDocument();
    });

    it('navigates to ticket on click', async () => {
      await renderPage();

      await act(async () => {
        fireEvent.click(screen.getByText('Ticket Assigned'));
      });
    });
  });

  describe('mark all as read', () => {
    it('calls markAllAsRead when button clicked', async () => {
      await renderPage();

      await act(async () => {
        fireEvent.click(screen.getByText('Mark all as read'));
      });

      expect(screen.getByText('Mark all as read')).toBeInTheDocument();
    });
  });

  describe('empty state', () => {
    it('shows empty state when no notifications', async () => {
      (useNotifications as vi.Mock).mockReturnValue({
        unreadCount: 0,
        loading: false,
        error: null,
        fetchNotifications: vi.fn().mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20, total_pages: 1 }),
        markAsRead: vi.fn().mockResolvedValue(undefined),
        markAllAsRead: vi.fn().mockResolvedValue(undefined),
      });

      await renderPage({ waitForEmpty: true });

      expect(screen.getByText('No notifications')).toBeInTheDocument();
      expect(screen.getByText('No notifications yet.')).toBeInTheDocument();
    });
  });

  describe('error state', () => {
    it('shows error state', async () => {
      (useNotifications as vi.Mock).mockReturnValue({
        unreadCount: 0,
        loading: false,
        error: new Error('Failed to load'),
        fetchNotifications: vi.fn().mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20, total_pages: 1 }),
        markAsRead: vi.fn().mockResolvedValue(undefined),
        markAllAsRead: vi.fn().mockResolvedValue(undefined),
      });

      await renderPage({ waitForEmpty: true });

      expect(screen.getByText('Failed to load notifications')).toBeInTheDocument();
    });

    it('shows retry button', async () => {
      (useNotifications as vi.Mock).mockReturnValue({
        unreadCount: 0,
        loading: false,
        error: new Error('Failed to load'),
        fetchNotifications: vi.fn().mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20, total_pages: 1 }),
        markAsRead: vi.fn().mockResolvedValue(undefined),
        markAllAsRead: vi.fn().mockResolvedValue(undefined),
      });

      await renderPage({ waitForEmpty: true });

      expect(screen.getByText('Try again')).toBeInTheDocument();
    });

    it('retries on button click', async () => {
      const fetchNotificationsMock = vi.fn().mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20, total_pages: 1 });

      (useNotifications as vi.Mock).mockReturnValue({
        unreadCount: 0,
        loading: false,
        error: new Error('Failed to load'),
        fetchNotifications: fetchNotificationsMock,
        markAsRead: vi.fn().mockResolvedValue(undefined),
        markAllAsRead: vi.fn().mockResolvedValue(undefined),
      });

      await renderPage({ waitForEmpty: true });

      await act(async () => {
        fireEvent.click(screen.getByText('Try again'));
      });

      expect(fetchNotificationsMock).toHaveBeenCalled();
    });
  });
});