import { motion } from "framer-motion";
import type { ReactNode } from "react";

import { useReducedMotion } from "../../hooks/useReducedMotion";

interface RevealProps {
  children: ReactNode;
  className?: string;
  /** Delay before the reveal starts, in seconds. */
  delay?: number;
  /** Vertical offset (px) the content travels while fading in. */
  y?: number;
  /** Reveal direction. */
  direction?: "up" | "down" | "left" | "right";
  /** Keep the element revealed after it leaves the viewport. */
  once?: boolean;
  /** How much of the element must be visible before revealing (0-1). */
  amount?: number;
}

const offsets: Record<NonNullable<RevealProps["direction"]>, { x: number; y: number }> = {
  up: { x: 0, y: 1 },
  down: { x: 0, y: -1 },
  left: { x: 1, y: 0 },
  right: { x: -1, y: 0 },
};

/**
 * Reusable scroll-triggered reveal wrapper.
 *
 * Fades and slides its children into view the first time they enter the
 * viewport. When the user prefers reduced motion, it renders a plain wrapper
 * with no animation at all.
 */
export default function Reveal({
  children,
  className = "",
  delay = 0,
  y = 28,
  direction = "up",
  once = true,
  amount = 0.2,
}: RevealProps) {
  const reducedMotion = useReducedMotion();

  if (reducedMotion) {
    return <div className={className}>{children}</div>;
  }

  const offset = offsets[direction];

  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, x: offset.x * y, y: offset.y * y }}
      whileInView={{ opacity: 1, x: 0, y: 0 }}
      viewport={{ once, amount }}
      transition={{ duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}
