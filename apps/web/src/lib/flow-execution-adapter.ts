/**
 * Flow Execution Adapter
 *
 * Maps execution_history to FlowDefinition for wiring Flow Designer to Simulation.
 *
 * This adapter enables the "design → simulate → debug" loop by:
 * 1. Converting Execution.graph_snapshot → FlowDefinition (for Flow Designer)
 * 2. Mapping Execution.brain_outputs → node statuses (for Simulation)
 * 3. Handling unmapped nodes gracefully (grayed out in Simulation)
 *
 * @see apps/web/src/components/flow-designer/types.ts - FlowDefinition types
 * @see apps/web/src/stores/simulationStore.ts - Execution types
 */

import type { FlowDefinition, FlowNode } from '@/components/flow-designer/types'
import type { Execution } from '@/stores/simulationStore'
import { logger } from '@/lib/logger'

// ─── Type Guards ────────────────────────────────────────────────────────────────

/**
 * isValidBrainOutput — runtime type guard for BrainOutput
 *
 * Validates that an unknown value is a valid BrainOutput.
 * Used to catch API response errors early with better error messages.
 *
 * @param output - unknown value to validate
 * @returns true if output is a valid BrainOutput
 *
 * @example
 * ```ts
 * if (!isValidBrainOutput(data)) {
 *   throw new Error('Invalid brain output from API')
 * }
 * ```
 */
function isValidBrainOutput(output: unknown): output is {
  brain_id: string
  status: 'idle' | 'running' | 'complete' | 'error'
  output?: string
  duration_ms?: number
  timestamp?: number
} {
  return (
    typeof output === 'object' &&
    output !== null &&
    'brain_id' in output &&
    'status' in output &&
    typeof output.brain_id === 'string' &&
    ['idle', 'running', 'complete', 'error'].includes(output.status as string)
  )
}

// ─── Public API ─────────────────────────────────────────────────────────────

/**
 * adaptExecutionToFlow — converts Execution.graph_snapshot to FlowDefinition
 *
 * Extracts the flow structure from an execution's graph_snapshot.
 * Returns a valid FlowDefinition even if graph_snapshot is null/undefined.
 *
 * @param execution - Execution record from API
 * @returns FlowDefinition compatible with Flow Designer
 *
 * @example
 * ```ts
 * const execution = await api.getExecution('exec-123')
 * const flow = adaptExecutionToFlow(execution)
 * // flow can be loaded into FlowDesignerCanvas
 * ```
 */
export function adaptExecutionToFlow(execution: Execution): FlowDefinition {
  const snapshot = execution.graph_snapshot

  // Handle null/undefined graph_snapshot gracefully
  if (!snapshot || typeof snapshot !== 'object') {
    return {
      id: execution.id,
      name: execution.brief || `Execution ${execution.id}`,
      nodes: [],
      edges: [],
      metadata: {
        createdAt: execution.created_at,
        updatedAt: execution.created_at,
        version: '1.0.0',
      },
    }
  }

  // Extract nodes from snapshot (default to empty array)
  const nodes = Array.isArray(snapshot.nodes) ? snapshot.nodes : []

  // Extract edges from snapshot (default to empty array)
  const edges = Array.isArray(snapshot.edges) ? snapshot.edges : []

  // Extract snapshot properties with proper type guards
  const snapshotId = typeof snapshot.id === 'string' ? snapshot.id : execution.id
  const snapshotName = typeof snapshot.name === 'string' ? snapshot.name : execution.brief

  // Build FlowDefinition
  return {
    id: snapshotId,
    name: snapshotName || `Execution ${execution.id}`,
    description: snapshot.description,
    nodes,
    edges,
    viewport: snapshot.viewport,
    metadata: snapshot.metadata || {
      createdAt: execution.created_at,
      updatedAt: execution.created_at,
      version: '1.0.0',
    },
  }
}

/**
 * mapExecutionEventsToNodes — maps brain outputs to node statuses
 *
 * Enriches flow nodes with execution status from brain_outputs.
 * Nodes without matching brain_id default to 'idle' status.
 *
 * @param execution - Execution record with brain_outputs
 * @param nodes - Flow nodes from FlowDefinition
 * @returns Flow nodes with updated status field
 *
 * @example
 * ```ts
 * const flow = adaptExecutionToFlow(execution)
 * const nodesWithStatus = mapExecutionEventsToNodes(execution, flow.nodes)
 * // nodesWithStatus can be rendered in SimulationCanvas with status indicators
 * ```
 */
export function mapExecutionEventsToNodes(
  execution: Execution,
  nodes: FlowNode[],
): FlowNode[] {
  // Create a map of brain_id → status for quick lookup
  const brainStatusMap = new Map<string, 'idle' | 'running' | 'success' | 'error'>()

  Object.entries(execution.brain_outputs || {}).forEach(([brainId, output]) => {
    // Validate brain output structure
    if (!isValidBrainOutput(output)) {
      logger.warn(
        `[flow-execution-adapter:brain_output_validation] Invalid brain output for brain_id: ${brainId}`,
        { brainId, output }
      )
      return
    }

    // Map API status to node status
    // API: 'idle' | 'running' | 'complete' | 'error'
    // Node: 'idle' | 'running' | 'success' | 'error'
    const nodeStatus =
      output.status === 'complete' ? 'success' : (output.status as any)
    brainStatusMap.set(brainId, nodeStatus)
  })

  // Map each node to its status based on brainId
  return nodes.map((node) => {
    const brainId = node.data?.brainId

    // If node has a brainId and we have status for it, update the status
    if (brainId && brainStatusMap.has(brainId)) {
      const status = brainStatusMap.get(brainId)!
      return {
        ...node,
        data: {
          ...node.data,
          status,
        },
      }
    }

    // Unmapped nodes default to 'idle' (grayed out in Simulation)
    return {
      ...node,
      data: {
        ...node.data,
        status: 'idle',
      },
    }
  })
}
