/**
 * Flow Execution Adapter Tests
 *
 * Tests for mapping execution_history to FlowDefinition.
 * This adapter wires the Flow Designer to the Simulation engine.
 */

import { describe, it, expect } from 'vitest'
import { adaptExecutionToFlow, mapExecutionEventsToNodes } from '../flow-execution-adapter'
import type { FlowDefinition } from '@/components/flow-designer/types'
import type { Execution } from '@/stores/simulationStore'

describe('flow-execution-adapter', () => {
  describe('adaptExecutionToFlow', () => {
    it('should map execution graph_snapshot to FlowDefinition', () => {
      const execution: Execution = {
        id: 'exec-1',
        task_id: 'task-1',
        brief: 'Test execution',
        status: 'success',
        duration_ms: 5000,
        brain_count: 3,
        created_at: '2026-04-17T18:00:00Z',
        milestones: [
          { index: 0, timestamp: 1000, label: 'Start', brain_count: 0 },
          { index: 1, timestamp: 5000, label: 'Complete', brain_count: 3 },
        ],
        brain_outputs: {
          'brain-1': {
            brain_id: 'brain-1',
            status: 'complete',
            output: 'Output 1',
            duration_ms: 1000,
            timestamp: 1000,
          },
          'brain-2': {
            brain_id: 'brain-2',
            status: 'complete',
            output: 'Output 2',
            duration_ms: 1500,
            timestamp: 2000,
          },
        },
        graph_snapshot: {
          id: 'flow-1',
          name: 'Test Flow',
          nodes: [
            {
              id: 'node-1',
              type: 'brain',
              position: { x: 100, y: 100 },
              data: { label: 'Brain 1', brainId: 'brain-1' },
            },
            {
              id: 'node-2',
              type: 'brain',
              position: { x: 300, y: 100 },
              data: { label: 'Brain 2', brainId: 'brain-2' },
            },
          ],
          edges: [
            {
              id: 'edge-1',
              source: 'node-1',
              target: 'node-2',
            },
          ],
        },
      }

      const result = adaptExecutionToFlow(execution)

      expect(result).toBeDefined()
      expect(result.id).toBe('flow-1')
      expect(result.name).toBe('Test Flow')
      expect(result.nodes).toHaveLength(2)
      expect(result.edges).toHaveLength(1)
      expect(result.nodes[0].id).toBe('node-1')
      expect(result.nodes[0].data.brainId).toBe('brain-1')
    })

    it('should handle execution with null graph_snapshot gracefully', () => {
      const execution: Execution = {
        id: 'exec-2',
        task_id: 'task-2',
        brief: 'Test execution',
        status: 'error',
        duration_ms: 0,
        brain_count: 0,
        created_at: '2026-04-17T18:00:00Z',
        milestones: [],
        brain_outputs: {},
        graph_snapshot: null as any,
      }

      const result = adaptExecutionToFlow(execution)

      expect(result).toBeDefined()
      expect(result.nodes).toEqual([])
      expect(result.edges).toEqual([])
    })

    it('should preserve viewport and metadata from graph_snapshot', () => {
      const execution: Execution = {
        id: 'exec-3',
        task_id: 'task-3',
        brief: 'Test execution',
        status: 'success',
        duration_ms: 3000,
        brain_count: 1,
        created_at: '2026-04-17T18:00:00Z',
        milestones: [{ index: 0, timestamp: 1000, label: 'Start', brain_count: 0 }],
        brain_outputs: {},
        graph_snapshot: {
          id: 'flow-3',
          name: 'Test Flow with metadata',
          nodes: [],
          edges: [],
          viewport: { x: 100, y: 200, zoom: 1.5 },
          metadata: {
            createdAt: '2026-04-17T10:00:00Z',
            updatedAt: '2026-04-17T12:00:00Z',
            version: '1.0.0',
            tags: ['test', 'demo'],
          },
        },
      }

      const result = adaptExecutionToFlow(execution)

      expect(result.viewport).toEqual({ x: 100, y: 200, zoom: 1.5 })
      expect(result.metadata).toEqual({
        createdAt: '2026-04-17T10:00:00Z',
        updatedAt: '2026-04-17T12:00:00Z',
        version: '1.0.0',
        tags: ['test', 'demo'],
      })
    })
  })

  describe('mapExecutionEventsToNodes', () => {
    it('should map brain outputs to node status', () => {
      const execution: Execution = {
        id: 'exec-4',
        task_id: 'task-4',
        brief: 'Test execution',
        status: 'success',
        duration_ms: 5000,
        brain_count: 3,
        created_at: '2026-04-17T18:00:00Z',
        milestones: [],
        brain_outputs: {
          'brain-success': {
            brain_id: 'brain-success',
            status: 'complete',
            output: 'Success output',
            duration_ms: 500,
            timestamp: 1000,
          },
          'brain-error': {
            brain_id: 'brain-error',
            status: 'error',
            output: 'Error occurred',
            duration_ms: 200,
            timestamp: 2000,
          },
          'brain-running': {
            brain_id: 'brain-running',
            status: 'running',
            output: 'Still running',
            duration_ms: 0,
            timestamp: 3000,
          },
        },
        graph_snapshot: {
          id: 'flow-4',
          name: 'Test Flow',
          nodes: [
            {
              id: 'node-1',
              type: 'brain',
              position: { x: 100, y: 100 },
              data: { label: 'Success Node', brainId: 'brain-success' },
            },
            {
              id: 'node-2',
              type: 'brain',
              position: { x: 300, y: 100 },
              data: { label: 'Error Node', brainId: 'brain-error' },
            },
            {
              id: 'node-3',
              type: 'brain',
              position: { x: 500, y: 100 },
              data: { label: 'Running Node', brainId: 'brain-running' },
            },
            {
              id: 'node-unmapped',
              type: 'brain',
              position: { x: 700, y: 100 },
              data: { label: 'Unmapped Node', brainId: 'brain-unknown' },
            },
          ],
          edges: [],
        },
      }

      const flow = adaptExecutionToFlow(execution)
      const result = mapExecutionEventsToNodes(execution, flow.nodes)

      expect(result).toHaveLength(4)
      expect(result[0].data.status).toBe('success')
      expect(result[1].data.status).toBe('error')
      expect(result[2].data.status).toBe('running')
      expect(result[3].data.status).toBe('idle') // unmapped nodes default to idle
    })

    it('should handle empty nodes array', () => {
      const execution: Execution = {
        id: 'exec-5',
        task_id: 'task-5',
        brief: 'Test execution',
        status: 'success',
        duration_ms: 1000,
        brain_count: 0,
        created_at: '2026-04-17T18:00:00Z',
        milestones: [],
        brain_outputs: {},
        graph_snapshot: { id: 'flow-5', name: 'Test', nodes: [], edges: [] },
      }

      const flow = adaptExecutionToFlow(execution)
      const result = mapExecutionEventsToNodes(execution, flow.nodes)

      expect(result).toEqual([])
    })

    it('should handle nodes without brainId gracefully', () => {
      const execution: Execution = {
        id: 'exec-6',
        task_id: 'task-6',
        brief: 'Test execution',
        status: 'success',
        duration_ms: 1000,
        brain_count: 0,
        created_at: '2026-04-17T18:00:00Z',
        milestones: [],
        brain_outputs: {},
        graph_snapshot: {
          id: 'flow-6',
          name: 'Test',
          nodes: [
            {
              id: 'node-1',
              type: 'gateway',
              position: { x: 100, y: 100 },
              data: { label: 'Gateway' }, // no brainId
            },
          ],
          edges: [],
        },
      }

      const flow = adaptExecutionToFlow(execution)
      const result = mapExecutionEventsToNodes(execution, flow.nodes)

      expect(result).toHaveLength(1)
      expect(result[0].data.status).toBe('idle')
    })
  })
})
