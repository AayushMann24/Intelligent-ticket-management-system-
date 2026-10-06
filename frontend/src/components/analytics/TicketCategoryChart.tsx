import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useTheme } from "../../context/useTheme";

interface TicketCategoryChartProps {
  data: Array<{ category: string; count: number }>;
}

function TicketCategoryChart({ data }: TicketCategoryChartProps) {
  const { theme } = useTheme();
  const dark = theme === "dark";

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center">
        <p className="text-slate-500 dark:text-slate-400">No category data available.</p>
      </div>
    );
  }

  // Sort by count descending and take top 10
  const sortedData = [...data].sort((a, b) => b.count - a.count).slice(0, 10);

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={sortedData}
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
            dataKey="category"
            stroke={dark ? "#94a3b8" : "#64748b"}
            tick={{ fill: dark ? "#94a3b8" : "#64748b" }}
            width={140}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: dark ? "#0f172a" : "#ffffff",
              border: dark ? "1px solid #334155" : "1px solid #e2e8f0",
              borderRadius: "12px",
              color: dark ? "#ffffff" : "#0f172a",
            }}
            formatter={(value: number | string | ReadonlyArray<number | string> | undefined, name: string | number | undefined) => [(typeof value === "number" ? value : 0), String(name ?? "")]}
          />
          <Bar
            dataKey="count"
            fill="#8b5cf6"
            radius={[0, 4, 4, 0]}
            maxBarSize={40}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TicketCategoryChart;