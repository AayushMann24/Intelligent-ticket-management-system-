import {
  Plus,
  Users,
  Bot,
  BarChart3,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

const actions = [
  {
    title: "New Ticket",
    icon: Plus,
    color: "bg-blue-600",
    path: "/tickets",
  },
  {
    title: "Manage Users",
    icon: Users,
    color: "bg-green-600",
    path: "/users",
  },
  {
    title: "AI Assistant",
    icon: Bot,
    color: "bg-purple-600",
    path: "/assistant",
  },
  {
    title: "Analytics",
    icon: BarChart3,
    color: "bg-orange-500",
    path: "/analytics",
  },
];

export default function QuickActions() {

  const navigate = useNavigate();

  return (

    <div className="mt-10">

      <h2 className="mb-5 text-2xl font-bold text-white">
        Quick Actions
      </h2>

      <div className="grid grid-cols-2 gap-6 lg:grid-cols-4">

        {actions.map((action) => {

          const Icon = action.icon;

          return (

            <button
              key={action.title}
              onClick={() => navigate(action.path)}
              className="
                rounded-2xl
                border
                border-zinc-800
                bg-zinc-900
                p-6
                transition-all
                duration-300
                hover:-translate-y-1
                hover:border-blue-500
                hover:shadow-xl
              "
            >

              <div
                className={`mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-xl ${action.color}`}
              >
                <Icon size={28} className="text-white" />
              </div>

              <h3 className="font-semibold text-white">
                {action.title}
              </h3>

            </button>

          );

        })}

      </div>

    </div>

  );

}