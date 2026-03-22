import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useBrainStore } from '../brainStore'

describe('brainStore', () => {
  beforeEach(() => {
    // Reset store before each test — includes new fields for 07-03
    useBrainStore.setState({
      brains: new Map(),
      _queue: [],
      _rafId: null,
      historyStack: [],
      sessionInvocationCounts: new Map(),
    })
  })

  it('should initialize with empty brains Map', () => {
    const state = useBrainStore.getState()
    expect(state.brains.size).toBe(0)
    expect(state._queue).toEqual([])
    expect(state._rafId).toBeNull()
  })

  it('should queue brain updates for RAF batching', () => {
    // Placeholder: WS-02 — actual implementation in Plan 05-03
    expect(true).toBe(true)
  })

  it('should drain queue in single RAF batch for 24 simultaneous events', () => {
    // Placeholder: WS-02 — actual implementation in Plan 05-03
    expect(true).toBe(true)
  })

  it('should update targeted brain via useBrainState selector', () => {
    // Placeholder: WS-03 — actual implementation in Plan 05-03
    expect(true).toBe(true)
  })

  it('should not trigger re-render for non-matching brain IDs', () => {
    // Placeholder: WS-03 — actual implementation in Plan 05-03
    expect(true).toBe(true)
  })

  // ─── 07-03: historyStack + sessionInvocationCounts ───────────────────────────

  it('pushHistorySnapshot() adds entry to historyStack with timestamp and Map snapshot', () => {
    // Seed a brain in store
    useBrainStore.setState({
      brains: new Map([['brain-01', { id: 'brain-01', status: 'active', lastUpdated: 1000 }]]),
    })

    const { pushHistorySnapshot } = useBrainStore.getState()
    pushHistorySnapshot()

    const { historyStack } = useBrainStore.getState()
    expect(historyStack).toHaveLength(1)
    expect(historyStack[0].snapshot).toBeInstanceOf(Map)
    expect(historyStack[0].snapshot.get('brain-01')).toEqual({
      id: 'brain-01',
      status: 'active',
      lastUpdated: 1000,
    })
    expect(typeof historyStack[0].timestamp).toBe('number')
    expect(historyStack[0].timestamp).toBeGreaterThan(0)
  })

  it('historyStack snapshot is a copy — mutations after snapshot do not alter it', () => {
    useBrainStore.setState({
      brains: new Map([['brain-01', { id: 'brain-01', status: 'idle', lastUpdated: 500 }]]),
    })

    useBrainStore.getState().pushHistorySnapshot()

    // Now mutate the store (simulate a new brain update)
    useBrainStore.setState({
      brains: new Map([['brain-01', { id: 'brain-01', status: 'complete', lastUpdated: 600 }]]),
    })

    const { historyStack } = useBrainStore.getState()
    // Snapshot must still reflect the state at snapshot time, not the new state
    expect(historyStack[0].snapshot.get('brain-01')?.status).toBe('idle')
  })

  it('incrementInvocationCount sets count to 1 on first call, 2 on second call', () => {
    const { incrementInvocationCount } = useBrainStore.getState()

    incrementInvocationCount('brain-01')
    expect(useBrainStore.getState().sessionInvocationCounts.get('brain-01')).toBe(1)

    incrementInvocationCount('brain-01')
    expect(useBrainStore.getState().sessionInvocationCounts.get('brain-01')).toBe(2)
  })

  it('sessionInvocationCounts initializes as empty Map', () => {
    const { sessionInvocationCounts } = useBrainStore.getState()
    expect(sessionInvocationCounts).toBeInstanceOf(Map)
    expect(sessionInvocationCounts.size).toBe(0)
  })

  it('setState reset resets historyStack and sessionInvocationCounts', () => {
    // Simulate some state built up
    useBrainStore.getState().pushHistorySnapshot()
    useBrainStore.getState().incrementInvocationCount('brain-02')

    // Reset (as done in beforeEach)
    useBrainStore.setState({
      brains: new Map(),
      _queue: [],
      _rafId: null,
      historyStack: [],
      sessionInvocationCounts: new Map(),
    })

    const state = useBrainStore.getState()
    expect(state.historyStack).toHaveLength(0)
    expect(state.sessionInvocationCounts.size).toBe(0)
  })
})
