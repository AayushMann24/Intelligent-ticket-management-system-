import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { useTheme } from "../../context/useTheme";

interface TrendPoint {
  period: string;
  tickets_created: number;
  tickets_resolved: number;
  sla_breaches: number;
  escalations: number;
}

interface TicketTrendChartProps {
  data: TrendPoint[];
  granularity: string;
}

function TicketTrendChart({ data, granularity }: TicketTrendChartProps) {
  const { theme } = useTheme();
  const dark = theme === "dark";

  if (!data || data.length === 0) {
    return (
      <div
        className="
          rounded-2xl
          border
          border-slate-200
          bg-white
          p-6
          shadow-sm
          transition-all
          duration-300
          dark:border-slate-800
          dark:bg-slate-900
        "
      >
        <h2 className="mb-6 text-xl font-semibold text-slate-900 dark:text-white">
          Ticket Trends
        </h2>
        <div className="flex h-80 items-center justify-center">
          <p className="text-slate-500 dark:text-slate-400">
            No trend data available for the selected period.
          </p>
        </div>
      </div>
    );
  }

  // Format period for display based on granularity
  const formatPeriod = (period: string) => {
    if (granularity === "monthly") {
      // Format YYYY-MM to MMM YYYY
      const [year, month] = period.split("-");
      const date = new Date(parseInt(year), parseInt(month) - 1);
      return date.toLocaleDateString("en-US", { month: "short", year: "numeric" });
    }
    if (granularity === "weekly") {
      // Format YYYY-WW to Week WW, YYYY
      return period.replace("-", " Week ");
    }
    return period; // daily
  };

  const chartData = data.map((d) => ({
    ...d,
    formattedPeriod: formatPeriod(d.period),
  }));

  return (
    <div
      className="
        rounded-2xl
        border
        border-slate-200
        bg-white
        p-6
        shadow-sm
        transition-all
        duration-300
        dark:border-slate-800
        dark:bg-slate-900
      "
    >
      <div className="mb-4 flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
          Ticket Trends ({granularity.charAt(0).toUpperCase() + granularity.slice(1)})
        </h2>
        <Legend
          layout="horizontal"
          align="center"
          formatter={(value) => (
            <span className="text-slate-600 dark:text-slate-300">{value}</span>
          )}
        />
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 10, right: 20, left: 0, bottom: 10 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke={dark ? "#334155" : "#e2e8f0"}
            />
            <XAxis
              dataKey="formattedPeriod"
              stroke={dark ? "#94a3b8" : "#64748b"}
              tick={{ fill: dark ? "#94a3b8" : "#64748b" }}
              tickLine={false}
              interval={Math.max(1, Math.floor(data.length / 10))}
            />
            <YAxis
              stroke={dark ? "#94a3b8" : "#64748b"}
              tick={{ fill: dark ? "#94a3b8" : "#64748b" }}
              tickFormatter={(value) => (value >= 1000 ? `${(value / 1000).toFixed(1)}k` : value)}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: dark ? "#0f172a" : "#ffffff",
                border: dark ? "1px solid #334155" : "1px solid #e2e8f0",
                borderRadius: "12px",
                color: dark ? "#ffffff" : "#0f172a",
              }}
              formatter={(value: number | string | ReadonlyArray<number | string> | undefined, name: string | number | undefined) => [
                typeof value === "number" ? value : 0,
                name === "tickets_created"
                  ? "Created"
                  : name === "tickets_resolved"
                  ? "Resolved"
                  : name === "sla_breaches"
                  ? "SLA Breaches"
                  : "Escalations",
              ] as [number, string]}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="tickets_created"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={{ r: 4, fill: "#3b82f6" }}
              activeDot={{ r: 6 }}
              name="Created"
            />
            <Line
              type="monotone"
              dataKey="tickets_resolved"
              stroke="#22c55e"
              strokeWidth={3}
              dot={{ r: 4, fill: "#22c55e" }}
              activeDot={{ r: 6 }}
              name="Resolved"
            />
            <Line
              type="monotone"
              dataKey="sla_breaches"
              stroke="#ef4444"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ r: 4, fill: "#ef4444" }}
              activeDot={{ r: 6 }}
              name="SLA Breaches"
            />
            <Line
              type="monotone"
              dataKey="escalations"
              stroke="#8b5cf6"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ r: 4, fill: "#8b5cf6" }}
              activeDot={{ r: 6 }}
              name="Escalations"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default TicketTrendChart;