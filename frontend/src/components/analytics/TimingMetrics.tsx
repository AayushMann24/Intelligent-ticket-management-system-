import { useTheme } from "../../context/useTheme";
import { Clock, Timer } from "lucide-react";

interface TimingMetricsProps {
  data: {
    average_first_response_minutes: number | null;
    average_resolution_minutes: number | null;
    note: string;
  };
}

function TimingMetrics({ data }: TimingMetricsProps) {
  const { theme } = useTheme();
  const dark = theme === "dark";

  if (!data || (data.average_first_response_minutes === null && data.average_resolution_minutes === null)) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="text-center">
          <Timer className="mx-auto h-12 w-12 text-slate-400" />
          <p className="mt-4 text-slate-500 dark:text-slate-400">
            {data?.note || "Insufficient data to calculate timing metrics."}
          </p>
        </div>
      </div>
    );
  }

  const formatDurationDisplay = (minutes: number | null) => {
    if (minutes === null) return "N/A";
    const total = Math.round(minutes);
    if (total < 60) return `${total}m`;
    const h = Math.floor(total / 60);
    const m = total % 60;
    if (h < 24) return `${h}h ${m}m`;
    const d = Math.floor(h / 24);
    return `${d}d ${h % 24}h`;
  };

  return (
    <div className="space-y-6">
      {/* Response Time */}
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
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Clock className="h-5 w-5 text-blue-600" />
            Average First Response Time
          </h3>
          {data.average_first_response_minutes === null ? (
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400">
              Insufficient Data
            </span>
          ) : (
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
              {formatDurationDisplay(data.average_first_response_minutes)}
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div
            className={`
              rounded-lg
              p-4
              text-center
              ${dark ? "bg-slate-800 border-slate-700" : "bg-slate-50 border-slate-200"}
            `}
          >
            <p className="text-sm text-slate-500 dark:text-slate-400">Avg Response</p>
            <p className="mt-2 text-3xl font-bold text-blue-600 dark:text-blue-400">
              {data.average_first_response_minutes !== null ? formatDurationDisplay(data.average_first_response_minutes) : "N/A"}
            </p>
          </div>

          <div
            className={`
              rounded-lg
              p-4
              text-center
              ${dark ? "bg-slate-800 border-slate-700" : "bg-slate-50 border-slate-200"}
            `}
          >
            <p className="text-sm text-slate-500 dark:text-slate-400">Target (SLA)</p>
            <p className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
              Based on SLA
            </p>
          </div>
        </div>
      </div>

      {/* Resolution Time */}
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
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Timer className="h-5 w-5 text-purple-600" />
            Average Resolution Time
          </h3>
          {data.average_resolution_minutes === null ? (
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400">
              Insufficient Data
            </span>
          ) : (
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300">
              {formatDurationDisplay(data.average_resolution_minutes)}
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div
            className={`
              rounded-lg
              p-4
              text-center
              ${dark ? "bg-slate-800 border-slate-700" : "bg-slate-50 border-slate-200"}
            `}
          >
            <p className="text-sm text-slate-500 dark:text-slate-400">Avg Resolution</p>
            <p className="mt-2 text-3xl font-bold text-purple-600 dark:text-purple-400">
              {data.average_resolution_minutes !== null ? formatDurationDisplay(data.average_resolution_minutes) : "N/A"}
            </p>
          </div>

          <div
            className={`
              rounded-lg
              p-4
              text-center
              ${dark ? "bg-slate-800 border-slate-700" : "bg-slate-50 border-slate-200"}
            `}
          >
            <p className="text-sm text-slate-500 dark:text-slate-400">SLA Target</p>
            <p className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
              Per Policy
            </p>
          </div>
        </div>
      </div>

      {/* Note */}
      <div
        className={`
          rounded-lg
          p-4
          border-l-4
          ${dark ? "bg-slate-800 border-slate-700 border-l-amber-500" : "bg-amber-50 border-l-amber-500"}
        `}
      >
        <p className="text-sm text-slate-700 dark:text-slate-300 flex items-start gap-2">
          <span className="mt-0.5 flex-shrink-0">ℹ️</span>
          <span className="text-slate-600 dark:text-slate-400">
            {data.note || "Metrics calculated from tickets with applicable timestamps. Returns N/A if insufficient data."}
          </span>
        </p>
      </div>
    </div>
  );
}

export default TimingMetrics;