import { useReducedMotion } from "../../hooks/useReducedMotion";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  onClick?: () => void;
}

export default function Card({
  children,
  className = "",
  hover = false,
  onClick,
}: CardProps) {
  const reducedMotion = useReducedMotion();
  const cursorClass = hover || onClick ? "cursor-pointer" : "";
  const hoverClass = hover && !reducedMotion ? "hover:-translate-y-1 hover:shadow-xl" : "";

  return (
    <div
      className={`
        bg-white
        border
        border-slate-200
        rounded-2xl
        p-6
        shadow-sm
        transition-all
        duration-300
        dark:border-slate-800
        dark:bg-slate-900
        ${cursorClass}
        ${hoverClass}
        ${className}
      `}
    >
      {children}
    </div>
  );
}