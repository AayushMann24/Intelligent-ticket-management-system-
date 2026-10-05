import { useEffect, useRef, useState } from "react";
import { Check, ExternalLink, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { useNotifications } from "../../hooks/useNotifications";
import { formatRelativeTime } from "../../utils/notificationPresentation";
import { getNotificationPresentation } from "../../utils/notificationPresentation";
import type { Notification } from "../../types/notification";

interface NotificationDropdownProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function NotificationDropdown({
  isOpen,
  onClose,
}: NotificationDropdownProps) {
  const navigate = useNavigate();
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [hoveredId, setHoveredId] = useState<number | null>(null);

  const {
    notifications,
    unreadCount,
    loading,
    error,
    markAsRead,
    markAllAsRead,
    fetchNotifications,
  } = useNotifications();

  // Load notifications when dropdown opens
  useEffect(() => {
    if (isOpen) {
      fetchNotifications({ page: 1, page_size: 10 });
    }
  }, [isOpen, fetchNotifications]);

  // Close dropdown when clicking outside
  useEffect(() => {
    if (!isOpen) return;

    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        onClose();
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen, onClose]);

  // Handle escape key
  useEffect(() => {
    if (!isOpen) return;

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const hasNotifications = notifications.length > 0;

  const handleMarkAsRead = async (notification: Notification) => {
    if (!notification.is_read) {
      await markAsRead(notification.id);
    }
    // Navigate to ticket if exists
    if (notification.ticket_id) {
      onClose();
      navigate(`/tickets/${notification.ticket_id}`);
    }
  };

  const handleMarkAllAsRead = async () => {
    await markAllAsRead();
  };

  return (
    <div
      ref={dropdownRef}
      className="
        absolute
        right-0
        mt-3
        w-96
        max-h-[60vh]
        rounded-xl
        border
        border-slate-300
        bg-white
        shadow-2xl
        dark:border-slate-700
        dark:bg-slate-900
        overflow-hidden
      "
      role="menu"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700">
        <h3 className="font-semibold text-slate-900 dark:text-white">
          Notifications
          {unreadCount > 0 && (
            <span className="ml-2 inline-flex items-center justify-center px-2 py-0.5 text-xs font-medium leading-none text-red-700 bg-red-100 rounded-full dark:bg-red-900 dark:text-red-300">
              {unreadCount}
            </span>
          )}
        </h3>
        {unreadCount > 0 && (
          <button
            onClick={handleMarkAllAsRead}
            className="text-xs text-cyan-600 hover:text-cyan-700 dark:text-cyan-400 dark:hover:text-cyan-300 font-medium"
          >
            Mark all read
          </button>
        )}
      </div>

      {/* Content */}
      <div className="max-h-[50vh] overflow-y-auto">
        {loading && (
          <div className="flex h-32 items-center justify-center">
            <Loader2 className="h-6 w-6 animate-spin text-cyan-600" />
          </div>
        )}

        {!loading && !hasNotifications && (
          <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
            <span className="text-4xl mb-2">🔔</span>
            <p className="text-slate-500 dark:text-slate-400">
              No notifications yet
            </p>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
              You're all caught up!
            </p>
          </div>
        )}

        {!loading && hasNotifications && (
          <ul className="divide-y divide-slate-200 dark:divide-slate-700" role="list">
            {notifications.map((notification) => {
              const presentation = getNotificationPresentation(
                notification.notification_type
              );
              const isUnread = !notification.is_read;

              return (
                <li
                  key={notification.id}
                  className={`
                    relative
                    p-4
                    transition-colors
                    ${isUnread ? "bg-blue-50 dark:bg-blue-900/20" : ""}
                    hover:bg-slate-50 dark:hover:bg-slate-800/50
                    cursor-pointer
                  `}
                  role="menuitem"
                  onMouseEnter={() => setHoveredId(notification.id)}
                  onMouseLeave={() => setHoveredId(null)}
                  onClick={() => handleMarkAsRead(notification)}
                >
                  <div className="flex gap-3">
                    {/* Type Icon */}
                    <div
                      className={`
                        flex-shrink-0
                        flex h-10 w-10 items-center justify-center rounded-lg
                        ${presentation.bgColor}
                        ${isUnread ? "ring-2 ring-offset-2" : ""}
                        ${isUnread ? "ring-cyan-500" : "ring-1"}
                        ${isUnread
                          ? "ring-offset-cyan-500"
                          : `ring-offset-0 ${presentation.borderColor}`}
                      `}
                    >
                      <span className="text-lg" aria-hidden="true">
                        {presentation.icon}
                      </span>
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0 flex-1">
                          <h4 className={`
                            font-medium text-slate-900 dark:text-white
                            ${isUnread ? "font-semibold" : ""}
                            truncate
                          `}>
                            {notification.title}
                          </h4>
                          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400 truncate">
                            {notification.message}
                          </p>
                          <p className="mt-1 text-xs text-slate-500 dark:text-slate-500">
                            {formatRelativeTime(notification.created_at)}
                          </p>
                        </div>

                        {/* Unread indicator / actions on hover */}
                        {hoveredId === notification.id && (
                          <div className="flex flex-col items-end gap-1">
                            {isUnread && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  markAsRead(notification.id);
                                }}
                                className="
                                  p-1.5
                                  rounded-lg
                                  text-slate-500
                                  hover:text-cyan-600
                                  hover:bg-slate-100
                                  dark:hover:bg-slate-800
                                  transition-colors
                                "
                                aria-label="Mark as read"
                              >
                                <Check size={14} />
                              </button>
                            )}
                            {notification.ticket_id && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  navigate(`/tickets/${notification.ticket_id}`);
                                  onClose();
                                }}
                                className="
                                  p-1.5
                                  rounded-lg
                                  text-slate-500
                                  hover:text-cyan-600
                                  hover:bg-slate-100
                                  dark:hover:bg-slate-800
                                  transition-colors
                                "
                                aria-label="View ticket"
                              >
                                <ExternalLink size={14} />
                              </button>
                            )}
                          </div>
                        )}

                        {/* Unread dot when not hovering */}
                        {hoveredId !== notification.id && isUnread && (
                          <div
                            className="
                              flex-shrink-0
                              h-2.5 w-2.5
                              rounded-full
                              bg-cyan-500
                              mt-1.5
                            "
                            aria-label="Unread"
                          />
                        )}
                      </div>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        )}

        {/* Error state */}
        {error && (
          <div className="p-4 text-center">
            <p className="text-sm text-red-600 dark:text-red-400">
              Failed to load notifications
            </p>
            <button
              onClick={() => fetchNotifications()}
              className="mt-2 text-xs text-cyan-600 hover:underline"
            >
              Try again
            </button>
          </div>
        )}
      </div>

      {/* Footer - View all link */}
      {hasNotifications && (
        <div className="border-t border-slate-200 dark:border-slate-700 px-4 py-3">
          <button
            onClick={() => {
              navigate("/notifications");
              onClose();
            }}
            className="
              flex w-full items-center justify-center gap-2
              text-sm text-cyan-600 hover:text-cyan-700
              dark:text-cyan-400 dark:hover:text-cyan-300
              font-medium
            "
          >
            View all notifications
          </button>
        </div>
      )}
    </div>
  );
}