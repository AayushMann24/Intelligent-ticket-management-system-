import { useEffect, useState } from "react";

import {
  getDashboardSummary,
  getRecentTickets,
  getTicketTrend,
  getRecentActivity,
  type DashboardSummary,
  type RecentTicket,
  type TicketTrend,
  type Activity,
} from "../services/dashboardService";

export default function useDashboard() {
  const [summary, setSummary] =
    useState<DashboardSummary | null>(null);

  const [recentTickets, setRecentTickets] =
    useState<RecentTicket[]>([]);

  const [trendData, setTrendData] =
    useState<TicketTrend[]>([]);

  const [activity, setActivity] =
    useState<Activity[]>([]);

  const [loading, setLoading] =
    useState(true);

  const loadDashboard = async () => {
    try {
      const [
        summaryData,
        ticketsData,
        trend,
        activityData,
      ] = await Promise.all([
        getDashboardSummary(),
        getRecentTickets(),
        getTicketTrend(),
        getRecentActivity(),
      ]);

      setSummary(summaryData);
      setRecentTickets(ticketsData);
      setTrendData(trend);
      setActivity(activityData);
    } catch (error) {
      console.error("Failed to load dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const priorityData = summary
    ? [
        {
          name: "High",
          value: summary.high_priority,
        },
        {
          name: "Medium",
          value: summary.medium_priority,
        },
        {
          name: "Low",
          value: summary.low_priority,
        },
      ]
    : [];

  return {
    summary,
    recentTickets,
    priorityData,
    trendData,
    activity,
    loading,
    reloadDashboard: loadDashboard,
  };
}