/**
 * simulationStore.test.ts — Unit tests for simulationStore
 *
 * Tests the simulation replay store with TDD approach:
 * - Execution loading with error/slow node detection
 * - Playback controls (play/pause/reset/speed)
 * - Milestone navigation
 * - Error summary computation
 * - Event filtering
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useSimulationStore } from '../simulationStore'
import type { FlowDefinition } from '@/components/flow-designer/types'

// Mock execution data
const mockExecution = {
  id: 'exec-123',
  task_id: 'task-456',
  brief: 'Test execution brief',
  status: 'success',
  duration_ms: 5000,
  brain_count: 3,
  created_at: '2026-04-16T10:00:00Z',
  milestones: [
    { index: 0, timestamp: 1000, label: 'Start', brain_count: 0 },
    { index: 1, timestamp: 2000, label: 'Brain #1 complete', brain_count: 1 },
    { index: 2, timestamp: 3000, label: 'Brain #2 complete', brain_count: 2 },
    { index: 3, timestamp: 4000, label: 'Complete', brain_count: 3 },
  ],
  brain_outputs: {
    'brain-01': {
      brain_id: 'brain-01',
      status: 'complete',
      output: 'Output 1',
      duration_ms: 500,
      timestamp: 1500,
    },
    'brain-02': {
      brain_id: 'brain-02',
      status: 'error',
      output: 'Error occurred',
      duration_ms: 1500,
      timestamp: 2500,
    },
    'brain-03': {
      brain_id: 'brain-03',
      status: 'complete',
      output: 'Output 3',
      duration_ms: 1200, // Slow node (> 1000ms)
      timestamp: 3500,
    },
  },
  graph_snapshot: {
    nodes: [
      {
        id: 'node-1',
        type: 'brain',
        position: { x: 100, y: 100 },
        data: { label: 'Brain 1', brainId: 'brain-01' },
      },
      {
        id: 'node-2',
        type: 'brain',
        position: { x: 300, y: 100 },
        data: { label: 'Brain 2', brainId: 'brain-02' },
      },
      {
        id: 'node-3',
        type: 'brain',
        position: { x: 500, y: 100 },
        data: { label: 'Brain 3', brainId: 'brain-03' },
      },
    ],
    edges: [
      { id: 'edge-1', source: 'node-1', target: 'node-2' },
      { id: 'edge-2', source: 'node-2', target: 'node-3' },
    ],
  },
}

describe('simulationStore', () => {
  beforeEach(() => {
    // Reset store before each test
    const store = useSimulationStore.getState()
    store.reset()
  })

  describe('Initial State', () => {
    it('should start with empty state', () => {
      const store = useSimulationStore.getState()

      expect(store.currentExecution).toBeNull()
      expect(store.isPlaying).toBe(false)
      expect(store.playbackSpeed).toBe(1)
      expect(store.currentMilestoneIndex).toBe(0)
      expect(store.errorNodes.size).toBe(0)
      expect(store.slowNodes.size).toBe(0)
      expect(store.filteredEvents).toEqual([])
    })
  })

  describe('loadExecution', () => {
    it('should load execution and detect errors', () => {
      useSimulationStore.getState().loadExecution(mockExecution)

      expect(useSimulationStore.getState().currentExecution).toEqual(mockExecution)
      expect(useSimulationStore.getState().errorNodes.size).toBe(1)
      expect(useSimulationStore.getState().errorNodes.has('node-2')).toBe(true) // brain-02 has error
    })

    it('should load execution and populate error messages map', () => {
      useSimulationStore.getState().loadExecution(mockExecution)

      const errorMessages = useSimulationStore.getState().errorMessages
      expect(errorMessages.size).toBe(1)
      expect(errorMessages.has('node-2')).toBe(true)
      expect(errorMessages.get('node-2')).toBe('Error occurred') // From brain-02 output
    })

    it('should load execution and detect slow nodes', () => {
      useSimulationStore.getState().loadExecution(mockExecution)

      expect(useSimulationStore.getState().slowNodes.size).toBe(2)
      expect(useSimulationStore.getState().slowNodes.has('node-2')).toBe(true) // 1500ms
      expect(useSimulationStore.getState().slowNodes.has('node-3')).toBe(true) // 1200ms
      expect(useSimulationStore.getState().slowNodes.get('node-2')).toBe(1500)
      expect(useSimulationStore.getState().slowNodes.get('node-3')).toBe(1200)
    })

    it('should reset milestone index to 0 when loading', () => {
      useSimulationStore.getState().loadExecution(mockExecution)
      expect(useSimulationStore.getState().currentMilestoneIndex).toBe(0)
    })

    it('should generate filtered events from brain outputs', () => {
      useSimulationStore.getState().loadExecution(mockExecution)

      expect(useSimulationStore.getState().filteredEvents.length).toBeGreaterThan(0)
      expect(useSimulationStore.getState().filteredEvents[0]).toHaveProperty('timestamp')
      expect(useSimulationStore.getState().filteredEvents[0]).toHaveProperty('type')
      expect(useSimulationStore.getState().filteredEvents[0]).toHaveProperty('message')
    })

    it('should throw error when execution is missing required id field', () => {
      const invalidExecution = { ...mockExecution, id: undefined as unknown as string }

      expect(() => {
        useSimulationStore.getState().loadExecution(invalidExecution)
      }).toThrow('Execution validation failed: missing required field')
    })

    it('should throw error when execution is missing required task_id field', () => {
      const invalidExecution = { ...mockExecution, task_id: undefined as unknown as string }

      expect(() => {
        useSimulationStore.getState().loadExecution(invalidExecution)
      }).toThrow('Execution validation failed: missing required field')
    })

    it('should throw error when execution is missing required brain_outputs field', () => {
      const invalidExecution = { ...mockExecution, brain_outputs: undefined as unknown as Record<string, unknown> }

      expect(() => {
        useSimulationStore.getState().loadExecution(invalidExecution)
      }).toThrow('Execution validation failed: missing required field')
    })

    it('should throw error when execution is missing required milestones field', () => {
      const invalidExecution = { ...mockExecution, milestones: undefined as unknown as unknown[] }

      expect(() => {
        useSimulationStore.getState().loadExecution(invalidExecution)
      }).toThrow('Execution validation failed: missing required field')
    })

    it('should throw error when execution is missing required graph_snapshot field', () => {
      const invalidExecution = { ...mockExecution, graph_snapshot: undefined as unknown as Record<string, unknown> }

      expect(() => {
        useSimulationStore.getState().loadExecution(invalidExecution)
      }).toThrow('Execution validation failed: missing required field')
    })

    it('should throw error when milestones array is empty', () => {
      const invalidExecution = { ...mockExecution, milestones: [] }

      expect(() => {
        useSimulationStore.getState().loadExecution(invalidExecution)
      }).toThrow('Execution validation failed: milestones cannot be empty')
    })

    it('should validate when all required fields are present', () => {
      expect(() => {
        useSimulationStore.getState().loadExecution(mockExecution)
      }).not.toThrow()
    })
  })

  describe('Playback Controls', () => {
    beforeEach(() => {
      useSimulationStore.getState().loadExecution(mockExecution)
    })

    it('should start playing when play() is called', () => {
      useSimulationStore.getState().play()
      expect(useSimulationStore.getState().isPlaying).toBe(true)
    })

    it('should pause when pause() is called', () => {
      useSimulationStore.getState().play()
      useSimulationStore.getState().pause()
      expect(useSimulationStore.getState().isPlaying).toBe(false)
    })

    it('should reset state when reset() is called', () => {
      useSimulationStore.getState().play()
      useSimulationStore.getState().jumpToMilestone(2)
      useSimulationStore.getState().reset()

      expect(useSimulationStore.getState().isPlaying).toBe(false)
      expect(useSimulationStore.getState().currentMilestoneIndex).toBe(0)
    })

    it('should advance timeline when playing with requestAnimationFrame loop', async () => {
      const store = useSimulationStore.getState()

      // Start at milestone 0
      expect(store.currentMilestoneIndex).toBe(0)

      // Start playback
      store.play()

      // Wait for animation frame to advance timeline
      await new Promise(resolve => setTimeout(resolve, 100))

      // Timeline should have advanced
      const newStore = useSimulationStore.getState()
      expect(newStore.currentMilestoneIndex).toBeGreaterThan(0)

      // Clean up: stop playback
      newStore.pause()
    })

    it('should stop advancing timeline when paused', async () => {
      const store = useSimulationStore.getState()

      store.play()
      await new Promise(resolve => setTimeout(resolve, 100))

      const playingIndex = useSimulationStore.getState().currentMilestoneIndex

      store.pause()
      await new Promise(resolve => setTimeout(resolve, 100))

      const pausedIndex = useSimulationStore.getState().currentMilestoneIndex

      // Index should not have changed after pause
      expect(pausedIndex).toBe(playingIndex)
    })
  })

  describe('Playback Speed', () => {
    it('should set playback speed to 0.5x', () => {
      useSimulationStore.getState().setPlaybackSpeed(0.5)
      expect(useSimulationStore.getState().playbackSpeed).toBe(0.5)
    })

    it('should set playback speed to 2x', () => {
      useSimulationStore.getState().setPlaybackSpeed(2)
      expect(useSimulationStore.getState().playbackSpeed).toBe(2)
    })

    it('should set playback speed to 5x', () => {
      useSimulationStore.getState().setPlaybackSpeed(5)
      expect(useSimulationStore.getState().playbackSpeed).toBe(5)
    })
  })

  describe('Milestone Navigation', () => {
    beforeEach(() => {
      useSimulationStore.getState().loadExecution(mockExecution)
    })

    it('should jump to specific milestone index', () => {
      useSimulationStore.getState().jumpToMilestone(2)
      expect(useSimulationStore.getState().currentMilestoneIndex).toBe(2)
    })

    it('should clamp index to milestones bounds', () => {
      useSimulationStore.getState().jumpToMilestone(10)
      expect(useSimulationStore.getState().currentMilestoneIndex).toBe(3) // Max index
    })

    it('should clamp negative index to 0', () => {
      useSimulationStore.getState().jumpToMilestone(-1)
      expect(useSimulationStore.getState().currentMilestoneIndex).toBe(0)
    })
  })

  describe('Error Summary', () => {
    beforeEach(() => {
      const store = useSimulationStore.getState()
      store.loadExecution(mockExecution)
    })

    it('should compute total errors', () => {
      const store = useSimulationStore.getState()

      const summary = store.getErrorSummary()
      expect(summary.totalErrors).toBe(1)
    })

    it('should compute slow nodes count', () => {
      const store = useSimulationStore.getState()

      const summary = store.getErrorSummary()
      expect(summary.slowNodes).toBe(2)
    })

    it('should return total execution time', () => {
      const store = useSimulationStore.getState()

      const summary = store.getErrorSummary()
      expect(summary.totalTime).toBe(5000)
    })
  })

  describe('Event Filtering', () => {
    beforeEach(() => {
      const store = useSimulationStore.getState()
      store.loadExecution(mockExecution)
    })

    it('should filter events up to current milestone timestamp', () => {
      const store = useSimulationStore.getState()

      store.jumpToMilestone(1) // timestamp: 2000
      const events = store.getFilteredEvents()

      // All events should have timestamp <= 2000
      events.forEach((event) => {
        expect(event.timestamp).toBeLessThanOrEqual(2000)
      })
    })

    it('should return all events when at last milestone', () => {
      const store = useSimulationStore.getState()

      store.jumpToMilestone(3) // Last milestone
      const events = store.getFilteredEvents()

      expect(events.length).toBeGreaterThan(0)
    })
  })

  describe('Graph Snapshot', () => {
    it('should return null when no execution loaded', () => {
      const store = useSimulationStore.getState()

      const graph = store.getCurrentGraphSnapshot()
      expect(graph).toBeNull()
    })

    it('should return current graph snapshot', () => {
      const store = useSimulationStore.getState()
      store.loadExecution(mockExecution)

      const graph = store.getCurrentGraphSnapshot()
      expect(graph).not.toBeNull()
      expect(graph?.nodes).toHaveLength(3)
      expect(graph?.edges).toHaveLength(2)
    })
  })

  describe('Selector Hooks', () => {
    beforeEach(() => {
      const store = useSimulationStore.getState()
      store.loadExecution(mockExecution)
    })

    it('useCurrentExecution should return current execution', () => {
      const execution = useSimulationStore.getState().currentExecution
      expect(execution).toEqual(mockExecution)
    })

    it('useIsPlaying should return playing state', () => {
      const store = useSimulationStore.getState()
      store.play()

      const isPlaying = useSimulationStore.getState().isPlaying
      expect(isPlaying).toBe(true)
    })

    it('useErrorSummary should return error summary', () => {
      const summary = useSimulationStore.getState().getErrorSummary()
      expect(summary).toHaveProperty('totalErrors')
      expect(summary).toHaveProperty('slowNodes')
      expect(summary).toHaveProperty('totalTime')
    })
  })
})
