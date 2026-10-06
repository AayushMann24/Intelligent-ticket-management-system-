import { forwardRef } from "react";

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
    const isClickable = typeof onClick === "function";

    return (
      <div
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
          ${isClickable ? "cursor-pointer hover:shadow-lg" : "hover:shadow-md"}
        `}
        onClick={onClick}
        role={isClickable ? "button" : undefined}
        tabIndex={isClickable ? 0 : undefined}
        onKeyDown={(e) => isClickable && (e.key === "Enter" || e.key === " ") && onClick()}
      >
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-500 dark:text-slate-400 truncate">
              {title}
            </p>
            <h2 className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
              {value}
            </h2>
            {description && (
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                {description}
              </p>
            )}
            {trend && (
              <div className="mt-2 flex items-center gap-1">
                <span
                  className={`text-xs font-medium ${
                    trend.positive
                      ? "text-green-600 dark:text-green-400"
                      : "text-red-600 dark:text-red-400"
                  }`}
                >
                  {trend.positive ? "▲" : "▼"} {Math.abs(trend.value)}%
                </span>
                <span className="text-xs text-slate-500 dark:text-slate-400">
                  {trend.label}
                </span>
              </div>
            )}
          </div>

          <div className={`rounded-2xl p-5 text-white ${color}`}>
            {icon}
          </div>
        </div>
      </div>
    );
  }
);

KPICard.displayName = "KPICard";

export default KPICard;