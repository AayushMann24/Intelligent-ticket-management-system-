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

  created_by: number;

  assigned_to: number | null;
  assigned_name?: string;

  assignment_reason?: string;

  ai_processed?: boolean;

  created_at: string;
}