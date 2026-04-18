"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "./ThemeProvider";
import { Button } from "../ui/button";

/**
 * ThemeToggle - Button component for switching between light and dark themes
 *
 * Features:
 * - Displays sun icon in dark mode (clicking switches to light)
 * - Displays moon icon in light mode (clicking switches to dark)
 * - Fully accessible with ARIA labels and pressed state
 * - Integrates with ThemeProvider for state management
 *
 * @example
 * ```tsx
 * <ThemeProvider>
 *   <ThemeToggle />
 * </ThemeProvider>
 * ```
 */
export function ThemeToggle() {
  const { theme, setTheme, actualTheme } = useTheme();

  const toggleTheme = () => {
    setTheme(actualTheme === "dark" ? "light" : "dark");
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggleTheme}
      aria-label={`Toggle theme (current: ${actualTheme})`}
      aria-pressed={actualTheme === "dark"}
    >
      {actualTheme === "dark" ? (
        <Sun className="h-5 w-5" data-lucide="sun" />
      ) : (
        <Moon className="h-5 w-5" data-lucide="moon" />
      )}
    </Button>
  );
}
