"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "../theme-provider";
import { Button } from "../ui/button";

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
        <Sun className="h-5 w-5" />
      ) : (
        <Moon className="h-5 w-5" />
      )}
    </Button>
  );
}
