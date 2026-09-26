import api from "./api";
import type { 
  TicketCommentListResponse, 
  TimelineResponse, 
  TicketAttachmentListResponse, 
  TicketComment, 
  TicketAttachment, 
  CommentPayload,
  WorkflowActions,
  SLAPolicy,
  TicketSLA,
} from "../types/ticket";

// ======================================
// Types
// ======================================
export interface TicketPayload {
  title: string;
  description: string;
  priority: string;
  ticket_type?: string;
}

export interface TicketUpdatePayload {
  title: string;
  description: string;
  priority: string;
  status: string;
  assigned_to: number | null;
  ticket_type?: string;
}

// ======================================
// Get All Tickets
// ======================================
export async function getAllTickets(params?: {
  page?: number;
  page_size?: number;
  status?: string;
  priority?: string;
  ticket_type?: string;
  search?: string;
  sort_by?: string;
  sort_order?: string;
}) {
  const response = await api.get("/tickets", { params });
  return response.data;
}

// ======================================
// Create Ticket
// ======================================
export async function createTicket(
  ticket: TicketPayload
) {
  const response = await api.post("/tickets", ticket);
  return response.data;
}

// ======================================
// Update Ticket
// ======================================
export async function updateTicket(
  ticketId: number,
  ticket: TicketUpdatePayload
) {
  const response = await api.put(`/tickets/${ticketId}`, ticket);
  return response.data;
}

// ======================================
// Delete Ticket
// ======================================
export async function deleteTicket(
  ticketId: number
) {
  const response = await api.delete(`/tickets/${ticketId}`);
  return response.data;
}

// ======================================
// WORKFLOW ENDPOINTS (Phase 2B)
// ======================================

// --- Assign Ticket ---
export async function assignTicket(
  ticketId: number,
  assignedTo: number
) {
  const response = await api.put(
    `/tickets/${ticketId}/assign`,
    { assigned_to: assignedTo }
  );
  return response.data;
}

// --- Reassign Ticket ---
export async function reassignTicket(
  ticketId: number,
  assignedTo: number
) {
  const response = await api.put(
    `/tickets/${ticketId}/reassign`,
    { assigned_to: assignedTo }
  );
  return response.data;
}

// --- Unassign Ticket ---
export async function unassignTicket(
  ticketId: number
) {
  const response = await api.post(
    `/tickets/${ticketId}/unassign`,
    {}
  );
  return response.data;
}

// --- Start Work ---
export async function startWork(
  ticketId: number
) {
  const response = await api.post(
    `/tickets/${ticketId}/start-work`,
    {}
  );
  return response.data;
}

// --- Mark Pending ---
export async function markPending(
  ticketId: number
) {
  const response = await api.post(
    `/tickets/${ticketId}/mark-pending`,
    {}
  );
  return response.data;
}

// --- Resolve Ticket ---
export async function resolveTicket(
  ticketId: number,
  resolutionSummary: string
) {
  const response = await api.post(
    `/tickets/${ticketId}/resolve`,
    { resolution_summary: resolutionSummary }
  );
  return response.data;
}

// --- Reopen Ticket ---
export async function reopenTicket(
  ticketId: number,
  reason?: string
) {
  const response = await api.post(
    `/tickets/${ticketId}/reopen`,
    { reason }
  );
  return response.data;
}

// --- Close Ticket ---
export async function closeTicket(
  ticketId: number
) {
  const response = await api.post(
    `/tickets/${ticketId}/close`,
    {}
  );
  return response.data;
}

// --- Escalate Ticket ---
export async function escalateTicket(
  ticketId: number,
  escalatedTo: number,
  escalationReason: string
) {
  const response = await api.post(
    `/tickets/${ticketId}/escalate`,
    { escalated_to: escalatedTo, escalation_reason: escalationReason }
  );
  return response.data;
}

// --- Get Workflow Actions ---
export async function getWorkflowActions(
  ticketId: number
): Promise<WorkflowActions> {
  const response = await api.get<WorkflowActions>(
    `/tickets/${ticketId}/workflow-actions`
  );
  return response.data;
}

// ======================================
// Update Ticket Status (Legacy)
// ======================================
export async function updateTicketStatus(
  ticketId: number,
  status: string
) {
  const response = await api.patch(
    `/tickets/${ticketId}/status`,
    { status }
  );
  return response.data;
}

// ======================================
// Comments
// ======================================
export async function getComments(
  ticketId: number,
  params?: { page?: number; page_size?: number; include_internal?: boolean }
) {
  const response = await api.get<TicketCommentListResponse>(`/tickets/${ticketId}/comments`, { params });
  return response.data;
}

export async function createComment(
  ticketId: number,
  comment: CommentPayload
) {
  const response = await api.post<TicketComment>(`/tickets/${ticketId}/comments`, comment);
  return response.data;
}

export async function updateComment(
  ticketId: number,
  commentId: number,
  comment: { body?: string; is_internal?: boolean }
) {
  const response = await api.put<TicketComment>(`/tickets/${ticketId}/comments/${commentId}`, comment);
  return response.data;
}

export async function deleteComment(
  ticketId: number,
  commentId: number
) {
  const response = await api.delete(`/tickets/${ticketId}/comments/${commentId}`);
  return response.data;
}

// ======================================
// History & Timeline
// ======================================
export async function getHistory(
  ticketId: number,
  params?: { page?: number; page_size?: number }
) {
  const response = await api.get(`/tickets/${ticketId}/history`, { params });
  return response.data;
}

export async function getTimeline(
  ticketId: number,
  params?: { page?: number; page_size?: number }
) {
  const response = await api.get<TimelineResponse>(`/tickets/${ticketId}/timeline`, { params });
  return response.data;
}

// ======================================
// Attachments
// ======================================
export async function getAttachments(
  ticketId: number,
  params?: { page?: number; page_size?: number }
) {
  const response = await api.get<TicketAttachmentListResponse>(`/tickets/${ticketId}/attachments`, { params });
  return response.data;
}

export async function uploadAttachment(
  ticketId: number,
  file: File
) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post<TicketAttachment>(`/tickets/${ticketId}/attachments`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function downloadAttachment(
  ticketId: number,
  attachmentId: number
) {
  const response = await api.get(`/tickets/${ticketId}/attachments/${attachmentId}/download`, {
    responseType: "blob",
  });
  return response.data;
}

export async function deleteAttachment(
  ticketId: number,
  attachmentId: number
) {
  const response = await api.delete(`/tickets/${ticketId}/attachments/${attachmentId}`);
  return response.data;
}

// ======================================
// SLA Endpoints (Phase 2C)
// ======================================

export interface SLAPolicyCreatePayload {
  name: string;
  description?: string;
  priority: string;
  ticket_type?: string;
  category?: string;
  response_time_minutes: number;
  resolution_time_minutes: number;
  warning_threshold_percentage?: number;
}

export interface SLAPolicyUpdatePayload {
  name?: string;
  description?: string;
  priority?: string;
  ticket_type?: string;
  category?: string;
  response_time_minutes?: number;
  resolution_time_minutes?: number;
  warning_threshold_percentage?: number;
  is_active?: boolean;
}

// --- SLA Policy Management (Admin) ---
export async function getSLAPolicies(params?: {
  page?: number;
  page_size?: number;
  is_active?: boolean;
  priority?: string;
}) {
  const response = await api.get("/sla/policies", { params });
  return response.data;
}

export async function getSLAPolicy(policyId: number) {
  const response = await api.get<SLAPolicy>(`/sla/policies/${policyId}`);
  return response.data;
}

export async function createSLAPolicy(policy: SLAPolicyCreatePayload) {
  const response = await api.post("/sla/policies", policy);
  return response.data;
}

export async function updateSLAPolicy(policyId: number, policy: SLAPolicyUpdatePayload) {
  const response = await api.put(`/sla/policies/${policyId}`, policy);
  return response.data;
}

export async function deleteSLAPolicy(policyId: number) {
  const response = await api.delete(`/sla/policies/${policyId}`);
  return response.data;
}

// --- Ticket SLA Information ---
export async function getTicketSLA(ticketId: number): Promise<TicketSLA> {
  const response = await api.get<TicketSLA>(`/sla/tickets/${ticketId}`);
  return response.data;
}