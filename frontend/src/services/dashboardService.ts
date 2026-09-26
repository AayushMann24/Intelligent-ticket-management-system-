import api from "./api";
import type {
  DashboardSummary,
  RecentTicket,
  TicketTrend,
  Activity,
} from "../types/dashboard";

// Re-export types for consumers
export type {
  DashboardSummary,
  RecentTicket,
  TicketTrend,
  Activity,
};

// ======================================
// API Calls
// ======================================

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const response = await api.get<DashboardSummary>(
    "/dashboard/summary"
  );

  return response.data;
}

export async function getRecentTickets(): Promise<RecentTicket[]> {
  const response = await api.get<RecentTicket[]>(
    "/dashboard/recent-tickets"
  );

  return response.data;
}

export async function getTicketTrend(): Promise<TicketTrend[]> {
  const response = await api.get<TicketTrend[]>(
    "/dashboard/trend"
  );

  return response.data;
}

export async function getRecentActivity(): Promise<Activity[]> {
  const response = await api.get<Activity[]>(
    "/dashboard/activity"
  );

  return response.data;
}