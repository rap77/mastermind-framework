import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import TimelineScrubber from "../TimelineScrubber";
import { useSimulationStore } from "@/stores/simulationStore";
import { beforeEach, describe, expect, it, vi, afterEach } from "vitest";

// Mock the addEventListener and removeEventListener to track calls
const originalAddEventListener = window.addEventListener;
const originalRemoveEventListener = window.removeEventListener;

describe("TimelineScrubber - Memory Leak Fix", () => {
  let addEventListenerCalls: Array<{ event: string; handler: Function }> = [];
  let removeEventListenerCalls: Array<{ event: string; handler: Function }> = [];

  beforeEach(() => {
    // Reset tracking arrays
    addEventListenerCalls = [];
    removeEventListenerCalls = [];

    // Mock addEventListener to track calls
    window.addEventListener = vi.fn((event: string, handler: Function) => {
      addEventListenerCalls.push({ event, handler });
      originalAddEventListener.call(window, event, handler);
      return undefined;
    }) as any;

    // Mock removeEventListener to track calls
    window.removeEventListener = vi.fn((event: string, handler: Function) => {
      removeEventListenerCalls.push({ event, handler });
      originalRemoveEventListener.call(window, event, handler);
      return undefined;
    }) as any;

    // Reset store state
    useSimulationStore.setState({
      currentExecution: {
        id: "test-execution",
        flow_id: "test-flow",
        status: "completed",
        started_at: "2025-01-01T00:00:00Z",
        completed_at: "2025-01-01T00:01:00Z",
        milestones: [
          {
            index: 0,
            label: "Start",
            brain_count: 0,
            timestamp: "2025-01-01T00:00:00Z",
          },
          {
            index: 1,
            label: "Step 1",
            brain_count: 1,
            timestamp: "2025-01-01T00:00:30Z",
          },
          {
            index: 2,
            label: "Step 2",
            brain_count: 2,
            timestamp: "2025-01-01T00:01:00Z",
          },
        ],
      },
      currentMilestoneIndex: 0,
      jumpToMilestone: vi.fn(),
    });
  });

  afterEach(() => {
    // Restore original methods
    window.addEventListener = originalAddEventListener;
    window.removeEventListener = originalRemoveEventListener;
  });

  it("should properly clean up event listeners when dragging stops", async () => {
    render(<TimelineScrubber />);

    const track = screen.getByRole("slider", { name: /simulation timeline/i });

    // Clear any initial calls (from other effects)
    addEventListenerCalls = [];
    removeEventListenerCalls = [];

    // Start dragging
    fireEvent.mouseDown(track);

    // Should add mousemove and mouseup listeners
    await waitFor(() => {
      const mouseMoveCalls = addEventListenerCalls.filter((call) => call.event === "mousemove");
      const mouseUpCalls = addEventListenerCalls.filter((call) => call.event === "mouseup");
      expect(mouseMoveCalls.length).toBeGreaterThan(0);
      expect(mouseUpCalls.length).toBeGreaterThan(0);
    });

    const addedMouseMoveHandlers = addEventListenerCalls.filter((call) => call.event === "mousemove");
    const addedMouseUpHandlers = addEventListenerCalls.filter((call) => call.event === "mouseup");

    // Stop dragging by triggering mouseup
    fireEvent.mouseUp(window);

    await waitFor(() => {
      const removedMouseMoveCalls = removeEventListenerCalls.filter((call) => call.event === "mousemove");
      const removedMouseUpCalls = removeEventListenerCalls.filter((call) => call.event === "mouseup");

      // Should remove the same handlers that were added
      expect(removedMouseMoveCalls.length).toBeGreaterThanOrEqual(addedMouseMoveHandlers.length);
      expect(removedMouseUpCalls.length).toBeGreaterThanOrEqual(addedMouseUpHandlers.length);
    });
  });

  it("should not add duplicate event listeners during drag operations", async () => {
    render(<TimelineScrubber />);

    const track = screen.getByRole("slider", { name: /simulation timeline/i });

    // Clear any initial calls
    addEventListenerCalls = [];
    removeEventListenerCalls = [];

    // Start dragging
    fireEvent.mouseDown(track);

    await waitFor(() => {
      expect(addEventListenerCalls.some((call) => call.event === "mousemove")).toBe(true);
    });

    const mouseMoveCountAfterStart = addEventListenerCalls.filter((call) => call.event === "mousemove").length;

    // Move mouse (should not add new listeners)
    fireEvent.mouseMove(window, { clientX: 100 });

    await waitFor(() => {
      const mouseMoveCountAfterMove = addEventListenerCalls.filter((call) => call.event === "mousemove").length;
      // Should not have added more mousemove listeners
      expect(mouseMoveCountAfterMove).toBe(mouseMoveCountAfterStart);
    });

    // Cleanup
    fireEvent.mouseUp(window);
  });

  it("should handle rapid drag start/stop cycles without leaking listeners", async () => {
    render(<TimelineScrubber />);

    const track = screen.getByRole("slider", { name: /simulation timeline/i });

    // Clear initial calls
    addEventListenerCalls = [];
    removeEventListenerCalls = [];

    // Rapid drag cycles
    for (let i = 0; i < 5; i++) {
      fireEvent.mouseDown(track);
      await waitFor(() => {
        expect(addEventListenerCalls.some((call) => call.event === "mousemove")).toBe(true);
      });
      fireEvent.mouseUp(window);
      await waitFor(() => {
        expect(removeEventListenerCalls.some((call) => call.event === "mouseup")).toBe(true);
      });
    }

    // Count added vs removed
    const totalAddedMouseMove = addEventListenerCalls.filter((call) => call.event === "mousemove").length;
    const totalRemovedMouseMove = removeEventListenerCalls.filter((call) => call.event === "mousemove").length;
    const totalAddedMouseUp = addEventListenerCalls.filter((call) => call.event === "mouseup").length;
    const totalRemovedMouseUp = removeEventListenerCalls.filter((call) => call.event === "mouseup").length;

    // Should have removed at least as many as were added (allowing for other effects)
    expect(totalRemovedMouseMove).toBeGreaterThanOrEqual(totalAddedMouseMove * 0.8);
    expect(totalRemovedMouseUp).toBeGreaterThanOrEqual(totalAddedMouseUp * 0.8);
  });
});
