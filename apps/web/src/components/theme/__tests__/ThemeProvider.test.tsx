import { render, screen, act } from "@testing-library/react";
import { ThemeProvider, useTheme } from "../ThemeProvider";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock window.matchMedia
const mockMatchMedia = vi.fn();
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => mockMatchMedia(query),
});

describe("ThemeProvider", () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Reset document class
    document.documentElement.classList.remove("dark");
    // Reset matchMedia mock
    mockMatchMedia.mockReset();
  });

  it("should provide theme context with default light theme", () => {
    const TestComponent = () => {
      const { theme, actualTheme } = useTheme();
      return (
        <div>
          <span data-testid="theme">{theme}</span>
          <span data-testid="actual-theme">{actualTheme}</span>
        </div>
      );
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId("theme").textContent).toBe("light");
    expect(screen.getByTestId("actual-theme").textContent).toBe("light");
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });

  it("should read theme from localStorage on mount", () => {
    localStorage.setItem("theme", "dark");

    const TestComponent = () => {
      const { actualTheme } = useTheme();
      return <span data-testid="actual-theme">{actualTheme}</span>;
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId("actual-theme").textContent).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("should default to light theme when no localStorage value exists", () => {
    mockMatchMedia.mockReturnValue({ matches: true });

    const TestComponent = () => {
      const { actualTheme } = useTheme();
      return <span data-testid="actual-theme">{actualTheme}</span>;
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    // Should default to light when no localStorage value
    expect(screen.getByTestId("actual-theme").textContent).toBe("light");
  });

  it("should toggle between light and dark themes", () => {
    const TestComponent = () => {
      const { theme, setTheme, actualTheme } = useTheme();
      return (
        <div>
          <span data-testid="theme">{theme}</span>
          <span data-testid="actual-theme">{actualTheme}</span>
          <button onClick={() => setTheme("dark")}>Set Dark</button>
          <button onClick={() => setTheme("light")}>Set Light</button>
        </div>
      );
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    // Initial state
    expect(screen.getByTestId("theme").textContent).toBe("light");

    // Switch to dark
    act(() => {
      screen.getByText("Set Dark").click();
    });

    expect(screen.getByTestId("theme").textContent).toBe("dark");
    expect(screen.getByTestId("actual-theme").textContent).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
    expect(localStorage.getItem("theme")).toBe("dark");

    // Switch to light
    act(() => {
      screen.getByText("Set Light").click();
    });

    expect(screen.getByTestId("theme").textContent).toBe("light");
    expect(screen.getByTestId("actual-theme").textContent).toBe("light");
    expect(document.documentElement.classList.contains("dark")).toBe(false);
    expect(localStorage.getItem("theme")).toBe("light");
  });

  it("should respect system preference when theme is set to system", () => {
    mockMatchMedia.mockReturnValue({ matches: true });

    const TestComponent = () => {
      const { theme, setTheme, actualTheme } = useTheme();
      return (
        <div>
          <span data-testid="theme">{theme}</span>
          <span data-testid="actual-theme">{actualTheme}</span>
          <button onClick={() => setTheme("system")}>Set System</button>
        </div>
      );
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    act(() => {
      screen.getByText("Set System").click();
    });

    expect(screen.getByTestId("theme").textContent).toBe("system");
    expect(screen.getByTestId("actual-theme").textContent).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("should throw error when useTheme is used outside ThemeProvider", () => {
    const TestComponent = () => {
      const { theme } = useTheme();
      return <span>{theme}</span>;
    };

    // Suppress console.error for this test
    const consoleError = console.error;
    console.error = vi.fn();

    expect(() => {
      render(<TestComponent />);
    }).toThrow("useTheme must be used within ThemeProvider");

    console.error = consoleError;
  });

  it("should persist theme selection across page reloads", () => {
    const TestComponent = () => {
      const { theme, setTheme } = useTheme();
      return (
        <div>
          <span data-testid="theme">{theme}</span>
          <button onClick={() => setTheme("dark")}>Set Dark</button>
        </div>
      );
    };

    // First render - set to dark
    const { unmount } = render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    act(() => {
      screen.getByText("Set Dark").click();
    });

    expect(localStorage.getItem("theme")).toBe("dark");
    unmount();

    // Second render - should load from localStorage
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId("theme").textContent).toBe("dark");
  });
});
