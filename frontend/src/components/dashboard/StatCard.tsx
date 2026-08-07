import type { ReactNode } from "react";

interface StatCardProps {
  title: string;
  value: number;
  icon: ReactNode;
  color: string;
  onClick?: () => void;
}

export default function StatCard({
  title,
  value,
  icon,
  color,
  onClick,
}: StatCardProps) {
  return (
    <div
      onClick={onClick}
      className="
        cursor-pointer
        rounded-2xl
        border
        border-slate-200
        bg-white
        p-6
        shadow-sm
        transition-all
        duration-300
        hover:-translate-y-1
        hover:border-blue-500
        hover:shadow-xl

        dark:border-slate-800
        dark:bg-slate-900
      "
    >
      <div className="flex items-center justify-between">

        <div>

          <p className="text-slate-500 dark:text-slate-400">
            {title}
          </p>

          <h2 className="mt-4 text-5xl font-bold text-slate-900 dark:text-white">
            {value}
          </h2>

        </div>

        <div className={`rounded-2xl p-5 text-white ${color}`}>
          {icon}
        </div>

      </div>
    </div>
  );
}