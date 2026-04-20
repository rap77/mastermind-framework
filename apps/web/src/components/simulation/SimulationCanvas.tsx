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
import { Button } from '@/components/ui/button'
import { SLOW_NODE_THRESHOLD_MS } from '@/config/constants'

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
  const isSlow = data.latencyMs !== undefined && data.latencyMs > SLOW_NODE_THRESHOLD_MS
  const isRunning = data.simulationStatus === 'running'
  const isSuccess = data.simulationStatus === 'success'

  const statusStyles = useMemo(() => {
    const styles: React.CSSProperties = {}

    if (isError) {
      styles.backgroundColor = 'var(--color-error)'
      styles.color = 'var(--color-error-foreground)'
    } else if (isRunning) {
      styles.boxShadow = '0 0 20px var(--color-primary)'
      styles.borderWidth = '2px'
      styles.borderStyle = 'solid'
      styles.borderColor = 'var(--color-primary)'
    } else if (isSuccess) {
      styles.borderWidth = '2px'
      styles.borderStyle = 'solid'
      styles.borderColor = 'var(--color-success)'
    } else if (isSlow) {
      styles.borderWidth = '2px'
      styles.borderStyle = 'solid'
      styles.borderColor = 'var(--color-warning)'
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
  const isLoading = useSimulationStore((state) => state.isLoading)
  const loadError = useSimulationStore((state) => state.loadError)

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
      const targetNode = graphSnapshot.nodes.find((n: FlowNode) => n.id === edge.target)

      // Try source node's brainId first, fall back to target node's brainId
      // This handles gateway → brain edges where gateway has no brainId
      let brainId = sourceNode?.data?.brainId
      if (!brainId) {
        brainId = targetNode?.data?.brainId
      }

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
    if (isLoading) {
      return (
        <div
          className="flex flex-col items-center justify-center h-full gap-4"
          style={{ backgroundColor: 'var(--color-background)' }}
        >
          <div
            className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"
            style={{ borderColor: 'var(--color-primary)', borderTopColor: 'transparent' }}
            role="status"
            aria-label="Loading simulation"
          />
          <p className="text-lg" style={{ color: 'var(--color-text-secondary)' }}>
            Loading simulation...
          </p>
        </div>
      )
    }

    if (loadError) {
      return (
        <div
          className="flex flex-col items-center justify-center h-full gap-4 p-8"
          style={{ backgroundColor: 'var(--color-background)' }}
        >
          <div
            className="w-16 h-16 rounded-full flex items-center justify-center"
            style={{ backgroundColor: 'var(--color-error)', color: 'var(--color-error-foreground)' }}
            role="img"
            aria-label="Error icon"
          >
            <span className="text-3xl">⚠️</span>
          </div>
          <div className="text-center max-w-md">
            <h2 className="text-xl font-semibold mb-2" style={{ color: 'var(--color-error)' }}>
              Failed to Load Simulation
            </h2>
            <p className="text-sm mb-4" style={{ color: 'var(--color-text-secondary)' }}>
              {loadError.message || 'An unexpected error occurred while loading the simulation.'}
            </p>
            <div className="flex gap-3 justify-center">
              <Button
                onClick={() => window.location.reload()}
                variant="default"
                size="sm"
              >
                Try Again
              </Button>
              <Button
                onClick={() => (window.location.href = '/simulation')}
                variant="outline"
                size="sm"
              >
                Select Different Execution
              </Button>
            </div>
          </div>
        </div>
      )
    }

    return (
      <div
        className="flex flex-col items-center justify-center h-full gap-4"
        style={{ backgroundColor: 'var(--color-background)' }}
      >
        <div
          className="w-16 h-16 rounded-full flex items-center justify-center"
          style={{ backgroundColor: 'var(--color-muted)', color: 'var(--color-muted-foreground)' }}
          role="img"
          aria-label="No execution loaded"
        >
          <span className="text-3xl">📊</span>
        </div>
        <div className="text-center max-w-md">
          <h2 className="text-xl font-semibold mb-2" style={{ color: 'var(--color-text-primary)' }}>
            No Execution Loaded
          </h2>
          <p className="text-sm mb-4" style={{ color: 'var(--color-text-secondary)' }}>
            Select an execution from the list to replay the simulation.
          </p>
          <Button
            onClick={() => (window.location.href = '/simulation')}
            variant="outline"
            size="sm"
          >
            Browse Executions
          </Button>
        </div>
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
