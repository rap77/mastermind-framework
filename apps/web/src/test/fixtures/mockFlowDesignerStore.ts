/**
 * Mock Flow Designer Store Fixture
 *
 * Provides a complete mock Zustand store for Flow Designer testing.
 * Use this to avoid duplicating mock store setup across test files.
 *
 * @example
 * import { createMockFlowDesignerStore } from '@/test/fixtures/mockFlowDesignerStore'
 * const { useFlowDesignerStore } = createMockFlowDesignerStore({
 *   nodes: [{ id: '1', type: NodeType.BRAIN, data: { label: 'Test' } }],
 * })
 */

import { vi } from 'vitest'
import type { FlowDesignerState } from '@/stores/flowDesignerStore'
import type { FlowNode, FlowEdge } from '@/components/flow-designer/types'
import { NodeType } from '@/components/flow-designer/types'

/**
 * Default mock state matching FlowDesignerStore interface
 */
export const mockFlowDesignerStoreState: Partial<FlowDesignerState> = {
  // Flow structure
  nodes: [],
  edges: [],
  selectedNodeId: null,
  selectedEdgeId: null,

  // Viewport state (pan/zoom)
  viewport: { x: 0, y: 0, zoom: 1 },

  // Flow metadata
  flowId: null,
  flowName: 'Untitled Flow',
  isDirty: false,

  // Validation state
  orphanedNodeCount: 0,

  // Canvas lock state
  isLocked: false,

  // Actions — Node management
  addNode: vi.fn(),
  removeNode: vi.fn(),
  updateNode: vi.fn(),
  duplicateNode: vi.fn(),

  // Actions — Edge management
  addEdge: vi.fn(),
  removeEdge: vi.fn(),
  updateEdge: vi.fn(),

  // Actions — Selection
  selectNode: vi.fn(),
  selectEdge: vi.fn(),
  clearSelection: vi.fn(),

  // Actions — Viewport
  setViewport: vi.fn(),
  resetViewport: vi.fn(),

  // Actions — Flow management
  loadFlow: vi.fn(),
  clearFlow: vi.fn(),
  createNewFlow: vi.fn(),
  markDirty: vi.fn(),
  markClean: vi.fn(),

  // Actions — Validation
  validateFlow: vi.fn(() => ({ valid: true, errors: [] })),

  // Actions — Canvas lock
  toggleLock: vi.fn(),

  // Actions — Utilities
  getNodeById: vi.fn(),
  getConnectedEdges: vi.fn(() => []),
  getIncomingEdges: vi.fn(() => []),
  getOutgoingEdges: vi.fn(() => []),
}

/**
 * Creates a mock Flow Designer store with optional custom state
 *
 * @param customState - Partial state to override defaults
 * @returns Mock store object with useFlowDesignerStore hook
 *
 * @example
 * // Basic usage
 * const { useFlowDesignerStore } = createMockFlowDesignerStore()
 *
 * // With custom state
 * const { useFlowDesignerStore } = createMockFlowDesignerStore({
 *   nodes: [{ id: 'node-1', type: NodeType.BRAIN, data: { label: 'Test Brain' } }],
 *   isDirty: true,
 * })
 *
 * // In tests
 * vi.mocked(useFlowDesignerStore).mockReturnValue({ nodes: mockNodes })
 */
export function createMockFlowDesignerStore(
  customState: Partial<FlowDesignerState> = {}
) {
  const state = {
    ...mockFlowDesignerStoreState,
    ...customState,
  }

  const useFlowDesignerStore = vi.fn((selector) => {
    if (selector) return selector(state as FlowDesignerState)
    return state
  })

  // Add getState method for advanced use cases
  ;(useFlowDesignerStore as any).getState = () => state

  return {
    useFlowDesignerStore,
    getState: () => state,
  }
}
