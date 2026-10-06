import { useState } from "react";

import MainLayout from "../layouts/MainLayout";
import { useAuth } from "../context/useAuth";

import {
  FileText,
  Download,
  Filter,
  X,
  RefreshCw,
  Loader2,
  BarChart2,
  Users,
  AlertTriangle,
  Clock,
} from "lucide-react";

import { Button } from "../components/common/Button";
import { Select } from "../components/common/Select";
import { Input } from "../components/common/Input";

import {
  getTicketReport,
  exportTicketReport,
  getSLAReport,
  exportSLAReport,
  getSLABreachReport,
  exportSLABreachReport,
  getEscalationReport,
  exportEscalationReport,
  getTechnicianReport,
  exportTechnicianReport,
  downloadBlob,
  getReportFilename,
  type ReportFilters,
} from "../services/reportService";

// Date range presets (module-level to avoid impure Date.now() during render)
const PRESETS = [
  { label: "Last 7 days", startDate: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000), endDate: new Date() },
  { label: "Last 30 days", startDate: new Date(Date.now() - 29 * 24 * 60 * 60 * 1000), endDate: new Date() },
  { label: "Last 90 days", startDate: new Date(Date.now() - 89 * 24 * 60 * 60 * 1000), endDate: new Date() },
];

interface ReportTypeConfig {
  type: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  filters: string[];
}

const REPORT_TYPES: Record<string, ReportTypeConfig> = {
  tickets: {
    type: "tickets",
    name: "Ticket Report",
    description: "Detailed ticket listing with all fields including SLA status",
    icon: <FileText className="h-5 w-5" />,
    color: "bg-blue-600",
    filters: ["start_date", "end_date", "priority", "category", "ticket_type", "assignee_id", "status"],
  },
  sla: {
    type: "sla",
    name: "SLA Compliance Report",
    description: "SLA compliance metrics and ticket-level details",
    icon: <Clock className="h-5 w-5" />,
    color: "bg-green-600",
    filters: ["start_date", "end_date", "priority", "category", "ticket_type", "assignee_id"],
  },
  sla_breaches: {
    type: "sla_breaches",
    name: "SLA Breach Report",
    description: "Detailed SLA breach listing with breach types",
    icon: <AlertTriangle className="h-5 w-5" />,
    color: "bg-red-600",
    filters: ["start_date", "end_date", "priority", "category", "ticket_type", "assignee_id", "breach_type"],
  },
  escalations: {
    type: "escalations",
    name: "Escalation Report",
    description: "Escalation events and details",
    icon: <AlertTriangle className="h-5 w-5" />,
    color: "bg-purple-600",
    filters: ["start_date", "end_date", "priority", "category", "ticket_type", "assignee_id"],
  },
  technicians: {
    type: "technicians",
    name: "Technician Workload Report",
    description: "Technician workload and performance metrics",
    icon: <Users className="h-5 w-5" />,
    color: "bg-orange-600",
    filters: ["start_date", "end_date"],
  },
};

const PRIORITY_OPTIONS = [
  { value: "", label: "All Priorities" },
  { value: "Critical", label: "Critical" },
  { value: "High", label: "High" },
  { value: "Medium", label: "Medium" },
  { value: "Low", label: "Low" },
];

const TICKET_TYPE_OPTIONS = [
  { value: "", label: "All Types" },
  { value: "INCIDENT", label: "Incident" },
  { value: "PROBLEM", label: "Problem" },
  { value: "CHANGE", label: "Change" },
  { value: "REQUEST", label: "Request" },
  { value: "TASK", label: "Task" },
];

const STATUS_OPTIONS = [
  { value: "", label: "All Statuses" },
  { value: "Open", label: "Open" },
  { value: "Assigned", label: "Assigned" },
  { value: "Pending", label: "Pending" },
  { value: "Resolved", label: "Resolved" },
  { value: "Closed", label: "Closed" },
];

const BREACH_TYPE_OPTIONS = [
  { value: "", label: "All Breach Types" },
  { value: "response", label: "Response Breach" },
  { value: "resolution", label: "Resolution Breach" },
];

export default function ReportsPage() {
  const { user } = useAuth();

  // Check if user is admin
  const isAdmin = user?.role === "Admin";

  const [selectedReportType, setSelectedReportType] = useState<string>("tickets");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reportData, setReportData] = useState<unknown>(null);
  const [filters, setFilters] = useState<ReportFilters>({});
  const [showFilters, setShowFilters] = useState(true);

  // Get selected report config
  const reportConfig = REPORT_TYPES[selectedReportType];

  // Handle filter change
  const handleFilterChange = (key: string, value: string | number | undefined) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value === "" ? undefined : value,
    }));
  };

  const handlePresetSelect = (preset: { label: string; startDate: Date; endDate: Date }) => {
    setFilters((prev) => ({
      ...prev,
      start_date: preset.startDate.toISOString().split("T")[0],
      end_date: preset.endDate.toISOString().split("T")[0],
    }));
  };

  const handleClearFilters = () => {
    setFilters({});
  };

  const hasActiveFilters = Object.values(filters).some((v) => v !== undefined && v !== "");

  // Generate report (fetch JSON summary)
  const handleGenerateReport = async () => {
    setLoading(true);
    setError(null);
    try {
      let data;
      switch (selectedReportType) {
        case "tickets":
          data = await getTicketReport(filters);
          break;
        case "sla":
          data = await getSLAReport(filters);
          break;
        case "sla_breaches":
          data = await getSLABreachReport(filters);
          break;
        case "escalations":
          data = await getEscalationReport(filters);
          break;
        case "technicians":
          data = await getTechnicianReport(filters);
          break;
        default:
          throw new Error(`Unknown report type: ${selectedReportType}`);
      }
      setReportData(data);
    } catch (err) {
      console.error("Failed to generate report:", err);
      setError("Failed to generate report. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Export report as CSV
  const handleExportReport = async () => {
    setLoading(true);
    setError(null);
    try {
      let blob: Blob;
      switch (selectedReportType) {
        case "tickets":
          blob = await exportTicketReport(filters);
          break;
        case "sla":
          blob = await exportSLAReport(filters);
          break;
        case "sla_breaches":
          blob = await exportSLABreachReport(filters);
          break;
        case "escalations":
          blob = await exportEscalationReport(filters);
          break;
        case "technicians":
          blob = await exportTechnicianReport(filters);
          break;
        default:
          throw new Error(`Unknown report type: ${selectedReportType}`);
      }
      const filename = getReportFilename(selectedReportType, filters);
      downloadBlob(blob, filename);
    } catch (err) {
      console.error("Failed to export report:", err);
      setError("Failed to export report. Please try again.");
    } finally {
      setLoading(false);
    }
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
              You must be an Admin to access reports.
            </p>
          </div>
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
              Admin Reports
            </h1>
            <p className="mt-1 text-slate-500 dark:text-slate-400">
              Generate and export operational reports
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Button onClick={handleGenerateReport} variant="secondary" disabled={loading}>
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
              Generate Report
            </Button>
            <Button onClick={handleExportReport} variant="primary" disabled={loading}>
              <Download className="mr-2 h-4 w-4" />
              Export CSV
            </Button>
          </div>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-900/30">
          <div className="flex items-center gap-3">
            <svg className="h-5 w-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77-1.333.192 3 1.732 3z" />
            </svg>
            <p className="text-red-700 dark:text-red-300">{error}</p>
            <button
              onClick={() => setError(null)}
              className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Report Type Selector */}
      <div className="mb-6 rounded-xl border bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex flex-wrap items-center gap-4">
          <span className="text-sm font-medium text-slate-500 dark:text-slate-400">Report Type:</span>
          <div className="flex flex-wrap gap-2">
            {Object.values(REPORT_TYPES).map((config) => (
              <button
                key={config.type}
                onClick={() => {
                  setSelectedReportType(config.type);
                  setReportData(null);
                  setError(null);
                }}
                className={`
                  px-4 py-2 rounded-lg text-sm font-medium transition-all
                  ${selectedReportType === config.type
                    ? `${config.color} text-white shadow-lg`
                    : "text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700"
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  {config.icon}
                  {config.name}
                </div>
              </button>
            ))}
          </div>
        </div>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          {reportConfig?.description}
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Filters</h2>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 flex items-center gap-1"
          >
            {showFilters ? (
              <>
                <X className="h-4 w-4" />
                Hide
              </>
            ) : (
              <>
                <Filter className="h-4 w-4" />
                Show
              </>
            )}
          </button>
        </div>

        {showFilters && (
          <div className="rounded-xl border bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            {/* Date Range Presets */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Quick Date Ranges
              </label>
              <div className="flex flex-wrap gap-2">
                {PRESETS.map((preset) => (
                  <Button
                    key={preset.label}
                    onClick={() => handlePresetSelect(preset)}
                    variant="outline"
                    size="sm"
                    className="whitespace-nowrap"
                  >
                    {preset.label}
                  </Button>
                ))}
              </div>
            </div>

            {/* Custom Date Range */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-4">
              <div>
                <label htmlFor="start-date" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Start Date
                </label>
                <Input
                  id="start-date"
                  type="date"
                  value={filters.start_date || ""}
                  onChange={(e) => handleFilterChange("start_date", e.target.value)}
                  className="w-full"
                />
              </div>
              <div>
                <label htmlFor="end-date" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  End Date
                </label>
                <Input
                  id="end-date"
                  type="date"
                  value={filters.end_date || ""}
                  onChange={(e) => handleFilterChange("end_date", e.target.value)}
                  className="w-full"
                />
              </div>
              {reportConfig?.filters.includes("priority") && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Priority
                  </label>
                  <Select
                    value={filters.priority || ""}
                    onValueChange={(value) => handleFilterChange("priority", value)}
                    placeholder="All Priorities"
                    options={PRIORITY_OPTIONS}
                    className="w-full"
                  />
                </div>
              )}
              {reportConfig?.filters.includes("status") && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Status
                  </label>
                  <Select
                    value={filters.status || ""}
                    onValueChange={(value) => handleFilterChange("status", value)}
                    placeholder="All Statuses"
                    options={STATUS_OPTIONS}
                    className="w-full"
                  />
                </div>
              )}
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-4">
              {reportConfig?.filters.includes("category") && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Category
                  </label>
                  <Input
                    type="text"
                    placeholder="Category"
                    value={filters.category || ""}
                    onChange={(e) => handleFilterChange("category", e.target.value)}
                    className="w-full"
                  />
                </div>
              )}
              {reportConfig?.filters.includes("ticket_type") && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Ticket Type
                  </label>
                  <Select
                    value={filters.ticket_type || ""}
                    onValueChange={(value) => handleFilterChange("ticket_type", value)}
                    placeholder="All Types"
                    options={TICKET_TYPE_OPTIONS}
                    className="w-full"
                  />
                </div>
              )}
              {reportConfig?.filters.includes("assignee_id") && (
                <div>
                  <label htmlFor="assignee-id" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Assignee ID
                  </label>
                  <Input
                    id="assignee-id"
                    type="number"
                    placeholder="Assignee ID"
                    value={filters.assignee_id || ""}
                    onChange={(e) => handleFilterChange("assignee_id", e.target.value ? parseInt(e.target.value) : undefined)}
                    className="w-full"
                  />
                </div>
              )}
              {reportConfig?.filters.includes("breach_type") && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    Breach Type
                  </label>
                  <Select
                    value={filters.breach_type || ""}
                    onValueChange={(value) => handleFilterChange("breach_type", value)}
                    placeholder="All Breach Types"
                    options={BREACH_TYPE_OPTIONS}
                    className="w-full"
                  />
                </div>
              )}
            </div>

            {/* Clear Filters */}
            {hasActiveFilters && (
              <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                <Button onClick={handleClearFilters} variant="ghost" size="sm">
                  <X className="mr-1 h-4 w-4" />
                  Clear All Filters
                </Button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Report Summary / Results */}
      <div className="space-y-6">
        {loading && (
          <div className="rounded-xl border bg-white p-8 shadow-sm text-center dark:border-slate-800 dark:bg-slate-900">
            <div className="flex flex-col items-center gap-4">
              <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
              <p className="text-lg font-medium text-slate-700 dark:text-slate-300">
                Generating report...
              </p>
            </div>
          </div>
        )}

        {!loading && !reportData && !error && (
          <div className="rounded-xl border bg-white p-8 shadow-sm text-center dark:border-slate-800 dark:bg-slate-900">
            <BarChart2 className="mx-auto h-12 w-12 text-slate-400" />
            <p className="mt-4 text-slate-500 dark:text-slate-400">
              Select a report type, configure filters, and click "Generate Report" to view summary data,
              or click "Export CSV" to download the full report.
            </p>
          </div>
        )}

        {(function() {
            if (!reportData || typeof reportData !== "object" || !("summary" in reportData)) {
              return null;
            }
            return (
              <div className="rounded-xl border bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
              <div className="flex items-center gap-3">
                {reportConfig?.icon}
                <div>
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-white">
                    {reportConfig?.name}
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {reportConfig?.description}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {hasActiveFilters && (
                  <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                    Filters Applied
                  </span>
                )}
              </div>
            </div>

            <div className="p-6">
              {/* Summary Cards */}
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
                {renderSummaryCards((reportData as Record<string, unknown>).summary)}
              </div>

              {/* Applied Filters Display */}
              {hasActiveFilters && (
                <div className="mb-6 p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                  <h4 className="font-medium text-slate-900 dark:text-white mb-2">Applied Filters</h4>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(filters).map(([key, value]) =>
                      value !== undefined && value !== "" && (
                        <span key={key} className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                          {formatFilterKey(key)}: {String(value)}
                        </span>
                      )
                    )}
                  </div>
                </div>
              )}

              {/* Report-specific details */}
              {renderReportDetails(reportData)}
            </div>
          </div>
        )
      })()}
      </div>
    </MainLayout>
  );
}

function renderSummaryCards(summary: unknown) {
  if (!summary || typeof summary !== "object") return null;

  const cards: React.ReactNode[] = [];

  // Common cards for all reports
  const s = summary as Record<string, unknown>;
  
  if ("total_tickets" in s) {
    const byStatus = s.by_status as Record<string, number> | undefined;
    const byStatusTotal = byStatus ? Object.values(byStatus).reduce((a: number, b: number) => a + b, 0) : 0;
    
    cards.push(
      <SummaryCard key="total" title="Total Tickets" value={s.total_tickets as number} color="bg-blue-600" />,
      <SummaryCard key="by_status" title="By Status" value={byStatusTotal} color="bg-purple-600" />
    );
  }

  if ("total_escalations" in s) {
    cards.push(
      <SummaryCard key="total_esc" title="Total Escalations" value={s.total_escalations as number} color="bg-purple-600" />,
      <SummaryCard key="by_type" title="By Type" value={Object.keys((s.by_event_type as Record<string, number>) || {}).length} color="bg-orange-600" />
    );
  }

  if ("total_technicians" in s) {
    cards.push(
      <SummaryCard key="total_tech" title="Technicians" value={s.total_technicians as number} color="bg-green-600" />,
      <SummaryCard key="resolved" title="Total Resolved" value={s.total_resolved as number} color="bg-green-600" />
    );
  }

  // SLA specific
  if ("response_sla" in s && "resolution_sla" in s && !("by_event_type" in s)) {
    const respSla = s.response_sla as { compliance_percentage: number } | undefined;
    const resSla = s.resolution_sla as { compliance_percentage: number } | undefined;
    
    cards.push(
      <SummaryCard key="resp_compliance" title="Response Compliance" value={`${respSla?.compliance_percentage ?? 0}%`} color={respSla && respSla.compliance_percentage >= 90 ? "bg-green-600" : respSla && respSla.compliance_percentage >= 70 ? "bg-yellow-500" : "bg-red-600"} />,
      <SummaryCard key="res_compliance" title="Resolution Compliance" value={`${resSla?.compliance_percentage ?? 0}%`} color={resSla && resSla.compliance_percentage >= 90 ? "bg-green-600" : resSla && resSla.compliance_percentage >= 70 ? "bg-yellow-500" : "bg-red-600"} />
    );
  }

  return cards;
}

function SummaryCard({ title, value, color }: { title: string; value: string | number; color: string }) {
  return (
    <div className={`rounded-xl border p-4 ${color} text-white`}>
      <p className="text-sm opacity-90">{title}</p>
      <p className="mt-2 text-2xl font-bold">{value}</p>
    </div>
  );
}

function renderReportDetails(reportData: unknown) {
  if (!reportData || typeof reportData !== "object") return null;

  const summary = (reportData as Record<string, unknown>).summary as Record<string, unknown> | undefined;
  if (!summary) return null;

  // Status breakdown for ticket report
  if ("by_status" in summary && "by_priority" in summary && "by_ticket_type" in summary) {
    return (
      <div className="grid gap-6 lg:grid-cols-3">
        <DetailSection title="By Status" data={summary.by_status as Record<string, number>} />
        <DetailSection title="By Priority" data={summary.by_priority as Record<string, number>} />
        <DetailSection title="By Ticket Type" data={summary.by_ticket_type as Record<string, number>} />
      </div>
    );
  }

  // SLA by priority
  if ("by_priority" in summary && "response_sla" in summary) {
    const byPriority = summary.by_priority as Record<string, {
      response: { total: number; met: number; breached: number; compliance: number };
      resolution: { total: number; met: number; breached: number; compliance: number };
    }>;
    
    return (
      <div className="overflow-x-auto">
        <h4 className="mb-3 font-semibold text-slate-900 dark:text-white">SLA by Priority</h4>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-700 text-left text-slate-500 dark:text-slate-400">
              <th className="py-2 px-3">Priority</th>
              <th className="py-2 px-3">Response Total</th>
              <th className="py-2 px-3">Response Met</th>
              <th className="py-2 px-3">Response Breached</th>
              <th className="py-2 px-3">Response Compliance</th>
              <th className="py-2 px-3">Resolution Total</th>
              <th className="py-2 px-3">Resolution Met</th>
              <th className="py-2 px-3">Resolution Breached</th>
              <th className="py-2 px-3">Resolution Compliance</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {Object.entries(byPriority).map(([priority, data]) => (
              <tr key={priority} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                <td className="py-2 px-3 font-medium">{priority}</td>
                <td className="py-2 px-3">{data.response.total}</td>
                <td className="py-2 px-3 text-green-600">{data.response.met}</td>
                <td className="py-2 px-3 text-red-600">{data.response.breached}</td>
                <td className="py-2 px-3 font-medium">{data.response.compliance}%</td>
                <td className="py-2 px-3">{data.resolution.total}</td>
                <td className="py-2 px-3 text-green-600">{data.resolution.met}</td>
                <td className="py-2 px-3 text-red-600">{data.resolution.breached}</td>
                <td className="py-2 px-3 font-medium">{data.resolution.compliance}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  // Escalation details
  if ("by_event_type" in summary) {
    return (
      <div className="grid gap-6 lg:grid-cols-3">
        <DetailSection title="By Event Type" data={summary.by_event_type as Record<string, number>} />
        <DetailSection title="By Priority" data={summary.by_priority as Record<string, number>} />
        <DetailSection title="By Recipient Role" data={summary.by_recipient_role as Record<string, number>} />
      </div>
    );
  }

  return null;
}

function DetailSection({ title, data }: { title: string; data: Record<string, number> }) {
  return (
    <div className="rounded-lg border border-slate-200 p-4 dark:border-slate-700">
      <h4 className="mb-3 font-semibold text-slate-900 dark:text-white">{title}</h4>
      <div className="space-y-2">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="flex justify-between">
            <span className="text-slate-600 dark:text-slate-300 capitalize">{key}</span>
            <span className="font-medium text-slate-900 dark:text-white">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function formatFilterKey(key: string): string {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}