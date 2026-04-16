import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "../theme-provider";
import { beforeEach, describe, expect, it, vi } from "vitest";

describe("ThemeProvider", () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Reset document class
    document.documentElement.classList.remove("dark");
  });

  it("should provide theme context with default light theme", () => {
    const TestComponent = () => {
      return <div data-testid="test">Test</div>;
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId("test")).toBeInTheDocument();
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });

  it("should read theme from localStorage on mount", () => {
    localStorage.setItem("theme", "dark");

    const TestComponent = () => {
      return <div data-testid="test">Test</div>;
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("should default to light theme when no localStorage value exists", () => {
    const TestComponent = () => {
      return <div data-testid="test">Test</div>;
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(document.documentElement.classList.contains("dark")).toBe(false);
    expect(localStorage.getItem("theme")).toBe(null);
  });
});
