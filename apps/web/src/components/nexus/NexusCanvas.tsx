'use client'

import { useState, useEffect } from 'react'
import { useBrainStore } from '@/stores/brainStore'
import { ReactFlow, Background, Controls } from '@xyflow/react'
import type { Node, Edge } from '@xyflow/react'
import dagre from '@dagrejs/dagre'
import { BrainNode } from './BrainNode'
import { HybridFlowEdge } from './HybridFlowEdge'
import { NodeDetailPanel } from './NodeDetailPanel'
import { CooldownFAB } from './CooldownFAB'
import { useWSStore } from '@/stores/wsStore'
import type { Brain } from '@/lib/api'

// ─── CRITICAL: NODE_TYPES at MODULE LEVEL — NEVER inline in JSX ───────────────
// Inline definition causes React Flow to remount the canvas on every render.
// This is an invariant from BRAIN-FEED.md: always module-level constant.
// Exported as NODE_TYPES_EXPORT for test verification of reference stability.
// ──────────────────────────────────────────────────────────────────────────────
const NODE_TYPES = {
  brainNode: BrainNode,
} as const

// ─── CRITICAL: EDGE_TYPES at MODULE LEVEL — same rule as NODE_TYPES ───────────
// Inline edgeTypes in JSX causes React Flow infinite re-render loop.
// ──────────────────────────────────────────────────────────────────────────────
const EDGE_TYPES = {
  hybridFlow: HybridFlowEdge,
} as const

// Export for test isolation — verifies module-level stability without rendering
export const NODE_TYPES_EXPORT = NODE_TYPES
export const EDGE_TYPES_EXPORT = EDGE_TYPES

// Node dimensions — fixed constants, never use node.measured (Pitfall 2 from research)
const BRAIN_NODE_W = 160
const BRAIN_NODE_H = 60
const COORDINATOR_W = 100
const COORDINATOR_H = 100

// Module-level dagre graph singleton — reused between calls for stability
const dagreGraph = new dagre.graphlib.Graph()
dagreGraph.setDefaultEdgeLabel(() => ({}))

/**
 * getLayoutedNodes — dagre TB layout for the Ghost Architecture
 *
 * CRITICAL: Uses fixed constants for node dimensions (not node.measured).
 * Positions are latched in useState — only runs once at mount.
 *
 * @param nodes - React Flow nodes with id and type
 * @param edges - React Flow edges with source/target
 * @returns nodes with position set by dagre (centered via x - w/2, y - h/2)
 */
export function getLayoutedNodes(nodes: Node[], edges: Edge[]): Node[] {
  dagreGraph.setGraph({
    rankdir: 'LR',
    nodesep: 40,
    ranksep: 80,
  })

  // Clear previous graph state to ensure stability across multiple calls
  for (const nodeId of dagreGraph.nodes()) {
    dagreGraph.removeNode(nodeId)
  }

  for (const edgeId of dagreGraph.edges()) {
    dagreGraph.removeEdge(edgeId.v, edgeId.w)
  }

  // Register nodes with their fixed dimensions
  for (const node of nodes) {
    const isCoordinator = node.id === 'brain-08' || (node.data as { niche?: string }).niche === 'coordinator'
    const w = isCoordinator ? COORDINATOR_W : BRAIN_NODE_W
    const h = isCoordinator ? COORDINATOR_H : BRAIN_NODE_H
    dagreGraph.setNode(node.id, { width: w, height: h })
  }

  // Register edges
  for (const edge of edges) {
    dagreGraph.setEdge(edge.source, edge.target)
  }

  dagre.layout(dagreGraph)

  return nodes.map(node => {
    const { x, y, width, height } = dagreGraph.node(node.id)
    return {
      ...node,
      position: {
        x: x - width / 2,
        y: y - height / 2,
      },
      draggable: false,
    }
  })
}

/**
 * buildBlueprintNodes — converts API brains into React Flow nodes
 *
 * Shows ALL brains. Status visibility handled by BrainNode:
 * - Ghost nodes (blueprint) render dim/dashed
 * - Active nodes render with color ring
 *
 * Status data comes from brainStore via useBrainState(id) in BrainNode.
 * This keeps the nodes array as layout-only (never mutated by WS events).
 */
function buildBlueprintNodes(
  blueprintBrains: Brain[],
  onSelect: (id: string) => void,
  _activeBrainIds: Set<string>
): Node[] {
  return blueprintBrains.map(brain => ({
    id: brain.id,
    type: 'brainNode',
    data: {
      label: brain.name,
      niche: brain.niche,
      onSelect,
    },
    position: { x: 0, y: 0 },
    width: brain.niche === 'coordinator' ? COORDINATOR_W : BRAIN_NODE_W,
    height: brain.niche === 'coordinator' ? COORDINATOR_H : BRAIN_NODE_H,
  }))
}

/**
 * buildBlueprintEdges — star topology: coordinator → all brains
 *
 * Uses 'hybridFlow' edge type for the HybridFlowEdge neon glow state machine.
 * EDGE_TYPES must be at module level (not inline) for React Flow stability.
 */
function buildBlueprintEdges(blueprintBrains: Brain[], visibleNodes: Node[]): Edge[] {
  const coordinator = blueprintBrains.find(b => b.niche === 'coordinator') ?? blueprintBrains.find(b => b.id === 'brain-08')
  if (!coordinator) return []

  return blueprintBrains
    .filter(b => b.id !== coordinator.id)
    .map(b => ({
      id: `edge-${coordinator.id}-${b.id}`,
      source: coordinator.id,
      target: b.id,
      type: 'hybridFlow',
    }))
}

interface NexusCanvasProps {
  blueprintBrains: Brain[]
}

/**
 * NexusCanvas — The Nexus screen's React Flow canvas
 *
 * Architecture:
 * - NODE_TYPES + EDGE_TYPES at module level (CRITICAL — prevents remount)
 * - dagre layout runs ONCE via useState initializer (never recalculated)
 * - nodes array is layout-only — brain status read from brainStore in BrainNode
 * - HybridFlowEdge reads source brain status for neon glow state machine
 * - NodeDetailPanel (Sheet) opens on brain node click
 * - Cooldown Mode activates on task_completed WS event (CooldownFAB visible, bg shifts)
 */
export function NexusCanvas({ blueprintBrains }: NexusCanvasProps) {
  const [selectedBrainId, setSelectedBrainId] = useState<string | null>(null)
  // Cooldown Mode: active after task_completed WS event
  const [cooldownMode, setCooldownMode] = useState(false)
  const subscribe = useWSStore(state => state.subscribe)

  // Get active brain IDs from brainStore
  const brainStates = useBrainStore(state => state.brains)
  const activeBrainIds = new Set(
    Array.from(brainStates.values())
      .filter(brain => brain.status !== 'blueprint')
      .map(brain => brain.id)
  )

  // Build nodes/edges once at mount with active brains
  const [nodes] = useState<Node[]>(() => {
    const rawNodes = buildBlueprintNodes(blueprintBrains, setSelectedBrainId, activeBrainIds)
    const edges = buildBlueprintEdges(blueprintBrains, rawNodes)
    return getLayoutedNodes(rawNodes, edges)
  })

  const [edges] = useState<Edge[]>(() => {
    const rawNodes = buildBlueprintNodes(blueprintBrains, setSelectedBrainId, activeBrainIds)
    return buildBlueprintEdges(blueprintBrains, rawNodes)
  })

  // Subscribe to task_completed to enter Cooldown Mode
  useEffect(() => {
    const unsubscribe = subscribe('task_completed', () => {
      setCooldownMode(true)
    })
    return unsubscribe
  }, [subscribe])

  const handleClosePanel = () => setSelectedBrainId(null)
  const handleCooldownEscape = () => setCooldownMode(false)

  // Background shifts to near-black in Cooldown Mode
  const canvasBackground = cooldownMode ? '#111113' : '#0B0C10'

  return (
    <div className="relative h-full w-full">
      {/* Canvas shrinks when panel opens (stays 85% width, panel 15%) */}
      <div
        className={
          selectedBrainId
            ? 'h-full transition-all duration-300 w-[85%]'
            : 'h-full transition-all duration-300 w-full'
        }
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={NODE_TYPES}
          edgeTypes={EDGE_TYPES}
          fitView
          panOnScroll
          zoomOnScroll
          nodesDraggable={false}
          // Canvas is read-only in Cooldown Mode
          nodesFocusable={!cooldownMode}
          edgesFocusable={!cooldownMode}
          style={{ background: canvasBackground, transition: 'background 0.3s ease' }}
        >
          <Background />
          <Controls />
        </ReactFlow>
      </div>

      <NodeDetailPanel
        brainId={selectedBrainId}
        blueprintBrains={blueprintBrains}
        onClose={handleClosePanel}
      />

      {/* CooldownFAB: appears on task_completed, Esc resets to Ghost Architecture */}
      <CooldownFAB
        visible={cooldownMode}
        taskId={null}
        onEscape={handleCooldownEscape}
      />
    </div>
  )
}
