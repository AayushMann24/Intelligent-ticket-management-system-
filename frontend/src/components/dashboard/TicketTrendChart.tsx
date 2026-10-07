import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { motion } from "framer-motion";
import { useTheme } from "../../context/useTheme";
import type { TicketTrend } from "../../services/dashboardService";

interface TicketTrendChartProps {
  data: TicketTrend[];
}

export default function TicketTrendChart({ data }: TicketTrendChartProps) {
  const { theme } = useTheme();
  const dark = theme === "dark";

  if (!data || data.length === 0) {
    return (
      <motion.div
        className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 dark:border-slate-800 dark:bg-slate-900"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
      >
        <motion.h2
          className="mb-6 text-xl font-semibold text-slate-900 dark:text-white"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2 }}
        >
          Ticket Trend
        </motion.h2>

        <motion.div
          className="flex h-80 items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <p className="text-slate-500 dark:text-slate-400">No ticket trend data available.</p>
        </motion.div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 dark:border-slate-800 dark:bg-slate-900"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      <motion.h2
        className="mb-6 text-xl font-semibold text-slate-900 dark:text-white"
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.2 }}
      >
        Ticket Trend
      </motion.h2>

      <motion.div
        className="h-80"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.1, type: "spring", stiffness: 200, damping: 20 }}
      >
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={dark ? "#334155" : "#e2e8f0"} />
            <XAxis dataKey="date" stroke={dark ? "#94a3b8" : "#64748b"} tick={{ fill: dark ? "#94a3b8" : "#64748b" }} />
            <YAxis stroke={dark ? "#94a3b8" : "#64748b"} tick={{ fill: dark ? "#94a3b8" : "#64748b" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: dark ? "#0f172a" : "#ffffff",
                border: dark ? "1px solid #334155" : "1px solid #e2e8f0",
                borderRadius: "12px",
                color: dark ? "#ffffff" : "#0f172a",
              }}
            />
            <Line
              type="monotone"
              dataKey="tickets"
              stroke="#2563eb"
              strokeWidth={3}
              dot={{ r: 5, fill: "#2563eb" }}
              activeDot={{ r: 8 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </motion.div>
    </motion.div>
  );
}