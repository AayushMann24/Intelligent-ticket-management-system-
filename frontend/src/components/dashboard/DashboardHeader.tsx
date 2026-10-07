import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useReducedMotion } from "../../hooks/useReducedMotion";

export default function DashboardHeader() {
  const navigate = useNavigate();
  const reducedMotion = useReducedMotion();

  const today = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <motion.div
      className="mb-8 flex items-center justify-between"
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0, 0, 0.2, 1] }}
    >
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3, ease: [0, 0, 0.2, 1] }}
      >
        <motion.h1
          className="text-4xl font-bold text-slate-900 transition-colors duration-300 dark:text-white"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          Welcome back, Aayush 👋
        </motion.h1>

        <motion.p
          className="mt-2 text-slate-500 transition-colors duration-300 dark:text-slate-400"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.15 }}
        >
          {today}
        </motion.p>
      </motion.div>

      <motion.button
        onClick={() => navigate("/tickets?create=true")}
        className="rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition-all duration-300 hover:bg-blue-700 hover:shadow-lg"
        whileHover={reducedMotion ? {} : { y: -2, boxShadow: "0 10px 25px -5px rgba(37, 99, 235, 0.4)" }}
        whileTap={reducedMotion ? {} : { scale: 0.98 }}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3, delay: 0.2 }}
      >
        + Create Ticket
      </motion.button>
    </motion.div>
  );
}