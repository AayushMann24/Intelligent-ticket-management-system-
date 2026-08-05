export interface Ticket {
  id: number;

  title: string;
  description: string;

  priority: string;
  status: string;

  created_by: number;

  assigned_to: number | null;

  created_at: string;
}