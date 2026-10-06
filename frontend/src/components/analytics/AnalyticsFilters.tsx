import { forwardRef } from "react";
import { X } from "lucide-react";
import { Button } from "../common/Button";
import { Select } from "../common/Select";
import { Input } from "../common/Input";
import { useTheme } from "../../context/useTheme";

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

    return (
      <div
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
      >
        {/* Date Range Presets */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-medium text-slate-500 dark:text-slate-400">Period:</span>
          {presets.map((preset) => (
            <Button
              key={preset.label}
              onClick={() => onPresetSelect(preset)}
              variant="outline"
              size="sm"
              className="whitespace-nowrap"
            >
              {preset.label}
            </Button>
          ))}
        </div>

        {/* Custom Date Range */}
        <div className="flex items-center gap-2">
          <label htmlFor="start-date" className="sr-only">
            Start Date
          </label>
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
        </div>

        {/* Priority Filter */}
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

        {/* Category Filter */}
        <Input
          type="text"
          placeholder="Category"
          value={filters.category || ""}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => onChange({ category: e.target.value || undefined })}
          className="w-40"
          aria-label="Filter by category"
        />

        {/* Ticket Type Filter */}
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

        {/* Granularity */}
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

        {/* Clear Filters */}
        {hasActiveFilters && (
          <Button onClick={onClear} variant="ghost" size="sm" className="ml-auto">
            <X className="mr-1 h-4 w-4" />
            Clear
          </Button>
        )}
      </div>
    );
  }
);

AnalyticsFilters.displayName = "AnalyticsFilters";

export default AnalyticsFilters;