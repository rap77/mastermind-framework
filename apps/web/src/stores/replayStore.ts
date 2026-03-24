import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { enableMapSet } from 'immer'

// Enable Immer MapSet plugin — required for Map iteration inside set() callbacks
enableMapSet()

// ─── Types ────────────────────────────────────────────────────────────────────

export type BrainStatusReplay = 'idle' | 'running' | 'complete' | 'error'

export interface BrainStateReplay {
  brain_id: string
  status: BrainStatusReplay
  output?: string
  duration_ms?: number
  timestamp?: number
}

export interface Snapshot {
  timestamp: number
  snapshot: Map<string, BrainStateReplay> // brain_id → BrainStateReplay
}

export interface SnapshotMilestone {
  index: number
  timestamp: number
  label: string
  brainCount: number
}

// ─── Store Interface ──────────────────────────────────────────────────────────

interface ReplayState {
  snapshots: Snapshot[]
  milestones: SnapshotMilestone[]
  currentSnapshotIndex: number
  taskId: string | null

  // Actions
  setSnapshots: (snapshots: Snapshot[]) => void
  computeMilestones: () => void
  jumpToMilestone: (index: number) => void
  getCurrentSnapshot: () => Map<string, BrainStateReplay> | null
  getScrubberPercentage: () => number
  reset: () => void
}

// ─── Milestone computation helper (Miller's Law: max 7) ──────────────────────

const computeMilestonesFromSnapshots = (snapshots: Snapshot[]): SnapshotMilestone[] => {
  if (!snapshots.length) return []

  const interval = Math.ceil(snapshots.length / 7)
  const milestones: SnapshotMilestone[] = []

  for (let i = 0; i < snapshots.length; i += interval) {
    const snapshot = snapshots[i]
    const activeBrains = Array.from(snapshot.snapshot.values()).filter(
      (b) => b.status !== 'idle'
    ).length

    milestones.push({
      index: i,
      timestamp: snapshot.timestamp,
      label: `${Math.round((i / snapshots.length) * 100)}% (${activeBrains} active)`,
      brainCount: activeBrains,
    })
  }

  return milestones
}

// ─── Store ────────────────────────────────────────────────────────────────────

/**
 * useReplayStore — Zustand store for managing Strategy Vault scrubber state.
 *
 * Manages snapshot navigation for execution replay (08-02).
 * Uses Immer middleware with MapSet plugin for Map iteration in set() callbacks.
 * Milestones computed once on setSnapshots (Miller's Law: max 7 points).
 *
 * Lifecycle:
 * 1. Init: empty (no execution loaded)
 * 2. Load: setSnapshots(execution.snapshots) → milestones computed automatically
 * 3. Scrub: jumpToMilestone(index) updates currentSnapshotIndex
 * 4. Exit: reset() clears all state
 */
export const useReplayStore = create<ReplayState>()(
  immer((set, get) => ({
    snapshots: [],
    milestones: [],
    currentSnapshotIndex: 0,
    taskId: null,

    setSnapshots: (snapshots) => {
      set((state) => {
        state.snapshots = snapshots
        state.currentSnapshotIndex = 0
        state.milestones = computeMilestonesFromSnapshots(snapshots)
      })
    },

    computeMilestones: () => {
      set((state) => {
        state.milestones = computeMilestonesFromSnapshots(state.snapshots)
      })
    },

    jumpToMilestone: (index) => {
      set((state) => {
        const clamped = Math.max(0, Math.min(index, state.snapshots.length - 1))
        state.currentSnapshotIndex = clamped
      })
    },

    getCurrentSnapshot: () => {
      const { snapshots, currentSnapshotIndex } = get()
      if (!snapshots.length) return null
      return snapshots[currentSnapshotIndex]?.snapshot ?? null
    },

    getScrubberPercentage: () => {
      const { snapshots, currentSnapshotIndex } = get()
      if (snapshots.length <= 1) return 0
      return Math.round((currentSnapshotIndex / (snapshots.length - 1)) * 100)
    },

    reset: () => {
      set((state) => {
        state.snapshots = []
        state.milestones = []
        state.currentSnapshotIndex = 0
        state.taskId = null
      })
    },
  }))
)
