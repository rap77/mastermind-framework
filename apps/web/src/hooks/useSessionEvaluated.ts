/**
 * useSessionEvaluated — React hook for Brain #7 session_evaluated WS events.
 *
 * Listens to the `session_evaluated` WebSocket event type dispatched by the
 * Python task_runner after Brain #7 scores a completed brain flow. Provides
 * the latest quality score and insights for display in the Command Center badge.
 *
 * Event payload (from Python _post_session_evaluated_event):
 * {
 *   trace_id: string,
 *   brain_id: string,
 *   status: "session_evaluated",
 *   quality_score: number,
 *   brain_ids: string[],
 *   scores: Record<string, number>
 * }
 */

"use client"

import { useEffect, useState } from "react"
import { wsDispatcher } from "@/lib/wsDispatcher"

export interface SessionEvaluatedEvent {
  trace_id: string
  brain_id: string
  status: "session_evaluated"
  quality_score: number
  brain_ids: string[]
  scores: Record<string, number>
  timestamp?: string
}

export interface SessionEvaluatedState {
  /** Latest quality score from Brain #7 (0.0 – 1.0). Null if no event received. */
  lastScore: number | null
  /** Trace ID of the last evaluated session. */
  lastTraceId: string | null
  /** Brain IDs that ran in the last evaluated session. */
  lastBrainIds: string[]
  /** Per-brain scores from the last evaluated session. */
  lastScores: Record<string, number>
  /** Whether any session_evaluated event has been received. */
  hasScore: boolean
}

/**
 * Subscribe to Brain #7 session_evaluated WebSocket events.
 *
 * Uses the global wsDispatcher singleton (same bus as wsStore.onmessage).
 * Safe to call in SSR — event listener only attaches in the browser.
 *
 * @example
 * ```tsx
 * const { lastScore, hasScore } = useSessionEvaluated()
 * if (hasScore) {
 *   return <Badge>Last session: score {lastScore?.toFixed(2)}</Badge>
 * }
 * ```
 */
export function useSessionEvaluated(): SessionEvaluatedState {
  const [state, setState] = useState<SessionEvaluatedState>({
    lastScore: null,
    lastTraceId: null,
    lastBrainIds: [],
    lastScores: {},
    hasScore: false,
  })

  useEffect(() => {
    const unsubscribe = wsDispatcher.subscribe(
      "session_evaluated",
      (data: unknown) => {
        const event = data as SessionEvaluatedEvent
        if (
          event &&
          typeof event.quality_score === "number" &&
          event.status === "session_evaluated"
        ) {
          setState({
            lastScore: event.quality_score,
            lastTraceId: event.trace_id ?? null,
            lastBrainIds: event.brain_ids ?? [],
            lastScores: event.scores ?? {},
            hasScore: true,
          })
        }
      }
    )

    return unsubscribe
  }, [])

  return state
}
