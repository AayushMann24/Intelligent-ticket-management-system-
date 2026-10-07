import { useEffect, useState, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, Filter } from "lucide-react";

import { useNotifications } from "../hooks/useNotifications";
import { formatRelativeTime } from "../utils/notificationPresentation";
import { getNotificationPresentation } from "../utils/notificationPresentation";
import type { Notification, NotificationType, GetNotificationsParams } from "../types/notification";
import { useReducedMotion } from "../hooks/useReducedMotion";

const NOTIFICATION_TYPES: NotificationType[] = [
  "TICKET_ASSIGNED",
  "TICKET_REASSIGNED",
  "SLA_RESPONSE_WARNING",
  "SLA_RESPONSE_BREACHED",
  "SLA_RESOLUTION_WARNING",
  "SLA_RESOLUTION_BREACHED",
  "TICKET_ESCALATED",
  "SYSTEM",
];

const itemVariants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
  transition: { duration: 0.15, ease: [0, 0, 0.2, 1] },
};

const containerVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { staggerChildren: 0.03, delayChildren: 0.05 } },
  exit: { opacity: 0 },
};

export default function NotificationsCenterPage() {
  const navigate = useNavigate();
  const reducedMotion = useReducedMotion();

  const {
    unreadCount,
    loading,
    error,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
  } = useNotifications();

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState<GetNotificationsParams>({
    unread_only: false,
    sort_by: "created_at",
    sort_order: "desc",
  });
  const [showFilters, setShowFilters] = useState(false);
  const [selectedType, setSelectedType] = useState<NotificationType | null>(null);

  const loadNotifications = useCallback(
    async (page: number) => {
      const params: GetNotificationsParams = {
        page,
        page_size: 20,
        ...filters,
      };
      if (selectedType) {
        params.notification_type = selectedType;
      }
      try {
        const response = await fetchNotifications(params);
        if (response) {
          setNotifications(response.items);
          setTotalPages(response.total_pages);
        }
      } catch {
        // Error handled by hook
      }
    },
    [fetchNotifications, filters, selectedType]
  );

  const initialLoadRef = useRef(true);

  useEffect(() => {
    if (initialLoadRef.current) {
      initialLoadRef.current = false;
      loadNotifications(1);
    }
  }, [loadNotifications]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    loadNotifications(page);
  };

  const handleFilterChange = (newFilters: Partial<GetNotificationsParams>) => {
    setFilters((prev: GetNotificationsParams) => ({ ...prev, ...newFilters }));
    setCurrentPage(1);
  };

  const handleTypeFilterChange = (type: NotificationType | null) => {
    setSelectedType(type);
    setCurrentPage(1);
  };

  const handleMarkAsRead = async (notification: Notification) => {
    if (!notification.is_read) {
      await markAsRead(notification.id);
    }
    if (notification.ticket_id) {
      navigate(`/tickets/${notification.ticket_id}`);
    }
  };

  const handleMarkAllAsRead = async () => {
    await markAllAsRead();
  };

  const handleClearFilters = () => {
    setFilters({
      unread_only: false,
      sort_by: "created_at",
      sort_order: "desc",
    });
    setSelectedType(null);
    setCurrentPage(1);
  };

  const hasActiveFilters =
    filters.unread_only ||
    selectedType ||
    filters.sort_by !== "created_at" ||
    filters.sort_order !== "desc";

  return (
    <motion.div
      className="flex-1 p-6 space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: [0, 0, 0.2, 1] }}
    >
      {/* Header */}
      <motion.div
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div>
          <motion.h1
            className="text-2xl font-bold text-slate-900 dark:text-white"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            Notifications
          </motion.h1>
          <motion.p
            className="mt-1 text-slate-500 dark:text-slate-400"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: 0.05 }}
          >
            Manage and view your notifications
          </motion.p>
        </div>

        <motion.div className="flex flex-wrap items-center gap-3" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.3, delay: 0.1 }}>
          {unreadCount > 0 && (
            <motion.button
              onClick={handleMarkAllAsRead}
              className="px-4 py-2 rounded-lg bg-cyan-600 text-white font-medium hover:bg-cyan-700 transition-colors"
              whileHover={reducedMotion ? {} : { scale: 1.02 }}
              whileTap={reducedMotion ? {} : { scale: 0.98 }}
            >
              Mark all as read
            </motion.button>
          )}

          <motion.button
            onClick={() => setShowFilters(!showFilters)}
            className={`
              px-4 py-2 rounded-lg border bg-white font-medium text-slate-700 hover:bg-slate-50
              dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700
              ${hasActiveFilters ? "ring-2 ring-cyan-500 border-cyan-500" : ""}
            `}
            whileHover={reducedMotion ? {} : { scale: 1.02 }}
            whileTap={reducedMotion ? {} : { scale: 0.98 }}
          >
            <Filter className="w-4 h-4 mr-1" />
            Filters
            <AnimatePresence>
              {hasActiveFilters && (
                <motion.span
                  key="filter-badge"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0 }}
                  transition={{ type: "spring", stiffness: 400, damping: 20 }}
                  className="ml-1 inline-flex items-center justify-center px-1.5 py-0.5 text-xs font-medium leading-none text-cyan-700 bg-cyan-100 rounded-full dark:bg-cyan-900 dark:text-cyan-300"
                >
                  *
                </motion.span>
              )}
            </AnimatePresence>
          </motion.button>
        </motion.div>
      </motion.div>

      {/* Filters */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            key="filters"
            className="p-4 rounded-xl border bg-slate-50 dark:border-slate-700 dark:bg-slate-800/50"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
          >
            <motion.div className="grid grid-cols-1 md:grid-cols-4 gap-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ staggerChildren: 0.05, delayChildren: 0.1 }}>
              <motion.div variants={itemVariants}>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Status</label>
                <select
                  value={filters.unread_only ? "unread" : "all"}
                  onChange={(e) => handleFilterChange({ unread_only: e.target.value === "unread" })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-cyan-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                >
                  <option value="all">All</option>
                  <option value="unread">Unread only</option>
                </select>
              </motion.div>

              <motion.div variants={itemVariants}>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Type</label>
                <select
                  value={selectedType ?? ""}
                  onChange={(e) => handleTypeFilterChange(e.target.value as NotificationType | null)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-cyan-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                >
                  <option value="">All types</option>
                  {NOTIFICATION_TYPES.map((type) => {
                    const p = getNotificationPresentation(type);
                    return (
                      <option key={type} value={type}>
                        {p.icon} {p.label}
                      </option>
                    );
                  })}
                </select>
              </motion.div>

              <motion.div variants={itemVariants}>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Sort by</label>
                <select
                  value={filters.sort_by}
                  onChange={(e) => handleFilterChange({ sort_by: e.target.value as GetNotificationsParams["sort_by"] })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-cyan-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                >
                  <option value="created_at">Date</option>
                  <option value="notification_type">Type</option>
                  <option value="is_read">Read status</option>
                </select>
              </motion.div>

              <motion.div variants={itemVariants}>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Order</label>
                <select
                  value={filters.sort_order}
                  onChange={(e) => handleFilterChange({ sort_order: e.target.value as "asc" | "desc" })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-cyan-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                >
                  <option value="desc">Newest first</option>
                  <option value="asc">Oldest first</option>
                </select>
              </motion.div>
            </motion.div>

            {hasActiveFilters && (
              <motion.div
                className="mt-4 pt-4 border-t border-slate-300 dark:border-slate-700"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: 0.2 }}
              >
                <motion.button
                  onClick={handleClearFilters}
                  className="text-sm text-cyan-600 hover:text-cyan-700 dark:text-cyan-400 dark:hover:text-cyan-300 font-medium"
                  whileHover={reducedMotion ? {} : { scale: 1.02 }}
                >
                  Clear all filters
                </motion.button>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Notifications List */}
      <motion.div
        className="rounded-xl border border-slate-300 bg-white dark:border-slate-700 dark:bg-slate-900 overflow-hidden"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        {loading && notifications.length === 0 && (
          <motion.div
            className="flex h-48 items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            <Loader2 className="h-8 w-8 animate-spin text-cyan-600" />
          </motion.div>
        )}

        {!loading && notifications.length === 0 && (
          <motion.div
            className="flex flex-col items-center justify-center py-16 px-4 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <span className="text-5xl mb-3">🔔</span>
            <motion.h3
              className="text-lg font-medium text-slate-900 dark:text-white mb-1"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
            >
              No notifications
            </motion.h3>
            <motion.p
              className="text-slate-500 dark:text-slate-400"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.05 }}
            >
              {filters.unread_only ? "No unread notifications. You're all caught up!" : "No notifications yet."}
            </motion.p>
          </motion.div>
        )}

        {!loading && notifications.length > 0 && (
          <motion.div
            className="divide-y divide-slate-200 dark:divide-slate-700"
            variants={containerVariants}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            {notifications.map((notification) => {
              const presentation = getNotificationPresentation(notification.notification_type);
              const isUnread = !notification.is_read;

              return (
                <motion.div
                  key={notification.id}
                  className={`
                    p-4 transition-colors cursor-pointer
                    ${isUnread ? "bg-blue-50 dark:bg-blue-900/20" : ""}
                    hover:bg-slate-50 dark:hover:bg-slate-800/50
                  `}
                  onClick={() => handleMarkAsRead(notification)}
                  variants={itemVariants}
                >
                  <div className="flex gap-4">
                    {/* Type Icon */}
                    <motion.div
                      className={`
                        flex-shrink-0 flex h-12 w-12 items-center justify-center rounded-lg
                        ${presentation.bgColor}
                        ${isUnread ? "ring-2 ring-cyan-500" : ""}
                      `}
                      whileHover={reducedMotion ? {} : { scale: 1.05 }}
                    >
                      <span className="text-xl" aria-hidden="true">{presentation.icon}</span>
                    </motion.div>

                    {/* Content */}
                    <motion.div className="flex-1 min-w-0" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                      <div className="flex items-start justify-between gap-4">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-3 flex-wrap">
                            <motion.h4
                              className={`
                                font-medium text-slate-900 dark:text-white
                                ${isUnread ? "font-semibold" : ""}
                              `}
                              animate={isUnread ? { fontWeight: 600 } : {}}
                            >
                              {notification.title}
                            </motion.h4>
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${presentation.bgColor} ${presentation.textColor}`}>
                              {presentation.icon} {presentation.label}
                            </span>
                          </div>
                          <motion.p className="mt-1 text-sm text-slate-600 dark:text-slate-400" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.05 }}>
                            {notification.message}
                          </motion.p>
                          <motion.div className="mt-2 flex items-center gap-4 text-xs text-slate-500 dark:text-slate-500" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
                            <span>{formatRelativeTime(notification.created_at)}</span>
                            {notification.ticket_id && (
                              <span className="text-cyan-600 hover:underline cursor-pointer">Ticket #{notification.ticket_id}</span>
                            )}
                          </motion.div>
                        </div>

                        <motion.div
                          className="flex flex-col items-end gap-2 flex-shrink-0"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                        >
                          <AnimatePresence>
                            {isUnread && (
                              <motion.div
                                key="unread-dot"
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                exit={{ scale: 0 }}
                                transition={{ type: "spring", stiffness: 400, damping: 20 }}
                                className="w-2.5 h-2.5 rounded-full bg-cyan-500"
                                aria-label="Unread"
                              />
                            )}
                          </AnimatePresence>
                        </motion.div>
                      </div>
                    </motion.div>
                  </div>
                </motion.div>
              );
            })}
          </motion.div>
        )}

        {/* Error state */}
        <AnimatePresence>
          {error && !loading && (
            <motion.div
              key="error"
              className="p-6 text-center"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
            >
              <motion.p className="text-red-600 dark:text-red-400 mb-2" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                Failed to load notifications
              </motion.p>
              <motion.button
                onClick={() => loadNotifications(currentPage)}
                className="px-4 py-2 text-sm text-cyan-600 hover:text-cyan-700 dark:text-cyan-400 dark:hover:text-cyan-300 font-medium"
                whileHover={reducedMotion ? {} : { scale: 1.02 }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                Try again
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Pagination */}
      {totalPages > 1 && (
        <motion.div
          className="flex items-center justify-center gap-2 px-4 py-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          <motion.button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className={`
              px-3 py-1.5 rounded-lg text-sm font-medium transition-colors
              ${currentPage === 1
                ? "text-slate-400 cursor-not-allowed"
                : "text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"}
            `}
            whileHover={reducedMotion || currentPage === 1 ? {} : { scale: 1.02 }}
            whileTap={reducedMotion || currentPage === 1 ? {} : { scale: 0.98 }}
          >
            Previous
          </motion.button>

          <motion.span
            className="px-3 text-sm text-slate-600 dark:text-slate-400"
            key={currentPage}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
          >
            Page {currentPage} of {totalPages}
          </motion.span>

          <motion.button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage >= totalPages}
            className={`
              px-3 py-1.5 rounded-lg text-sm font-medium transition-colors
              ${currentPage >= totalPages
                ? "text-slate-400 cursor-not-allowed"
                : "text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"}
            `}
            whileHover={reducedMotion || currentPage >= totalPages ? {} : { scale: 1.02 }}
            whileTap={reducedMotion || currentPage >= totalPages ? {} : { scale: 0.98 }}
          >
            Next
          </motion.button>
        </motion.div>
      )}
    </motion.div>
  );
}