import type { ButtonHTMLAttributes, ReactNode } from "react";
interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: "primary" | "secondary";
}

export default function Button({
  children,
  variant = "primary",
  className = "",
  ...props
}: ButtonProps) {
  const base =
    "px-5 py-2 rounded-xl font-medium transition-all duration-200";

  const styles = {
    primary:
      "bg-blue-600 hover:bg-blue-700 text-white",
    secondary:
      "bg-zinc-800 hover:bg-zinc-700 text-white border border-zinc-700",
  };

  return (
    <button
      className={`${base} ${styles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}