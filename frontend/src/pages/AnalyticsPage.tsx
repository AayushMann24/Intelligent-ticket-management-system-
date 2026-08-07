import { useEffect, useState } from "react";

import MainLayout from "../layouts/MainLayout";

import {
  Ticket,
  Clock3,
  ClipboardList,
  CheckCircle,
  AlertTriangle,
  Circle,
  CheckCircle2,
} from "lucide-react";

import {
  getDashboardSummary,
  getRecentActivity,
  getRecentTickets,
} from "../services/dashboardService";

import type {
  DashboardSummary,
  RecentTicket,
  Activity,
} from "../services/dashboardService";

export default function AnalyticsPage() {
  const [summary, setSummary] =
    useState<DashboardSummary | null>(null);

  const [tickets, setTickets] =
    useState<RecentTicket[]>([]);

  const [activity, setActivity] =
    useState<Activity[]>([]);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [
          summaryData,
          recentTickets,
          activityData,
        ] = await Promise.all([
          getDashboardSummary(),
          getRecentTickets(),
          getRecentActivity(),
        ]);

        setSummary(summaryData);
        setTickets(recentTickets);
        setActivity(activityData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  if (loading) {
    return (
      <MainLayout>
        <div className="flex h-96 items-center justify-center">
          <h2 className="text-xl font-semibold text-slate-700 dark:text-white">
            Loading Analytics...
          </h2>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>

      <div className="mb-8">

        <h1 className="text-4xl font-bold text-slate-900 dark:text-white">
          Analytics Dashboard
        </h1>

        <p className="mt-2 text-slate-500 dark:text-slate-400">
          Overview of tickets and system performance.
        </p>

      </div>

      {/* KPI */}

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">

        <StatCard
          title="Total Tickets"
          value={summary?.total_tickets ?? 0}
          icon={<Ticket />}
          color="bg-blue-600"
        />

        <StatCard
          title="Open"
          value={summary?.open_tickets ?? 0}
          icon={<Clock3 />}
          color="bg-yellow-500"
        />

        <StatCard
          title="Assigned"
          value={summary?.assigned_tickets ?? 0}
          icon={<ClipboardList />}
          color="bg-purple-600"
        />

        <StatCard
          title="Resolved"
          value={summary?.resolved_tickets ?? 0}
          icon={<CheckCircle />}
          color="bg-green-600"
        />

      </div>

      {/* Priority */}

      <div className="mt-6 grid gap-6 md:grid-cols-3">

        <StatCard
          title="High Priority"
          value={summary?.high_priority ?? 0}
          icon={<AlertTriangle />}
          color="bg-red-600"
        />

        <StatCard
          title="Medium Priority"
          value={summary?.medium_priority ?? 0}
          icon={<Circle />}
          color="bg-yellow-500"
        />

        <StatCard
          title="Low Priority"
          value={summary?.low_priority ?? 0}
          icon={<CheckCircle2 />}
          color="bg-green-600"
        />

      </div>

      {/* Recent Tickets */}

      <div className="mt-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">

        <h2 className="mb-6 text-2xl font-bold text-slate-900 dark:text-white">
          Recent Tickets
        </h2>

        <div className="overflow-x-auto">

          <table className="w-full">

            <thead>

              <tr className="border-b border-slate-200 text-left text-slate-600 dark:border-slate-700 dark:text-slate-300">

                <th className="py-3">Title</th>

                <th>Status</th>

                <th>Priority</th>

                <th>Assigned To</th>

              </tr>

            </thead>

            <tbody>

              {tickets.map((ticket) => (

                <tr
                  key={ticket.id}
                  className="border-b border-slate-100 transition hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/50"
                >

                  <td className="py-4 font-medium text-slate-900 dark:text-white">
                    {ticket.title}
                  </td>

                  <td>{ticket.status}</td>

                  <td>{ticket.priority}</td>

                  <td>{ticket.assigned_to}</td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      </div>

      {/* Activity */}

      <div className="mt-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">

        <h2 className="mb-6 text-2xl font-bold text-slate-900 dark:text-white">
          Recent Activity
        </h2>

        <div className="space-y-5">

          {activity.map((item, index) => (

            <div
              key={index}
              className="rounded-xl border border-slate-200 p-4 dark:border-slate-700"
            >

              <p className="font-medium text-slate-900 dark:text-white">
                {item.message}
              </p>

              <p className="mt-1 text-sm text-slate-500">
                {item.time}
              </p>

            </div>

          ))}

        </div>

      </div>

    </MainLayout>
  );
}

interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}

function StatCard({
  title,
  value,
  icon,
  color,
}: StatCardProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:shadow-lg dark:border-slate-800 dark:bg-slate-900">

      <div className="flex items-center justify-between">

        <div>

          <p className="text-slate-500 dark:text-slate-400">
            {title}
          </p>

          <h2 className="mt-3 text-4xl font-bold text-slate-900 dark:text-white">
            {value}
          </h2>

        </div>

        <div className={`rounded-2xl p-5 text-white ${color}`}>
          {icon}
        </div>

      </div>

    </div>
  );
}