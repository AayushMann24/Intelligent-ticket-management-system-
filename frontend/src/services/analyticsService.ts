import api from "./api";

// ======================================
// Types
// ======================================

export interface TicketOverview {
  total_tickets: number;
  open_tickets: number;
  assigned_tickets: number;
  pending_tickets: number;
  resolved_tickets: number;
  closed_tickets: number;
  unassigned_tickets: number;
  escalated_tickets: number;
}

export interface PriorityCount {
  priority: string;
  count: number;
}

export interface CategoryCount {
  category: string;
  count: number;
}

export interface TicketTypeCount {
  ticket_type: string;
  count: number;
}

export interface SLAResponseMetrics {
  tickets_with_response_sla: number;
  met_count: number;
  breached_count: number;
  compliance_percentage: number;
}

export interface SLAResolutionMetrics {
  tickets_with_resolution_sla: number;
  met_count: number;
  breached_count: number;
  compliance_percentage: number;
}

export interface SLAAnalytics {
  response_sla: SLAResponseMetrics;
  resolution_sla: SLAResolutionMetrics;
  tickets_with_sla: number;
}

export interface EscalationAnalytics {
  total_escalations: number;
  response_sla_escalations: number;
  resolution_sla_escalations: number;
  by_priority: Record<string, number>;
  by_recipient_role: Record<string, number>;
  escalations_over_time: Array<{ date: string; count: number }>;
  currently_escalated_tickets: number;
}

export interface ResponseResolutionTime {
  average_first_response_minutes: number | null;
  average_resolution_minutes: number | null;
  note: string;
}

export interface TechnicianWorkloadItem {
  technician_id: number;
  technician_name: string;
  technician_email: string;
  role: string;
  tickets_currently_assigned: number;
  open_assigned_tickets: number;
  tickets_resolved: number;
  escalations_received: number;
  escalations_initiated: number;
}

export interface TechnicianWorkloadResponse {
  workload: TechnicianWorkloadItem[];
}

export interface TrendPoint {
  period: string;
  tickets_created: number;
  tickets_resolved: number;
  sla_breaches: number;
  escalations: number;
}

export interface TrendResponse {
  granularity: string;
  trends: TrendPoint[];
}

export interface FilteredTicketAnalytics {
  total: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
}

export interface AnalyticsFilters {
  start_date?: string;
  end_date?: string;
  priority?: string;
  category?: string;
  ticket_type?: string;
  assignee_id?: number;
  granularity?: "daily" | "weekly" | "monthly";
}

export interface ComprehensiveDashboard {
  overview: TicketOverview;
  priority: PriorityCount[];
  category: CategoryCount[];
  ticket_type: TicketTypeCount[];
  sla: SLAAnalytics;
  escalations: EscalationAnalytics;
  timing: ResponseResolutionTime;
  technicians: TechnicianWorkloadItem[];
  trends: TrendResponse;
  filtered?: FilteredTicketAnalytics;
}

export interface CategoryCount {
  category: string;
  count: number;
}

export interface TicketTypeCount {
  ticket_type: string;
  count: number;
}

// ======================================
// API Calls
// ======================================

export async function getTicketOverview(): Promise<TicketOverview> {
  const response = await api.get<TicketOverview>("/analytics/overview");
  return response.data;
}

export async function getPriorityAnalytics(): Promise<PriorityCount[]> {
  const response = await api.get<PriorityCount[]>("/analytics/tickets/priority");
  return response.data;
}

export async function getCategoryAnalytics(limit = 20): Promise<CategoryCount[]> {
  const response = await api.get<CategoryCount[]>(
    `/analytics/tickets/category?limit=${limit}`
  );
  return response.data;
}

export async function getTicketTypeAnalytics(): Promise<TicketTypeCount[]> {
  const response = await api.get<TicketTypeCount[]>("/analytics/tickets/type");
  return response.data;
}

export async function getSLAAnalytics(): Promise<SLAAnalytics> {
  const response = await api.get<SLAAnalytics>("/analytics/sla");
  return response.data;
}

export async function getEscalationAnalytics(): Promise<EscalationAnalytics> {
  const response = await api.get<EscalationAnalytics>("/analytics/escalations");
  return response.data;
}

export async function getResponseResolutionTime(): Promise<ResponseResolutionTime> {
  const response = await api.get<ResponseResolutionTime>("/analytics/timing");
  return response.data;
}

export async function getTechnicianWorkload(): Promise<TechnicianWorkloadResponse> {
  const response = await api.get<TechnicianWorkloadResponse>("/analytics/technicians");
  return response.data;
}

export async function getTrends(
  startDate?: string,
  endDate?: string,
  granularity: "daily" | "weekly" | "monthly" = "daily"
): Promise<TrendResponse> {
  const params = new URLSearchParams();
  if (startDate) params.append("start_date", startDate);
  if (endDate) params.append("end_date", endDate);
  params.append("granularity", granularity);
  const response = await api.get<TrendResponse>(`/analytics/trends?${params.toString()}`);
  return response.data;
}

export async function getFilteredTicketAnalytics(
  filters: AnalyticsFilters
): Promise<FilteredTicketAnalytics> {
  const params = new URLSearchParams();
  if (filters.start_date) params.append("start_date", filters.start_date);
  if (filters.end_date) params.append("end_date", filters.end_date);
  if (filters.priority) params.append("priority", filters.priority);
  if (filters.category) params.append("category", filters.category);
  if (filters.ticket_type) params.append("ticket_type", filters.ticket_type);
  if (filters.assignee_id) params.append("assignee_id", String(filters.assignee_id));
  const response = await api.get<FilteredTicketAnalytics>(
    `/analytics/tickets/filtered?${params.toString()}`
  );
  return response.data;
}

export async function getComprehensiveDashboard(
  startDate?: string,
  endDate?: string,
  granularity: "daily" | "weekly" | "monthly" = "daily"
): Promise<ComprehensiveDashboard> {
  const params = new URLSearchParams();
  if (startDate) params.append("start_date", startDate);
  if (endDate) params.append("end_date", endDate);
  params.append("granularity", granularity);
  const response = await api.get<ComprehensiveDashboard>(`/analytics/dashboard?${params.toString()}`);
  return response.data;
}

// ======================================
// Utility Functions
// ======================================

export function formatMinutesToDuration(minutes: number | null): string {
  if (minutes === null || minutes === undefined || isNaN(minutes)) {
    return "N/A";
  }
  const totalMinutes = Math.round(minutes);
  if (totalMinutes < 60) {
    return `${totalMinutes}m`;
  }
  const hours = Math.floor(totalMinutes / 60);
  const remainingMinutes = totalMinutes % 60;
  if (hours < 24) {
    return `${hours}h ${remainingMinutes}m`;
  }
  const days = Math.floor(hours / 24);
  const remainingHours = hours % 24;
  return `${days}d ${remainingHours}h`;
}

export function formatDateForAPI(date: Date): string {
  return date.toISOString().split("T")[0];
}

export function getDateRangePresets(): { label: string; startDate: Date; endDate: Date }[] {
  const now = new Date();
  now.setHours(23, 59, 59, 999);
  
  const last7Days = new Date(now);
  last7Days.setDate(last7Days.getDate() - 6);
  last7Days.setHours(0, 0, 0, 0);

  const last30Days = new Date(now);
  last30Days.setDate(last30Days.getDate() - 29);
  last30Days.setHours(0, 0, 0, 0);

  const last90Days = new Date(now);
  last90Days.setDate(last90Days.getDate() - 89);
  last90Days.setHours(0, 0, 0, 0);

  return [
    { label: "Last 7 days", startDate: last7Days, endDate: now },
    { label: "Last 30 days", startDate: last30Days, endDate: now },
    { label: "Last 90 days", startDate: last90Days, endDate: now },
  ];
}