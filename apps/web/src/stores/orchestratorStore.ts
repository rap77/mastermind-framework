/**
 * orchestratorStore — Zustand store for task execution + Focus Mode state.
 *
 * **Purpose:** Tracks active task lifecycle and Focus Mode activation.
 * **Phase:** 08-04 — Wave 3 (Focus Mode)
 *
 * **Semantics:**
 * - state='running' + userOverride=false → Focus Mode ACTIVE
 * - state='running' + userOverride=true  → Focus Mode DISABLED (user escape)
 * - state='complete'                     → Focus Mode exits (userOverride reset)
 *
 * **Computed:** isFocusMode = (state === 'running') && !userOverride
 *
 * **No persistence** — page refresh resets to idle.
 */

import { create } from 'zustand'

// ─── Types ────────────────────────────────────────────────────────────────────

export type TaskState = 'idle' | 'running' | 'complete' | 'error'

export interface OrchestratorState {
  // Task state
  taskId: string | null
  state: TaskState
  briefText: string
  startedAt: number
  completedAt: number | null

  // Focus Mode
  userOverride: boolean // true = user pressed [Esc]/[F], don't auto-activate
  isFocusMode: boolean // computed: state === 'running' && !userOverride

  // Actions
  startTask: (taskId: string, brief: string) => void
  completeTask: () => void
  setError: () => void
  toggleOverride: () => void // called on [F] or [Esc] key
  reset: () => void
}

// ─── Store ────────────────────────────────────────────────────────────────────

export const useOrchestratorStore = create<OrchestratorState>()((set, get) => ({
  // Initial state
  taskId: null,
  state: 'idle',
  briefText: '',
  startedAt: 0,
  completedAt: null,
  userOverride: false,
  isFocusMode: false,

  startTask: (taskId: string, brief: string) => {
    set({
      taskId,
      state: 'running',
      briefText: brief,
      startedAt: Date.now(),
      completedAt: null,
      userOverride: false,
      // isFocusMode = state === 'running' && !userOverride → true
      isFocusMode: true,
    })
  },

  completeTask: () => {
    set((state) => ({
      state: 'complete',
      completedAt: Date.now(),
      userOverride: false,
      // isFocusMode = state === 'complete' → false
      isFocusMode: false,
    }))
  },

  setError: () => {
    set({
      state: 'error',
      completedAt: Date.now(),
      userOverride: false,
      isFocusMode: false,
    })
  },

  toggleOverride: () => {
    set((state) => {
      const newOverride = !state.userOverride
      return {
        userOverride: newOverride,
        // Recompute: isFocusMode = running AND not overridden
        isFocusMode: state.state === 'running' && !newOverride,
      }
    })
  },

  reset: () => {
    set({
      taskId: null,
      state: 'idle',
      briefText: '',
      startedAt: 0,
      completedAt: null,
      userOverride: false,
      isFocusMode: false,
    })
  },
}))
