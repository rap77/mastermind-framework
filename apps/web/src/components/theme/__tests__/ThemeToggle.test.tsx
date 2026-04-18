import { render, screen, fireEvent } from "@testing-library/react";
import { ThemeProvider, useTheme } from "../ThemeProvider";
import { ThemeToggle } from "../ThemeToggle";
import { beforeEach, describe, expect, it } from "vitest";

describe("ThemeToggle", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove("dark");
  });

  it("should render toggle button with sun icon in light mode", () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole("button", { name: /toggle theme/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute("aria-label", "Toggle theme (current: light)");
    expect(button).toHaveAttribute("aria-pressed", "false");

    // Should show moon icon in light mode (clicking switches to dark)
    const moonIcon = button.querySelector('[data-lucide="moon"]');
    expect(moonIcon).toBeInTheDocument();
  });

  it("should render toggle button with moon icon in dark mode", () => {
    localStorage.setItem("theme", "dark");

    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole("button", { name: /toggle theme/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute("aria-label", "Toggle theme (current: dark)");
    expect(button).toHaveAttribute("aria-pressed", "true");

    // Should show sun icon in dark mode (clicking switches to light)
    const sunIcon = button.querySelector('[data-lucide="sun"]');
    expect(sunIcon).toBeInTheDocument();
  });

  it("should toggle from light to dark mode on click", () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole("button", { name: /toggle theme/i });

    expect(document.documentElement.classList.contains("dark")).toBe(false);
    expect(localStorage.getItem("theme")).toBe(null);

    fireEvent.click(button);

    expect(document.documentElement.classList.contains("dark")).toBe(true);
    expect(localStorage.getItem("theme")).toBe("dark");
  });

  it("should toggle from dark to light mode on click", () => {
    localStorage.setItem("theme", "dark");

    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole("button", { name: /toggle theme/i });

    expect(document.documentElement.classList.contains("dark")).toBe(true);

    fireEvent.click(button);

    expect(document.documentElement.classList.contains("dark")).toBe(false);
    expect(localStorage.getItem("theme")).toBe("light");
  });

  it("should be accessible with proper ARIA attributes", () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole("button", { name: /toggle theme/i });
    expect(button).toHaveAttribute("aria-label");
    expect(button).toHaveAttribute("aria-pressed");
    expect(button).toHaveAttribute("type", "button");
  });

  it("should update icon when theme changes externally", () => {
    const TestComponent = () => {
      const { setTheme } = useTheme();
      return (
        <div>
          <ThemeToggle />
          <button onClick={() => setTheme("dark")}>External Change</button>
        </div>
      );
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    const toggleButton = screen.getByRole("button", { name: /toggle theme/i });
    expect(toggleButton).toHaveAttribute("aria-label", "Toggle theme (current: light)");

    // Externally change theme
    fireEvent.click(screen.getByText("External Change"));

    expect(toggleButton).toHaveAttribute("aria-label", "Toggle theme (current: dark)");
  });

  it("should render as a button with proper styling", () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole("button", { name: /toggle theme/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute("type", "button");
  });
});
