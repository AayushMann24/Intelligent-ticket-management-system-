import { useEffect, useState } from "react";

import {
  getDashboardSummary,
  getRecentTickets,
  getTicketTrend,
} from "../services/dashboardService";

import type { DashboardSummary } from "../types/dashboard";
import type { Ticket } from "../types/ticket";
import type { TrendData } from "../services/dashboardService";

export default function useDashboard() {
  const [summary, setSummary] =
    useState<DashboardSummary | null>(null);

  const [recentTickets, setRecentTickets] =
    useState<Ticket[]>([]);

  const [trend, setTrend] =
    useState<TrendData[]>([]);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [
          summaryData,
          recentData,
          trendData,
        ] = await Promise.all([
          getDashboardSummary(),
          getRecentTickets(),
          getTicketTrend(),
        ]);

        setSummary(summaryData);
        setRecentTickets(recentData);
        setTrend(trendData);

      } catch (error) {
        console.error("Failed to load dashboard:", error);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  return {
    summary,
    recentTickets,
    trend,

    priorityData: [
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
    ],

    loading,
  };
}