import { useReducedMotion } from "../../hooks/useReducedMotion";

interface AnimatedBackgroundProps {
  /**
   * "public" -> rich, dark marketing atmosphere (landing / auth pages).
   * "app"    -> softer, theme-aware atmosphere behind the authenticated shell.
   */
  variant?: "public" | "app";
  className?: string;
}

/**
 * Full-viewport atmospheric background built purely from CSS gradients and
 * softly floating, glowing orbs.
 *
 * - Sits behind all content (`-z-10`) and never intercepts pointer events.
 * - Uses only transform/opacity animations for GPU-friendly rendering.
 * - Automatically freezes when the user prefers reduced motion.
 * - Marked `aria-hidden` so it is invisible to assistive tech.
 */
export default function AnimatedBackground({
  variant = "public",
  className = "",
}: AnimatedBackgroundProps) {
  const reducedMotion = useReducedMotion();
  const isApp = variant === "app";

  return (
    <div
      aria-hidden="true"
      className={`itms-bg ${isApp ? "itms-bg--app" : ""} ${
        reducedMotion ? "" : "itms-motion"
      } ${className}`}
    >
      <div className="itms-aurora" />

      <span className="itms-orb itms-orb--cyan" />
      <span className="itms-orb itms-orb--violet" />
      <span className="itms-orb itms-orb--blue" />
      <span className="itms-orb itms-orb--fuchsia" />

      <div className="itms-grid-overlay" />

      {!isApp && <div className="itms-vignette" />}
    </div>
  );
}
