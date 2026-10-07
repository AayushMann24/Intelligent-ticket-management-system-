import { forwardRef, type ButtonHTMLAttributes } from "react";
import { useReducedMotion } from "../../hooks/useReducedMotion";

interface BadgeProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: "primary" | "secondary";
  pulse?: boolean;
}

const Badge = forwardRef<HTMLButtonElement, BadgeProps>(
  ({ children, variant = "primary", className = "", pulse = false, ...props }, ref) => {
    const reducedMotion = useReducedMotion();

    const base = "px-5 py-2 rounded-xl font-medium transition-all duration-200";

    const styles = {
      primary: "bg-blue-600 hover:bg-blue-700 text-white",
      secondary: "bg-zinc-800 hover:bg-zinc-700 text-white border border-zinc-700",
    };

    const hoverClass = reducedMotion ? "" : "hover:scale-105 active:scale-95";
    const pulseClass = pulse && !reducedMotion ? "animate-pulse" : "";

    return (
      <button
        ref={ref}
        className={`${base} ${styles[variant]} ${className} ${hoverClass} ${pulseClass}`}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Badge.displayName = "Badge";

export default Badge;