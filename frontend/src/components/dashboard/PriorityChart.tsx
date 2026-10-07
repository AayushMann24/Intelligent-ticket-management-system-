import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { motion } from "framer-motion";

interface ChartData {
  name: string;
  value: number;
}

interface PriorityChartProps {
  data: ChartData[];
}

const COLORS = ["#ef4444", "#f59e0b", "#22c55e"];

export default function PriorityChart({ data }: PriorityChartProps) {
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
        Priority Breakdown
      </motion.h2>

      <motion.div
        className="h-80"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.1, type: "spring", stiffness: 200, damping: 20 }}
      >
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius={70}
              outerRadius={100}
              paddingAngle={3}
            >
              {data.map((_, index) => (
                <Cell key={index} fill={COLORS[index]} />
              ))}
            </Pie>

            <Tooltip
              contentStyle={{
                backgroundColor: "#ffffff",
                borderRadius: "12px",
                border: "1px solid #e2e8f0",
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </motion.div>

      <motion.div
        className="mt-6 flex justify-around"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.3 }}
      >
        {data.map((item, index) => (
          <motion.div
            key={item.name}
            className="flex items-center gap-2"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: 0.35 + index * 0.05 }}
          >
            <motion.div
              className="h-3 w-3 rounded-full"
              style={{ backgroundColor: COLORS[index] }}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
            />
            <span className="text-slate-600 dark:text-slate-300">{item.name}</span>
            <span className="font-bold text-slate-900 dark:text-white">{item.value}</span>
          </motion.div>
        ))}
      </motion.div>
    </motion.div>
  );
}