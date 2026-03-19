import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

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
  updateBrain: (brain: BrainState) => void
  _drainQueue: () => void
}

export const useBrainStore = create<BrainStoreState>()(
  immer((set, get) => ({
    brains: new Map(),
    _queue: [],
    _rafId: null,

    updateBrain: (brain) => {
      // Accumulate in queue — RAF drains before each paint (WS-02 requirement)
      get()._queue.push(brain)
      if (!get()._rafId) {
        const id = requestAnimationFrame(() => {
          get()._drainQueue()
        })
        set(state => { state._rafId = id })
      }
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
  }))
)

// Targeted selector — prevents cascade re-renders (WS-03 requirement)
export const useBrainState = (id: string) =>
  useBrainStore(state => state.brains.get(id))
