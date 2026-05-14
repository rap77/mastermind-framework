/**
 * SessionEvaluatedBadge Tests — C3.11
 *
 * TDD: WS event `session_evaluated` → badge updates in real-time.
 */

import { render, screen, act } from "@testing-library/react"
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { SessionEvaluatedBadge } from "../SessionEvaluatedBadge"
import { wsDispatcher } from "@/lib/wsDispatcher"

// ─── Setup ────────────────────────────────────────────────────────────────────

describe("SessionEvaluatedBadge", () => {
  beforeEach(() => {
    wsDispatcher.clear()
  })

  afterEach(() => {
    wsDispatcher.clear()
  })

  // ─── C3.11: WS event session_evaluated → badge updates ─────────────────────

  it("renders nothing when no session_evaluated event received", () => {
    const { container } = render(<SessionEvaluatedBadge />)
    expect(container.firstChild).toBeNull()
  })

  it("renders badge after receiving session_evaluated event", async () => {
    render(<SessionEvaluatedBadge />)

    // Dispatch WS event
    act(() => {
      wsDispatcher.dispatch("session_evaluated", {
        trace_id: "trace-abc-123",
        brain_id: "brain-01-product",
        status: "session_evaluated",
        quality_score: 0.87,
        brain_ids: ["brain-01-product"],
        scores: { "brain-01-product": 0.87 },
      })
    })

    const badge = await screen.findByTestId("session-evaluated-badge")
    expect(badge).toBeDefined()
    expect(badge.textContent).toContain("0.87")
    expect(badge.textContent).toContain("Última sesión")
  })

  it("updates badge when a second session_evaluated event arrives", async () => {
    render(<SessionEvaluatedBadge />)

    act(() => {
      wsDispatcher.dispatch("session_evaluated", {
        trace_id: "trace-1",
        brain_id: "brain-01",
        status: "session_evaluated",
        quality_score: 0.65,
        brain_ids: ["brain-01"],
        scores: { "brain-01": 0.65 },
      })
    })

    const badge1 = await screen.findByTestId("session-evaluated-badge")
    expect(badge1.textContent).toContain("0.65")

    act(() => {
      wsDispatcher.dispatch("session_evaluated", {
        trace_id: "trace-2",
        brain_id: "brain-01",
        status: "session_evaluated",
        quality_score: 0.92,
        brain_ids: ["brain-01"],
        scores: { "brain-01": 0.92 },
      })
    })

    const badge2 = await screen.findByTestId("session-evaluated-badge")
    expect(badge2.textContent).toContain("0.92")
    expect(badge2.textContent).not.toContain("0.65")
  })

  it("applies green color class for high scores (>= 0.75)", async () => {
    render(<SessionEvaluatedBadge />)

    act(() => {
      wsDispatcher.dispatch("session_evaluated", {
        trace_id: "trace-high",
        brain_id: "brain-01",
        status: "session_evaluated",
        quality_score: 0.90,
        brain_ids: ["brain-01"],
        scores: { "brain-01": 0.90 },
      })
    })

    const badge = await screen.findByTestId("session-evaluated-badge")
    expect(badge.className).toContain("green")
  })

  it("applies red color class for low scores (< 0.50)", async () => {
    render(<SessionEvaluatedBadge />)

    act(() => {
      wsDispatcher.dispatch("session_evaluated", {
        trace_id: "trace-low",
        brain_id: "brain-01",
        status: "session_evaluated",
        quality_score: 0.30,
        brain_ids: ["brain-01"],
        scores: { "brain-01": 0.30 },
      })
    })

    const badge = await screen.findByTestId("session-evaluated-badge")
    expect(badge.className).toContain("red")
  })

  it("ignores events without session_evaluated status", () => {
    render(<SessionEvaluatedBadge />)

    act(() => {
      wsDispatcher.dispatch("session_evaluated", {
        trace_id: "trace-wrong",
        brain_id: "brain-01",
        status: "completed",  // Wrong status
        quality_score: 0.80,
        brain_ids: ["brain-01"],
        scores: {},
      })
    })

    const badge = screen.queryByTestId("session-evaluated-badge")
    expect(badge).toBeNull()
  })

  it("ignores malformed events (missing quality_score)", () => {
    render(<SessionEvaluatedBadge />)

    act(() => {
      wsDispatcher.dispatch("session_evaluated", {
        trace_id: "trace-malformed",
        // quality_score missing
        brain_id: "brain-01",
        status: "session_evaluated",
      })
    })

    const badge = screen.queryByTestId("session-evaluated-badge")
    expect(badge).toBeNull()
  })
})
