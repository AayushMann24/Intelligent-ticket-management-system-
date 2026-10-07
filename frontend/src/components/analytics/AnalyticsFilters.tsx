import { forwardRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { Button } from "../common/Button";
import { Select } from "../common/Select";
import { Input } from "../common/Input";
import { useTheme } from "../../context/useTheme";
import { useReducedMotion } from "../../hooks/useReducedMotion";

export interface AnalyticsFilters {
  start_date?: string;
  end_date?: string;
  priority?: string;
  category?: string;
  ticket_type?: string;
  assignee_id?: number;
  granularity?: "daily" | "weekly" | "monthly";
}

interface AnalyticsFiltersProps {
  filters: AnalyticsFilters;
  onChange: (filters: Partial<AnalyticsFilters>) => void;
  presets: Array<{ label: string; startDate: Date; endDate: Date }>;
  onPresetSelect: (preset: { label: string; startDate: Date; endDate: Date }) => void;
  onClear: () => void;
  hasActiveFilters: boolean;
}

export const AnalyticsFilters = forwardRef<HTMLDivElement, AnalyticsFiltersProps>(
  (
    {
      filters,
      onChange,
      presets,
      onPresetSelect,
      onClear,
      hasActiveFilters,
    },
    ref
  ) => {
    const { theme } = useTheme();
    const dark = theme === "dark";
    const reducedMotion = useReducedMotion();

    const containerVariants = {
      initial: { opacity: 0, height: 0 },
      animate: { opacity: 1, height: "auto" },
      exit: { opacity: 0, height: 0 },
      transition: { duration: 0.3, ease: "easeOut" },
    };

    const itemVariants = {
      initial: { opacity: 0, y: -10 },
      animate: { opacity: 1, y: 0 },
      transition: { duration: 0.2 },
    };

    return (
      <motion.div
        ref={ref}
        className={`
          flex flex-wrap items-center gap-3
          rounded-xl
          border
          p-4
          transition-all
          duration-300
          ${dark ? "bg-slate-800/50 border-slate-700" : "bg-white border-slate-200"}
        `}
        initial={containerVariants.initial}
        animate={containerVariants.animate}
        exit={containerVariants.exit}
        variants={containerVariants}
      >
        {/* Date Range Presets */}
        <motion.div className="flex flex-wrap items-center gap-2" variants={itemVariants}>
          <span className="text-sm font-medium text-slate-500 dark:text-slate-400">Period:</span>
          {presets.map((preset) => (
            <motion.div key={preset.label} variants={itemVariants}>
              <Button
                onClick={() => onPresetSelect(preset)}
                variant="outline"
                size="sm"
                className="whitespace-nowrap"
              >
                {preset.label}
              </Button>
            </motion.div>
          ))}
        </motion.div>

        {/* Custom Date Range */}
        <motion.div className="flex items-center gap-2" variants={itemVariants}>
          <label htmlFor="start-date" className="sr-only">Start Date</label>
          <Input
            id="start-date"
            type="date"
            value={filters.start_date || ""}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => onChange({ start_date: e.target.value || undefined })}
            className="w-36"
            aria-label="Start date"
          />
          <span className="text-slate-400">to</span>
          <Input
            id="end-date"
            type="date"
            value={filters.end_date || ""}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => onChange({ end_date: e.target.value || undefined })}
            className="w-36"
            aria-label="End date"
          />
        </motion.div>

        {/* Priority Filter */}
        <motion.div variants={itemVariants}>
          <Select
            value={filters.priority || ""}
            onValueChange={(value: string) => onChange({ priority: value || undefined })}
            placeholder="Priority"
            options={[
              { value: "", label: "All Priorities" },
              { value: "Critical", label: "Critical" },
              { value: "High", label: "High" },
              { value: "Medium", label: "Medium" },
              { value: "Low", label: "Low" },
            ]}
            className="w-40"
            aria-label="Filter by priority"
          />
        </motion.div>

        {/* Category Filter */}
        <motion.div variants={itemVariants}>
          <Input
            type="text"
            placeholder="Category"
            value={filters.category || ""}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => onChange({ category: e.target.value || undefined })}
            className="w-40"
            aria-label="Filter by category"
          />
        </motion.div>

        {/* Ticket Type Filter */}
        <motion.div variants={itemVariants}>
          <Select
            value={filters.ticket_type || ""}
            onValueChange={(value: string) => onChange({ ticket_type: value || undefined })}
            placeholder="Ticket Type"
            options={[
              { value: "", label: "All Types" },
              { value: "INCIDENT", label: "Incident" },
              { value: "PROBLEM", label: "Problem" },
              { value: "CHANGE", label: "Change" },
              { value: "REQUEST", label: "Request" },
              { value: "TASK", label: "Task" },
            ]}
            className="w-40"
            aria-label="Filter by ticket type"
          />
        </motion.div>

        {/* Granularity */}
        <motion.div variants={itemVariants}>
          <Select
            value={filters.granularity || "daily"}
            onValueChange={(value: string) => onChange({ granularity: value as "daily" | "weekly" | "monthly" })}
            options={[
              { value: "daily", label: "Daily" },
              { value: "weekly", label: "Weekly" },
              { value: "monthly", label: "Monthly" },
            ]}
            className="w-36"
            aria-label="Trend granularity"
          />
        </motion.div>

        {/* Clear Filters */}
        <AnimatePresence>
          {hasActiveFilters && (
            <motion.div
              key="clear"
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              transition={{ duration: 0.2 }}
              className="ml-auto"
            >
              <Button onClick={onClear} variant="ghost" size="sm">
                <motion.span
                  animate={{ rotate: reducedMotion ? 0 : 360 }}
                  transition={{ duration: 0.3, ease: "easeOut" }}
                >
                  <X className="mr-1 h-4 w-4" />
                </motion.span>
                Clear
              </Button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    );
  }
);

AnalyticsFilters.displayName = "AnalyticsFilters";

export default AnalyticsFilters;