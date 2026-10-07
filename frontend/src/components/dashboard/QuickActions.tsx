import { BarChart3, Bot, Plus, Users } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useReducedMotion } from "../../hooks/useReducedMotion";

export default function QuickActions() {
  const navigate = useNavigate();
  const reducedMotion = useReducedMotion();

  const actions = [
    { title: "New Ticket", icon: <Plus size={34} />, color: "bg-blue-600", onClick: () => navigate("/tickets?create=true") },
    { title: "Manage Users", icon: <Users size={34} />, color: "bg-green-600", onClick: () => navigate("/users") },
    { title: "AI Assistant", icon: <Bot size={34} />, color: "bg-purple-600", onClick: () => navigate("/assistant") },
    { title: "Analytics", icon: <BarChart3 size={34} />, color: "bg-orange-500", onClick: () => navigate("/analytics") },
  ];

  const itemVariants = {
    initial: { opacity: 0, y: 20, scale: 0.95 },
    animate: { opacity: 1, y: 0, scale: 1 },
    exit: { opacity: 0, y: -20, scale: 0.95 },
    transition: { duration: 0.3, ease: [0, 0, 0.2, 1] },
  };

  const containerVariants = {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { staggerChildren: 0.08, delayChildren: 0.1 } },
    exit: { opacity: 0 },
  };

  return (
    <>
      <motion.h2
        className="mb-6 text-2xl font-bold text-slate-900 transition-colors duration-300 dark:text-white"
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.2 }}
      >
        Quick Actions
      </motion.h2>

      <motion.div
        className="grid gap-6 md:grid-cols-2 xl:grid-cols-4"
        variants={containerVariants}
        initial="initial"
        animate="animate"
        exit="exit"
      >
        {actions.map((action) => (
          <motion.div
            key={action.title}
            onClick={action.onClick}
            className="cursor-pointer rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition-all duration-300 hover:border-blue-500 dark:border-slate-800 dark:bg-slate-900"
            variants={itemVariants}
            whileHover={reducedMotion ? {} : { y: -4, boxShadow: "0 20px 40px -10px rgba(0, 0, 0, 0.15)" }}
            whileTap={reducedMotion ? {} : { scale: 0.98 }}
          >
            <motion.div className="flex flex-col items-center">
              <motion.div
                className={`${action.color} mb-6 rounded-2xl p-5 text-white shadow-md`}
                initial={{ opacity: 0, scale: 0.8, rotate: -5 }}
                animate={{ opacity: 1, scale: 1, rotate: 0 }}
                transition={{ type: "spring", stiffness: 300, damping: 25, delay: 0.1 }}
              >
                {action.icon}
              </motion.div>

              <motion.h3
                className="text-xl font-semibold text-slate-900 transition-colors duration-300 dark:text-white"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: 0.2 }}
              >
                {action.title}
              </motion.h3>
            </motion.div>
          </motion.div>
        ))}
      </motion.div>
    </>
  );
}