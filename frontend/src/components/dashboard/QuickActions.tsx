import {
  BarChart3,
  Bot,
  Plus,
  Users,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

export default function QuickActions() {
  const navigate = useNavigate();

  const actions = [
    {
      title: "New Ticket",
      icon: <Plus size={34} />,
      color: "bg-blue-600",
      onClick: () => navigate("/tickets?create=true"),
  },
    {
      title: "Manage Users",
      icon: <Users size={34} />,
      color: "bg-green-600",
      onClick: () => navigate("/users"),
    },
    {
      title: "AI Assistant",
      icon: <Bot size={34} />,
      color: "bg-purple-600",
      onClick: () => navigate("/assistant"),
    },
    {
      title: "Analytics",
      icon: <BarChart3 size={34} />,
      color: "bg-orange-500",
      onClick: () => navigate("/analytics"),
    },
  ];

  return (
    <>
      <h2 className="mb-6 text-2xl font-bold text-white">
        Quick Actions
      </h2>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        {actions.map((action) => (
          <div
            key={action.title}
            onClick={action.onClick}
            className="
              cursor-pointer
              rounded-2xl
              border
              border-zinc-800
              bg-zinc-900
              p-8
              transition-all
              duration-300
              hover:-translate-y-1
              hover:border-blue-500
              hover:shadow-lg
              hover:shadow-blue-500/10
            "
          >
            <div className="flex flex-col items-center">

              <div
                className={`${action.color} mb-6 rounded-2xl p-5 text-white`}
              >
                {action.icon}
              </div>

              <h3 className="text-xl font-semibold text-white">
                {action.title}
              </h3>

            </div>
          </div>
        ))}
      </div>
    </>
  );
}