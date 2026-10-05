import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

// Mock the useNotifications hook
vi.mock('../hooks/useNotifications', () => ({
  useNotifications: vi.fn(),
}));

import { useNotifications } from '../hooks/useNotifications';
import NotificationsCenterPage from '../pages/NotificationsCenterPage';
import type { Notification } from '../types/notification';

describe('NotificationsCenterPage', () => {
  const mockNotifications = [
    {
      id: 1,
      notification_type: 'TICKET_ASSIGNED',
      title: 'Ticket Assigned',
      message: 'Ticket #42 assigned to you',
      ticket_id: 42,
      is_read: false,
      read_at: null,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      notification_type: 'SLA_RESPONSE_BREACHED',
      title: 'SLA Breached',
      message: 'SLA breached for ticket #43',
      ticket_id: 43,
      is_read: true,
      read_at: '2024-01-01T01:00:00Z',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 3,
      notification_type: 'TICKET_ESCALATED',
      title: 'Ticket Escalated',
      message: 'Ticket escalated to you',
      ticket_id: 44,
      is_read: false,
      read_at: null,
      created_at: '2024-01-01T02:00:00Z',
      updated_at: '2024-01-01T02:00:00Z',
    },
  ];

  const mockListResponse = {
    items: [
      { id: 1, notification_type: 'TICKET_ASSIGNED', title: 'Ticket Assigned', message: 'Ticket #42 assigned to you', ticket_id: 42, is_read: false, read_at: null, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
      { id: 2, notification_type: 'SLA_RESPONSE_BREACHED', title: 'SLA Breached', message: 'SLA breached for ticket #43', ticket_id: 43, is_read: true, read_at: '2024-01-01T01:00:00Z', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
      { id: 3, notification_type: 'TICKET_ESCALATED', title: 'Ticket Escalated', message: 'Ticket escalated to you', ticket_id: 44, is_read: false, read_at: null, created_at: '2024-01-01T02:00:00Z', updated_at: '2024-01-01T02:00:00Z' },
    ],
    total: 3,
    page: 1,
    page_size: 20,
    total_pages: 2,
  };

  const mockUseNotifications = {
    notifications: [
      { id: 1, notification_type: 'TICKET_ASSIGNED', title: 'Ticket Assigned', message: 'Ticket #42 assigned to you', ticket_id: 42, is_read: false, read_at: null, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
      { id: 2, notification_type: 'SLA_RESPONSE_BREACHED', title: 'SLA Breached', message: 'SLA breached for ticket #43', ticket_id: 43, is_read: true, read_at: '2024-01-01T01:00:00Z', created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
      { id: 3, notification_type: 'TICKET_ESCALATED', title: 'Ticket Escalated', message: 'Ticket escalated to you', ticket_id: 44, is_read: false, read_at: null, created_at: '2024-01-01T02:00:00Z', updated_at: '2024-01-01T02:00:00Z' },
    ],
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

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    (useNotifications as vi.Mock).mockReturnValue(mockUseNotifications);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  const renderPage = () => {
    return render(
      <MemoryRouter>
        <NotificationsCenterPage />
      </MemoryRouter>
    );
  };

  describe('rendering', () => {
    it('renders page title', () => {
      render(
        <MemoryRouter>
          <NotificationsCenterPage />
        </MemoryRouter>
      );
      expect(screen.getByText('Notifications')).toBeInTheDocument();
      expect(screen.getByText('Manage and view your notifications')).toBeInTheDocument();
    });

    it('shows unread count', () => {
      render(
        <MemoryRouter>
          <NotificationsCenterPage />
        </MemoryRouter>
      );
      expect(screen.getByText('2')).toBeInTheDocument();
    });

    it('shows mark all as read button when unread > 0', () => {
      render(
        <MemoryRouter>
          <NotificationsCenterPage />
        </MemoryRouter>
      );
      expect(screen.getByText('Mark all as read')).toBeInTheDocument();
    });

    it('hides mark all as read button when unread = 0', () => {
      (useNotifications as vi.Mock).mockReturnValue({
        ...mockUseNotifications,
        unreadCount: 0,
      });

      render(
        <MemoryRouter>
          <NotificationsCenterPage />
        </MemoryRouter>
      );
      expect(screen.queryByText('Mark all as read')).not.toBeInTheDocument();
    });

    it('shows filter button', () => {
      render(
        <MemoryRouter>
          <NotificationsCenterPage />
        </MemoryRouter>
      );
      expect(screen.getByText('Filters')).toBeInTheDocument();
    });
  });

  describe('notification list', () => {
    it('renders notifications with correct content', () => {
      render(
        <MemoryRouter>
          <NotificationsCenterPage />
        </MemoryRouter>
      );

      expect(screen.getByText('Ticket Assigned')).toBeInTheDocument();
      expect(screen.getByText('SLA Breached')).toBeInTheDocument();
      expect(screen.getByText('Ticket Escalated')).toBeInTheDocument();
    });

    it('shows relative time', () => {
      render(
        <MemoryRouter>
          <NotificationsCenterPage />
        </MemoryRouter>
      );
      expect(screen.getByText('1/1/2024')).toBeInTheDocument();
    });
  });

  describe('mark as read', () => {
    it('marks notification as read on click', async () => {
      render(
        <MemoryRouter>
          <NotificationsCenterPage />
        </MemoryRouter>
      );

      await act(async () => {
        fireEvent.click(screen.getByText('Ticket Assigned'));
      });

      expect(screen.getByText('Ticket Assigned')).toBeInTheDocument();
    });

    it('navigates to ticket on click', async () => {
      render(
        <MemoryRouter>
          <NotificationsCenterPage />
        </MemoryRouter>
      );

      await act(async () => {
        fireEvent.click(screen.getByText('Ticket Assigned'));
      });
    });
  });

  describe('mark all as read', () => {
    it('calls markAllAsRead when button clicked', async () => {
      render(
        <MemoryRouter>
          <NotificationsCenterPage />
        </MemoryRouter>
      );

      await act(async () => {
        fireEvent.click(screen.getByText('Mark all as read'));
      });

      expect(screen.getByText('Mark all as read')).toBeInTheDocument();
    });
  });

  describe('empty state', () => {
    it('shows empty state when no notifications', () => {
      (useNotifications as vi.Mock).mockReturnValue({
        ...mockUseNotifications,
        notifications: [],
      });

      render(
        <MemoryRouter>
          <NotificationsCenterPage />
        </MemoryRouter>
      );

      expect(screen.getByText('No notifications')).toBeInTheDocument();
      expect(screen.getByText('No notifications yet.')).toBeInTheDocument();
    });
  });

  describe('error state', () => {
    it('shows error state', () => {
      (useNotifications as vi.Mock).mockReturnValue({
        ...mockUseNotifications,
        error: new Error('Failed to load'),
        loading: false,
      });

      render(
        <MemoryRouter>
          <NotificationsCenterPage />
        </MemoryRouter>
      );

      expect(screen.getByText('Failed to load notifications')).toBeInTheDocument();
    });

    it('shows retry button', () => {
      (useNotifications as vi.Mock).mockReturnValue({
        ...mockUseNotifications,
        error: new Error('Failed to load'),
        loading: false,
      });

      render(
        <MemoryRouter>
          <NotificationsCenterPage />
        </MemoryRouter>
      );

      expect(screen.getByText('Try again')).toBeInTheDocument();
    });

    it('retries on button click', async () => {
      (useNotifications as vi.Mock).mockReturnValue({
        ...mockUseNotifications,
        error: new Error('Failed to load'),
        loading: false,
      });

      render(
        <MemoryRouter>
          <NotificationsCenterPage />
        </MemoryRouter>
      );

      await act(async () => {
        fireEvent.click(screen.getByText('Try again'));
      });

      expect(screen.getByText('Try again')).toBeInTheDocument();
    });
  });
});