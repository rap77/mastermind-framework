/**
 * Mock Simulation Store Fixture
 *
 * Provides a complete mock Zustand store for Simulation testing.
 * Use this to avoid duplicating mock store setup across test files.
 *
 * @example
 * import { createMockSimulationStore } from '@/test/fixtures/mockSimulationStore'
 * const { useSimulationStore } = createMockSimulationStore({
 *   isPlaying: true,
 *   currentMilestoneIndex: 5,
 * })
 */

import { vi } from 'vitest'
import type { SimulationState } from '@/stores/simulationStore'
import type { Execution, SimulationEvent, ErrorSummary } from '@/stores/simulationStore'

/**
 * Default mock state matching SimulationState interface
 */
export const mockSimulationStoreState: Partial<SimulationState> = {
  // Execution data
  currentExecution: null,

  // Loading state
  isLoading: false,
  loadError: null,

  // Playback state
  isPlaying: false,
  playbackSpeed: 1,
  currentMilestoneIndex: 0,
  playbackFrameId: null,

  // Analysis results
  errorNodes: new Set(),
  errorMessages: new Map(),
  slowNodes: new Map(),
  slowThreshold: 1000,
  filteredEvents: [],

  // Actions — Execution management
  validateExecution: vi.fn(),
  loadExecution: vi.fn(),
  setLoading: vi.fn(),
  setLoadError: vi.fn(),
  reset: vi.fn(),

  // Actions — Playback controls
  play: vi.fn(),
  pause: vi.fn(),
  setPlaybackSpeed: vi.fn(),
  setSlowThreshold: vi.fn(),

  // Actions — Navigation
  jumpToMilestone: vi.fn(),

  // Actions — Computed values
  getErrorSummary: vi.fn(() => ({ totalErrors: 0, slowNodes: 0, totalTime: 0 })),
  getFilteredEvents: vi.fn(() => []),
  getCurrentGraphSnapshot: vi.fn(() => null),
}

/**
 * Creates a mock Simulation store with optional custom state
 *
 * @param customState - Partial state to override defaults
 * @returns Mock store object with useSimulationStore hook
 *
 * @example
 * // Basic usage
 * const { useSimulationStore } = createMockSimulationStore()
 *
 * // With custom state
 * const { useSimulationStore } = createMockSimulationStore({
 *   isPlaying: true,
 *   currentMilestoneIndex: 5,
 *   errorNodes: new Set(['node-1', 'node-2']),
 * })
 *
 * // In tests
 * vi.mocked(useSimulationStore).mockReturnValue({ isPlaying: true })
 */
export function createMockSimulationStore(
  customState: Partial<SimulationState> = {}
) {
  const state = {
    ...mockSimulationStoreState,
    ...customState,
  }

  const useSimulationStore = vi.fn((selector) => {
    if (selector) return selector(state as SimulationState)
    return state
  })

  // Add getState method for advanced use cases
  ;(useSimulationStore as any).getState = () => state

  return {
    useSimulationStore,
    getState: () => state,
  }
}
