import { useTheme } from "../../context/useTheme";
import { CheckCircle, AlertCircle, TrendingUp, TrendingDown } from "lucide-react";

interface SLAResponseMetrics {
  tickets_with_response_sla: number;
  met_count: number;
  breached_count: number;
  compliance_percentage: number;
}

interface SLAResolutionMetrics {
  tickets_with_resolution_sla: number;
  met_count: number;
  breached_count: number;
  compliance_percentage: number;
}

interface SLAAnalyticsProps {
  data: {
    response_sla: SLAResponseMetrics;
    resolution_sla: SLAResolutionMetrics;
    tickets_with_sla: number;
  };
}

function SLAOverview({ data }: SLAAnalyticsProps) {
  const { theme } = useTheme();
  const dark = theme === "dark";

  const response = data.response_sla;
  const resolution = data.resolution_sla;

  const getComplianceColor = (percentage: number) => {
    if (percentage >= 90) return "text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30";
    if (percentage >= 70) return "text-yellow-600 dark:text-yellow-400 bg-yellow-100 dark:bg-yellow-900/30";
    return "text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/30";
  };

  if (!data) {
    return (
      <div className="h-64 flex items-center justify-center">
        <p className="text-slate-500 dark:text-slate-400">No SLA data available.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Response SLA */}
      <div
        className={`
          rounded-xl
          p-5
          border
          transition-all
          duration-300
          dark:border-slate-800
          dark:bg-slate-900/50
          ${dark ? "bg-slate-800/50" : "bg-slate-50"}
        `}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <TrendingDown className="h-5 w-5 text-blue-600" />
            Response SLA
          </h3>
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getComplianceColor(response.compliance_percentage)}`}>
            {response.compliance_percentage.toFixed(1)}% Compliance
          </span>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-lg p-4 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
            <p className="text-sm text-slate-500 dark:text-slate-400">With Response SLA</p>
            <p className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
              {data.tickets_with_sla}
            </p>
          </div>
          <div className="rounded-lg p-4 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
            <p className="text-sm text-slate-500 dark:text-slate-400">Met</p>
            <div className="mt-2 flex items-center gap-2">
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">{response.met_count}</p>
              <CheckCircle className="h-5 w-5 text-green-600" />
            </div>
          </div>
          <div className="rounded-lg p-4 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
            <p className="text-sm text-slate-500 dark:text-slate-400">Breached</p>
            <div className="mt-2 flex items-center gap-2">
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">{response.breached_count}</p>
              <AlertCircle className="h-5 w-5 text-red-600" />
            </div>
          </div>
        </div>

        <div className="mt-4 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${Math.min(response.compliance_percentage, 100)}%`,
              backgroundColor:
                response.compliance_percentage >= 90
                  ? "#22c55e"
                  : response.compliance_percentage >= 70
                  ? "#f59e0b"
                  : "#ef4444",
            }}
          />
        </div>
      </div>

      {/* Resolution SLA */}
      <div
        className={`
          rounded-xl
          p-5
          border
          transition-all
          duration-300
          dark:border-slate-800
          dark:bg-slate-900/50
          ${dark ? "bg-slate-800/50" : "bg-slate-50"}
        `}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-purple-600" />
            Resolution SLA
          </h3>
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getComplianceColor(resolution.compliance_percentage)}`}>
            {resolution.compliance_percentage.toFixed(1)}% Compliance
          </span>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="rounded-lg p-4 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
            <p className="text-sm text-slate-500 dark:text-slate-400">With Resolution SLA</p>
            <p className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
              {resolution.tickets_with_resolution_sla}
            </p>
          </div>
          <div className="rounded-lg p-4 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
            <p className="text-sm text-slate-500 dark:text-slate-400">Met</p>
            <div className="mt-2 flex items-center gap-2">
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">{resolution.met_count}</p>
              <CheckCircle className="h-5 w-5 text-green-600" />
            </div>
          </div>
          <div className="rounded-lg p-4 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
            <p className="text-sm text-slate-500 dark:text-slate-400">Breached</p>
            <div className="mt-2 flex items-center gap-2">
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">{resolution.breached_count}</p>
              <AlertCircle className="h-5 w-5 text-red-600" />
            </div>
          </div>
        </div>

        <div className="mt-4 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${Math.min(resolution.compliance_percentage, 100)}%`,
              backgroundColor:
                resolution.compliance_percentage >= 90
                  ? "#22c55e"
                  : resolution.compliance_percentage >= 70
                  ? "#f59e0b"
                  : "#ef4444",
            }}
          />
        </div>
      </div>
    </div>
  );
}

export default SLAOverview;