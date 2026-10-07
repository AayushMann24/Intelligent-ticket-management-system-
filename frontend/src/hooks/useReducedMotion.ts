import { useEffect, useState } from "react";

/**
 * Hook to detect if the user prefers reduced motion.
 * Returns true if the user has enabled "Reduce motion" in their OS settings.
 */
export function useReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    /* eslint-disable react-hooks/set-state-in-effect -- Initial sync with media query is required */
    setPrefersReducedMotion(mediaQuery.matches);
    /* eslint-enable react-hooks/set-state-in-effect */

    const handler = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    mediaQuery.addEventListener("change", handler);
    return () => mediaQuery.removeEventListener("change", handler);
  }, []);

  return prefersReducedMotion;
}

/**
 * Motion configuration constants for consistent animation behavior.
 * These values are designed for a professional enterprise SaaS feel.
 */
export const motionConfig = {
  // Duration constants (in seconds)
  durations: {
    instant: 0.05,
    fast: 0.15,
    normal: 0.2,
    slow: 0.3,
    slower: 0.4,
  },

  // Easing functions - use Framer Motion easing strings
  easings: {
    standard: "easeOut",
    enter: "easeOut",
    exit: "easeIn",
    emphasized: "easeInOut",
  },

  // Spring configurations
  springs: {
    standard: { type: "spring", stiffness: 300, damping: 30 },
    gentle: { type: "spring", stiffness: 200, damping: 25 },
    snappy: { type: "spring", stiffness: 400, damping: 35 },
  },

  // Stagger delays for lists
  stagger: {
    fast: 0.03,
    normal: 0.05,
    slow: 0.08,
  },

  // Scale factors for hover/active states
  scale: {
    hover: 1.02,
    active: 0.98,
    cardHover: 1.01,
  },
};

/**
 * Get motion props based on reduced motion preference.
 * Returns Framer Motion props with animations disabled if prefers-reduced-motion is set.
 */
export function getMotionProps(reducedMotion: boolean, props: {
  animate?: Record<string, unknown>;
  initial?: Record<string, unknown>;
  exit?: Record<string, unknown>;
  transition?: Record<string, unknown>;
  whileHover?: Record<string, unknown>;
  whileTap?: Record<string, unknown>;
  whileFocus?: Record<string, unknown>;
}) {
  if (reducedMotion) {
    return {
      animate: props.animate,
      transition: { duration: 0 },
    };
  }

  return props;
}

/**
 * Common animation variants for consistent motion across components.
 */
export const variants = {
  fade: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: motionConfig.durations.normal, ease: motionConfig.easings.standard },
  },

  fadeUp: {
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -10 },
    transition: { duration: motionConfig.durations.normal, ease: motionConfig.easings.enter },
  },

  fadeDown: {
    initial: { opacity: 0, y: -10 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 10 },
    transition: { duration: motionConfig.durations.normal, ease: motionConfig.easings.enter },
  },

  slideRight: {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 },
    transition: { duration: motionConfig.durations.normal, ease: motionConfig.easings.enter },
  },

  slideLeft: {
    initial: { opacity: 0, x: 20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 },
    transition: { duration: motionConfig.durations.normal, ease: motionConfig.easings.enter },
  },

  scale: {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 },
    transition: { duration: motionConfig.durations.fast, ...motionConfig.springs.standard },
  },

  modal: {
    initial: { opacity: 0, scale: 0.95, y: 20 },
    animate: { opacity: 1, scale: 1, y: 0 },
    exit: { opacity: 0, scale: 0.95, y: 20 },
    transition: { duration: motionConfig.durations.normal, ...motionConfig.springs.standard },
  },

  backdrop: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: motionConfig.durations.fast },
  },

  dropdown: {
    initial: { opacity: 0, y: -8, scale: 0.98 },
    animate: { opacity: 1, y: 0, scale: 1 },
    exit: { opacity: 0, y: -8, scale: 0.98 },
    transition: { duration: motionConfig.durations.fast, ...motionConfig.springs.snappy },
  },

  sidebar: {
    initial: { width: 0 },
    animate: { width: "16rem" },
    exit: { width: 0 },
    transition: { duration: motionConfig.durations.normal, ease: motionConfig.easings.standard },
  },

  card: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: motionConfig.durations.slow, ease: motionConfig.easings.enter },
  },

  listItem: {
    initial: { opacity: 0, x: -10 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 10 },
    transition: { duration: motionConfig.durations.fast, ease: motionConfig.easings.enter },
  },

  toast: {
    initial: { opacity: 0, x: 100, scale: 0.95 },
    animate: { opacity: 1, x: 0, scale: 1 },
    exit: { opacity: 0, x: 100, scale: 0.95 },
    transition: { duration: motionConfig.durations.normal, ...motionConfig.springs.snappy },
  },

  pulse: {
    animate: {
      scale: [1, 1.1, 1],
      opacity: [1, 0.7, 1],
    },
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },

  button: {
    whileHover: { scale: motionConfig.scale.hover },
    whileTap: { scale: motionConfig.scale.active },
    whileFocus: { boxShadow: "0 0 0 3px rgba(59, 130, 246, 0.5)" },
  },

  cardHover: {
    whileHover: {
      y: -4,
      boxShadow: "0 20px 40px -10px rgba(0, 0, 0, 0.15)",
      transition: { duration: motionConfig.durations.fast, ease: motionConfig.easings.standard },
    },
  },

  navLink: {
    whileHover: { x: 4 },
    whileTap: { scale: motionConfig.scale.active },
  },
};

/**
 * Stagger container variant for animating children with delay.
 */
export const staggerContainer = {
  initial: { opacity: 0 },
  animate: {
    opacity: 1,
    transition: {
      staggerChildren: motionConfig.stagger.normal,
      delayChildren: 0.1,
    },
  },
};

/**
 * Page transition variants for smooth page changes.
 */
export const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: motionConfig.durations.normal, ease: motionConfig.easings.standard },
};