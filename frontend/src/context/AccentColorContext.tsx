import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

export type AccentColor = "blue" | "purple" | "green";

interface AccentContextType {
  accent: AccentColor;
  setAccent: (color: AccentColor) => void;
}

const AccentContext = createContext<AccentContextType | undefined>(
  undefined
);

export function AccentProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [accent, setAccent] = useState<AccentColor>(() => {
    const saved = localStorage.getItem("accent");

    if (
      saved === "blue" ||
      saved === "purple" ||
      saved === "green"
    ) {
      return saved;
    }

    return "blue";
  });

  useEffect(() => {
    document.documentElement.dataset.accent = accent;
    localStorage.setItem("accent", accent);
  }, [accent]);

  return (
    <AccentContext.Provider
      value={{
        accent,
        setAccent,
      }}
    >
      {children}
    </AccentContext.Provider>
  );
}

export function useAccent() {
  const context = useContext(AccentContext);

  if (!context) {
    throw new Error(
      "useAccent must be used inside AccentProvider"
    );
  }

  return context;
}

/* =======================================================
   Accent Classes
======================================================= */

export function useAccentClasses() {
  const { accent } = useAccent();

  switch (accent) {
    case "purple":
      return {
        bg: "bg-purple-600",
        bgHover: "hover:bg-purple-700",

        text: "text-purple-600",
        textDark: "dark:text-purple-400",

        border: "border-purple-500",

        ring: "ring-purple-400",

        light: "bg-purple-100 dark:bg-purple-900/30",
      };

    case "green":
      return {
        bg: "bg-green-600",
        bgHover: "hover:bg-green-700",

        text: "text-green-600",
        textDark: "dark:text-green-400",

        border: "border-green-500",

        ring: "ring-green-400",

        light: "bg-green-100 dark:bg-green-900/30",
      };

    default:
      return {
        bg: "bg-blue-600",
        bgHover: "hover:bg-blue-700",

        text: "text-blue-600",
        textDark: "dark:text-blue-400",

        border: "border-blue-500",

        ring: "ring-blue-400",

        light: "bg-blue-100 dark:bg-blue-900/30",
      };
  }
}