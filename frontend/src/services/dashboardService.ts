import axios from "axios";

const API = "http://127.0.0.1:8000";

const getToken = () => localStorage.getItem("token");

const authHeaders = () => ({
  headers: {
    Authorization: `Bearer ${getToken()}`,
  },
});

// ======================================
// Dashboard Summary
// ======================================

export interface DashboardSummary {
  total_tickets: number;
  open_tickets: number;
  assigned_tickets: number;
  resolved_tickets: number;

  high_priority: number;
  medium_priority: number;
  low_priority: number;
}

// ======================================
// Recent Tickets
// ======================================

export interface RecentTicket {
  id: number;
  title: string;
  status: string;
  priority: string;
  assigned_to: string;
  created_at: string;
}

// ======================================
// Ticket Trend
// ======================================

export interface TicketTrend {
  date: string;
  tickets: number;
}

// ======================================
// Activity
// (Matches your backend response)
// ======================================

export interface Activity {
  message: string;
  time: string;
}

// ======================================
// API Calls
// ======================================

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const response = await axios.get<DashboardSummary>(
    `${API}/dashboard/summary`,
    authHeaders()
  );

  return response.data;
}

export async function getRecentTickets(): Promise<RecentTicket[]> {
  const response = await axios.get<RecentTicket[]>(
    `${API}/dashboard/recent-tickets`,
    authHeaders()
  );

  return response.data;
}

export async function getTicketTrend(): Promise<TicketTrend[]> {
  const response = await axios.get<TicketTrend[]>(
    `${API}/dashboard/trend`,
    authHeaders()
  );

  return response.data;
}

export async function getRecentActivity(): Promise<Activity[]> {
  const response = await axios.get<Activity[]>(
    `${API}/dashboard/activity`,
    authHeaders()
  );

  return response.data;
}