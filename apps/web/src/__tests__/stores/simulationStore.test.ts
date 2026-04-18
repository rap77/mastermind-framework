/**
 * Tests for simulationStore.ts — Slow threshold configuration
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useSimulationStore } from '@/stores/simulationStore'
import type { Execution } from '@/stores/simulationStore'

// Mock execution data
const mockExecution: Execution = {
  id: 'test-exec-1',
  task_id: 'task-1',
  brief: 'Test execution',
  status: 'success',
  duration_ms: 5000,
  brain_count: 2,
  created_at: '2026-04-17T00:00:00Z',
  milestones: [
    { index: 0, timestamp: 0, label: 'Start', brain_count: 0 },
    { index: 1, timestamp: 5000, label: 'End', brain_count: 2 },
  ],
  brain_outputs: {
    'brain-1': {
      brain_id: 'brain-1',
      status: 'complete',
      output: 'Output 1',
      duration_ms: 500, // Fast
      timestamp: 0,
    },
    'brain-2': {
      brain_id: 'brain-2',
      status: 'complete',
      output: 'Output 2',
      duration_ms: 1500, // Slow (default threshold 1000ms)
      timestamp: 1000,
    },
  },
  graph_snapshot: {
    nodes: [
      { id: 'node-1', data: { brainId: 'brain-1' } },
      { id: 'node-2', data: { brainId: 'brain-2' } },
    ],
    edges: [],
  },
}

describe('SimulationStore - Slow Threshold Configuration', () => {
  beforeEach(() => {
    // Reset store state before each test
    useSimulationStore.getState().reset()
  })

  describe('Default Slow Threshold', () => {
    it('should have default slow threshold of 1000ms', () => {
      const state = useSimulationStore.getState()
      expect(state.slowThreshold).toBe(1000)
    })

    it('should detect slow nodes using default threshold (1000ms)', () => {
      const store = useSimulationStore.getState()
      store.loadExecution(mockExecution)

      const state = useSimulationStore.getState()
      // brain-2 has duration 1500ms, which is > 1000ms (default threshold)
      expect(state.slowNodes.size).toBe(1)
      expect(state.slowNodes.has('node-2')).toBe(true)
    })
  })

  describe('Custom Slow Threshold', () => {
    it('should allow setting custom slow threshold', () => {
      const store = useSimulationStore.getState()

      // Set custom threshold
      store.setSlowThreshold(2000)

      const state = useSimulationStore.getState()
      expect(state.slowThreshold).toBe(2000)
    })

    it('should re-detect slow nodes after changing threshold', () => {
      const store = useSimulationStore.getState()

      // Load with default threshold (1000ms)
      store.loadExecution(mockExecution)
      expect(useSimulationStore.getState().slowNodes.size).toBe(1) // node-2 is slow

      // Increase threshold to 2000ms
      store.setSlowThreshold(2000)

      // Now brain-2 (1500ms) should NOT be slow
      expect(useSimulationStore.getState().slowNodes.size).toBe(0)
    })

    it('should detect more slow nodes when decreasing threshold', () => {
      const store = useSimulationStore.getState()

      // Load with default threshold (1000ms)
      store.loadExecution(mockExecution)
      expect(useSimulationStore.getState().slowNodes.size).toBe(1) // node-2 is slow

      // Decrease threshold to 200ms
      store.setSlowThreshold(200)

      // Now both nodes should be slow
      const state = useSimulationStore.getState()
      expect(state.slowNodes.size).toBe(2)
      expect(state.slowNodes.has('node-1')).toBe(true)
      expect(state.slowNodes.has('node-2')).toBe(true)
    })
  })

  describe('Threshold Validation', () => {
    it('should not allow negative threshold', () => {
      const store = useSimulationStore.getState()
      store.setSlowThreshold(-100)

      // Should stay at previous value (default 1000ms)
      expect(useSimulationStore.getState().slowThreshold).toBe(1000)
    })

    it('should not allow zero threshold', () => {
      const store = useSimulationStore.getState()
      store.setSlowThreshold(0)

      // Should stay at previous value
      expect(useSimulationStore.getState().slowThreshold).toBe(1000)
    })

    it('should allow very large threshold values', () => {
      const store = useSimulationStore.getState()
      store.setSlowThreshold(100000) // 100 seconds

      expect(useSimulationStore.getState().slowThreshold).toBe(100000)
    })
  })
})
