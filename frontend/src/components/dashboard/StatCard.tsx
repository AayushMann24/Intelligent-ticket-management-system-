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
        border-zinc-800
        bg-zinc-900
        p-6
        transition-all
        duration-300
        hover:-translate-y-1
        hover:border-blue-500
        hover:shadow-lg
        hover:shadow-blue-500/10
      "
    >
      <div className="flex items-center justify-between">

        <div>

          <p className="text-zinc-400">
            {title}
          </p>

          <h2 className="mt-4 text-5xl font-bold text-white">
            {value}
          </h2>

        </div>

        <div
          className={`rounded-2xl p-5 text-white ${color}`}
        >
          {icon}
        </div>

      </div>

    </div>
  );
}