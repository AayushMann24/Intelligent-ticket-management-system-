import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { useTheme } from "../../context/useTheme";

interface TicketTypeChartProps {
  data: Array<{ ticket_type: string; count: number }>;
}

const TYPE_COLORS: Record<string, string> = {
  INCIDENT: "#ef4444",
  PROBLEM: "#f59e0b",
  CHANGE: "#22c55e",
  REQUEST: "#3b82f6",
  TASK: "#8b5cf6",
  DEFAULT: "#94a3b8",
};

function TicketTypeChart({ data }: TicketTypeChartProps) {
  const { theme } = useTheme();
  const dark = theme === "dark";

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center">
        <p className="text-slate-500 dark:text-slate-400">No ticket type data available.</p>
      </div>
    );
  }

  // Filter out zero counts for pie chart
  const chartData = data.filter((d) => d.count > 0);

  if (chartData.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center">
        <p className="text-slate-500 dark:text-slate-400">No ticket type data available.</p>
      </div>
    );
  }

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            dataKey="count"
            nameKey="ticket_type"
            innerRadius={70}
            outerRadius={100}
            paddingAngle={3}
          >
            {chartData.map((_, index) => (
              <Cell
                key={index}
                fill={TYPE_COLORS[chartData[index]?.ticket_type] || TYPE_COLORS.DEFAULT}
              />
            ))}
          </Pie>

          <Tooltip
            contentStyle={{
              backgroundColor: dark ? "#0f172a" : "#ffffff",
              border: dark ? "1px solid #334155" : "1px solid #e2e8f0",
              borderRadius: "12px",
              color: dark ? "#ffffff" : "#0f172a",
            }}
            formatter={(value: number | string | ReadonlyArray<number | string> | undefined) => [typeof value === "number" ? value : 0, "Tickets"]}
          />
        </PieChart>
      </ResponsiveContainer>

      <Legend
        layout="vertical"
        align="right"
        verticalAlign="middle"
        iconType="circle"
        iconSize={10}
        formatter={(value) => (
          <span className="text-slate-600 dark:text-slate-300">{value}</span>
        )}
      />

      <div className="mt-4 flex flex-wrap justify-center gap-4">
        {chartData.map((item) => (
          <div key={item.ticket_type} className="flex items-center gap-2">
            <div
              className="h-3 w-3 rounded-full"
              style={{ backgroundColor: TYPE_COLORS[item.ticket_type] || TYPE_COLORS.DEFAULT }}
            />
            <span className="text-slate-600 dark:text-slate-300">{item.ticket_type}</span>
            <span className="font-bold text-slate-900 dark:text-white">{item.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TicketTypeChart;