export interface DashboardSummary {
  total_tickets: number;
  open_tickets: number;
  assigned_tickets: number;
  resolved_tickets: number;

  high_priority: number;
  medium_priority: number;
  low_priority: number;
}