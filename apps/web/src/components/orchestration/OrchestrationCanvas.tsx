'use client'

/**
 * OrchestrationCanvas — Middle column of the Orchestration Canvas.
 *
 * Extends the NexusCanvas patterns (module-level NODE_TYPES, dagre layout once,
 * status from brainStore) without rewriting NexusCanvas itself.
 *
 * Key differences from NexusCanvas:
 * - Accepts `selectedBrainId` + `onSelect` props for cross-panel selection sync
 * - Uses OrchestrationBrainNode which adds a "selected" visual ring
 * - No CooldownFAB, no NodeDetailPanel (OutputPanel replaces detail panel)
 * - No Cooldown Mode — pure read/select path
 *
 * CRITICAL: NODE_TYPES + EDGE_TYPES at module level — never inline in JSX.
 * (Same invariant as NexusCanvas — prevents React Flow remount on render.)
 */

import { useState } from 'react'
import { ReactFlow, Background, Controls } from '@xyflow/react'
import type { Node, Edge } from '@xyflow/react'
import dagre from '@dagrejs/dagre'
import type { Brain } from '@/lib/api'
import { HybridFlowEdge } from '@/components/nexus/HybridFlowEdge'
import { OrchestrationBrainNode } from './OrchestrationBrainNode'

// ─── CRITICAL: NODE_TYPES + EDGE_TYPES at MODULE LEVEL ────────────────────────
// See NexusCanvas.tsx for the invariant explanation.
const NODE_TYPES = {
  orchestrationBrainNode: OrchestrationBrainNode,
} as const

const EDGE_TYPES = {
  hybridFlow: HybridFlowEdge,
} as const

// Node dimensions — match NexusCanvas constants
const BRAIN_NODE_W = 220
const BRAIN_NODE_H = 70
const COORDINATOR_W = 120
const COORDINATOR_H = 120

// Dagre graph singleton — reused between layout calls
const dagreGraph = new dagre.graphlib.Graph()
dagreGraph.setDefaultEdgeLabel(() => ({}))

// ─── Layout helpers (mirrors NexusCanvas pattern) ─────────────────────────────

function getLayoutedNodes(nodes: Node[], edges: Edge[]): Node[] {
  dagreGraph.setGraph({ rankdir: 'LR', nodesep: 80, ranksep: 240 })

  for (const nodeId of dagreGraph.nodes()) dagreGraph.removeNode(nodeId)
  for (const edgeId of dagreGraph.edges()) dagreGraph.removeEdge(edgeId.v, edgeId.w)

  for (const node of nodes) {
    const isCoordinator =
      node.id === 'brain-08' ||
      (node.data as { niche?: string }).niche === 'universal'
    const w = isCoordinator ? COORDINATOR_W : BRAIN_NODE_W
    const h = isCoordinator ? COORDINATOR_H : BRAIN_NODE_H
    dagreGraph.setNode(node.id, { width: w, height: h })
  }

  for (const edge of edges) {
    dagreGraph.setEdge(edge.source, edge.target)
  }

  dagre.layout(dagreGraph)

  return nodes.map((node) => {
    const { x, y, width, height } = dagreGraph.node(node.id)
    return {
      ...node,
      position: { x: x - width / 2, y: y - height / 2 },
      draggable: false,
    }
  })
}

function buildNodes(
  brains: Brain[],
  onSelect: (id: string) => void,
): Node[] {
  return brains.map((brain) => ({
    id: brain.id,
    type: 'orchestrationBrainNode',
    data: {
      label: brain.name,
      niche: brain.niche,
      onSelect,
    },
    position: { x: 0, y: 0 },
    width: brain.niche === 'universal' ? COORDINATOR_W : BRAIN_NODE_W,
    height: brain.niche === 'universal' ? COORDINATOR_H : BRAIN_NODE_H,
  }))
}

function buildEdges(brains: Brain[]): Edge[] {
  const coordinator =
    brains.find((b) => b.niche === 'universal') ??
    brains.find((b) => b.id === 'brain-08')
  if (!coordinator) return []

  return brains
    .filter((b) => b.id !== coordinator.id)
    .map((b) => ({
      id: `oc-edge-${coordinator.id}-${b.id}`,
      source: coordinator.id,
      target: b.id,
      type: 'hybridFlow',
    }))
}

// ─── Component ─────────────────────────────────────────────────────────────────

interface OrchestrationCanvasProps {
  blueprintBrains: Brain[]
  selectedBrainId: string | null
  onSelect: (brainId: string) => void
}

export function OrchestrationCanvas({
  blueprintBrains,
  selectedBrainId,
  onSelect,
}: OrchestrationCanvasProps) {
  // Layout runs once at mount — same as NexusCanvas
  const [nodes] = useState<Node[]>(() => {
    const rawNodes = buildNodes(blueprintBrains, onSelect)
    const edges = buildEdges(blueprintBrains)
    return getLayoutedNodes(rawNodes, edges)
  })

  const [edges] = useState<Edge[]>(() => buildEdges(blueprintBrains))

  // Inject selectedBrainId into nodes so OrchestrationBrainNode can highlight
  const nodesWithSelection = nodes.map((node) => ({
    ...node,
    data: {
      ...(node.data as object),
      isSelected: node.id === selectedBrainId,
    },
  }))

  return (
    <div className="h-full w-full" data-testid="orchestration-canvas">
      <ReactFlow
        nodes={nodesWithSelection}
        edges={edges}
        nodeTypes={NODE_TYPES}
        edgeTypes={EDGE_TYPES}
        fitView
        panOnScroll
        zoomOnScroll
        nodesDraggable={false}
        nodesFocusable
        edgesFocusable
        className="nexus-canvas-bg"
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  )
}
