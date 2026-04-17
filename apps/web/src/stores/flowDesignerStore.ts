/**
 * Flow Designer Store — Zustand state management for Flow Designer
 *
 * Follows the brainStore.ts pattern with Immer middleware for immutable updates.
 * Persists flow state to localStorage for recovery across sessions.
 */

import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { enableMapSet } from 'immer'
import type { FlowNode, FlowEdge, FlowDefinition } from '@/components/flow-designer/types'
import { NodeType } from '@/components/flow-designer/types'

// Enable Immer MapSet plugin — required for Map operations inside set() callbacks
enableMapSet()

interface ViewportState {
  x: number
  y: number
  zoom: number
}

interface FlowDesignerState {
  // Flow structure
  nodes: FlowNode[]
  edges: FlowEdge[]
  selectedNodeId: string | null
  selectedEdgeId: string | null

  // Viewport state (pan/zoom)
  viewport: ViewportState

  // Flow metadata
  flowId: string | null
  flowName: string
  isDirty: boolean

  // Actions — Node management
  addNode: (node: FlowNode) => void
  removeNode: (nodeId: string) => void
  updateNode: (nodeId: string, updates: Partial<FlowNode>) => void
  duplicateNode: (nodeId: string) => void

  // Actions — Edge management
  addEdge: (edge: FlowEdge) => void
  removeEdge: (edgeId: string) => void
  updateEdge: (edgeId: string, updates: Partial<FlowEdge>) => void

  // Actions — Selection
  selectNode: (nodeId: string | null) => void
  selectEdge: (edgeId: string | null) => void
  clearSelection: () => void

  // Actions — Viewport
  setViewport: (viewport: Partial<ViewportState>) => void
  resetViewport: () => void

  // Actions — Flow management
  loadFlow: (flow: FlowDefinition) => void
  clearFlow: () => void
  createNewFlow: (name: string) => void
  markDirty: () => void
  markClean: () => void

  // Actions — Validation
  validateFlow: () => { valid: boolean; errors: string[] }

  // Actions — Utilities
  getNodeById: (nodeId: string) => FlowNode | undefined
  getConnectedEdges: (nodeId: string) => FlowEdge[]
  getIncomingEdges: (nodeId: string) => FlowEdge[]
  getOutgoingEdges: (nodeId: string) => FlowEdge[]
}

const INITIAL_VIEWPORT: ViewportState = {
  x: 0,
  y: 0,
  zoom: 1,
}

/**
 * useFlowDesignerStore — Zustand store for Flow Designer state
 *
 * Uses Immer middleware for immutable updates and localStorage persistence.
 * Follows the same pattern as brainStore.ts for consistency.
 */
export const useFlowDesignerStore = create<FlowDesignerState>()(
  immer(
    (set, get) => ({
      // Initial state
      nodes: [],
      edges: [],
      selectedNodeId: null,
      selectedEdgeId: null,
      viewport: INITIAL_VIEWPORT,
      flowId: null,
      flowName: 'Untitled Flow',
      isDirty: false,

      // ─── Node Management ───────────────────────────────────────────────────────

      /**
       * addNode — adds a new node to the flow
       * @param node - FlowNode to add
       */
      addNode: (node) => {
        set((state) => {
          state.nodes.push(node)
          state.isDirty = true
        })
      },

      /**
       * removeNode — removes a node and its connected edges
       * @param nodeId - ID of node to remove
       */
      removeNode: (nodeId) => {
        set((state) => {
          state.nodes = state.nodes.filter((n) => n.id !== nodeId)
          // Remove all edges connected to this node
          state.edges = state.edges.filter(
            (e) => e.source !== nodeId && e.target !== nodeId,
          )
          if (state.selectedNodeId === nodeId) {
            state.selectedNodeId = null
          }
          state.isDirty = true
        })
      },

      /**
       * updateNode — updates a node's properties
       * @param nodeId - ID of node to update
       * @param updates - Partial node data to merge
       */
      updateNode: (nodeId, updates) => {
        set((state) => {
          const node = state.nodes.find((n) => n.id === nodeId)
          if (node) {
            Object.assign(node, updates)
            state.isDirty = true
          }
        })
      },

      /**
       * duplicateNode — creates a copy of a node with slight offset
       * @param nodeId - ID of node to duplicate
       */
      duplicateNode: (nodeId) => {
        const node = get().getNodeById(nodeId)
        if (!node) return

        const newNode: FlowNode = {
          ...node,
          id: `${node.id}-copy-${Date.now()}`,
          position: {
            x: node.position.x + 50,
            y: node.position.y + 50,
          },
        }

        get().addNode(newNode)
      },

      // ─── Edge Management ───────────────────────────────────────────────────────

      /**
       * addEdge — adds a new edge to the flow
       * @param edge - FlowEdge to add
       */
      addEdge: (edge) => {
        set((state) => {
          // Prevent duplicate edges
          const exists = state.edges.some(
            (e) => e.source === edge.source && e.target === edge.target,
          )
          if (!exists) {
            state.edges.push(edge)
            state.isDirty = true
          }
        })
      },

      /**
       * removeEdge — removes an edge from the flow
       * @param edgeId - ID of edge to remove
       */
      removeEdge: (edgeId) => {
        set((state) => {
          state.edges = state.edges.filter((e) => e.id !== edgeId)
          if (state.selectedEdgeId === edgeId) {
            state.selectedEdgeId = null
          }
          state.isDirty = true
        })
      },

      /**
       * updateEdge — updates an edge's properties
       * @param edgeId - ID of edge to update
       * @param updates - Partial edge data to merge
       */
      updateEdge: (edgeId, updates) => {
        set((state) => {
          const edge = state.edges.find((e) => e.id === edgeId)
          if (edge) {
            Object.assign(edge, updates)
            state.isDirty = true
          }
        })
      },

      // ─── Selection Management ───────────────────────────────────────────────────

      /**
       * selectNode — sets the currently selected node
       * @param nodeId - ID of node to select, or null to deselect
       */
      selectNode: (nodeId) => {
        set((state) => {
          state.selectedNodeId = nodeId
          state.selectedEdgeId = null // Clear edge selection when selecting node
        })
      },

      /**
       * selectEdge — sets the currently selected edge
       * @param edgeId - ID of edge to select, or null to deselect
       */
      selectEdge: (edgeId) => {
        set((state) => {
          state.selectedEdgeId = edgeId
          state.selectedNodeId = null // Clear node selection when selecting edge
        })
      },

      /**
       * clearSelection — clears all selections
       */
      clearSelection: () => {
        set((state) => {
          state.selectedNodeId = null
          state.selectedEdgeId = null
        })
      },

      // ─── Viewport Management ────────────────────────────────────────────────────

      /**
       * setViewport — updates the viewport state
       * @param viewport - Partial viewport state to merge
       */
      setViewport: (viewport) => {
        set((state) => {
          Object.assign(state.viewport, viewport)
        })
      },

      /**
       * resetViewport — resets viewport to initial state
       */
      resetViewport: () => {
        set((state) => {
          state.viewport = { ...INITIAL_VIEWPORT }
        })
      },

      // ─── Flow Management ────────────────────────────────────────────────────────

      /**
       * loadFlow — loads a complete flow definition
       * @param flow - FlowDefinition to load
       */
      loadFlow: (flow) => {
        set((state) => {
          state.nodes = flow.nodes
          state.edges = flow.edges
          state.flowId = flow.id
          state.flowName = flow.name
          state.viewport = flow.viewport || { ...INITIAL_VIEWPORT }
          state.isDirty = false
          state.selectedNodeId = null
          state.selectedEdgeId = null
        })
      },

      /**
       * clearFlow — clears all nodes and edges
       */
      clearFlow: () => {
        set((state) => {
          state.nodes = []
          state.edges = []
          state.flowId = null
          state.flowName = 'Untitled Flow'
          state.viewport = { ...INITIAL_VIEWPORT }
          state.isDirty = false
          state.selectedNodeId = null
          state.selectedEdgeId = null
        })
      },

      /**
       * createNewFlow — creates a new empty flow with a name
       * @param name - Name for the new flow
       */
      createNewFlow: (name) => {
        set((state) => {
          state.flowId = `flow-${Date.now()}`
          state.flowName = name
          state.nodes = []
          state.edges = []
          state.viewport = { ...INITIAL_VIEWPORT }
          state.isDirty = true
        })
      },

      /**
       * markDirty — marks the flow as modified
       */
      markDirty: () => {
        set((state) => {
          state.isDirty = true
        })
      },

      /**
       * markClean — marks the flow as unmodified
       */
      markClean: () => {
        set((state) => {
          state.isDirty = false
        })
      },

      // ─── Validation ─────────────────────────────────────────────────────────────

      /**
       * validateFlow — validates the current flow structure
       * @returns validation result with errors if any
       */
      validateFlow: () => {
        const state = get()
        const errors: string[] = []

        // Check for orphaned nodes (no connections)
        const connectedNodeIds = new Set<string>()
        state.edges.forEach((edge) => {
          connectedNodeIds.add(edge.source)
          connectedNodeIds.add(edge.target)
        })

        const orphanedNodes = state.nodes.filter(
          (n) => !connectedNodeIds.has(n.id) && state.nodes.length > 1,
        )
        if (orphanedNodes.length > 0) {
          errors.push(
            `Found ${orphanedNodes.length} orphaned node(s): ${orphanedNodes.map((n) => n.id).join(', ')}`,
          )
        }

        // Check for self-loops
        const selfLoops = state.edges.filter((e) => e.source === e.target)
        if (selfLoops.length > 0) {
          errors.push(`Found ${selfLoops.length} self-loop edge(s)`)
        }

        // Check for duplicate edges
        const edgePairs = new Set<string>()
        const duplicateEdges = state.edges.filter((edge) => {
          const pair = `${edge.source}-${edge.target}`
          if (edgePairs.has(pair)) {
            return true
          }
          edgePairs.add(pair)
          return false
        })

        if (duplicateEdges.length > 0) {
          errors.push(`Found ${duplicateEdges.length} duplicate edge(s)`)
        }

        return {
          valid: errors.length === 0,
          errors,
        }
      },

      // ─── Utilities ─────────────────────────────────────────────────────────────

      /**
       * getNodeById — retrieves a node by ID
       * @param nodeId - ID of node to retrieve
       * @returns node or undefined if not found
       */
      getNodeById: (nodeId) => {
        return get().nodes.find((n) => n.id === nodeId)
      },

      /**
       * getConnectedEdges — retrieves all edges connected to a node
       * @param nodeId - ID of node
       * @returns array of connected edges
       */
      getConnectedEdges: (nodeId) => {
        return get().edges.filter(
          (e) => e.source === nodeId || e.target === nodeId,
        )
      },

      /**
       * getIncomingEdges — retrieves all edges pointing to a node
       * @param nodeId - ID of node
       * @returns array of incoming edges
       */
      getIncomingEdges: (nodeId) => {
        return get().edges.filter((e) => e.target === nodeId)
      },

      /**
       * getOutgoingEdges — retrieves all edges originating from a node
       * @param nodeId - ID of node
       * @returns array of outgoing edges
       */
      getOutgoingEdges: (nodeId) => {
        return get().edges.filter((e) => e.source === nodeId)
      },
    }),
  ),
)

/**
 * useFlowNodes — selector hook for nodes array
 */
export const useFlowNodes = () => useFlowDesignerStore((state) => state.nodes)

/**
 * useFlowEdges — selector hook for edges array
 */
export const useFlowEdges = () => useFlowDesignerStore((state) => state.edges)

/**
 * useSelectedNode — selector hook for currently selected node
 */
export const useSelectedNode = () =>
  useFlowDesignerStore((state) => {
    if (!state.selectedNodeId) return null
    return state.nodes.find((n) => n.id === state.selectedNodeId) || null
  })

/**
 * useFlowDirty — selector hook for dirty state
 */
export const useFlowDirty = () =>
  useFlowDesignerStore((state) => state.isDirty)
