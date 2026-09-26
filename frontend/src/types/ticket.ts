export type TicketType = "INCIDENT" | "SERVICE_REQUEST";
export type TicketStatus = "Open" | "Assigned" | "In Progress" | "Pending" | "Resolved" | "Closed";
export type TicketPriority = "Low" | "Medium" | "High" | "Critical";

// SLA Types (Phase 2C)
export type SLAStatus = 
  | "NO_SLA" 
  | "RESPONSE_PENDING" 
  | "RESPONSE_MET" 
  | "RESPONSE_BREACHED" 
  | "RESOLUTION_PENDING" 
  | "RESOLUTION_MET" 
  | "RESOLUTION_BREACHED";

export interface SLAPolicy {
  id: number;
  name: string;
  description?: string;
  priority: string;
  ticket_type?: string;
  category?: string;
  response_time_minutes: number;
  resolution_time_minutes: number;
  warning_threshold_percentage?: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface TicketSLA {
  has_sla: boolean;
  policy: SLAPolicy | null;
  response_deadline: string | null;
  resolution_deadline: string | null;
  response_status: SLAStatus;
  resolution_status: SLAStatus;
  response_met_at?: string;
  resolution_met_at?: string;
  response_breached: boolean;
  resolution_breached: boolean;
}

export interface Ticket {
  id: number;

  title: string;
  description: string;

  category?: string;
  subcategory?: string;
  keywords?: string[];

  confidence?: number;

  priority: string;
  priority_reason?: string;

  status: string;

  ticket_type: TicketType;

  created_by: number;

  assigned_to: number | null;
  assigned_name?: string;

  assignment_reason?: string;

  // Resolution (Phase 2B)
  resolution_summary?: string;
  resolved_at?: string;
  resolved_by?: number;
  resolved_by_name?: string;

  // Escalation (Phase 2B)
  escalated_by?: number;
  escalated_by_name?: string;
  escalated_to?: number;
  escalated_to_name?: string;
  escalation_reason?: string;
  escalated_at?: string;

  // SLA (Phase 2C)
  sla_policy_id?: number;
  sla_response_deadline?: string;
  sla_resolution_deadline?: string;
  sla_response_status?: string;
  sla_resolution_status?: string;
  sla_response_breached?: boolean;
  sla_resolution_breached?: boolean;

  ai_processed?: boolean;

  created_at: string;
  updated_at?: string;
}

export interface TicketComment {
  id: number;
  ticket_id: number;
  author_id: number;
  author_name?: string;
  body: string;
  is_internal: boolean;
  created_at: string;
  updated_at: string;
}

export interface TicketCommentListResponse {
  items: TicketComment[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CommentPayload {
  body: string;
  is_internal?: boolean;
}

export interface TicketHistory {
  id: number;
  ticket_id: number;
  actor_id: number;
  actor_name?: string;
  event_type: string;
  old_value?: string;
  new_value?: string;
  metadata_json?: string;
  created_at: string;
}

export interface TicketHistoryListResponse {
  items: TicketHistory[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Workflow payload types (Phase 2B)
export interface AssignPayload {
  assigned_to: number;
}

export interface ResolvePayload {
  resolution_summary: string;
}

export interface ReopenPayload {
  reason?: string;
}

export interface ClosePayload {
  // Empty - just confirmation
}

export interface EscalatePayload {
  escalated_to: number;
  escalation_reason: string;
}

// Workflow actions response
export interface WorkflowActions {
  can_assign: boolean;
  can_reassign: boolean;
  can_unassign: boolean;
  can_start_work: boolean;
  can_mark_pending: boolean;
  can_resolve: boolean;
  can_reopen: boolean;
  can_close: boolean;
  can_escalate: boolean;
  valid_status_transitions: string[];
}

export interface TicketAttachment {
  id: number;
  ticket_id: number;
  uploaded_by: number;
  uploader_name?: string;
  original_filename: string;
  stored_filename: string;
  content_type: string;
  file_size: number;
  created_at: string;
}

export interface TicketAttachmentListResponse {
  items: TicketAttachment[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export type TimelineItemType = "HISTORY" | "COMMENT" | "INTERNAL_NOTE" | "ATTACHMENT";

export interface TimelineItem {
  type: TimelineItemType;
  id: number;
  actor_id: number;
  actor_name?: string;
  timestamp: string;
  event_type?: string;
  old_value?: string;
  new_value?: string;
  body?: string;
  is_internal?: boolean;
  filename?: string;
  file_size?: number;
  content_type?: string;
}

export interface TimelineResponse {
  items: TimelineItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}