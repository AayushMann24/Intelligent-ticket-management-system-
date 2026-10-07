import { motion, type HTMLMotionProps } from "framer-motion";
import type { ReactNode } from "react";
import { useReducedMotion } from "../../hooks/useReducedMotion";

interface StatCardProps {
  title: string;
  value: number;
  icon: ReactNode;
  color: string;
  onClick?: () => void;
}

export default function StatCard({ title, value, icon, color, onClick }: StatCardProps) {
  const reducedMotion = useReducedMotion();
  const isClickable = typeof onClick === "function";

  const hoverTransition = { duration: 0.2, ease: "easeOut" as const };

  const motionProps: Partial<HTMLMotionProps<"div">> = isClickable && !reducedMotion
    ? {
        whileHover: {
          y: -4,
          boxShadow: "0 20px 40px -10px rgba(0, 0, 0, 0.15)",
          transition: hoverTransition,
        },
        whileTap: { scale: 0.98 },
      }
    : {};

  return (
    <motion.div
      onClick={onClick}
      className={`
        cursor-pointer rounded-2xl border border-slate-200 bg-white p-6 shadow-sm
        transition-all duration-300 hover:border-blue-500 dark:border-slate-800 dark:bg-slate-900
        ${isClickable ? "hover:shadow-xl" : ""}
      `}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      {...motionProps}
    >
      <div className="flex items-center justify-between">
        <div>
          <motion.p
            className="text-slate-500 dark:text-slate-400"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: 0.1 }}
          >
            {title}
          </motion.p>
          <motion.h2
            className="mt-4 text-5xl font-bold text-slate-900 dark:text-white"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 25, delay: 0.15 }}
          >
            {value}
          </motion.h2>
        </div>
        <motion.div
          className={`rounded-2xl p-5 text-white ${color}`}
          initial={{ opacity: 0, scale: 0.8, rotate: -10 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 25, delay: 0.2 }}
        >
          {icon}
        </motion.div>
      </div>
    </motion.div>
  );
}