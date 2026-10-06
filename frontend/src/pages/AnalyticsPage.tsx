import { useEffect, useState, useCallback } from "react";

import MainLayout from "../layouts/MainLayout";
import { useAuth } from "../context/useAuth";

import { Button } from "../components/common/Button";

import {
  getComprehensiveDashboard,
  type ComprehensiveDashboard,
  type AnalyticsFilters as AnalyticsFiltersType,
  getDateRangePresets,
} from "../services/analyticsService";

import AnalyticsFilters from "../components/analytics/AnalyticsFilters";

import TicketPriorityChart from "../components/analytics/TicketPriorityChart";
import TicketCategoryChart from "../components/analytics/TicketCategoryChart";
import TicketTypeChart from "../components/analytics/TicketTypeChart";
import TicketTrendChart from "../components/analytics/TicketTrendChart";
import SLAOverview from "../components/analytics/SLAOverview";
import EscalationOverview from "../components/analytics/EscalationOverview";
import TechnicianWorkload from "../components/analytics/TechnicianWorkload";
import TimingMetrics from "../components/analytics/TimingMetrics";
import KPICard from "../components/analytics/KPICard";
import SectionCard from "../components/analytics/SectionCard";

function AnalyticsPage() {
  const { user } = useAuth();

  // Check if user is admin
  const isAdmin = user?.role === "Admin";

  const [dashboard, setDashboard] = useState<ComprehensiveDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<AnalyticsFiltersType>({
    granularity: "daily",
  });
  const [filterError, setFilterError] = useState<string | null>(null);

  const loadDashboard = useCallback(async () => {
    const startDate = filters.start_date ? filters.start_date : undefined;
    const endDate = filters.end_date ? filters.end_date : undefined;
    const granularity = filters.granularity || "daily";

    const data = await getComprehensiveDashboard(startDate, endDate, granularity);
    return data;
  }, [filters.start_date, filters.end_date, filters.granularity]);

  // Fetch data when loadDashboard changes (i.e., when filters change)
  useEffect(() => {
    let mounted = true;
    loadDashboard()
      .then((data) => {
        if (mounted) {
          setDashboard(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          console.error("Failed to load analytics dashboard:", err);
          setError("Failed to load analytics data. Please try again.");
          setLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, [loadDashboard]);

  // We could debounce this effect for real-time filtering
  // useEffect(() => {
  //   const timer = setTimeout(() => loadFilteredAnalytics(), 300);
  //   return () => clearTimeout(timer);
  // }, [loadFilteredAnalytics]);

  const handleFilterChange = (newFilters: Partial<AnalyticsFilters>) => {
    setLoading(true);
    setError(null);
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const handlePresetSelect = (preset: { label: string; startDate: Date; endDate: Date }) => {
    setLoading(true);
    setError(null);
    setFilters((prev) => ({
      ...prev,
      start_date: formatDateForAPI(preset.startDate),
      end_date: formatDateForAPI(preset.endDate),
    }));
  };

  const handleClearFilters = () => {
    setLoading(true);
    setError(null);
    setFilters({ granularity: "daily" });
  };

  const hasActiveFilters = Boolean(
    filters.start_date || filters.end_date || filters.priority ||
    filters.category || filters.ticket_type || filters.assignee_id
  );

  const handleRefresh = () => {
    setLoading(true);
    setError(null);
    loadDashboard();
  };

  // Render access denied state
  if (!isAdmin) {
    return (
      <MainLayout>
        <div className="flex h-96 items-center justify-center bg-slate-50 dark:bg-slate-900">
          <div className="text-center">
            <svg className="mx-auto h-12 w-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77-1.333.192 3 1.732 3z" />
            </svg>
            <h2 className="mt-4 text-2xl font-bold text-slate-900 dark:text-white">
              Access Denied
            </h2>
            <p className="mt-2 text-slate-500 dark:text-slate-400">
              You must be an Admin to access analytics.
            </p>
          </div>
        </div>
      </MainLayout>
    );
  }

  // Render loading state
  if (loading) {
    return (
      <MainLayout>
        <div className="flex h-96 items-center justify-center bg-slate-50 dark:bg-slate-900">
          <div className="flex flex-col items-center gap-4">
            <svg className="h-12 w-12 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <p className="text-lg font-medium text-slate-700 dark:text-slate-300">
              Loading Analytics...
            </p>
          </div>
        </div>
      </MainLayout>
    );
  }

  // Render error state
  if (error && !dashboard) {
    return (
      <MainLayout>
        <div className="flex h-96 items-center justify-center bg-slate-50 dark:bg-slate-900">
          <div className="text-center p-8">
            <svg className="mx-auto h-12 w-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77-1.333.192 3 1.732 3z" />
            </svg>
            <h2 className="mt-4 text-2xl font-bold text-slate-900 dark:text-white">
              Failed to Load Analytics
            </h2>
            <p className="mt-2 text-slate-500 dark:text-slate-400">{error}</p>
            <Button onClick={handleRefresh} className="mt-6" variant="primary">
              <svg className="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Try Again
            </Button>
          </div>
        </div>
      </MainLayout>
    );
  }

  // Render empty state
  if (!dashboard) {
    return (
      <MainLayout>
        <div className="flex h-96 items-center justify-center bg-slate-50 dark:bg-slate-900">
          <p className="text-slate-500 dark:text-slate-400">No analytics data available.</p>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
              Analytics Dashboard
            </h1>
            <p className="mt-1 text-slate-500 dark:text-slate-400">
              Operational metrics and insights for ITSM system
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <AnalyticsFilters
              filters={filters}
              onChange={handleFilterChange}
              presets={getDateRangePresets()}
              onPresetSelect={handlePresetSelect}
              onClear={handleClearFilters}
              hasActiveFilters={hasActiveFilters}
            />
            <Button onClick={handleRefresh} variant="secondary">
              <svg className="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </Button>
          </div>
        </div>
      </div>

      {/* Error banner for filter errors */}
        {filterError && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-900/30">
            <div className="flex items-center gap-3">
              <svg className="h-5 w-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77-1.333.192 3 1.732 3z" />
              </svg>
              <p className="text-red-700 dark:text-red-300">{filterError}</p>
              <button
                onClick={() => setFilterError(null)}
                className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* KPI Cards */}
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4 mb-8">
          <KPICard
            title="Total Tickets"
            value={dashboard.overview.total_tickets}
            icon={<svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>}
            color="bg-blue-600"
            description="Total tickets in system"
          />
          <KPICard
            title="Open"
            value={dashboard.overview.open_tickets}
            icon={<svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
            color="bg-yellow-500"
            description="Awaiting assignment"
          />
          <KPICard
            title="Pending"
            value={dashboard.overview.pending_tickets}
            icon={<svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
            color="bg-orange-500"
            description="In progress"
          />
          <KPICard
            title="Resolved"
            value={dashboard.overview.resolved_tickets}
            icon={<svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>}
            color="bg-green-600"
            description="Completed"
          />
          <KPICard
            title="Closed"
            value={dashboard.overview.closed_tickets}
            icon={<svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>}
            color="bg-blue-500"
            description="Finalized"
          />
          <KPICard
            title="Unassigned"
            value={dashboard.overview.unassigned_tickets}
            icon={<svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77-1.333.192 3 1.732 3z" /></svg>}
            color="bg-red-500"
            description="Need assignment"
          />
          <KPICard
            title="Escalated"
            value={dashboard.overview.escalated_tickets}
            icon={<svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>}
            color="bg-purple-600"
            description="Active escalations"
          />
          <KPICard
            title="SLA Compliance"
            value={`${dashboard.sla.response_sla.compliance_percentage.toFixed(1)}%`}
            icon={<svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>}
            color={
              dashboard.sla.response_sla.compliance_percentage >= 90
                ? "bg-green-600"
                : dashboard.sla.response_sla.compliance_percentage >= 70
                ? "bg-yellow-500"
                : "bg-red-600"
            }
            description="Response SLA compliance"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid gap-6 lg:grid-cols-2 mb-8">
          <SectionCard title="Priority Distribution">
            <TicketPriorityChart data={dashboard.priority} />
          </SectionCard>

          <SectionCard title="Ticket Categories (Top 20)">
            <TicketCategoryChart data={dashboard.category} />
          </SectionCard>
        </div>

        <div className="grid gap-6 lg:grid-cols-2 mb-8">
          <SectionCard title="Ticket Types">
            <TicketTypeChart data={dashboard.ticket_type} />
          </SectionCard>

          <SectionCard title="SLA Compliance">
            <SLAOverview data={dashboard.sla} />
          </SectionCard>
        </div>

        <div className="grid gap-6 lg:grid-cols-2 mb-8">
          <SectionCard title="Escalation Analytics">
            <EscalationOverview data={dashboard.escalations} />
          </SectionCard>

          <SectionCard title="Timing Metrics">
            <TimingMetrics data={dashboard.timing} />
          </SectionCard>
        </div>

        <div className="grid gap-6 lg:grid-cols-2 mb-8">
          <SectionCard title="Technician Workload" className="lg:col-span-2">
            <TechnicianWorkload data={dashboard.technicians} />
          </SectionCard>
        </div>

        <div className="mb-8">
          <SectionCard title="Ticket Trends" className="lg:col-span-2">
            <TicketTrendChart data={dashboard.trends.trends} granularity={dashboard.trends.granularity} />
          </SectionCard>
        </div>

        {/* Filtered Analytics Section */}
        {hasActiveFilters && (
          <div className="mb-8">
            <SectionCard title="Filtered Ticket Analytics">
              {dashboard && (
                <div className="grid gap-4 md:grid-cols-3">
                  <KPICard
                    title="Total (Filtered)"
                    value={dashboard.filtered?.total ?? 0}
                    icon={<svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>}
                    color="bg-blue-600"
                  />
                  <KPICard
                    title="By Status"
                    value={Object.values(dashboard.filtered?.by_status ?? {}).reduce((a, b) => a + b, 0)}
                    icon={<svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>}
                    color="bg-purple-600"
                  />
                  <KPICard
                    title="By Priority"
                    value={Object.values(dashboard.filtered?.by_priority ?? {}).reduce((a, b) => a + b, 0)}
                    icon={<svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77-1.333.192 3 1.732 3z" /></svg>}
                    color="bg-orange-600"
                  />
                </div>
              )}
            </SectionCard>
          </div>
        )}
      </MainLayout>
    );
  }

function formatDateForAPI(date: Date): string {
  return date.toISOString().split("T")[0];
}

export default AnalyticsPage;