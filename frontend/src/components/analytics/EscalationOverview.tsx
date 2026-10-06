import { useTheme } from "../../context/useTheme";
import { AlertTriangle, Users, TrendingUp, Flag, Activity } from "lucide-react";

interface EscalationAnalyticsProps {
  data: {
    total_escalations: number;
    response_sla_escalations: number;
    resolution_sla_escalations: number;
    by_priority: Record<string, number>;
    by_recipient_role: Record<string, number>;
    escalations_over_time: Array<{ date: string; count: number }>;
    currently_escalated_tickets: number;
  };
}

const PRIORITY_COLORS: Record<string, string> = {
  Critical: "#ef4444",
  High: "#f59e0b",
  Medium: "#22c55e",
  Low: "#64748b",
};

const PRIORITY_ORDER = ["Critical", "High", "Medium", "Low"];

function EscalationOverview({ data }: EscalationAnalyticsProps) {
  const { theme } = useTheme();
  const dark = theme === "dark";

  if (!data || data.total_escalations === 0) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="text-center">
          <Activity className="mx-auto h-12 w-12 text-slate-400" />
          <p className="mt-4 text-slate-500 dark:text-slate-400">No escalation data available.</p>
        </div>
      </div>
    );
  }

  // Sort priority data
  const priorityData = PRIORITY_ORDER.map((priority) => ({
    priority,
    count: data.by_priority[priority] || 0,
    color: PRIORITY_COLORS[priority] || "#94a3b8",
  }));

  // Sort role data by count
  const roleEntries = Object.entries(data.by_recipient_role).sort((a, b) => b[1] - a[1]);

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <div
          className={`
            rounded-xl
            p-4
            border
            text-center
            transition-all
            duration-300
            ${dark ? "bg-slate-800/50 border-slate-700" : "bg-white border-slate-200"}
          `}
        >
          <p className="text-sm text-slate-500 dark:text-slate-400">Total Escalations</p>
          <p className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
            {data.total_escalations}
          </p>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">All time</p>
        </div>

        <div
          className={`
            rounded-xl
            p-4
            border
            text-center
            transition-all
            duration-300
            ${dark ? "bg-red-900/20 border-red-800" : "bg-red-50 border-red-200"}
          `}
        >
          <div className="flex items-center justify-center gap-1 mb-1">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <p className="text-sm font-medium text-red-700 dark:text-red-300">Response SLA</p>
          </div>
          <p className="text-3xl font-bold text-red-600 dark:text-red-400">
            {data.response_sla_escalations}
          </p>
        </div>

        <div
          className={`
            rounded-xl
            p-4
            border
            text-center
            transition-all
            duration-300
            ${dark ? "bg-purple-900/20 border-purple-800" : "bg-purple-50 border-purple-200"}
          `}
        >
          <div className="flex items-center justify-center gap-1 mb-1">
            <Flag className="h-4 w-4 text-purple-600" />
            <p className="text-sm font-medium text-purple-700 dark:text-purple-300">Resolution SLA</p>
          </div>
          <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">
            {data.resolution_sla_escalations}
          </p>
        </div>

        <div
          className={`
            rounded-xl
            p-4
            border
            text-center
            transition-all
            duration-300
            ${dark ? "bg-orange-900/20 border-orange-800" : "bg-orange-50 border-orange-200"}
          `}
        >
          <div className="flex items-center justify-center gap-1 mb-1">
            <TrendingUp className="h-4 w-4 text-orange-600" />
            <p className="text-sm font-medium text-orange-700 dark:text-orange-300">Currently Escalated</p>
          </div>
          <p className="text-3xl font-bold text-orange-600 dark:text-orange-400">
            {data.currently_escalated_tickets}
          </p>
        </div>
      </div>

      {/* Priority & Role Breakdown */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div
          className={`
            rounded-xl
            p-5
            border
            transition-all
            duration-300
            ${dark ? "bg-slate-800/50 border-slate-700" : "bg-white border-slate-200"}
          `}
        >
          <h4 className="mb-4 font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            By Priority
          </h4>
          <div className="space-y-3">
            {priorityData.map((item) => (
              <div key={item.priority} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className="h-3 w-3 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-slate-700 dark:text-slate-300 font-medium">
                    {item.priority}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div
                    className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full flex-1 max-w-[150px] overflow-hidden"
                  >
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${data.total_escalations > 0 ? (item.count / data.total_escalations) * 100 : 0}%`,
                        backgroundColor: item.color,
                      }}
                    />
                  </div>
                  <span className="font-bold text-slate-900 dark:text-white w-12 text-right">
                    {item.count}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div
          className={`
            rounded-xl
            p-5
            border
            transition-all
            duration-300
            ${dark ? "bg-slate-800/50 border-slate-700" : "bg-white border-slate-200"}
          `}
        >
          <h4 className="mb-4 font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Users className="h-5 w-5 text-blue-600" />
            By Recipient Role
          </h4>
          <div className="space-y-3">
            {roleEntries.map(([role, count]) => (
              <div key={role} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className="h-8 w-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
                    style={{
                      backgroundColor:
                        role === "Admin"
                          ? "#ef4444"
                          : role === "Technician"
                          ? "#3b82f6"
                          : "#22c55e",
                    }}
                  >
                    {role.charAt(0)}
                  </div>
                  <span className="text-slate-700 dark:text-slate-300 font-medium capitalize">
                    {role}
                  </span>
                </div>
                <span className="font-bold text-slate-900 dark:text-white">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Escalations Over Time */}
      {data.escalations_over_time.length > 0 && (
        <div
          className={`
            rounded-xl
            p-5
            border
            transition-all
            duration-300
            ${dark ? "bg-slate-800/50 border-slate-700" : "bg-white border-slate-200"}
          `}
        >
          <h4 className="mb-4 font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-600" />
            Escalations Over Time (Last 30 Days)
          </h4>
          <div className="h-48">
            <EscalationTrendChart data={data.escalations_over_time} />
          </div>
        </div>
      )}
    </div>
  );
}

// Simple trend chart component inline
function EscalationTrendChart({ data }: { data: Array<{ date: string; count: number }> }) {
  return (
    <div className="flex items-end justify-around h-full px-2 gap-1">
      {data.map((entry) => (
        <div key={entry.date} className="flex flex-col items-center flex-1 min-w-[30px]">
          <div
            className="w-full bg-blue-600 rounded-t transition-all duration-300 hover:bg-blue-500"
            style={{
              height: `${(entry.count / Math.max(...data.map((d) => d.count), 1)) * 100}%`,
              minHeight: entry.count > 0 ? "4px" : "0",
            }}
            title={`${entry.date}: ${entry.count} escalations`}
          />
          <span className="mt-2 text-xs text-slate-500 dark:text-slate-400 rotate-45 origin-bottom whitespace-nowrap">
            {entry.date}
          </span>
        </div>
      ))}
    </div>
  );
}

export default EscalationOverview;