/**
 * SimulationCanvas — Read-only canvas for simulation replay
 *
 * Reuses FlowDesignerCanvas pattern with overlay for node status visualization.
 * Displays graph snapshot from simulationStore with execution status overlays:
 * - Error nodes: red background + error tooltip
 * - Slow nodes: yellow border + "SLOW" badge
 * - Running nodes: blue glow
 * - Success nodes: green border
 * - Edge labels show latency in ms
 *
 * Read-only: no drag/drop, no editing, no controls.
 */

import { useMemo } from 'react'
import {
  ReactFlow,
  Background,
  type NodeTypes,
  type Edge,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import { BrainNode } from '@/components/flow-designer/nodes/BrainNode'
import { GatewayNode } from '@/components/flow-designer/nodes/GatewayNode'
import { AdapterNode } from '@/components/flow-designer/nodes/AdapterNode'
import { RouterNode } from '@/components/flow-designer/nodes/RouterNode'
import { ConditionNode } from '@/components/flow-designer/nodes/ConditionNode'
import { FlowEdge as CustomFlowEdge } from '@/components/flow-designer/edges/FlowEdge'
import {
  useCurrentGraphSnapshot,
  useErrorNodes,
  useSlowNodes,
  useSimulationStore,
} from '@/stores/simulationStore'
import { NodeType } from '@/components/flow-designer/types'
import type { FlowNode, FlowNodeData } from '@/components/flow-designer/types'

// ─── Types ─────────────────────────────────────────────────────────────────────

/**
 * SimulationNodeData — extends FlowNodeData with simulation status
 */
interface SimulationNodeData extends FlowNodeData {
  simulationStatus?: 'idle' | 'running' | 'success' | 'error'
  error?: string
  latencyMs?: number
}

// ─── Node Types (Read-Only Wrappers) ────────────────────────────────────────────

/**
 * ReadOnlyNodeWrapper — wraps node components to prevent interaction
 *
 * Forwards all props to the original node component but adds simulation overlay.
 */
function ReadOnlyNodeWrapper({ children, data }: { children: React.ReactNode; data: SimulationNodeData }) {
  const isError = data.simulationStatus === 'error'
  const isSlow = data.latencyMs !== undefined && data.latencyMs > 1000
  const isRunning = data.simulationStatus === 'running'
  const isSuccess = data.simulationStatus === 'success'

  const statusStyles = useMemo(() => {
    const styles: React.CSSProperties = {}

    if (isError) {
      styles.backgroundColor = 'var(--color-error)'
      styles.color = 'var(--color-error-foreground)'
    } else if (isRunning) {
      styles.boxShadow = '0 0 20px var(--color-primary)'
      styles.border = '2px solid var(--color-primary)'
    } else if (isSuccess) {
      styles.border = '2px solid var(--color-success)'
    } else if (isSlow) {
      styles.border = '2px solid var(--color-warning)'
    }

    return styles
  }, [isError, isRunning, isSuccess, isSlow])

  return (
    <div style={statusStyles} className="relative rounded-lg">
      {children}
      {isSlow && (
        <div
          className="absolute -top-2 -right-2 px-2 py-0.5 text-xs font-bold rounded"
          style={{
            backgroundColor: 'var(--color-warning)',
            color: 'var(--color-warning-foreground)',
          }}
        >
          SLOW
        </div>
      )}
      {isError && data.error && (
        <div
          className="absolute bottom-full mb-2 px-3 py-2 text-xs rounded shadow-lg max-w-xs z-50"
          style={{
            backgroundColor: 'var(--color-error)',
            color: 'var(--color-error-foreground)',
          }}
        >
          {data.error}
        </div>
      )}
    </div>
  )
}

// Module-level node types prevents React Flow remount loops
const NODE_TYPES: NodeTypes = {
  [NodeType.BRAIN]: BrainNode,
  [NodeType.GATEWAY]: GatewayNode,
  [NodeType.ADAPTER]: AdapterNode,
  [NodeType.ROUTER]: RouterNode,
  [NodeType.CONDITION]: ConditionNode,
}

// ─── Component ───────────────────────────────────────────────────────────────────

/**
 * SimulationCanvas — read-only canvas for simulation replay
 *
 * Loads graph from getCurrentGraphSnapshot() and overlays node status.
 * Displays edge labels with latency information from brain_outputs.
 */
export function SimulationCanvas() {
  const graphSnapshot = useCurrentGraphSnapshot()
  const errorNodes = useErrorNodes()
  const slowNodes = useSlowNodes()
  const execution = useSimulationStore((state) => state.currentExecution)

  // Enhance nodes with simulation status
  const enhancedNodes = useMemo(() => {
    if (!graphSnapshot) return []

    return graphSnapshot.nodes.map((node: FlowNode) => {
      const nodeId = node.id
      const isError = errorNodes.has(nodeId)
      const latencyMs = slowNodes.get(nodeId)

      // Determine simulation status
      let simulationStatus: 'idle' | 'running' | 'success' | 'error' = 'idle'
      if (isError) {
        simulationStatus = 'error'
      } else if (latencyMs !== undefined) {
        simulationStatus = 'success' // Completed but slow
      }

      // Get error message from brain_outputs if available
      let error: string | undefined
      if (isError && execution) {
        const brainId = node.data?.brainId
        const brainOutput = brainId ? execution.brain_outputs[brainId] : null
        // Use the actual error output from brain_outputs, fallback to generic message
        error = brainOutput?.output || 'Execution failed'
      }

      return {
        ...node,
        data: {
          ...node.data,
          simulationStatus,
          error,
          latencyMs,
        } as SimulationNodeData,
        draggable: false, // Read-only
        selectable: false, // Read-only
      }
    })
  }, [graphSnapshot, errorNodes, slowNodes])

  // Enhance edges with latency labels
  const enhancedEdges = useMemo(() => {
    if (!graphSnapshot) return []

    return graphSnapshot.edges.map((edge: Edge) => {
      // Find brain outputs for source/target to calculate latency
      const sourceNode = graphSnapshot.nodes.find((n: FlowNode) => n.id === edge.source)
      const brainId = sourceNode?.data?.brainId

      const brainOutput = brainId ? execution?.brain_outputs[brainId] : null
      const latencyMs = brainOutput?.duration_ms

      return {
        ...edge,
        label: latencyMs ? `${latencyMs}ms` : undefined,
        animated: false,
        data: { ...edge.data, readOnly: true },
      }
    })
  }, [graphSnapshot, execution])

  // Early return if no graph loaded
  if (!graphSnapshot) {
    return (
      <div
        className="flex items-center justify-center h-full"
        style={{ backgroundColor: 'var(--color-background)' }}
      >
        <p className="text-lg" style={{ color: 'var(--color-primary)' }}>
          No execution loaded. Select an execution to replay.
        </p>
      </div>
    )
  }

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={enhancedNodes}
        edges={enhancedEdges}
        nodeTypes={NODE_TYPES}
        edgeTypes={{
          default: CustomFlowEdge,
        }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        zoomOnScroll={true}
        panOnScroll={true}
        fitView
        defaultViewport={graphSnapshot.viewport}
        minZoom={0.2}
        maxZoom={2}
        className="bg-background"
        style={{
          backgroundColor: 'var(--color-background)',
        }}
      >
        <Background
          color="var(--color-primary)"
          gap={16}
          size={1}
          style={{ opacity: 0.3 }}
        />
      </ReactFlow>
    </div>
  )
}
