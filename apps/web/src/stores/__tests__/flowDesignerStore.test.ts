/**
 * FlowDesignerStore Tests
 *
 * Tests for the Zustand store including edge management and duplicate prevention.
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useFlowDesignerStore } from '../flowDesignerStore'
import type { FlowEdge } from '@/components/flow-designer/types'

describe('FlowDesignerStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useFlowDesignerStore.getState().clearFlow()
  })

  describe('edge management', () => {
    it('should add an edge to the flow', () => {
      const addEdge = useFlowDesignerStore.getState().addEdge

      const edge: FlowEdge = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
      }

      addEdge(edge)

      const edges = useFlowDesignerStore.getState().edges
      expect(edges).toHaveLength(1)
      expect(edges[0]).toEqual(edge)
    })

    it('should prevent duplicate edges without labels', () => {
      const addEdge = useFlowDesignerStore.getState().addEdge

      const edge1: FlowEdge = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
      }

      const edge2: FlowEdge = {
        id: 'edge-2',
        source: 'node-1',
        target: 'node-2',
      }

      addEdge(edge1)
      addEdge(edge2)

      const edges = useFlowDesignerStore.getState().edges
      // Should only have one edge (second is duplicate)
      expect(edges).toHaveLength(1)
      expect(edges[0].id).toBe('edge-1')
    })

    it('should allow edges with different labels between same nodes', () => {
      const addEdge = useFlowDesignerStore.getState().addEdge

      const edge1: FlowEdge = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
        label: 'success',
      }

      const edge2: FlowEdge = {
        id: 'edge-2',
        source: 'node-1',
        target: 'node-2',
        label: 'error',
      }

      addEdge(edge1)
      addEdge(edge2)

      const edges = useFlowDesignerStore.getState().edges
      // Should have both edges (different labels)
      expect(edges).toHaveLength(2)
      expect(edges[0].label).toBe('success')
      expect(edges[1].label).toBe('error')
    })

    it('should prevent edges with same label between same nodes', () => {
      const addEdge = useFlowDesignerStore.getState().addEdge

      const edge1: FlowEdge = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
        label: 'success',
      }

      const edge2: FlowEdge = {
        id: 'edge-2',
        source: 'node-1',
        target: 'node-2',
        label: 'success',
      }

      addEdge(edge1)
      addEdge(edge2)

      const edges = useFlowDesignerStore.getState().edges
      // Should only have one edge (duplicate with same label)
      expect(edges).toHaveLength(1)
      expect(edges[0].label).toBe('success')
    })

    it('should allow unlabeled edge alongside labeled edges', () => {
      const addEdge = useFlowDesignerStore.getState().addEdge

      const edge1: FlowEdge = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
        label: 'success',
      }

      const edge2: FlowEdge = {
        id: 'edge-2',
        source: 'node-1',
        target: 'node-2',
        // No label
      }

      addEdge(edge1)
      addEdge(edge2)

      const edges = useFlowDesignerStore.getState().edges
      // Should have both edges (one labeled, one unlabeled)
      expect(edges).toHaveLength(2)
      expect(edges[0].label).toBe('success')
      expect(edges[1].label).toBeUndefined()
    })

    it('should remove an edge from the flow', () => {
      const { addEdge, removeEdge } = useFlowDesignerStore.getState()

      const edge: FlowEdge = {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
      }

      addEdge(edge)
      expect(useFlowDesignerStore.getState().edges).toHaveLength(1)

      removeEdge('edge-1')
      expect(useFlowDesignerStore.getState().edges).toHaveLength(0)
    })
  })
})
