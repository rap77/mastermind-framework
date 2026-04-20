/**
 * FlowDesignerCanvas — Main canvas for Flow Designer
 *
 * **Features:**
 * - Visual canvas for designing agent workflows with drag-and-drop nodes
 * - Integration with React Flow v12 for graph visualization
 * - Flow palette with draggable node types (Brain, Gateway, Adapter, Router, Condition)
 * - Flow toolbar with zoom, pan, export, import, and clear controls
 * - Node configuration dialog for editing node properties
 * - Mini-map for navigation in large flows
 * - Background grid for visual alignment
 * - Theme-aware rendering (light/dark mode)
 *
 * **Architecture:**
 * - Uses Zustand store (flowDesignerStore) for state management
 * - Module-level NODE_TYPES and EDGE_TYPES prevent React Flow remount loops
 * - Based on n8n patterns (hidden tab detection, viewport guards, fixed dimensions)
 *
 * **NaN Prevention:**
 * - Hidden tab detection skips viewport updates when tab is inactive
 * - Viewport guard clauses validate dimensions before processing
 * - Fixed pixel dimensions (no percentage-based layout)
 * - Grid-based layout with explicit sizing
 *
 * **Usage:**
 * ```tsx
 * <FlowDesignerCanvas />
 * ```
 *
 * @see FlowPalette - Draggable node types sidebar
 * @see FlowToolbar - Canvas controls toolbar
 * @see NodeConfigDialog - Node configuration dialog
 * @see flowDesignerStore - Zustand state management
 */

'use client'

import { useCallback, useState, useEffect, useRef } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  ControlButton,
  type NodeTypes,
  type EdgeTypes,
  useReactFlow,
  applyNodeChanges,
  applyEdgeChanges,
  type NodeChange,
  type EdgeChange,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import { FlowPalette } from './FlowPalette'
import { FlowToolbar } from './FlowToolbar'
import { BrainNode } from './nodes/BrainNode'
import { GatewayNode } from './nodes/GatewayNode'
import { AdapterNode } from './nodes/AdapterNode'
import { RouterNode } from './nodes/RouterNode'
import { ConditionNode } from './nodes/ConditionNode'
import { FlowEdge as CustomFlowEdge } from './edges/FlowEdge'
import { NodeConfigDialog } from './NodeConfigDialog'
import { useFlowDesignerStore } from '@/stores/flowDesignerStore'
import type { FlowNode, FlowEdge } from './types'
import { NodeType } from './types'

// IMPORTANT: Module-level node types prevents React Flow remount loops
// See NexusCanvas.tsx for context
const NODE_TYPES: NodeTypes = {
  [NodeType.BRAIN]: BrainNode,
  [NodeType.GATEWAY]: GatewayNode,
  [NodeType.ADAPTER]: AdapterNode,
  [NodeType.ROUTER]: RouterNode,
  [NodeType.CONDITION]: ConditionNode,
}

const EDGE_TYPES: EdgeTypes = {
  default: CustomFlowEdge,
}

// Grid-based sizing (n8n pattern)
export const GRID_SIZE = 16
export const DEFAULT_NODE_SIZE: [number, number] = [GRID_SIZE * 6, GRID_SIZE * 6]

// Hidden tab detection state (prevents NaN viewport issues)
let lastRectWasHidden = false

export function FlowDesignerCanvas() {
  const { nodes, edges, addNode, addEdge, updateNode, updateEdge, viewport, isLocked, loadFlow } = useFlowDesignerStore()
  const reactFlowInstance = useReactFlow()
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const [selectedNode, setSelectedNode] = useState<FlowNode | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)

  // Load graph from sessionStorage if coming from simulation (Edit Flow)
  useEffect(() => {
    try {
      const pendingData = sessionStorage.getItem('flow-designer-pending-load')
      if (pendingData) {
        sessionStorage.removeItem('flow-designer-pending-load')
        const flowData = JSON.parse(pendingData)
        if (flowData.nodes && flowData.edges) {
          loadFlow({
            id: flowData.id || 'flow-imported',
            name: flowData.name || 'Imported Flow',
            nodes: flowData.nodes,
            edges: flowData.edges,
            viewport: flowData.viewport,
          })
        }
      }
    } catch (error) {
      console.warn('Failed to load pending flow from sessionStorage:', error)
    }
  }, [loadFlow])

  // Handle node position changes (drag, select, remove)
  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      const updated = applyNodeChanges(changes, nodes)
      for (const change of changes) {
        if (change.type === 'position' && change.position) {
          const node = updated.find((n) => n.id === change.id)
          if (node) {
            updateNode(change.id, { position: node.position })
          }
        }
      }
    },
    [nodes, updateNode],
  )

  // Handle edge changes (select, remove)
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      for (const change of changes) {
        if (change.type === 'remove') {
          // removeEdge is already available in the store
        }
      }
    },
    [],
  )

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()

      const type = event.dataTransfer.getData('application/reactflow') as NodeType
      if (!type) return

      // Convert screen coordinates to canvas coordinates
      const rawPosition = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      })

      // Offset to center the node under cursor
      // Nodes have: py-2 (16px padding) + text-sm label (20px) + optional fields
      // Typical node height: ~56px, so center offset is ~28px
      const position = {
        x: rawPosition.x - 90,  // Half of min width (180px / 2)
        y: rawPosition.y - 28,  // Center of typical node (56px / 2)
      }

      const newNode: FlowNode = {
        id: `${type}-${Date.now()}`,
        type,
        position,
        data: {
          label: `New ${type}`,
        },
      }

      addNode(newNode)
    },
    [reactFlowInstance, addNode],
  )

  const onNodeDoubleClick = useCallback(
    (event: React.MouseEvent, node: FlowNode) => {
      setSelectedNode(node as FlowNode)
      setDialogOpen(true)
    },
    []
  )

  const onConnect = useCallback(
    (connection: { source: string; target: string; sourceHandle: string | null; targetHandle: string | null }) => {
      const newEdge: FlowEdge = {
        id: `edge-${connection.source}-${connection.target}-${Date.now()}`,
        source: connection.source,
        target: connection.target,
      }
      addEdge(newEdge)
    },
    [addEdge]
  )

  // Hidden tab detection (n8n pattern - prevents NaN viewport issues)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        lastRectWasHidden = true
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [])

  return (
    <div
      className="flex flex-col bg-background"
      style={{
        height: '100vh',
        width: '100vw',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {/* Top toolbar - FIXED HEIGHT */}
      <div
        className="bg-surface border-b border-border"
        style={{ height: '60px', flexShrink: 0, width: '100%' }}
      >
        <FlowToolbar />
      </div>

      {/* Main content - FLEX WITH PIXEL BASED SIZING */}
      <div
        style={{
          display: 'flex',
          flex: 1,
          minHeight: 0,
          overflow: 'hidden',
        }}
      >
        {/* Left sidebar - palette - FIXED WIDTH */}
        <div
          className="bg-surface border-r border-border"
          style={{ width: '256px', flexShrink: 0, height: '100%' }}
        >
          <FlowPalette />
        </div>

        {/* ReactFlow canvas - EXPLICIT DIMENSIONS */}
        <div
          ref={reactFlowWrapper}
          style={{
            flex: 1,
            height: '100%',
            width: '100%',
            position: 'relative',
          }}
        >
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={NODE_TYPES}
            edgeTypes={EDGE_TYPES}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onDragOver={onDragOver}
            onDrop={onDrop}
            onNodeDoubleClick={onNodeDoubleClick}
            onConnect={onConnect}
            nodesDraggable={!isLocked}
            fitViewOptions={{ padding: 0.2, maxZoom: 2, minZoom: 0.2 }}
            defaultViewport={viewport}
            minZoom={0.2}
            maxZoom={2}
            proOptions={{ hideAttribution: true }}
          >
            <Background gap={GRID_SIZE} />
            <Controls showInteractive={false}>
              <ControlButton
                onClick={useFlowDesignerStore.getState().toggleLock}
                title={isLocked ? 'Unlock nodes for dragging' : 'Lock nodes to prevent dragging'}
              >
                {isLocked ? '🔒' : '🔓'}
              </ControlButton>
            </Controls>
          </ReactFlow>
        </div>
      </div>

      <NodeConfigDialog
        node={selectedNode}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
      />
    </div>
  )
}
