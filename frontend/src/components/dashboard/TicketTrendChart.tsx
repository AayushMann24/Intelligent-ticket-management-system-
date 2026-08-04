import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import type { TrendData } from "../../services/dashboardService";
interface TicketTrendChartProps {
  data: TrendData[];
}

export default function TicketTrendChart({
  data,
}: TicketTrendChartProps) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">

      <h2 className="mb-6 text-xl font-semibold text-white">
        Ticket Trend
      </h2>

      <div className="h-80">

        <ResponsiveContainer width="100%" height="100%">

          <LineChart data={data}>

            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#3f3f46"
            />

            <XAxis
              dataKey="date"
              stroke="#a1a1aa"
            />

            <YAxis
              stroke="#a1a1aa"
            />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="tickets"
              stroke="#2563eb"
              strokeWidth={3}
              dot={{ r: 5 }}
              activeDot={{ r: 8 }}
            />

          </LineChart>

        </ResponsiveContainer>

      </div>

    </div>
  );
}