import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { enableMapSet } from 'immer'

// Enable Immer MapSet plugin — required for Map.get/set/iteration inside set() callbacks
enableMapSet()

export type BrainStatus = 'idle' | 'active' | 'complete' | 'error'

export interface BrainState {
  id: string
  status: BrainStatus
  lastUpdated: number
}

interface BrainStoreState {
  brains: Map<string, BrainState>
  _queue: BrainState[]
  _rafId: number | null
  // 07-03: Ghost Trace data structures (prep for Phase 08 replay)
  historyStack: Array<{ timestamp: number; snapshot: Map<string, BrainState> }>
  sessionInvocationCounts: Map<string, number>
  updateBrain: (brain: BrainState) => void
  _drainQueue: () => void
  pushHistorySnapshot: () => void
  incrementInvocationCount: (brainId: string) => void
}

/**
 * useBrainStore — Zustand store for real-time brain state management.
 *
 * Uses Immer middleware for immutable Map updates and RAF batching for
 * WS burst events (24 brains completing simultaneously = 24 setState calls).
 * Extended in 07-03 with historyStack and sessionInvocationCounts for Ghost Trace.
 */
export const useBrainStore = create<BrainStoreState>()(
  immer((set, get) => ({
    brains: new Map(),
    _queue: [],
    _rafId: null,
    historyStack: [],
    sessionInvocationCounts: new Map(),

    updateBrain: (brain) => {
      // Accumulate in queue — RAF drains before each paint (WS-02 requirement)
      // All mutations must be inside set() callback for Immer compatibility
      set(state => {
        state._queue.push(brain)
        if (!state._rafId) {
          const id = requestAnimationFrame(() => {
            get()._drainQueue()
          })
          state._rafId = id
        }
      })
    },

    _drainQueue: () => {
      set(state => {
        for (const brain of state._queue) {
          state.brains.set(brain.id, brain)
        }
        state._queue = []
        state._rafId = null
      })
    },

    /**
     * pushHistorySnapshot — capture current brains Map as an immutable snapshot
     * for Ghost Trace replay (Phase 08). Called after every WS brain event.
     * Map is NOT tracked by Immer reference — use new Map() copy.
     */
    pushHistorySnapshot: () => {
      set(state => {
        const snapshot = new Map(state.brains)
        state.historyStack.push({ timestamp: Date.now(), snapshot })
      })
    },

    /**
     * incrementInvocationCount — track how many times each brain has been activated
     * in this session. Displayed in BrainNode as ×N counter.
     */
    incrementInvocationCount: (brainId: string) => {
      set(state => {
        const current = state.sessionInvocationCounts.get(brainId) ?? 0
        state.sessionInvocationCounts.set(brainId, current + 1)
      })
    },
  }))
)

/**
 * useBrainState — targeted selector for a single brain's state.
 *
 * Prevents cascade re-renders: only re-renders consumers when the specific
 * brain's state changes (O(1) Map lookup via Zustand selector). (WS-03 requirement)
 *
 * @param id - Brain ID to select (e.g. 'brain-01')
 * @returns BrainState for the given id, or undefined if not yet tracked
 */
export const useBrainState = (id: string) =>
  useBrainStore(state => state.brains.get(id))
