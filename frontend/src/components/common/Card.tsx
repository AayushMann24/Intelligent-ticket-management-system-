interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export default function Card({
  children,
  className = "",
}: CardProps) {
  return (
    <div
      className={`
        bg-zinc-900
        border
        border-zinc-800
        rounded-2xl
        p-6
        shadow-lg
        ${className}
      `}
    >
      {children}
    </div>
  );
}