import { forwardRef } from "react";
import { motion, type HTMLMotionProps } from "framer-motion";
import { useReducedMotion } from "../../hooks/useReducedMotion";

interface KPICardProps {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
  description?: string;
  onClick?: () => void;
  trend?: {
    value: number;
    label: string;
    positive: boolean;
  };
}

const KPICard = forwardRef<HTMLDivElement, KPICardProps>(
  ({ title, value, icon, color, description, onClick, trend }, ref) => {
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
        ref={ref}
        className={`
          rounded-2xl
          border
          bg-white
          p-6
          shadow-sm
          transition-all
          duration-300
          dark:border-slate-800
          dark:bg-slate-900
          ${isClickable ? "cursor-pointer" : ""}
        `}
        onClick={onClick}
        role={isClickable ? "button" : undefined}
        tabIndex={isClickable ? 0 : undefined}
        onKeyDown={(e) => isClickable && (e.key === "Enter" || e.key === " ") && onClick()}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        {...motionProps}
      >
        <div className="flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2 }}
          >
            <motion.p
              className="text-sm text-slate-500 dark:text-slate-400 truncate"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.05 }}
            >
              {title}
            </motion.p>
            <motion.h2
              className="mt-2 text-3xl font-bold text-slate-900 dark:text-white"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ type: "spring", stiffness: 300, damping: 25, delay: 0.1 }}
            >
              {value}
            </motion.h2>
            {description && (
              <motion.p
                className="mt-1 text-xs text-slate-500 dark:text-slate-400"
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: 0.15 }}
              >
                {description}
              </motion.p>
            )}
            {trend && (
              <motion.div
                className="mt-2 flex items-center gap-1"
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: 0.2 }}
              >
                <span
                  className={`text-xs font-medium ${
                    trend.positive
                      ? "text-green-600 dark:text-green-400"
                      : "text-red-600 dark:text-red-400"
                  }`}
                >
                  {trend.positive ? "▲" : "▼"} {Math.abs(trend.value)}%
                </span>
                <span className="text-xs text-slate-500 dark:text-slate-400">{trend.label}</span>
              </motion.div>
            )}
          </motion.div>

          <motion.div
            className={`rounded-2xl p-5 text-white ${color}`}
            initial={{ opacity: 0, scale: 0.8, rotate: -10 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 25, delay: 0.15 }}
          >
            {icon}
          </motion.div>
        </div>
      </motion.div>
    );
  }
);

KPICard.displayName = "KPICard";

export default KPICard;