import {
  CheckCircle2,
  Clock3,
  UserPlus,
  AlertTriangle,
} from "lucide-react";

interface Activity {
  message: string;
  time: string;
}

interface ActivityFeedProps {
  activity: Activity[];
}

function getIcon(message: string) {
  const text = message.toLowerCase();

  if (text.includes("resolved")) {
    return {
      Icon: CheckCircle2,
      color: "text-green-500",
    };
  }

  if (text.includes("created")) {
    return {
      Icon: UserPlus,
      color: "text-blue-500",
    };
  }

  if (text.includes("assigned")) {
    return {
      Icon: AlertTriangle,
      color: "text-yellow-500",
    };
  }

  return {
    Icon: Clock3,
    color: "text-purple-500",
  };
}

export default function ActivityFeed({
  activity,
}: ActivityFeedProps) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6">

      <h2 className="mb-6 text-xl font-semibold text-white">
        Recent Activity
      </h2>

      {activity.length === 0 ? (
        <div className="flex h-60 items-center justify-center text-zinc-500">
          No recent activity.
        </div>
      ) : (
        <div className="space-y-5">

          {activity.map((item, index) => {

            const { Icon, color } = getIcon(item.message);

            return (
              <div
                key={index}
                className="flex items-start gap-4"
              >

                <div
                  className={`mt-1 rounded-full bg-zinc-800 p-2 ${color}`}
                >
                  <Icon size={18} />
                </div>

                <div className="flex-1">

                  <p className="text-white">
                    {item.message}
                  </p>

                  <p className="mt-1 text-sm text-zinc-500">
                    {item.time}
                  </p>

                </div>

              </div>
            );

          })}

        </div>
      )}

    </div>
  );
}