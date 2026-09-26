export interface DashboardSummary {
  total_tickets: number;
  open_tickets: number;
  assigned_tickets: number;
  resolved_tickets: number;

  high_priority: number;
  medium_priority: number;
  low_priority: number;
}

export interface RecentTicket {
  id: number;
  title: string;
  status: string;
  priority: string;
  assigned_to: string;
  created_at: string;
}

export interface TicketTrend {
  date: string;
  tickets: number;
}

export interface Activity {
  message: string;
  time: string;
}