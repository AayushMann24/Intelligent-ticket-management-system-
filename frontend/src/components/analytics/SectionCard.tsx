import { forwardRef } from "react";
import { motion } from "framer-motion";
import { useTheme } from "../../context/useTheme";

interface SectionCardProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

const SectionCard = forwardRef<HTMLDivElement, SectionCardProps>(
  ({ title, children, className = "" }, ref) => {
    const { theme } = useTheme();
    const dark = theme === "dark";

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
          ${dark ? "border-slate-800 dark:border-slate-800 dark:bg-slate-900" : "border-slate-200"}
          ${className}
        `}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: [0, 0, 0.2, 1] }}
      >
        <motion.div
          className="mb-4 flex items-center justify-between"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2 }}
        >
          <motion.h2
            className="text-xl font-semibold text-slate-900 dark:text-white"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {title}
          </motion.h2>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          {children}
        </motion.div>
      </motion.div>
    );
  }
);

SectionCard.displayName = "SectionCard";

export default SectionCard;