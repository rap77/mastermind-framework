/**
 * wsEventsStore — Zustand store for brain state events from the Rust WS hub.
 *
 * B2.8 spec:
 *   - Key: trace_id (string)
 *   - Value: BrainStateEvent[] (ordered list of events for that trace)
 *   - appendEvent: idempotent append (deduplicates by trace+brain+status)
 *   - clearTrace: remove all events for a given trace_id
 *   - clearAll: reset to empty map
 *
 * The store mirrors the BrainStateEvent shape from Rust:
 *   { trace_id, brain_id, status, timestamp }
 *
 * Consumers (e.g. BrainStatusFeed) subscribe with a selector on the trace
 * they care about to avoid re-rendering on unrelated updates.
 */

import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { enableMapSet } from 'immer'

enableMapSet()

// ------------------------------------------------------------------ types

/** Mirrors the Rust BrainStateEvent schema from brain_state_event.rs */
export type BrainEventStatus = 'dispatched' | 'running' | 'completed' | 'failed'

export interface BrainStateEvent {
  trace_id: string
  brain_id: string
  status: BrainEventStatus
  /** ISO-8601 timestamp from Rust (UTC). */
  timestamp: string
}

// ------------------------------------------------------------------ store

interface WsEventsState {
  /** Map<trace_id, BrainStateEvent[]> — ordered by arrival. */
  events: Map<string, BrainStateEvent[]>

  /**
   * Append an event for the given trace_id.
   * Silently deduplicates (same trace_id + brain_id + status).
   */
  appendEvent: (event: BrainStateEvent) => void

  /** Remove all events recorded under a specific trace_id. */
  clearTrace: (traceId: string) => void

  /** Reset the entire store. */
  clearAll: () => void

  /** Convenience selector: get all events for a trace (or []). */
  getEventsForTrace: (traceId: string) => BrainStateEvent[]
}

export const useWsEventsStore = create<WsEventsState>()(
  immer((set, get) => ({
    events: new Map(),

    appendEvent: (event: BrainStateEvent) => {
      set((state) => {
        const list = state.events.get(event.trace_id) ?? []

        // Idempotency: skip if an identical status entry already exists
        const isDuplicate = list.some(
          (e) => e.brain_id === event.brain_id && e.status === event.status,
        )
        if (isDuplicate) return

        state.events.set(event.trace_id, [...list, event])
      })
    },

    clearTrace: (traceId: string) => {
      set((state) => {
        state.events.delete(traceId)
      })
    },

    clearAll: () => {
      set((state) => {
        state.events.clear()
      })
    },

    getEventsForTrace: (traceId: string): BrainStateEvent[] => {
      return get().events.get(traceId) ?? []
    },
  })),
)
