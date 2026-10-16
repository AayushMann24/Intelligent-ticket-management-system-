import type { ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useLocation } from "react-router-dom";

import Sidebar from "../components/layout/Sidebar";
import Navbar from "../components/layout/Navbar";
import AnimatedBackground from "../components/common/AnimatedBackground";
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
    <div className="relative flex min-h-screen text-slate-900 transition-colors duration-300 dark:text-white">
      <AnimatedBackground variant="app" />

      <Sidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar />

        <main className="relative flex-1 overflow-auto p-4 sm:p-6 lg:p-8">
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