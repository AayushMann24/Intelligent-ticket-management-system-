import { useEffect, useRef, useState } from "react";
import { Check, ExternalLink, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";

import { useNotifications } from "../../hooks/useNotifications";
import { formatRelativeTime } from "../../utils/notificationPresentation";
import { getNotificationPresentation } from "../../utils/notificationPresentation";
import type { Notification } from "../../types/notification";
import { useReducedMotion } from "../../hooks/useReducedMotion";

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
  const reducedMotion = useReducedMotion();

  const {
    notifications,
    unreadCount,
    loading,
    error,
    markAsRead,
    markAllAsRead,
    fetchNotifications,
  } = useNotifications();

  useEffect(() => {
    if (isOpen) {
      fetchNotifications({ page: 1, page_size: 10 });
    }
  }, [isOpen, fetchNotifications]);

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
    if (notification.ticket_id) {
      onClose();
      navigate(`/tickets/${notification.ticket_id}`);
    }
  };

  const handleMarkAllAsRead = async () => {
    await markAllAsRead();
  };

  const itemVariants = {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 },
    transition: { duration: 0.15, ease: [0, 0, 0.2, 1] },
  };

  const containerVariants = {
    initial: { opacity: 0 },
    animate: {
      opacity: 1,
      transition: { staggerChildren: 0.03, delayChildren: 0.05 },
    },
    exit: { opacity: 0 },
  };

  return (
    <motion.div
      ref={dropdownRef}
      className="
        absolute right-0 mt-3 w-96 max-h-[60vh] rounded-xl border border-slate-300 bg-white shadow-2xl
        dark:border-slate-700 dark:bg-slate-900 overflow-hidden
      "
      role="menu"
      initial={false}
      animate={containerVariants.animate}
      exit={containerVariants.exit}
      variants={containerVariants}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700">
        <motion.h3 className="font-semibold text-slate-900 dark:text-white">
          Notifications
          <AnimatePresence>
            {unreadCount > 0 && (
              <motion.span
                key="unread-badge"
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0, opacity: 0 }}
                transition={{ type: "spring", stiffness: 400, damping: 20 }}
                className="ml-2 inline-flex items-center justify-center px-2 py-0.5 text-xs font-medium leading-none text-red-700 bg-red-100 rounded-full dark:bg-red-900 dark:text-red-300"
              >
                {unreadCount}
              </motion.span>
            )}
          </AnimatePresence>
        </motion.h3>
        {unreadCount > 0 && (
          <motion.button
            onClick={handleMarkAllAsRead}
            className="text-xs text-cyan-600 hover:text-cyan-700 dark:text-cyan-400 dark:hover:text-cyan-300 font-medium"
            whileHover={reducedMotion ? {} : { scale: 1.05 }}
            whileTap={reducedMotion ? {} : { scale: 0.95 }}
          >
            Mark all read
          </motion.button>
        )}
      </div>

      {/* Content */}
      <div className="max-h-[50vh] overflow-y-auto">
        {loading && (
          <motion.div
            className="flex h-32 items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            <Loader2 className="h-6 w-6 animate-spin text-cyan-600" />
          </motion.div>
        )}

        {!loading && !hasNotifications && (
          <motion.div
            className="flex flex-col items-center justify-center py-8 px-4 text-center"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, ease: [0, 0, 0.2, 1] }}
          >
            <span className="text-4xl mb-2">🔔</span>
            <p className="text-slate-500 dark:text-slate-400">No notifications yet</p>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">You're all caught up!</p>
          </motion.div>
        )}

        {!loading && hasNotifications && (
          <motion.ul
            className="divide-y divide-slate-200 dark:divide-slate-700"
            role="list"
            variants={containerVariants}
          >
            {notifications.map((notification) => {
              const presentation = getNotificationPresentation(notification.notification_type);
              const isUnread = !notification.is_read;

              return (
                <motion.li
                  key={notification.id}
                  className={`
                    relative p-4 transition-colors
                    ${isUnread ? "bg-blue-50 dark:bg-blue-900/20" : ""}
                    hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer
                  `}
                  role="menuitem"
                  onMouseEnter={() => setHoveredId(notification.id)}
                  onMouseLeave={() => setHoveredId(null)}
                  onClick={() => handleMarkAsRead(notification)}
                  variants={itemVariants}
                >
                  <div className="flex gap-3">
                    {/* Type Icon */}
                    <motion.div
                      className={`
                        flex-shrink-0 flex h-10 w-10 items-center justify-center rounded-lg
                        ${presentation.bgColor}
                        ${isUnread ? "ring-2 ring-offset-2" : ""}
                        ${isUnread ? "ring-cyan-500" : "ring-1"}
                        ${isUnread ? "ring-offset-cyan-500" : `ring-offset-0 ${presentation.borderColor}`}
                      `}
                      whileHover={reducedMotion ? {} : { scale: 1.1 }}
                    >
                      <span className="text-lg" aria-hidden="true">{presentation.icon}</span>
                    </motion.div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0 flex-1">
                          <motion.h4
                            className={`
                              font-medium text-slate-900 dark:text-white truncate
                              ${isUnread ? "font-semibold" : ""}
                            `}
                            animate={isUnread ? { fontWeight: 600 } : {}}
                          >
                            {notification.title}
                          </motion.h4>
                          <motion.p
                            className="mt-1 text-sm text-slate-600 dark:text-slate-400 truncate"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                          >
                            {notification.message}
                          </motion.p>
                          <motion.p
                            className="mt-1 text-xs text-slate-500 dark:text-slate-500"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                          >
                            {formatRelativeTime(notification.created_at)}
                          </motion.p>
                        </div>

                        {/* Actions on hover */}
                        <AnimatePresence>
                          {hoveredId === notification.id && (
                            <motion.div
                              key="actions"
                              initial={{ opacity: 0, x: 10 }}
                              animate={{ opacity: 1, x: 0 }}
                              exit={{ opacity: 0, x: 10 }}
                              transition={{ duration: 0.15 }}
                              className="flex flex-col items-end gap-1"
                            >
                              {isUnread && (
                                <motion.button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    markAsRead(notification.id);
                                  }}
                                  className="p-1.5 rounded-lg text-slate-500 hover:text-cyan-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                                  aria-label="Mark as read"
                                  whileHover={reducedMotion ? {} : { scale: 1.1 }}
                                  whileTap={reducedMotion ? {} : { scale: 0.9 }}
                                >
                                  <Check size={14} />
                                </motion.button>
                              )}
                              {notification.ticket_id && (
                                <motion.button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    navigate(`/tickets/${notification.ticket_id}`);
                                    onClose();
                                  }}
                                  className="p-1.5 rounded-lg text-slate-500 hover:text-cyan-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                                  aria-label="View ticket"
                                  whileHover={reducedMotion ? {} : { scale: 1.1 }}
                                  whileTap={reducedMotion ? {} : { scale: 0.9 }}
                                >
                                  <ExternalLink size={14} />
                                </motion.button>
                              )}
                            </motion.div>
                          )}
                        </AnimatePresence>

                        {/* Unread dot when not hovering */}
                        <AnimatePresence>
                          {hoveredId !== notification.id && isUnread && (
                            <motion.div
                              key="unread-dot"
                              initial={{ scale: 0 }}
                              animate={{ scale: 1 }}
                              exit={{ scale: 0 }}
                              transition={{ type: "spring", stiffness: 400, damping: 20 }}
                              className="flex-shrink-0 h-2.5 w-2.5 rounded-full bg-cyan-500 mt-1.5"
                              aria-label="Unread"
                            />
                          )}
                        </AnimatePresence>
                      </div>
                    </div>
                  </div>
                </motion.li>
              );
            })}
          </motion.ul>
        )}

        {/* Error state */}
        {error && (
          <motion.div
            className="p-4 text-center"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            <p className="text-sm text-red-600 dark:text-red-400">Failed to load notifications</p>
            <motion.button
              onClick={() => fetchNotifications()}
              className="mt-2 text-xs text-cyan-600 hover:underline"
              whileHover={reducedMotion ? {} : { scale: 1.05 }}
            >
              Try again
            </motion.button>
          </motion.div>
        )}
      </div>

      {/* Footer - View all link */}
      {hasNotifications && (
        <motion.div
          className="border-t border-slate-200 dark:border-slate-700 px-4 py-3"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2, delay: 0.1 }}
        >
          <motion.button
            onClick={() => {
              navigate("/notifications");
              onClose();
            }}
            className="flex w-full items-center justify-center gap-2 text-sm text-cyan-600 hover:text-cyan-700 dark:text-cyan-400 dark:hover:text-cyan-300 font-medium"
            whileHover={reducedMotion ? {} : { scale: 1.02 }}
            whileTap={reducedMotion ? {} : { scale: 0.98 }}
          >
            View all notifications
          </motion.button>
        </motion.div>
      )}
    </motion.div>
  );
}