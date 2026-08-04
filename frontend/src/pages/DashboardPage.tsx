import {
  CheckCircle,
  ClipboardList,
  Clock3,
  Ticket,
} from "lucide-react";

import DashboardHeader from "../components/dashboard/DashboardHeader";
import StatCard from "../components/dashboard/StatCard";
import QuickActions from "../components/dashboard/QuickActions";
import RecentTickets from "../components/dashboard/RecentTickets";
import PriorityChart from "../components/dashboard/PriorityChart";
import TicketTrendChart from "../components/dashboard/TicketTrendChart";
import ActivityFeed from "../components/dashboard/ActivityFeed";

import MainLayout from "../layouts/MainLayout";

import useDashboard from "../hooks/useDashboard";

export default function DashboardPage() {
  const {
    summary,
    recentTickets,
    priorityData,
    trendData,
    loading,
  } = useDashboard();
  console.log("Dashboard trendData:", trendData);

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
        />

        <StatCard
          title="Open Tickets"
          value={summary.open_tickets}
          icon={<Clock3 size={28} />}
          color="bg-yellow-500"
        />

        <StatCard
          title="Assigned"
          value={summary.assigned_tickets}
          icon={<ClipboardList size={28} />}
          color="bg-purple-600"
        />

        <StatCard
          title="Resolved"
          value={summary.resolved_tickets}
          icon={<CheckCircle size={28} />}
          color="bg-green-600"
        />

      </div>

      {/* Quick Actions */}

      <div className="mt-8">
        <QuickActions />
      </div>

      {/* Priority + Recent Tickets */}

      <div className="mt-8 grid gap-6 lg:grid-cols-2">

        <PriorityChart
          data={priorityData}
        />

        <RecentTickets
          tickets={recentTickets}
        />

      </div>

      {/* Ticket Trend + Activity */}

      <div className="mt-8 grid gap-6 lg:grid-cols-2">

        <TicketTrendChart
          data={trendData}
        />

        <ActivityFeed />

      </div>

    </MainLayout>
  );
}