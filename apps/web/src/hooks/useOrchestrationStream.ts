/**
 * useOrchestrationStream — D2.01
 *
 * Consumes wsEventsStore and returns a flat, chronologically-sorted list of
 * BrainStateEvent entries. Optionally filtered by brain_id when a brain is
 * selected.
 *
 * Design decisions:
 * - Reads from wsEventsStore directly (no WS connection logic here — that
 *   lives in BrainStatusFeed / useWebSocket).
 * - Returns stable reference via useMemo to avoid needless re-renders of
 *   StatusTimeline.
 * - React Compiler is active in this project, so manual useMemo is only
 *   included for explicitness; RC may elide it.
 */

import { useMemo } from 'react'
import { useWsEventsStore } from '@/stores/wsEventsStore'
import type { BrainStateEvent } from '@/stores/wsEventsStore'

export interface UseOrchestrationStreamOptions {
  /**
   * When provided, only events from this brain_id are returned.
   * When null/undefined, all events across all trace_ids are returned.
   */
  brainId?: string | null
}

export interface UseOrchestrationStreamReturn {
  /** Flat, chronologically-sorted list of matching events. */
  events: BrainStateEvent[]
  /** Total number of distinct trace_ids currently in the store. */
  traceCount: number
}

export function useOrchestrationStream(
  options: UseOrchestrationStreamOptions = {},
): UseOrchestrationStreamReturn {
  const { brainId } = options

  // Subscribe to the raw events map — re-renders whenever the store updates.
  const eventsMap = useWsEventsStore((state) => state.events)

  const { events, traceCount } = useMemo(() => {
    // Flatten all events from all traces into a single array.
    const all: BrainStateEvent[] = []
    for (const list of eventsMap.values()) {
      all.push(...list)
    }

    // Optional brain filter.
    const filtered = brainId ? all.filter((e) => e.brain_id === brainId) : all

    // Sort chronologically (oldest first, newest at bottom for timeline).
    filtered.sort((a, b) => a.timestamp.localeCompare(b.timestamp))

    return {
      events: filtered,
      traceCount: eventsMap.size,
    }
  }, [eventsMap, brainId])

  return { events, traceCount }
}
