import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Cell } from "recharts";
import { useTheme } from "../../context/useTheme";

interface TicketPriorityChartProps {
  data: Array<{ priority: string; count: number }>;
}

const PRIORITY_COLORS: Record<string, string> = {
  Critical: "#ef4444",
  High: "#f59e0b",
  Medium: "#22c55e",
  Low: "#64748b",
};

const PRIORITY_ORDER = ["Critical", "High", "Medium", "Low"];

function TicketPriorityChart({ data }: TicketPriorityChartProps) {
  const { theme } = useTheme();
  const dark = theme === "dark";

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center">
        <p className="text-slate-500 dark:text-slate-400">No priority data available.</p>
      </div>
    );
  }

  // Sort data by priority order
  const sortedData = [...data].sort((a, b) => {
    const indexA = PRIORITY_ORDER.indexOf(a.priority);
    const indexB = PRIORITY_ORDER.indexOf(b.priority);
    return (indexA === -1 ? 99 : indexA) - (indexB === -1 ? 99 : indexB);
  });

  // Ensure all priorities are shown even with zero counts
  const chartData = PRIORITY_ORDER.map((priority) => {
    const existing = sortedData.find((d) => d.priority === priority);
    return {
      name: priority,
      value: existing?.count ?? 0,
      color: PRIORITY_COLORS[priority] || "#94a3b8",
    };
  });

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 10, right: 20, left: 0, bottom: 10 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke={dark ? "#334155" : "#e2e8f0"}
            vertical={false}
          />
          <XAxis
            type="number"
            stroke={dark ? "#94a3b8" : "#64748b"}
            tick={{ fill: dark ? "#94a3b8" : "#64748b" }}
            tickFormatter={(value) => (value >= 1000 ? `${(value / 1000).toFixed(1)}k` : value)}
          />
          <YAxis
            type="category"
            dataKey="name"
            stroke={dark ? "#94a3b8" : "#64748b"}
            tick={{ fill: dark ? "#94a3b8" : "#64748b" }}
            width={80}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: dark ? "#0f172a" : "#ffffff",
              border: dark ? "1px solid #334155" : "1px solid #e2e8f0",
              borderRadius: "12px",
              color: dark ? "#ffffff" : "#0f172a",
            }}
            formatter={(value: number | string | ReadonlyArray<number | string> | undefined) => [
              typeof value === "number" ? value : 0,
              "Tickets",
            ]}
          />
          <Legend />
          <Bar
            dataKey="value"
            fill="#2563eb"
            radius={[0, 4, 4, 0]}
            maxBarSize={40}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TicketPriorityChart;