import axios from "axios";

const API = "http://127.0.0.1:8000";

export interface TrendData {
  date: string;
  tickets: number;
}

export async function getDashboardSummary() {
  const response = await axios.get(
    `${API}/dashboard/summary`
  );

  return response.data;
}

export async function getRecentTickets() {
  const response = await axios.get(
    `${API}/dashboard/recent-tickets`
  );

  return response.data;
}

export async function getTicketTrend(): Promise<TrendData[]> {
  const response = await axios.get<TrendData[]>(
    `${API}/dashboard/trend`
  );

  return response.data;
}