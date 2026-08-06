import {
  CheckCircle,
  ClipboardList,
  Clock3,
  Ticket,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import MainLayout from "../layouts/MainLayout";

import DashboardHeader from "../components/dashboard/DashboardHeader";
import StatCard from "../components/dashboard/StatCard";
import QuickActions from "../components/dashboard/QuickActions";
import RecentTickets from "../components/dashboard/RecentTickets";
import PriorityChart from "../components/dashboard/PriorityChart";
import TicketTrendChart from "../components/dashboard/TicketTrendChart";
import ActivityFeed from "../components/dashboard/ActivityFeed";

import useDashboard from "../hooks/useDashboard";

export default function DashboardPage() {
  const {
    summary,
    recentTickets,
    priorityData,
    trendData,
    activity,
    loading,
  } = useDashboard();

  const navigate = useNavigate();

  if (loading) {
    return (
      <MainLayout>
        <div className="flex h-96 items-center justify-center">
          <h2 className="text-xl text-white">
            Loading Dashboard...
          </h2>
        </div>
      </MainLayout>
    );
  }

  if (!summary) {
    return (
      <MainLayout>
        <div className="flex h-96 items-center justify-center">
          <h2 className="text-xl text-red-500">
            Failed to load dashboard.
          </h2>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <DashboardHeader />

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Total Tickets"
          value={summary.total_tickets}
          icon={<Ticket size={28} />}
          color="bg-blue-600"
          onClick={() => navigate("/tickets")}
        />

        <StatCard
          title="Open Tickets"
          value={summary.open_tickets}
          icon={<Clock3 size={28} />}
          color="bg-yellow-500"
          onClick={() => navigate("/tickets?status=Open")}
        />

        <StatCard
          title="Assigned Tickets"
          value={summary.assigned_tickets}
          icon={<ClipboardList size={28} />}
          color="bg-purple-600"
          onClick={() => navigate("/tickets?status=Assigned")}
        />

        <StatCard
          title="Resolved Tickets"
          value={summary.resolved_tickets}
          icon={<CheckCircle size={28} />}
          color="bg-green-600"
          onClick={() => navigate("/tickets?status=Resolved")}
        />
      </div>

      {/* Quick Actions */}
      <div className="mt-8">
        <QuickActions />
      </div>

      {/* Charts + Recent Tickets */}
      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <PriorityChart data={priorityData} />

        <RecentTickets tickets={recentTickets} />
      </div>

      {/* Trend + Activity */}
      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <TicketTrendChart data={trendData} />

        <ActivityFeed activity={activity} />
      </div>
    </MainLayout>
  );
}