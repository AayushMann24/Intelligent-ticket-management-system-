import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

// Mock the useNotifications hook
vi.mock('../../hooks/useNotifications', () => ({
  useNotifications: vi.fn(),
}));

import { useNotifications } from '../../hooks/useNotifications';
import NotificationDropdown from '../../components/layout/NotificationDropdown';
import type { Notification } from '../../types/notification';

describe('NotificationDropdown', () => {
  const mockNotifications: Notification[] = [
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
  ];

  const mockUseNotifications = {
    notifications: mockNotifications,
    unreadCount: 1,
    loading: false,
    error: null,
    fetchNotifications: vi.fn().mockResolvedValue(undefined),
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

  const renderDropdown = (isOpen = true) => {
    return render(
      <MemoryRouter>
        <NotificationDropdown isOpen={isOpen} onClose={vi.fn()} />
      </MemoryRouter>
    );
  };

  describe('rendering', () => {
    it('does not render when closed', () => {
      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={false} onClose={vi.fn()} />
        </MemoryRouter>
      );
      expect(screen.queryByText('Notifications')).not.toBeInTheDocument();
    });

    it('renders bell icon with unread badge when open', () => {
      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      expect(screen.getByText('Notifications')).toBeInTheDocument();
      expect(screen.getByText('1')).toBeInTheDocument();
    });

    it('shows unread count in header', () => {
      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      expect(screen.getByText('Notifications')).toBeInTheDocument();
      expect(screen.getByText('1')).toBeInTheDocument();
    });

    it('shows mark all read button when unread > 0', () => {
      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      expect(screen.getByText('Mark all read')).toBeInTheDocument();
    });

    it('hides mark all read button when unread = 0', () => {
      (useNotifications as vi.Mock).mockReturnValue({
        ...mockUseNotifications,
        unreadCount: 0,
      });

      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      expect(screen.queryByText('Mark all read')).not.toBeInTheDocument();
    });
  });

  describe('notification list', () => {
    it('renders notifications with correct content', () => {
      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      expect(screen.getByText('Ticket Assigned')).toBeInTheDocument();
      expect(screen.getByText('Ticket #42 assigned to you')).toBeInTheDocument();
      expect(screen.getByText('SLA Breached')).toBeInTheDocument();
      expect(screen.getByText('SLA breached for ticket #43')).toBeInTheDocument();
    });

    it('shows unread indicator for unread notifications', () => {
      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      const unreadDot = screen.getByLabelText('Unread');
      expect(unreadDot).toBeInTheDocument();
    });

    it('does not show unread indicator for read notifications', () => {
      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      const unreadDots = screen.getAllByLabelText('Unread');
      expect(unreadDots).toHaveLength(1);
    });

    it('shows relative time', () => {
      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      expect(screen.getByText('1/1/2024')).toBeInTheDocument();
    });
  });

  describe('mark as read', () => {
    it('marks notification as read on click', async () => {
      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      await act(async () => {
        fireEvent.click(screen.getByText('Ticket Assigned'));
      });

      expect(mockUseNotifications.markAsRead).toHaveBeenCalledWith(1);
    });

    it('calls markAsRead when unread notification clicked', async () => {
      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      await act(async () => {
        fireEvent.click(screen.getByText('Ticket Assigned'));
      });

      expect(mockUseNotifications.markAsRead).toHaveBeenCalledWith(1);
    });
  });

  describe('mark all as read', () => {
    it('calls markAllAsRead when button clicked', async () => {
      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      await act(async () => {
        fireEvent.click(screen.getByText('Mark all read'));
      });

      expect(mockUseNotifications.markAllAsRead).toHaveBeenCalled();
    });
  });

  describe('empty state', () => {
    it('shows empty state when no notifications', () => {
      (useNotifications as vi.Mock).mockReturnValue({
        ...mockUseNotifications,
        notifications: [],
        unreadCount: 0,
      });

      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      expect(screen.getByText('No notifications yet')).toBeInTheDocument();
      expect(screen.getByText('You\'re all caught up!')).toBeInTheDocument();
    });
  });

  describe('error state', () => {
    it('shows error state and retry button', () => {
      (useNotifications as vi.Mock).mockReturnValue({
        ...mockUseNotifications,
        error: new Error('Failed to load'),
        loading: false,
      });

      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      expect(screen.getByText('Failed to load notifications')).toBeInTheDocument();
      expect(screen.getByText('Try again')).toBeInTheDocument();
    });

    it('calls fetchNotifications on retry', async () => {
      (useNotifications as vi.Mock).mockReturnValue({
        ...mockUseNotifications,
        error: new Error('Failed to load'),
        loading: false,
      });

      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      await act(async () => {
        fireEvent.click(screen.getByText('Try again'));
      });

      expect(mockUseNotifications.fetchNotifications).toHaveBeenCalled();
    });
  });

  describe('close behavior', () => {
    it('calls onClose when escape key pressed', async () => {
      const onClose = vi.fn();
      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={onClose} />
        </MemoryRouter>
      );

      await act(async () => {
        fireEvent.keyDown(document, { key: 'Escape' });
      });

      expect(onClose).toHaveBeenCalled();
    });

    it('calls onClose when clicking outside', async () => {
      const onClose = vi.fn();
      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={onClose} />
        </MemoryRouter>
      );

      await act(async () => {
        fireEvent.mouseDown(document.body);
      });

      expect(onClose).toHaveBeenCalled();
    });

    it('does not close when clicking inside dropdown', async () => {
      const onClose = vi.fn();
      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={onClose} />
        </MemoryRouter>
      );

      await act(async () => {
        fireEvent.mouseDown(screen.getByText('Notifications'));
      });

      expect(onClose).not.toHaveBeenCalled();
    });
  });

  describe('footer', () => {
    it('shows view all link when notifications exist', () => {
      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      expect(screen.getByText('View all notifications')).toBeInTheDocument();
    });

    it('hides view all link when no notifications', () => {
      (useNotifications as vi.Mock).mockReturnValue({
        ...mockUseNotifications,
        notifications: [],
      });

      render(
        <MemoryRouter>
          <NotificationDropdown isOpen={true} onClose={vi.fn()} />
        </MemoryRouter>
      );

      expect(screen.queryByText('View all notifications')).not.toBeInTheDocument();
    });
  });
});