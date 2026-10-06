import { Users, CheckCircle, AlertTriangle, TrendingUp } from "lucide-react";

interface TechnicianWorkloadItem {
  technician_id: number;
  technician_name: string;
  technician_email: string;
  role: string;
  tickets_currently_assigned: number;
  open_assigned_tickets: number;
  tickets_resolved: number;
  escalations_received: number;
  escalations_initiated: number;
}

interface TechnicianWorkloadProps {
  data: TechnicianWorkloadItem[];
}

function TechnicianWorkload({ data }: TechnicianWorkloadProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center">
        <p className="text-slate-500 dark:text-slate-400">No technician data available.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-200 dark:border-slate-700">
            <th className="py-3 px-4 text-left text-sm font-medium text-slate-500 dark:text-slate-400">
              Technician
            </th>
            <th className="py-3 px-4 text-right text-sm font-medium text-slate-500 dark:text-slate-400">
              <Users className="inline h-4 w-4" /> Assigned
            </th>
            <th className="py-3 px-4 text-right text-sm font-medium text-slate-500 dark:text-slate-400">
              <AlertTriangle className="inline h-4 w-4" /> Open
            </th>
            <th className="py-3 px-4 text-right text-sm font-medium text-slate-500 dark:text-slate-400">
              <CheckCircle className="inline h-4 w-4" /> Resolved
            </th>
            <th className="py-3 px-4 text-right text-sm font-medium text-slate-500 dark:text-slate-400">
              <AlertTriangle className="inline h-4 w-4" /> Received
            </th>
            <th className="py-3 px-4 text-right text-sm font-medium text-slate-500 dark:text-slate-400">
              <TrendingUp className="inline h-4 w-4" /> Initiated
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
          {data.map((tech) => (
            <tr
              key={tech.technician_id}
              className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
            >
              <td className="py-4 px-4">
                <div className="flex items-center gap-3">
                  <div
                    className="h-10 w-10 rounded-full flex items-center justify-center text-white text-sm font-medium"
                    style={{
                      backgroundColor:
                        tech.role === "Admin"
                          ? "#ef4444"
                          : tech.role === "Technician"
                          ? "#3b82f6"
                          : "#22c55e",
                    }}
                  >
                    {tech.technician_name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium text-slate-900 dark:text-white">
                      {tech.technician_name}
                    </p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {tech.technician_email}
                    </p>
                    <span
                      className={`
                        inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
                        ${tech.role === "Admin"
                          ? "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300"
                          : "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"}
                      `}
                    >
                      {tech.role}
                    </span>
                  </div>
                </div>
              </td>
              <td className="py-4 px-4 text-right font-medium text-slate-900 dark:text-white">
                {tech.tickets_currently_assigned}
              </td>
              <td className="py-4 px-4 text-right text-slate-900 dark:text-white">
                {tech.open_assigned_tickets}
              </td>
              <td className="py-4 px-4 text-right font-medium text-green-600 dark:text-green-400">
                {tech.tickets_resolved}
              </td>
              <td className="py-4 px-4 text-right font-medium text-red-600 dark:text-red-400">
                {tech.escalations_received}
              </td>
              <td className="py-4 px-4 text-right font-medium text-purple-600 dark:text-purple-400">
                {tech.escalations_initiated}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TechnicianWorkload;