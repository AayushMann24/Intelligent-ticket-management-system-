import type { ReactNode } from "react";
import { motion } from "framer-motion";

interface StatCardProps {
  title: string;
  value: number;
  icon: ReactNode;
  color: string;
}

export default function StatCard({
  title,
  value,
  icon,
  color,
}: StatCardProps) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      transition={{ duration: 0.2 }}
      className="
        rounded-2xl
        border
        border-zinc-800
        bg-zinc-900
        p-6
        shadow-lg
      "
    >
      <div className="flex items-center justify-between">

        <div>
          <p className="text-sm text-zinc-400">
            {title}
          </p>

          <h2 className="mt-4 text-4xl font-bold text-white">
            {value}
          </h2>
        </div>

        <div
          className={`flex h-14 w-14 items-center justify-center rounded-xl text-white ${color}`}
        >
          {icon}
        </div>

      </div>
    </motion.div>
  );
}