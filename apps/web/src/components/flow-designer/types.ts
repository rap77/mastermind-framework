/**
 * Flow Designer Types — n8n-style node-based flow editor
 *
 * Defines the data structures for the Flow Designer, compatible with React Flow v12.
 * All node types use semantic tokens for theming (var(--color-*)).
 */

import type { Node, Edge } from '@xyflow/react'

/**
 * NodeTypes — available node categories in the Flow Designer
 *
 * Each type maps to a custom React Flow node component:
 * - brain: Agent brain nodes (Product Strategy, UX Research, etc.)
 * - gateway: Entry/exit points for flows
 * - adapter: Integration nodes (APIs, databases, external services)
 * - router: Conditional routing nodes
 * - condition: Boolean logic nodes (if/else, switches)
 */
export enum NodeType {
  BRAIN = 'brain',
  GATEWAY = 'gateway',
  ADAPTER = 'adapter',
  ROUTER = 'router',
  CONDITION = 'condition',
}

/**
 * FlowNodeData — custom data attached to each node
 *
 * Extends React Flow's Node['data'] with Flow Designer-specific fields.
 */
export interface FlowNodeData {
  label: string
  description?: string
  icon?: string
  status?: 'idle' | 'running' | 'success' | 'error'
  config?: Record<string, unknown>
  // Brain-specific fields
  brainId?: string
  niche?: string
  // Adapter-specific fields
  adapterType?: 'http' | 'websocket' | 'database' | 'file'
  // Condition-specific fields
  expression?: string
}

/**
 * FlowNode — React Flow node with Flow Designer data
 *
 * Uses React Flow's Node type with our custom data.
 * Position is { x, y } in pixels from top-left.
 */
export interface FlowNode extends Node {
  id: string
  type: NodeType
  position: { x: number; y: number }
  data: FlowNodeData
}

/**
 * FlowEdge — React Flow edge with optional label
 *
 * Uses React Flow's Edge type with Flow Designer extensions.
 * Label displays on the edge (useful for router conditions).
 */
export interface FlowEdge extends Edge {
  id: string
  source: string
  target: string
  label?: string
  type?: string
}

/**
 * FlowDefinition — complete flow structure
 *
 * Represents an entire workflow with nodes, edges, and metadata.
 * Can be serialized to JSON for storage/import.
 */
export interface FlowDefinition {
  id: string
  name: string
  description?: string
  nodes: FlowNode[]
  edges: FlowEdge[]
  viewport?: {
    x: number
    y: number
    zoom: number
  }
  metadata?: {
    createdAt: string
    updatedAt: string
    version: string
    tags?: string[]
  }
}

/**
 * FlowTemplate — predefined flow patterns
 *
 * Reusable flow templates for common patterns.
 */
export interface FlowTemplate {
  id: string
  name: string
  description: string
  category: 'product' | 'ux' | 'development' | 'qa' | 'growth' | 'custom'
  definition: FlowDefinition
  thumbnail?: string
}

/**
 * FlowValidationError — validation error details
 *
 * Returned by validateFlow when the flow definition is invalid.
 */
export interface FlowValidationError {
  path: string
  message: string
  code: string
}

/**
 * ValidationResult — result of flow validation
 *
 * Indicates whether a flow is valid and includes error details if not.
 */
export interface ValidationResult {
  valid: boolean
  errors?: FlowValidationError[]
}
