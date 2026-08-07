import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface ChartData {
  name: string;
  value: number;
}

interface PriorityChartProps {
  data: ChartData[];
}

const COLORS = [
  "#ef4444",
  "#f59e0b",
  "#22c55e",
];

export default function PriorityChart({
  data,
}: PriorityChartProps) {
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
        Priority Breakdown
      </h2>

      <div className="h-80">

        <ResponsiveContainer
          width="100%"
          height="100%"
        >
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

                <Cell
                  key={index}
                  fill={COLORS[index]}
                />

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

      </div>

      <div className="mt-6 flex justify-around">

        {data.map((item, index) => (

          <div
            key={item.name}
            className="flex items-center gap-2"
          >

            <div
              className="h-3 w-3 rounded-full"
              style={{
                backgroundColor:
                  COLORS[index],
              }}
            />

            <span className="text-slate-600 dark:text-slate-300">
              {item.name}
            </span>

            <span className="font-bold text-slate-900 dark:text-white">
              {item.value}
            </span>

          </div>

        ))}

      </div>

    </div>
  );
}