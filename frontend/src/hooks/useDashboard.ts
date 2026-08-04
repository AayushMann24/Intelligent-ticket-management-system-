import { useEffect, useState } from "react";

import {
  getDashboardSummary,
  getRecentTickets,
  getTicketTrend,
} from "../services/dashboardService";

import type { DashboardSummary } from "../types/dashboard";
import type { Ticket } from "../types/ticket";
import type { TrendData } from "../types/trend";

export default function useDashboard() {
  const [summary, setSummary] =
    useState<DashboardSummary | null>(null);

  const [recentTickets, setRecentTickets] =
    useState<Ticket[]>([]);

  const [trendData, setTrendData] =
    useState<TrendData[]>([]);

  const [loading, setLoading] =
    useState(true);

  const loadDashboard = async () => {
    try {
      const [
        summaryResponse,
        recentTicketsResponse,
        trendResponse,
      ] = await Promise.all([
        getDashboardSummary(),
        getRecentTickets(),
        getTicketTrend(),
      ]);

      console.log("Dashboard Summary:", summaryResponse);
      console.log("Recent Tickets:", recentTicketsResponse);
      console.log("Trend Data:", trendResponse);

      setSummary(summaryResponse);
      setRecentTickets(recentTicketsResponse);
      setTrendData(trendResponse);
      console.log("Trend Response:", trendResponse);

    } catch (error) {
      console.error("Failed to load dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const priorityData = [
    {
      name: "High",
      value: summary?.high_priority ?? 0,
    },
    {
      name: "Medium",
      value: summary?.medium_priority ?? 0,
    },
    {
      name: "Low",
      value: summary?.low_priority ?? 0,
    },
  ];

  return {
    summary,
    recentTickets,
    trendData,
    priorityData,
    loading,
    reloadDashboard: loadDashboard,
  };
}