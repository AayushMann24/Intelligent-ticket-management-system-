import type { NotificationType } from "../types/notification";

export interface NotificationPresentation {
  icon: string;
  bgColor: string;
  textColor: string;
  borderColor: string;
  label: string;
}

const notificationPresentations: Record<NotificationType, NotificationPresentation> = {
  TICKET_ASSIGNED: {
    icon: "📋",
    bgColor: "bg-cyan-100 dark:bg-cyan-900/30",
    textColor: "text-cyan-800 dark:text-cyan-200",
    borderColor: "border-cyan-200 dark:border-cyan-800",
    label: "Assigned",
  },
  TICKET_REASSIGNED: {
    icon: "🔄",
    bgColor: "bg-purple-100 dark:bg-purple-900/30",
    textColor: "text-purple-800 dark:text-purple-200",
    borderColor: "border-purple-200 dark:border-purple-800",
    label: "Reassigned",
  },
  SLA_RESPONSE_WARNING: {
    icon: "⏰",
    bgColor: "bg-yellow-100 dark:bg-yellow-900/30",
    textColor: "text-yellow-800 dark:text-yellow-200",
    borderColor: "border-yellow-200 dark:border-yellow-800",
    label: "SLA Response Warning",
  },
  SLA_RESPONSE_BREACHED: {
    icon: "🚨",
    bgColor: "bg-red-100 dark:bg-red-900/30",
    textColor: "text-red-800 dark:text-red-200",
    borderColor: "border-red-200 dark:border-red-800",
    label: "SLA Response Breached",
  },
  SLA_RESOLUTION_WARNING: {
    icon: "⏳",
    bgColor: "bg-orange-100 dark:bg-orange-900/30",
    textColor: "text-orange-800 dark:text-orange-200",
    borderColor: "border-orange-200 dark:border-orange-800",
    label: "SLA Resolution Warning",
  },
  SLA_RESOLUTION_BREACHED: {
    icon: "💥",
    bgColor: "bg-red-200 dark:bg-red-900/40",
    textColor: "text-red-900 dark:text-red-100",
    borderColor: "border-red-300 dark:border-red-700",
    label: "SLA Resolution Breached",
  },
  TICKET_ESCALATED: {
    icon: "⬆️",
    bgColor: "bg-indigo-100 dark:bg-indigo-900/30",
    textColor: "text-indigo-800 dark:text-indigo-200",
    borderColor: "border-indigo-200 dark:border-indigo-800",
    label: "Escalated",
  },
  SYSTEM: {
    icon: "ℹ️",
    bgColor: "bg-slate-100 dark:bg-slate-800",
    textColor: "text-slate-800 dark:text-slate-200",
    borderColor: "border-slate-200 dark:border-slate-700",
    label: "System",
  },
};

export function getNotificationPresentation(
  type: NotificationType
): NotificationPresentation {
  return notificationPresentations[type] ?? notificationPresentations.SYSTEM;
}

export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) {
    return "just now";
  }
  if (diffMins < 60) {
    return `${diffMins}m ago`;
  }
  if (diffHours < 24) {
    return `${diffHours}h ago`;
  }
  if (diffDays < 7) {
    return `${diffDays}d ago`;
  }
  return date.toLocaleDateString();
}