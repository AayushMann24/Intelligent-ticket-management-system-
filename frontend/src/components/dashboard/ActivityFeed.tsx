import { CheckCircle2, Clock3, UserPlus, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";
import { useTheme } from "../../context/useTheme";
import { useReducedMotion } from "../../hooks/useReducedMotion";

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

const itemVariants = {
  initial: { opacity: 0, x: -10, scale: 0.98 },
  animate: { opacity: 1, x: 0, scale: 1 },
  exit: { opacity: 0, x: 10, scale: 0.98 },
  transition: { duration: 0.2, ease: [0, 0, 0.2, 1] },
};

const containerVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { staggerChildren: 0.05, delayChildren: 0.1 } },
  exit: { opacity: 0 },
};

export default function ActivityFeed({ activity }: ActivityFeedProps) {
  const { theme } = useTheme();
  const reducedMotion = useReducedMotion();
  const dark = theme === "dark";

  return (
    <motion.div
      className="rounded-2xl border bg-white p-6 shadow-sm transition-all duration-300 dark:border-slate-800 dark:bg-slate-900"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: [0, 0, 0.2, 1] }}
    >
      <motion.h2
        className="mb-6 text-xl font-semibold text-slate-900 dark:text-white"
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.2 }}
      >
        Recent Activity
      </motion.h2>

      {activity.length === 0 ? (
        <motion.div
          className="flex h-60 items-center justify-center text-slate-500 dark:text-slate-400"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          No recent activity.
        </motion.div>
      ) : (
        <motion.div variants={containerVariants} initial="initial" animate="animate" exit="exit" className="space-y-5">
          {activity.map((item, index) => {
            const { Icon, color, bg } = getIcon(item.message);

            return (
              <motion.div
                key={index}
                className="flex items-start gap-4 rounded-xl p-3 transition-all duration-300 hover:bg-slate-50 dark:hover:bg-slate-800"
                variants={itemVariants}
                whileHover={reducedMotion ? {} : { x: 4, backgroundColor: dark ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.02)" }}
              >
                <motion.div
                  className={`rounded-full p-3 ${bg}`}
                  initial={{ opacity: 0, scale: 0.8, rotate: -10 }}
                  animate={{ opacity: 1, scale: 1, rotate: 0 }}
                  transition={{ type: "spring", stiffness: 400, damping: 25, delay: 0.1 }}
                >
                  <Icon size={18} className={color} />
                </motion.div>

                <motion.div
                  className="flex-1"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2, delay: 0.05 }}
                >
                  <motion.p
                    className="font-medium text-slate-900 dark:text-white"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                  >
                    {item.message}
                  </motion.p>
                  <motion.p
                    className="mt-1 text-sm text-slate-500 dark:text-slate-400"
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2, delay: 0.1 }}
                  >
                    {item.time}
                  </motion.p>
                </motion.div>
              </motion.div>
            );
          })}
        </motion.div>
      )}
    </motion.div>
  );
}