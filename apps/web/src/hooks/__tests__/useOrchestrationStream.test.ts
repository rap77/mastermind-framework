/**
 * useOrchestrationStream.test.ts — D2.07
 *
 * Hook test: useOrchestrationStream with mock store returns correct state.
 *
 * Strategy: manipulate the real Zustand store (wsEventsStore) — no need to
 * mock it since it's an in-memory store. Tests isolate by calling clearAll()
 * in beforeEach.
 */

import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import { useOrchestrationStream } from '../useOrchestrationStream'
import { useWsEventsStore } from '@/stores/wsEventsStore'
import type { BrainStateEvent } from '@/stores/wsEventsStore'

// ─── Helpers ───────────────────────────────────────────────────────────────────

function makeEvent(
  overrides: Partial<BrainStateEvent> & {
    trace_id?: string
    brain_id?: string
  } = {},
): BrainStateEvent {
  return {
    trace_id: overrides.trace_id ?? 'trace-001',
    brain_id: overrides.brain_id ?? 'brain-01',
    status: overrides.status ?? 'dispatched',
    timestamp: overrides.timestamp ?? new Date().toISOString(),
    ...overrides,
  }
}

// ─── Tests ─────────────────────────────────────────────────────────────────────

describe('useOrchestrationStream (D2.07)', () => {
  beforeEach(() => {
    // Reset store between tests
    useWsEventsStore.getState().clearAll()
  })

  it('returns empty events and traceCount 0 when store is empty', () => {
    const { result } = renderHook(() => useOrchestrationStream())

    expect(result.current.events).toHaveLength(0)
    expect(result.current.traceCount).toBe(0)
  })

  it('returns all events when store has entries (no filter)', () => {
    act(() => {
      useWsEventsStore.getState().appendEvent(makeEvent({ brain_id: 'brain-01', status: 'dispatched' }))
      useWsEventsStore.getState().appendEvent(makeEvent({ brain_id: 'brain-01', status: 'running' }))
      useWsEventsStore.getState().appendEvent(makeEvent({ brain_id: 'brain-02', status: 'completed', trace_id: 'trace-002' }))
    })

    const { result } = renderHook(() => useOrchestrationStream())

    expect(result.current.events).toHaveLength(3)
    expect(result.current.traceCount).toBe(2)
  })

  it('returns only filtered events when brainId option is provided', () => {
    act(() => {
      useWsEventsStore.getState().appendEvent(makeEvent({ brain_id: 'brain-01', status: 'dispatched' }))
      useWsEventsStore.getState().appendEvent(makeEvent({ brain_id: 'brain-02', status: 'running', trace_id: 'trace-002' }))
    })

    const { result } = renderHook(() =>
      useOrchestrationStream({ brainId: 'brain-01' }),
    )

    expect(result.current.events).toHaveLength(1)
    expect(result.current.events[0].brain_id).toBe('brain-01')
  })

  it('returns events sorted chronologically (oldest first)', () => {
    act(() => {
      useWsEventsStore.getState().appendEvent(
        makeEvent({ brain_id: 'brain-01', status: 'running', timestamp: '2026-05-14T10:00:02.000Z' }),
      )
      useWsEventsStore.getState().appendEvent(
        makeEvent({ brain_id: 'brain-01', status: 'dispatched', timestamp: '2026-05-14T10:00:01.000Z' }),
      )
      useWsEventsStore.getState().appendEvent(
        makeEvent({ brain_id: 'brain-01', status: 'completed', timestamp: '2026-05-14T10:00:05.000Z' }),
      )
    })

    const { result } = renderHook(() => useOrchestrationStream())

    const statuses = result.current.events.map((e) => e.status)
    expect(statuses).toEqual(['dispatched', 'running', 'completed'])
  })

  it('traceCount reflects number of distinct trace_ids', () => {
    act(() => {
      useWsEventsStore.getState().appendEvent(makeEvent({ trace_id: 'trace-A', brain_id: 'brain-01', status: 'dispatched' }))
      useWsEventsStore.getState().appendEvent(makeEvent({ trace_id: 'trace-B', brain_id: 'brain-02', status: 'running' }))
      useWsEventsStore.getState().appendEvent(makeEvent({ trace_id: 'trace-C', brain_id: 'brain-03', status: 'completed' }))
    })

    const { result } = renderHook(() => useOrchestrationStream())

    expect(result.current.traceCount).toBe(3)
  })

  it('returns empty list when brainId filter matches no events', () => {
    act(() => {
      useWsEventsStore.getState().appendEvent(makeEvent({ brain_id: 'brain-01', status: 'dispatched' }))
    })

    const { result } = renderHook(() =>
      useOrchestrationStream({ brainId: 'brain-99' }),
    )

    expect(result.current.events).toHaveLength(0)
  })

  it('updates reactively when new events are appended', () => {
    const { result } = renderHook(() => useOrchestrationStream())

    expect(result.current.events).toHaveLength(0)

    act(() => {
      useWsEventsStore.getState().appendEvent(makeEvent())
    })

    expect(result.current.events).toHaveLength(1)

    act(() => {
      useWsEventsStore.getState().appendEvent(
        makeEvent({ brain_id: 'brain-01', status: 'completed' }),
      )
    })

    expect(result.current.events).toHaveLength(2)
  })

  it('does not duplicate events (store dedup is respected)', () => {
    const event = makeEvent({ brain_id: 'brain-01', status: 'dispatched' })

    act(() => {
      useWsEventsStore.getState().appendEvent(event)
      useWsEventsStore.getState().appendEvent(event) // duplicate — store deduplicates
    })

    const { result } = renderHook(() => useOrchestrationStream())

    expect(result.current.events).toHaveLength(1)
  })

  it('handles null brainId option as "no filter"', () => {
    act(() => {
      useWsEventsStore.getState().appendEvent(makeEvent({ brain_id: 'brain-01', status: 'dispatched' }))
      useWsEventsStore.getState().appendEvent(makeEvent({ brain_id: 'brain-02', status: 'running', trace_id: 'trace-002' }))
    })

    const { result } = renderHook(() =>
      useOrchestrationStream({ brainId: null }),
    )

    expect(result.current.events).toHaveLength(2)
  })
})
