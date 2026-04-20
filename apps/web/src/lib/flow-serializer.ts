/**
 * Flow Serializer — Import/export for Flow Designer
 *
 * Handles serialization and deserialization of FlowDefinition objects to/from JSON.
 * Includes validation and error handling for safe data interchange.
 */

import type {
  FlowDefinition,
  FlowNode,
  FlowEdge,
  ValidationResult,
  FlowValidationError,
} from '@/components/flow-designer/types'

/**
 * SerializerError — thrown when serialization/deserialization fails
 */
export class SerializerError extends Error {
  constructor(message: string, public readonly code: string) {
    super(message)
    this.name = 'SerializerError'
  }
}

/**
 * exportFlow — serializes a FlowDefinition to JSON string
 *
 * @param flow - FlowDefinition to serialize
 * @returns JSON string representation
 * @throws SerializerError if serialization fails
 */
export function exportFlow(flow: FlowDefinition): string {
  try {
    // Validate before export
    const validation = validateFlow(flow)
    if (!validation.valid) {
      throw new SerializerError(
        `Cannot export invalid flow: ${validation.errors?.map((e) => e.message).join(', ')}`,
        'INVALID_FLOW',
      )
    }

    // Add export metadata
    const exportData = {
      ...flow,
      metadata: {
        ...flow.metadata,
        exportedAt: new Date().toISOString(),
        version: flow.metadata?.version || '1.0.0',
      },
    }

    return JSON.stringify(exportData, null, 2)
  } catch (error) {
    if (error instanceof SerializerError) {
      throw error
    }
    throw new SerializerError(
      `Failed to serialize flow: ${error instanceof Error ? error.message : 'Unknown error'}`,
      'SERIALIZATION_FAILED',
    )
  }
}

/**
 * importFlow — deserializes a JSON string to FlowDefinition
 *
 * @param json - JSON string to deserialize
 * @returns FlowDefinition object
 * @throws SerializerError if deserialization fails
 */
export function importFlow(json: string): FlowDefinition {
  try {
    const data = JSON.parse(json)

    // Validate basic structure
    if (!data || typeof data !== 'object') {
      throw new SerializerError(
        'Invalid JSON: root must be an object',
        'INVALID_JSON',
      )
    }

    // Validate required fields
    if (!data.id || typeof data.id !== 'string') {
      throw new SerializerError('Flow must have an id field', 'MISSING_ID')
    }

    if (!data.name || typeof data.name !== 'string') {
      data.name = 'Imported Flow'
    }

    if (!Array.isArray(data.nodes)) {
      throw new SerializerError(
        'Flow must have a nodes array',
        'MISSING_NODES',
      )
    }

    if (!Array.isArray(data.edges)) {
      throw new SerializerError(
        'Flow must have an edges array',
        'MISSING_EDGES',
      )
    }

    // Validate nodes structure
    for (const node of data.nodes) {
      if (!node.id || typeof node.id !== 'string') {
        throw new SerializerError(
          `Node missing id at index ${data.nodes.indexOf(node)}`,
          'INVALID_NODE',
        )
      }
      if (!node.type || typeof node.type !== 'string') {
        throw new SerializerError(
          `Node ${node.id} missing type field`,
          'INVALID_NODE',
        )
      }
      if (!node.position || typeof node.position !== 'object') {
        throw new SerializerError(
          `Node ${node.id} missing position`,
          'INVALID_NODE',
        )
      }
      if (typeof node.position.x !== 'number' || typeof node.position.y !== 'number') {
        throw new SerializerError(
          `Node ${node.id} has invalid position`,
          'INVALID_NODE',
        )
      }
    }

    // Validate edges structure
    for (const edge of data.edges) {
      if (!edge.id || typeof edge.id !== 'string') {
        throw new SerializerError(
          `Edge missing id at index ${data.edges.indexOf(edge)}`,
          'INVALID_EDGE',
        )
      }
      if (!edge.source || typeof edge.source !== 'string') {
        throw new SerializerError(
          `Edge ${edge.id} missing source`,
          'INVALID_EDGE',
        )
      }
      if (!edge.target || typeof edge.target !== 'string') {
        throw new SerializerError(
          `Edge ${edge.id} missing target`,
          'INVALID_EDGE',
        )
      }
    }

    // Validate edge references
    const nodeIds = new Set(data.nodes.map((n) => n.id))
    for (const edge of data.edges) {
      if (!nodeIds.has(edge.source)) {
        throw new SerializerError(
          `Edge ${edge.id} references non-existent source node: ${edge.source}`,
          'INVALID_EDGE_REFERENCE',
        )
      }
      if (!nodeIds.has(edge.target)) {
        throw new SerializerError(
          `Edge ${edge.id} references non-existent target node: ${edge.target}`,
          'INVALID_EDGE_REFERENCE',
        )
      }
    }

    // Ensure metadata exists
    if (!data.metadata) {
      data.metadata = {
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        version: '1.0.0',
      }
    }

    return data as FlowDefinition
  } catch (error) {
    if (error instanceof SerializerError) {
      throw error
    }
    if (error instanceof SyntaxError) {
      throw new SerializerError(
        `Invalid JSON syntax: ${error.message}`,
        'INVALID_JSON',
      )
    }
    throw new SerializerError(
      `Failed to deserialize flow: ${error instanceof Error ? error.message : 'Unknown error'}`,
      'DESERIALIZATION_FAILED',
    )
  }
}

/**
 * validateFlow — validates a FlowDefinition structure
 *
 * @param flow - FlowDefinition to validate
 * @returns ValidationResult with valid flag and optional errors
 */
export function validateFlow(flow: FlowDefinition): ValidationResult {
  const errors: FlowValidationError[] = []

  // Validate required top-level fields
  if (!flow.id || typeof flow.id !== 'string') {
    errors.push({
      path: 'id',
      message: 'Flow must have an id field',
      code: 'MISSING_ID',
    })
  }

  if (!flow.name || typeof flow.name !== 'string') {
    errors.push({
      path: 'name',
      message: 'Flow must have a name field',
      code: 'MISSING_NAME',
    })
  }

  if (!Array.isArray(flow.nodes)) {
    errors.push({
      path: 'nodes',
      message: 'Flow must have a nodes array',
      code: 'INVALID_NODES',
    })
  }

  if (!Array.isArray(flow.edges)) {
    errors.push({
      path: 'edges',
      message: 'Flow must have an edges array',
      code: 'INVALID_EDGES',
    })
  }

  // Validate nodes
  if (Array.isArray(flow.nodes)) {
    flow.nodes.forEach((node, index) => {
      if (!node.id) {
        errors.push({
          path: `nodes[${index}].id`,
          message: 'Node must have an id',
          code: 'MISSING_NODE_ID',
        })
      }
      if (!node.type) {
        errors.push({
          path: `nodes[${index}].type`,
          message: 'Node must have a type',
          code: 'MISSING_NODE_TYPE',
        })
      }
      if (!node.position) {
        errors.push({
          path: `nodes[${index}].position`,
          message: 'Node must have a position',
          code: 'MISSING_NODE_POSITION',
        })
      } else {
        if (typeof node.position.x !== 'number') {
          errors.push({
            path: `nodes[${index}].position.x`,
            message: 'Position x must be a number',
            code: 'INVALID_POSITION',
          })
        }
        if (typeof node.position.y !== 'number') {
          errors.push({
            path: `nodes[${index}].position.y`,
            message: 'Position y must be a number',
            code: 'INVALID_POSITION',
          })
        }
      }
    })
  }

  // Validate edges
  if (Array.isArray(flow.edges)) {
    const nodeIds = new Set(flow.nodes?.map((n) => n.id) || [])

    flow.edges.forEach((edge, index) => {
      if (!edge.id) {
        errors.push({
          path: `edges[${index}].id`,
          message: 'Edge must have an id',
          code: 'MISSING_EDGE_ID',
        })
      }
      if (!edge.source) {
        errors.push({
          path: `edges[${index}].source`,
          message: 'Edge must have a source',
          code: 'MISSING_EDGE_SOURCE',
        })
      } else if (nodeIds.size > 0 && !nodeIds.has(edge.source)) {
        errors.push({
          path: `edges[${index}].source`,
          message: `Edge references non-existent source node: ${edge.source}`,
          code: 'INVALID_EDGE_SOURCE',
        })
      }
      if (!edge.target) {
        errors.push({
          path: `edges[${index}].target`,
          message: 'Edge must have a target',
          code: 'MISSING_EDGE_TARGET',
        })
      } else if (nodeIds.size > 0 && !nodeIds.has(edge.target)) {
        errors.push({
          path: `edges[${index}].target`,
          message: `Edge references non-existent target node: ${edge.target}`,
          code: 'INVALID_EDGE_TARGET',
        })
      }
    })
  }

  // Validate metadata
  if (flow.metadata) {
    if (flow.metadata.createdAt && typeof flow.metadata.createdAt !== 'string') {
      errors.push({
        path: 'metadata.createdAt',
        message: 'createdAt must be a string',
        code: 'INVALID_METADATA',
      })
    }
    if (flow.metadata.updatedAt && typeof flow.metadata.updatedAt !== 'string') {
      errors.push({
        path: 'metadata.updatedAt',
        message: 'updatedAt must be a string',
        code: 'INVALID_METADATA',
      })
    }
  }

  return {
    valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined,
  }
}

/**
 * exportFlowToFile — triggers a browser download of the flow JSON
 *
 * @param flow - FlowDefinition to export
 * @param filename - Optional filename (defaults to flow name)
 */
export function exportFlowToFile(
  flow: FlowDefinition,
  filename?: string,
): void {
  try {
    const json = exportFlow(flow)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.href = url
    link.download = filename || `${flow.name.replace(/\s+/g, '-')}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    URL.revokeObjectURL(url)
  } catch (error) {
    throw new SerializerError(
      `Failed to export flow to file: ${error instanceof Error ? error.message : 'Unknown error'}`,
      'FILE_EXPORT_FAILED',
    )
  }
}

/**
 * createEmptyFlow — creates a new empty FlowDefinition
 *
 * @param name - Name for the new flow
 * @returns new FlowDefinition with empty nodes/edges
 */
export function createEmptyFlow(name: string): FlowDefinition {
  return {
    id: `flow-${Date.now()}`,
    name,
    nodes: [],
    edges: [],
    viewport: {
      x: 0,
      y: 0,
      zoom: 1,
    },
    metadata: {
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      version: '1.0.0',
    },
  }
}

/**
 * cloneFlow — creates a deep copy of a FlowDefinition
 *
 * @param flow - FlowDefinition to clone
 * @returns new FlowDefinition with unique IDs
 */
export function cloneFlow(flow: FlowDefinition): FlowDefinition {
  const cloned: FlowDefinition = {
    ...flow,
    id: `flow-${Date.now()}`,
    name: `${flow.name} (Copy)`,
    nodes: flow.nodes.map((node) => ({
      ...node,
      id: `${node.id}-copy-${Date.now()}`,
    })),
    edges: flow.edges.map((edge) => ({
      ...edge,
      id: `${edge.id}-copy-${Date.now()}`,
      source: `${edge.source}-copy-${Date.now()}`,
      target: `${edge.target}-copy-${Date.now()}`,
    })),
    metadata: {
      ...flow.metadata,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  }

  return cloned
}
