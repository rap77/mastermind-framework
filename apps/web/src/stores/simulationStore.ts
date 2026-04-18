/**
 * Simulation Store — Zustand state management for execution replay
 *
 * Follows the replayStore.ts and flowDesignerStore.ts patterns with Immer middleware.
 * Manages simulation state for visual replay of past executions with timeline scrubbing.
 */

import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { enableMapSet } from 'immer'
import type { FlowDefinition } from '@/components/flow-designer/types'

// Enable Immer MapSet plugin — required for Map operations inside set() callbacks
enableMapSet()

// ─── Types ────────────────────────────────────────────────────────────────────

/**
 * BrainOutput — per-brain execution output from API
 */
export interface BrainOutput {
  brain_id: string
  status: 'idle' | 'running' | 'complete' | 'error'
  output: string
  duration_ms: number
  timestamp: number
}

/**
 * SnapshotMilestone — point-in-time milestone from execution
 */
export interface SnapshotMilestone {
  index: number
  timestamp: number
  label: string
  brain_count: number
}

/**
 * Execution — full execution record from API
 */
export interface Execution {
  id: string
  task_id: string
  brief: string
  status: 'success' | 'error' | 'running'
  duration_ms: number
  brain_count: number
  created_at: string
  milestones: SnapshotMilestone[]
  brain_outputs: Record<string, BrainOutput>
  graph_snapshot: Record<string, unknown>
}

/**
 * SimulationEvent — timeline event for filtering
 */
export interface SimulationEvent {
  timestamp: number
  type: 'info' | 'success' | 'error' | 'warning'
  message: string
  brainId?: string
}

/**
 * ErrorSummary — computed error statistics
 */
export interface ErrorSummary {
  totalErrors: number
  slowNodes: number
  totalTime: number
}

// ─── Store Interface ──────────────────────────────────────────────────────────

interface SimulationState {
  // Execution data
  currentExecution: Execution | null

  // Loading state
  isLoading: boolean
  loadError: Error | null

  // Playback state
  isPlaying: boolean
  playbackSpeed: 0.5 | 1 | 2 | 5
  currentMilestoneIndex: number
  playbackFrameId: number | null // requestAnimationFrame ID for cleanup

  // Analysis results
  errorNodes: Set<string> // Node IDs with error status
  errorMessages: Map<string, string> // Node ID → error message from brain_outputs
  slowNodes: Map<string, number> // Node ID → duration_ms for slow nodes (>slowThreshold)
  slowThreshold: number // Threshold in milliseconds for slow node detection (default: 1000ms)
  filteredEvents: SimulationEvent[]

  // Actions — Execution management
  validateExecution: (execution: Execution) => void
  loadExecution: (execution: Execution) => void
  setLoading: (loading: boolean) => void
  setLoadError: (error: Error | null) => void
  reset: () => void

  // Actions — Playback controls
  play: () => void
  pause: () => void
  setPlaybackSpeed: (speed: 0.5 | 1 | 2 | 5) => void
  setSlowThreshold: (threshold: number) => void

  // Actions — Navigation
  jumpToMilestone: (index: number) => void

  // Actions — Computed values
  getErrorSummary: () => ErrorSummary
  getFilteredEvents: () => SimulationEvent[]
  getCurrentGraphSnapshot: () => FlowDefinition | null
}

// ─── Constants ────────────────────────────────────────────────────────────────

const SLOW_NODE_THRESHOLD_MS = 1000 // 1 second = perceptible delay

// ─── Helper Functions ─────────────────────────────────────────────────────────

/**
 * detectErrors — identifies nodes with error status and maps error messages
 */
const detectErrors = (
  brainOutputs: Record<string, BrainOutput>,
  graphSnapshot: Record<string, unknown>,
): { errorNodes: Set<string>; errorMessages: Map<string, string> } => {
  const errorNodes = new Set<string>()
  const errorMessages = new Map<string, string>()

  // Map brain_id to node_id by matching brainId in node data
  const nodes = (graphSnapshot.nodes as Array<{ id: string; data: { brainId?: string } }>) || []

  nodes.forEach((node) => {
    const brainId = node.data?.brainId
    const brainOutput = brainId ? brainOutputs[brainId] : null

    if (brainId && brainOutput?.status === 'error') {
      errorNodes.add(node.id)
      // Store the actual error message from brain_outputs
      errorMessages.set(node.id, brainOutput.output || 'Execution failed')
    }
  })

  return { errorNodes, errorMessages }
}

/**
 * detectSlowNodes — identifies nodes with duration > threshold
 */
const detectSlowNodes = (
  brainOutputs: Record<string, BrainOutput>,
  graphSnapshot: Record<string, unknown>,
  thresholdMs: number,
): Map<string, number> => {
  const slowNodes = new Map<string, number>()

  const nodes = (graphSnapshot.nodes as Array<{ id: string; data: { brainId?: string } }>) || []

  nodes.forEach((node) => {
    const brainId = node.data?.brainId
    if (brainId && brainOutputs[brainId]) {
      const duration = brainOutputs[brainId].duration_ms
      if (duration > thresholdMs) {
        slowNodes.set(node.id, duration)
      }
    }
  })

  return slowNodes
}

/**
 * generateEvents — creates timeline events from brain outputs
 */
const generateEvents = (
  brainOutputs: Record<string, BrainOutput>,
  slowThreshold: number,
): SimulationEvent[] => {
  const events: SimulationEvent[] = []

  Object.values(brainOutputs).forEach((output) => {
    // Start event
    events.push({
      timestamp: output.timestamp,
      type: 'info',
      message: `Brain ${output.brain_id} started`,
      brainId: output.brain_id,
    })

    // Completion event
    if (output.status === 'complete') {
      events.push({
        timestamp: output.timestamp + output.duration_ms,
        type: 'success',
        message: `Brain ${output.brain_id} completed in ${output.duration_ms}ms`,
        brainId: output.brain_id,
      })
    } else if (output.status === 'error') {
      events.push({
        timestamp: output.timestamp + output.duration_ms,
        type: 'error',
        message: `Brain ${output.brain_id} failed: ${output.output.slice(0, 100)}`,
        brainId: output.brain_id,
      })
    }

    // Slow warning
    if (output.duration_ms > slowThreshold) {
      events.push({
        timestamp: output.timestamp + output.duration_ms,
        type: 'warning',
        message: `Brain ${output.brain_id} slow: ${output.duration_ms}ms`,
        brainId: output.brain_id,
      })
    }
  })

  // Sort by timestamp
  return events.sort((a, b) => a.timestamp - b.timestamp)
}

/**
 * filterEventsByTimestamp — returns events up to current milestone timestamp
 */
const filterEventsByTimestamp = (
  events: SimulationEvent[],
  currentTimestamp: number,
): SimulationEvent[] => {
  return events.filter((event) => event.timestamp <= currentTimestamp)
}

// ─── Store ────────────────────────────────────────────────────────────────────

/**
 * useSimulationStore — Zustand store for Simulation & Replay Engine
 *
 * Manages execution replay state with timeline scrubbing, error detection,
 * and playback controls. Uses Immer middleware with MapSet plugin for Map/Set operations.
 *
 * Lifecycle:
 * 1. Init: empty (no execution loaded)
 * 2. Load: loadExecution(execution) → errors/slow nodes detected automatically
 * 3. Play: play() → starts playback, RAF updates currentMilestoneIndex
 * 4. Navigate: jumpToMilestone(index) → updates current position
 * 5. Exit: reset() → clears all state
 *
 * Error detection:
 * - Error nodes: brain_outputs[brain_id].status === "error"
 * - Slow nodes: duration_ms > 1000ms threshold
 *
 * Event filtering:
 * - Events generated from brain_outputs (start, complete, error, slow)
 * - Filtered by current milestone timestamp for timeline scrubbing
 */
export const useSimulationStore = create<SimulationState>()(
  immer((set, get) => ({
    // Initial state
    currentExecution: null,
    isLoading: false,
    loadError: null,
    isPlaying: false,
    playbackSpeed: 1,
    currentMilestoneIndex: 0,
    playbackFrameId: null,
    errorNodes: new Set(),
    errorMessages: new Map(),
    slowNodes: new Map(),
    slowThreshold: 1000, // Default: 1 second = perceptible delay
    filteredEvents: [],

    // ─── Execution Management ─────────────────────────────────────────────────────

    /**
     * validateExecution — validates required execution fields at runtime
     * @throws Error if validation fails
     */
    validateExecution: (execution: Execution) => {
      const requiredFields: (keyof Execution)[] = [
        'id',
        'task_id',
        'brain_outputs',
        'milestones',
        'graph_snapshot',
      ]

      for (const field of requiredFields) {
        if (execution[field] === undefined || execution[field] === null) {
          throw new Error(`Execution validation failed: missing required field '${field}'`)
        }
      }

      // Validate milestones is not empty
      if (!Array.isArray(execution.milestones) || execution.milestones.length === 0) {
        throw new Error('Execution validation failed: milestones cannot be empty')
      }

      // Validate brain_outputs is an object
      if (typeof execution.brain_outputs !== 'object' || Array.isArray(execution.brain_outputs)) {
        throw new Error('Execution validation failed: brain_outputs must be an object')
      }

      // Validate graph_snapshot is an object
      if (typeof execution.graph_snapshot !== 'object' || Array.isArray(execution.graph_snapshot)) {
        throw new Error('Execution validation failed: graph_snapshot must be an object')
      }
    },

    /**
     * loadExecution — loads an execution and detects errors/slow nodes
     * @param execution - Execution record from API
     */
    loadExecution: (execution) => {
      // Validate execution before processing
      get().validateExecution(execution)

      // Detect errors and slow nodes first (outside set for performance)
      const { errorNodes, errorMessages } = detectErrors(execution.brain_outputs, execution.graph_snapshot)
      const slowNodes = detectSlowNodes(
        execution.brain_outputs,
        execution.graph_snapshot,
        get().slowThreshold, // Use state's threshold instead of constant
      )
      const filteredEvents = generateEvents(execution.brain_outputs, get().slowThreshold)

      set((state) => {
        state.currentExecution = execution
        state.currentMilestoneIndex = 0
        state.isPlaying = false
        state.errorNodes = errorNodes
        state.errorMessages = errorMessages
        state.slowNodes = slowNodes
        state.filteredEvents = filteredEvents
      })
    },

    /**
     * setLoading — sets the loading state for execution loading
     * @param loading - Whether an execution is currently being loaded
     */
    setLoading: (loading: boolean) => {
      set((state) => {
        state.isLoading = loading
      })
    },

    /**
     * setLoadError — sets the error state for execution loading
     * @param error - Error that occurred during loading, or null to clear
     */
    setLoadError: (error: Error | null) => {
      set((state) => {
        state.loadError = error
        state.isLoading = false // Clear loading state when error is set
      })
    },

    /**
     * reset — clears all execution state
     */
    reset: () => {
      const state = get()

      // Cancel any pending animation frame
      if (state.playbackFrameId !== null) {
        cancelAnimationFrame(state.playbackFrameId)
      }

      set((state) => {
        state.currentExecution = null
        state.isLoading = false
        state.loadError = null
        state.isPlaying = false
        state.playbackSpeed = 1
        state.currentMilestoneIndex = 0
        state.playbackFrameId = null
        state.errorNodes = new Set()
        state.errorMessages = new Map()
        state.slowNodes = new Map()
        state.slowThreshold = 1000 // Reset to default
        state.filteredEvents = []
      })
    },

    // ─── Playback Controls ───────────────────────────────────────────────────────

    /**
     * play — starts playback from current position using requestAnimationFrame
     */
    play: () => {
      const state = get()

      // Don't start if already playing or no execution loaded
      if (state.isPlaying || !state.currentExecution) {
        return
      }

      // Set playing state
      set((state) => {
        state.isPlaying = true
      })

      // Start the animation loop
      const animate = () => {
        const currentState = get()

        // Stop if not playing or no execution
        if (!currentState.isPlaying || !currentState.currentExecution) {
          return
        }

        // Check if we've reached the end
        const maxIndex = currentState.currentExecution.milestones.length - 1
        if (currentState.currentMilestoneIndex >= maxIndex) {
          // Auto-pause at end
          currentState.pause()
          return
        }

        // Advance to next milestone
        set((state) => {
          state.currentMilestoneIndex = state.currentMilestoneIndex + 1
        })

        // Schedule next frame (adjusted by playback speed)
        const frameId = requestAnimationFrame(animate)
        set((state) => {
          state.playbackFrameId = frameId
        })
      }

      // Start the loop
      const frameId = requestAnimationFrame(animate)
      set((state) => {
        state.playbackFrameId = frameId
      })
    },

    /**
     * pause — pauses playback and cancels animation frame
     */
    pause: () => {
      const state = get()

      // Cancel the animation frame
      if (state.playbackFrameId !== null) {
        cancelAnimationFrame(state.playbackFrameId)
      }

      set((state) => {
        state.isPlaying = false
        state.playbackFrameId = null
      })
    },

    /**
     * setPlaybackSpeed — changes playback speed
     * @param speed - Playback speed multiplier (0.5x, 1x, 2x, 5x)
     */
    setPlaybackSpeed: (speed) => {
      set((state) => {
        state.playbackSpeed = speed
      })
    },

    // ─── Navigation ───────────────────────────────────────────────────────────────

    /**
     * jumpToMilestone — jumps to a specific milestone index
     * @param index - Milestone index (clamped to [0, milestones.length - 1])
     */
    jumpToMilestone: (index) => {
      set((state) => {
        const maxIndex = state.currentExecution?.milestones.length
          ? state.currentExecution.milestones.length - 1
          : 0
        state.currentMilestoneIndex = Math.max(0, Math.min(index, maxIndex))
      })
    },

    /**
     * setSlowThreshold — changes the slow node detection threshold
     * @param threshold - Threshold in milliseconds (must be positive)
     *
     * Re-detects slow nodes for the current execution with the new threshold.
     * Invalid values (<= 0) are ignored.
     */
    setSlowThreshold: (threshold) => {
      // Validate threshold
      if (threshold <= 0) {
        return // Don't update for invalid values
      }

      const state = get()

      set((state) => {
        state.slowThreshold = threshold
      })

      // Re-detect slow nodes if execution is loaded
      if (state.currentExecution) {
        const newSlowNodes = detectSlowNodes(
          state.currentExecution.brain_outputs,
          state.currentExecution.graph_snapshot,
          threshold,
        )

        set((state) => {
          state.slowNodes = newSlowNodes
        })
      }
    },

    // ─── Computed Values ─────────────────────────────────────────────────────────

    /**
     * getErrorSummary — computes error statistics
     * @returns ErrorSummary with total errors, slow nodes count, total time
     */
    getErrorSummary: () => {
      const state = get()

      return {
        totalErrors: state.errorNodes.size,
        slowNodes: state.slowNodes.size,
        totalTime: state.currentExecution?.duration_ms || 0,
      }
    },

    /**
     * getFilteredEvents — returns events up to current milestone timestamp
     * @returns Array of SimulationEvent filtered by current position
     */
    getFilteredEvents: () => {
      const state = get()

      if (!state.currentExecution || state.currentExecution.milestones.length === 0) {
        return []
      }

      const currentMilestone = state.currentExecution.milestones[state.currentMilestoneIndex]
      if (!currentMilestone) {
        return []
      }

      return filterEventsByTimestamp(state.filteredEvents, currentMilestone.timestamp)
    },

    /**
     * getCurrentGraphSnapshot — returns the current graph snapshot as FlowDefinition
     * @returns FlowDefinition or null if no execution loaded
     */
    getCurrentGraphSnapshot: () => {
      const state = get()

      if (!state.currentExecution) {
        return null
      }

      // Cast graph_snapshot to FlowDefinition (already validated by API)
      return state.currentExecution.graph_snapshot as FlowDefinition
    },
  })),
)

// ─── Selector Hooks ───────────────────────────────────────────────────────────

/**
 * useCurrentExecution — selector hook for current execution
 */
export const useCurrentExecution = () =>
  useSimulationStore((state) => state.currentExecution)

/**
 * useIsPlaying — selector hook for playing state
 */
export const useIsPlaying = () => useSimulationStore((state) => state.isPlaying)

/**
 * usePlaybackSpeed — selector hook for playback speed
 */
export const usePlaybackSpeed = () => useSimulationStore((state) => state.playbackSpeed)

/**
 * useCurrentMilestoneIndex — selector hook for current milestone index
 */
export const useCurrentMilestoneIndex = () =>
  useSimulationStore((state) => state.currentMilestoneIndex)

/**
 * useErrorNodes — selector hook for error nodes set
 */
export const useErrorNodes = () => useSimulationStore((state) => state.errorNodes)

/**
 * useErrorMessages — selector hook for error messages map
 */
export const useErrorMessages = () => useSimulationStore((state) => state.errorMessages)

/**
 * useSlowNodes — selector hook for slow nodes map
 */
export const useSlowNodes = () => useSimulationStore((state) => state.slowNodes)

/**
 * useErrorSummary — selector hook for computed error summary
 */
export const useErrorSummary = () => useSimulationStore((state) => state.getErrorSummary())

/**
 * useFilteredEvents — selector hook for filtered events
 */
export const useFilteredEvents = () => useSimulationStore((state) => state.getFilteredEvents())

/**
 * useCurrentGraphSnapshot — selector hook for current graph snapshot
 */
export const useCurrentGraphSnapshot = () =>
  useSimulationStore((state) => state.getCurrentGraphSnapshot())
