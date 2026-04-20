/**
 * Flow Serializer Tests
 *
 * Tests for exportFlow, importFlow, and validateFlow functions.
 */

import { describe, it, expect } from 'vitest'
import {
  exportFlow,
  importFlow,
  validateFlow,
  createEmptyFlow,
  cloneFlow,
} from '../flow-serializer'
import type { FlowDefinition } from '@/components/flow-designer/types'
import { NodeType } from '@/components/flow-designer/types'

describe('flow-serializer', () => {
  describe('exportFlow', () => {
    it('should export a valid flow to JSON', () => {
      const flow: FlowDefinition = {
        id: 'test-flow-1',
        name: 'Test Flow',
        nodes: [
          {
            id: 'node-1',
            type: NodeType.BRAIN,
            position: { x: 100, y: 100 },
            data: { label: 'Test Node' },
          },
        ],
        edges: [],
        metadata: {
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z',
          version: '1.0.0',
        },
      }

      const json = exportFlow(flow)

      expect(json).toBeDefined()
      expect(typeof json).toBe('string')

      const parsed = JSON.parse(json)
      expect(parsed.id).toBe('test-flow-1')
      expect(parsed.name).toBe('Test Flow')
      expect(parsed.metadata.exportedAt).toBeDefined()
    })

    it('should throw error for invalid flow', () => {
      const invalidFlow = {
        id: 'invalid',
        name: '', // Empty name should fail validation
        nodes: [],
        edges: [],
      } as FlowDefinition

      expect(() => exportFlow(invalidFlow)).toThrow()
    })
  })

  describe('importFlow', () => {
    it('should import valid JSON to FlowDefinition', () => {
      const json = JSON.stringify({
        id: 'test-flow-2',
        name: 'Import Test',
        nodes: [
          {
            id: 'node-2',
            type: NodeType.GATEWAY,
            position: { x: 200, y: 200 },
            data: { label: 'Gateway' },
          },
        ],
        edges: [],
        metadata: {
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z',
          version: '1.0.0',
        },
      })

      const flow = importFlow(json)

      expect(flow.id).toBe('test-flow-2')
      expect(flow.name).toBe('Import Test')
      expect(flow.nodes).toHaveLength(1)
      expect(flow.nodes[0].type).toBe(NodeType.GATEWAY)
    })

    it('should throw error for invalid JSON', () => {
      const invalidJson = '{ invalid json }'

      expect(() => importFlow(invalidJson)).toThrow('Invalid JSON')
    })

    it('should set default name for missing name field', () => {
      const incompleteJson = JSON.stringify({
        id: 'test',
        // Missing 'name' field
        nodes: [],
        edges: [],
      })

      const flow = importFlow(incompleteJson)
      expect(flow.name).toBe('Imported Flow') // Default name
    })

    it('should throw error for invalid edge references', () => {
      const json = JSON.stringify({
        id: 'test-flow',
        name: 'Test',
        nodes: [
          {
            id: 'node-1',
            type: NodeType.BRAIN,
            position: { x: 0, y: 0 },
            data: { label: 'Node 1' },
          },
        ],
        edges: [
          {
            id: 'edge-1',
            source: 'node-1',
            target: 'non-existent-node',
          },
        ],
      })

      expect(() => importFlow(json)).toThrow('non-existent')
    })
  })

  describe('validateFlow', () => {
    it('should validate a correct flow structure', () => {
      const flow: FlowDefinition = {
        id: 'valid-flow',
        name: 'Valid Flow',
        nodes: [
          {
            id: 'node-1',
            type: NodeType.BRAIN,
            position: { x: 0, y: 0 },
            data: { label: 'Node 1' },
          },
          {
            id: 'node-2',
            type: NodeType.ADAPTER,
            position: { x: 100, y: 100 },
            data: { label: 'Node 2' },
          },
        ],
        edges: [
          {
            id: 'edge-1',
            source: 'node-1',
            target: 'node-2',
          },
        ],
        metadata: {
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z',
          version: '1.0.0',
        },
      }

      const result = validateFlow(flow)

      expect(result.valid).toBe(true)
      expect(result.errors).toBeUndefined()
    })

    it('should detect missing flow id', () => {
      const flow = {
        name: 'Test',
        nodes: [],
        edges: [],
      } as FlowDefinition

      const result = validateFlow(flow)

      expect(result.valid).toBe(false)
      expect(result.errors).toBeDefined()
      expect(result.errors?.some((e) => e.path === 'id')).toBe(true)
    })

    it('should detect missing flow name', () => {
      const flow = {
        id: 'test',
        nodes: [],
        edges: [],
      } as FlowDefinition

      const result = validateFlow(flow)

      expect(result.valid).toBe(false)
      expect(result.errors?.some((e) => e.path === 'name')).toBe(true)
    })

    it('should detect invalid node position', () => {
      const flow: FlowDefinition = {
        id: 'test',
        name: 'Test',
        nodes: [
          {
            id: 'node-1',
            type: NodeType.BRAIN,
            position: { x: 'invalid' as unknown as number, y: 0 },
            data: { label: 'Node' },
          },
        ],
        edges: [],
      }

      const result = validateFlow(flow)

      expect(result.valid).toBe(false)
      expect(result.errors?.some((e) => e.path.includes('position'))).toBe(true)
    })

    it('should detect invalid edge source reference', () => {
      const flow: FlowDefinition = {
        id: 'test',
        name: 'Test',
        nodes: [
          {
            id: 'node-1',
            type: NodeType.BRAIN,
            position: { x: 0, y: 0 },
            data: { label: 'Node' },
          },
        ],
        edges: [
          {
            id: 'edge-1',
            source: 'non-existent',
            target: 'node-1',
          },
        ],
      }

      const result = validateFlow(flow)

      expect(result.valid).toBe(false)
      expect(result.errors?.some((e) => e.code === 'INVALID_EDGE_SOURCE')).toBe(true)
    })
  })

  describe('createEmptyFlow', () => {
    it('should create a new empty flow', () => {
      const flow = createEmptyFlow('My Flow')

      expect(flow.id).toBeDefined()
      expect(flow.name).toBe('My Flow')
      expect(flow.nodes).toEqual([])
      expect(flow.edges).toEqual([])
      expect(flow.viewport).toEqual({ x: 0, y: 0, zoom: 1 })
      expect(flow.metadata).toBeDefined()
    })

    it('should generate unique IDs for each flow', async () => {
      const flow1 = createEmptyFlow('Flow 1')
      // Add small delay to ensure different timestamps
      await new Promise(resolve => setTimeout(resolve, 10))
      const flow2 = createEmptyFlow('Flow 2')

      expect(flow1.id).not.toBe(flow2.id)
    })
  })

  describe('cloneFlow', () => {
    it('should create a deep copy of a flow', () => {
      const original: FlowDefinition = {
        id: 'original',
        name: 'Original Flow',
        nodes: [
          {
            id: 'node-1',
            type: NodeType.BRAIN,
            position: { x: 10, y: 20 },
            data: { label: 'Node 1' },
          },
        ],
        edges: [
          {
            id: 'edge-1',
            source: 'node-1',
            target: 'node-1',
          },
        ],
        metadata: {
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z',
          version: '1.0.0',
        },
      }

      const cloned = cloneFlow(original)

      expect(cloned.id).not.toBe(original.id)
      expect(cloned.name).toBe('Original Flow (Copy)')
      expect(cloned.nodes).toHaveLength(1)
      expect(cloned.nodes[0].id).not.toBe(original.nodes[0].id)
      expect(cloned.edges).toHaveLength(1)
      expect(cloned.edges[0].id).not.toBe(original.edges[0].id)
    })

    it('should preserve viewport settings', () => {
      const original: FlowDefinition = {
        id: 'test',
        name: 'Test',
        nodes: [],
        edges: [],
        viewport: { x: 100, y: 200, zoom: 1.5 },
      }

      const cloned = cloneFlow(original)

      expect(cloned.viewport).toEqual({ x: 100, y: 200, zoom: 1.5 })
    })
  })

  describe('round-trip export/import', () => {
    it('should preserve data integrity', () => {
      const original: FlowDefinition = {
        id: 'test-flow',
        name: 'Round Trip Test',
        description: 'Testing export/import cycle',
        nodes: [
          {
            id: 'node-1',
            type: NodeType.BRAIN,
            position: { x: 50, y: 75 },
            data: {
              label: 'Brain Node',
              description: 'Test brain',
              icon: '🧠',
              status: 'idle',
              brainId: 'brain-1',
              niche: 'software-development',
            },
          },
          {
            id: 'node-2',
            type: NodeType.CONDITION,
            position: { x: 200, y: 150 },
            data: {
              label: 'Condition',
              expression: 'x > 10',
            },
          },
        ],
        edges: [
          {
            id: 'edge-1',
            source: 'node-1',
            target: 'node-2',
            label: 'trigger',
          },
        ],
        viewport: { x: 10, y: 20, zoom: 1.2 },
        metadata: {
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-02T00:00:00Z',
          version: '1.0.0',
          tags: ['test', 'example'],
        },
      }

      const exported = exportFlow(original)
      const imported = importFlow(exported)

      expect(imported.id).toBe(original.id)
      expect(imported.name).toBe(original.name)
      expect(imported.description).toBe(original.description)
      expect(imported.nodes).toHaveLength(2)
      expect(imported.nodes[0].data.label).toBe('Brain Node')
      expect(imported.nodes[1].data.expression).toBe('x > 10')
      expect(imported.edges).toHaveLength(1)
      expect(imported.edges[0].label).toBe('trigger')
      expect(imported.viewport?.zoom).toBe(1.2)
      expect(imported.metadata?.tags).toEqual(['test', 'example'])
    })
  })

  describe('edge cases', () => {
    it('should handle large flows', () => {
      const nodes = Array.from({ length: 100 }, (_, i) => ({
        id: `node-${i}`,
        type: NodeType.BRAIN,
        position: { x: i * 50, y: i * 30 },
        data: { label: `Node ${i}` },
      }))

      const edges = Array.from({ length: 99 }, (_, i) => ({
        id: `edge-${i}`,
        source: `node-${i}`,
        target: `node-${i + 1}`,
      }))

      const flow: FlowDefinition = {
        id: 'large-flow',
        name: 'Large Flow',
        nodes,
        edges,
        metadata: {
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z',
          version: '1.0.0',
        },
      }

      const json = exportFlow(flow)
      const imported = importFlow(json)

      expect(imported.nodes).toHaveLength(100)
      expect(imported.edges).toHaveLength(99)
    })

    it('should handle special characters in data', () => {
      const flow: FlowDefinition = {
        id: 'test-special',
        name: 'Test with "quotes" and \'apostrophes\'',
        nodes: [
          {
            id: 'node-1',
            type: NodeType.BRAIN,
            position: { x: 0, y: 0 },
            data: {
              label: 'Node with émojis 🎉 and spëcial çhars',
              description: 'Line 1\nLine 2\tTabbed',
            },
          },
        ],
        edges: [],
        metadata: {
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z',
          version: '1.0.0',
        },
      }

      const json = exportFlow(flow)
      const imported = importFlow(json)

      expect(imported.name).toContain('quotes')
      expect(imported.nodes[0].data.label).toContain('émojis')
      expect(imported.nodes[0].data.description).toContain('\n')
    })

    it('should handle circular references gracefully', () => {
      const flow: FlowDefinition = {
        id: 'circular',
        name: 'Circular Flow',
        nodes: [
          {
            id: 'node-1',
            type: NodeType.ROUTER,
            position: { x: 0, y: 0 },
            data: { label: 'Router' },
          },
          {
            id: 'node-2',
            type: NodeType.CONDITION,
            position: { x: 100, y: 0 },
            data: { label: 'Condition' },
          },
        ],
        edges: [
          {
            id: 'edge-1',
            source: 'node-1',
            target: 'node-2',
          },
          {
            id: 'edge-2',
            source: 'node-2',
            target: 'node-1', // Circular reference
          },
        ],
        metadata: {
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z',
          version: '1.0.0',
        },
      }

      const result = validateFlow(flow)

      // Circular references are valid in flows (e.g., loops)
      expect(result.valid).toBe(true)
    })
  })
})
