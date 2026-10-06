import api from "./api";

// ======================================
// Types
// ======================================

export interface ReportFilters {
  start_date?: string;
  end_date?: string;
  priority?: string;
  category?: string;
  ticket_type?: string;
  assignee_id?: number;
  status?: string;
  breach_type?: string;
}

export interface ReportMetadata {
  type: string;
  name: string;
  description: string;
  filters: string[];
  endpoints: {
    json: string;
    csv: string;
  };
}

export interface ReportListResponse {
  reports: ReportMetadata[];
}

// Ticket Report
export interface TicketReportSummary {
  total_tickets: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  by_ticket_type: Record<string, number>;
}

export interface TicketReportResponse {
  report_type: string;
  filters: ReportFilters;
  summary: TicketReportSummary;
}

// SLA Report
export interface SLAReportSummary {
  response_sla: {
    total: number;
    met: number;
    breached: number;
    pending: number;
    compliance_percentage: number;
  };
  resolution_sla: {
    total: number;
    met: number;
    breached: number;
    pending: number;
    compliance_percentage: number;
  };
  by_priority: Record<string, {
    response: { total: number; met: number; breached: number; compliance: number };
    resolution: { total: number; met: number; breached: number; compliance: number };
  }>;
}

export interface SLAReportResponse {
  report_type: string;
  filters: ReportFilters;
  summary: SLAReportSummary;
}

// Escalation Report
export interface EscalationReportSummary {
  total_escalations: number;
  by_event_type: Record<string, number>;
  by_priority: Record<string, number>;
  by_recipient_role: Record<string, number>;
  escalations_over_time: Array<{ date: string; count: number }>;
}

export interface EscalationReportResponse {
  report_type: string;
  filters: ReportFilters;
  summary: EscalationReportSummary;
}

// Technician Report
export interface TechnicianReportSummary {
  total_technicians: number;
  total_assigned: number;
  total_open: number;
  total_resolved: number;
  total_escalations_received: number;
  total_escalations_initiated: number;
  total_response_breached: number;
  total_resolution_breached: number;
}

export interface TechnicianReportResponse {
  report_type: string;
  filters: ReportFilters;
  summary: TechnicianReportSummary;
}

// ======================================
// API Calls
// ======================================

function buildParams(filters: ReportFilters): URLSearchParams {
  const params = new URLSearchParams();
  if (filters.start_date) params.append("start_date", filters.start_date);
  if (filters.end_date) params.append("end_date", filters.end_date);
  if (filters.priority) params.append("priority", filters.priority);
  if (filters.category) params.append("category", filters.category);
  if (filters.ticket_type) params.append("ticket_type", filters.ticket_type);
  if (filters.assignee_id) params.append("assignee_id", String(filters.assignee_id));
  if (filters.status) params.append("status", filters.status);
  if (filters.breach_type) params.append("breach_type", filters.breach_type);
  return params;
}

export async function getReportList(): Promise<ReportListResponse> {
  const response = await api.get<ReportListResponse>("/reports/");
  return response.data;
}

// Ticket Report
export async function getTicketReport(filters: ReportFilters = {}): Promise<TicketReportResponse> {
  const params = buildParams(filters);
  const response = await api.get<TicketReportResponse>(`/reports/tickets?${params.toString()}`);
  return response.data;
}

export async function exportTicketReport(filters: ReportFilters = {}): Promise<Blob> {
  const params = buildParams(filters);
  const response = await api.get(`/reports/tickets/export?${params.toString()}`, {
    responseType: "blob",
  });
  return response.data;
}

// SLA Report
export async function getSLAReport(filters: ReportFilters = {}): Promise<SLAReportResponse> {
  const params = buildParams(filters);
  const response = await api.get<SLAReportResponse>(`/reports/sla?${params.toString()}`);
  return response.data;
}

export async function exportSLAReport(filters: ReportFilters = {}): Promise<Blob> {
  const params = buildParams(filters);
  const response = await api.get(`/reports/sla/export?${params.toString()}`, {
    responseType: "blob",
  });
  return response.data;
}

// SLA Breach Report
export async function getSLABreachReport(filters: ReportFilters = {}): Promise<SLAReportResponse> {
  const params = buildParams(filters);
  const response = await api.get<SLAReportResponse>(`/reports/sla/breaches?${params.toString()}`);
  return response.data;
}

export async function exportSLABreachReport(filters: ReportFilters = {}): Promise<Blob> {
  const params = buildParams(filters);
  const response = await api.get(`/reports/sla/breaches/export?${params.toString()}`, {
    responseType: "blob",
  });
  return response.data;
}

// Escalation Report
export async function getEscalationReport(filters: ReportFilters = {}): Promise<EscalationReportResponse> {
  const params = buildParams(filters);
  const response = await api.get<EscalationReportResponse>(`/reports/escalations?${params.toString()}`);
  return response.data;
}

export async function exportEscalationReport(filters: ReportFilters = {}): Promise<Blob> {
  const params = buildParams(filters);
  const response = await api.get(`/reports/escalations/export?${params.toString()}`, {
    responseType: "blob",
  });
  return response.data;
}

// Technician Report
export async function getTechnicianReport(filters: ReportFilters = {}): Promise<TechnicianReportResponse> {
  const params = buildParams(filters);
  const response = await api.get<TechnicianReportResponse>(`/reports/technicians?${params.toString()}`);
  return response.data;
}

export async function exportTechnicianReport(filters: ReportFilters = {}): Promise<Blob> {
  const params = buildParams(filters);
  const response = await api.get(`/reports/technicians/export?${params.toString()}`, {
    responseType: "blob",
  });
  return response.data;
}

// ======================================
// Utility Functions
// ======================================

export function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

export function getReportFilename(reportType: string, filters: ReportFilters): string {
  const now = new Date();
  const dateStr = now.toISOString().split("T")[0].replace(/-/g, "");
  const timeStr = now.toTimeString().split(" ")[0].replace(/:/g, "");
  const dateRange = filters.start_date || filters.end_date
    ? `_${(filters.start_date || "start").replace(/-/g, "")}_to_${(filters.end_date || "end").replace(/-/g, "")}`
    : "";
  return `${reportType}_report${dateRange}_${dateStr}_${timeStr}.csv`;
}