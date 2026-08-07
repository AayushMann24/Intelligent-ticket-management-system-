import api from "./api";

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
// ======================================

export interface Activity {
  message: string;
  time: string;
}

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
import type {
  LoginData,
  LoginResponse,
} from "../types/auth";

const API = "http://127.0.0.1:8000";

// ======================================
// Login
// ======================================

export async function loginUser(
  data: LoginData
): Promise<LoginResponse> {

  const response = await api.post<LoginResponse>(
    `${API}/auth/login`,
    data
  );

  return response.data;
}

// ======================================
// Register
// ======================================

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  role: string;
}

export async function registerUser(
  data: RegisterData
) {
  const response = await api.post(
    `${API}/auth/register`,
    data
  );

  return response.data;
}