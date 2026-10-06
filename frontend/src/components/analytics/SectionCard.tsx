import { forwardRef } from "react";

interface SectionCardProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

const SectionCard = forwardRef<HTMLDivElement, SectionCardProps>(
  ({ title, children, className = "" }, ref) => {
    const dark = true; // We'll determine this from theme context in practice

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
          ${dark ? "border-slate-800 bg-white dark:border-slate-800 dark:bg-slate-900" : "border-slate-200"}
          ${className}
        `}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
            {title}
          </h2>
        </div>
        <div>{children}</div>
      </div>
    );
  }
);

SectionCard.displayName = "SectionCard";

export default SectionCard;