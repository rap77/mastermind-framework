'use client'

import { useState } from 'react'
import { ReactFlow, Background, Controls } from '@xyflow/react'
import type { Node, Edge } from '@xyflow/react'
import dagre from '@dagrejs/dagre'
import { BrainNode } from './BrainNode'
import { NodeDetailPanel } from './NodeDetailPanel'
import type { Brain } from '@/lib/api'

// ─── CRITICAL: NODE_TYPES at MODULE LEVEL — NEVER inline in JSX ───────────────
// Inline definition causes React Flow to remount the canvas on every render.
// This is an invariant from BRAIN-FEED.md: always module-level constant.
// Exported as NODE_TYPES_EXPORT for test verification of reference stability.
// ──────────────────────────────────────────────────────────────────────────────
const NODE_TYPES = {
  brainNode: BrainNode,
} as const

// Export for test isolation — verifies module-level stability without rendering
export const NODE_TYPES_EXPORT = NODE_TYPES

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
    rankdir: 'TB',
    nodesep: 60,
    ranksep: 100,
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
 * buildBlueprintNodes — converts API brains into React Flow nodes (Ghost Architecture)
 *
 * Status data is NOT stored in node.data — it comes from brainStore via useBrainState(id).
 * This keeps the nodes array as layout-only (never mutated by WS events).
 */
function buildBlueprintNodes(
  blueprintBrains: Brain[],
  onSelect: (id: string) => void
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
 * buildBlueprintEdges — star topology: coordinator → all other brains
 */
function buildBlueprintEdges(blueprintBrains: Brain[]): Edge[] {
  const coordinator = blueprintBrains.find(b => b.niche === 'coordinator') ?? blueprintBrains.find(b => b.id === 'brain-08')
  if (!coordinator) return []

  return blueprintBrains
    .filter(b => b.id !== coordinator.id)
    .map(b => ({
      id: `edge-${coordinator.id}-${b.id}`,
      source: coordinator.id,
      target: b.id,
    }))
}

interface NexusCanvasProps {
  blueprintBrains: Brain[]
}

/**
 * NexusCanvas — The Nexus screen's React Flow canvas
 *
 * Architecture:
 * - NODE_TYPES at module level (CRITICAL)
 * - dagre layout runs ONCE via useState initializer (never recalculated)
 * - nodes array is layout-only — brain status read from brainStore in BrainNode
 * - NodeDetailPanel (Sheet) opens on brain node click
 */
export function NexusCanvas({ blueprintBrains }: NexusCanvasProps) {
  const [selectedBrainId, setSelectedBrainId] = useState<string | null>(null)

  // CRITICAL: Layout runs once at mount — positions are latched
  // The initializer function form (setState(() => ...)) runs ONLY once
  const [nodes] = useState<Node[]>(() => {
    const rawNodes = buildBlueprintNodes(blueprintBrains, setSelectedBrainId)
    const edges = buildBlueprintEdges(blueprintBrains)
    return getLayoutedNodes(rawNodes, edges)
  })

  const [edges] = useState<Edge[]>(() =>
    buildBlueprintEdges(blueprintBrains)
  )

  const handleClosePanel = () => setSelectedBrainId(null)

  return (
    <div className="relative h-full w-full">
      {/* Canvas shrinks 30% when panel opens */}
      <div
        className={
          selectedBrainId
            ? 'h-full transition-all duration-300 w-[70%]'
            : 'h-full transition-all duration-300 w-full'
        }
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={NODE_TYPES}
          fitView
          panOnScroll
          zoomOnScroll
          nodesDraggable={false}
          style={{ background: '#0B0C10' }}
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
    </div>
  )
}
