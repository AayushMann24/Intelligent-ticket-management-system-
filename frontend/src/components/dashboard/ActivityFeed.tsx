import {
  CheckCircle2,
  Clock3,
  UserPlus,
  AlertTriangle,
} from "lucide-react";

const activities = [
  {
    id: 1,
    icon: CheckCircle2,
    color: "text-green-500",
    text: "Rahul resolved Printer Issue",
    time: "5 min ago",
  },
  {
    id: 2,
    icon: UserPlus,
    color: "text-blue-500",
    text: "Aman created Laptop Request",
    time: "20 min ago",
  },
  {
    id: 3,
    icon: AlertTriangle,
    color: "text-yellow-500",
    text: "High priority ticket assigned",
    time: "45 min ago",
  },
  {
    id: 4,
    icon: Clock3,
    color: "text-purple-500",
    text: "VPN issue moved to In Progress",
    time: "1 hour ago",
  },
];

export default function ActivityFeed() {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">

      <h2 className="mb-6 text-xl font-semibold text-white">
        Recent Activity
      </h2>

      <div className="space-y-5">

        {activities.map((activity) => {

          const Icon = activity.icon;

          return (
            <div
              key={activity.id}
              className="flex items-start gap-4"
            >

              <div
                className={`mt-1 rounded-full bg-zinc-800 p-2 ${activity.color}`}
              >
                <Icon size={18} />
              </div>

              <div className="flex-1">

                <p className="text-white">
                  {activity.text}
                </p>

                <p className="mt-1 text-sm text-zinc-500">
                  {activity.time}
                </p>

              </div>

            </div>
          );

        })}

      </div>

    </div>
  );
}