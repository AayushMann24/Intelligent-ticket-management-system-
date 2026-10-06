export default function LoadingSkeleton({ className = "", rows = 3 }: { className?: string; rows?: number }) {
  return (
    <div className={`space-y-4 ${className}`}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="animate-pulse">
          <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-3/4 mb-2" />
          <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded w-full" />
        </div>
      ))}
    </div>
  );
}