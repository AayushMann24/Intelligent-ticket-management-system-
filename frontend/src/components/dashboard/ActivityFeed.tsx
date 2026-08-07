import {
  CheckCircle2,
  Clock3,
  UserPlus,
  AlertTriangle,
} from "lucide-react";

import { useTheme } from "../../context/ThemeContext";

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
      bg: "bg-green-100 dark:bg-green-500/20",
    };
  }

  if (text.includes("created")) {
    return {
      Icon: UserPlus,
      color: "text-blue-500",
      bg: "bg-blue-100 dark:bg-blue-500/20",
    };
  }

  if (text.includes("assigned")) {
    return {
      Icon: AlertTriangle,
      color: "text-yellow-500",
      bg: "bg-yellow-100 dark:bg-yellow-500/20",
    };
  }

  return {
    Icon: Clock3,
    color: "text-purple-500",
    bg: "bg-purple-100 dark:bg-purple-500/20",
  };
}

export default function ActivityFeed({
  activity,
}: ActivityFeedProps) {

  useTheme();

  return (
    <div
      className="
        rounded-2xl
        border
        border-slate-200
        bg-white
        p-6
        shadow-sm
        transition-all
        duration-300

        dark:border-slate-800
        dark:bg-slate-900
      "
    >

      <h2 className="mb-6 text-xl font-semibold text-slate-900 dark:text-white">
        Recent Activity
      </h2>

      {activity.length === 0 ? (

        <div className="flex h-60 items-center justify-center text-slate-500 dark:text-slate-400">
          No recent activity.
        </div>

      ) : (

        <div className="space-y-5">

          {activity.map((item, index) => {

            const { Icon, color, bg } = getIcon(item.message);

            return (

              <div
                key={index}
                className="
                  flex
                  items-start
                  gap-4
                  rounded-xl
                  p-3
                  transition-all
                  duration-300

                  hover:bg-slate-50
                  dark:hover:bg-slate-800
                "
              >

                <div
                  className={`rounded-full p-3 ${bg}`}
                >

                  <Icon
                    size={18}
                    className={color}
                  />

                </div>

                <div className="flex-1">

                  <p className="font-medium text-slate-900 dark:text-white">
                    {item.message}
                  </p>

                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
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