import type { ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useLocation } from "react-router-dom";

import Sidebar from "../components/layout/Sidebar";
import Navbar from "../components/layout/Navbar";
import { useReducedMotion } from "../hooks/useReducedMotion";

interface MainLayoutProps {
  children: ReactNode;
}

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.25, ease: [0.4, 0, 0.2, 1] },
};

export default function MainLayout({ children }: MainLayoutProps) {
  const location = useLocation();
  const reducedMotion = useReducedMotion();

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900 transition-colors duration-300 dark:bg-slate-950 dark:text-white">
      <Sidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar />

        <main className="flex-1 overflow-auto p-8 bg-slate-50 transition-colors duration-300 dark:bg-slate-950">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={reducedMotion ? undefined : pageVariants.initial}
              animate={reducedMotion ? undefined : pageVariants.animate}
              exit={reducedMotion ? undefined : pageVariants.exit}
              variants={pageVariants}
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}