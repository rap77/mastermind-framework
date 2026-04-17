/**
 * FlowDesignerCanvas — Main canvas for Flow Designer
 *
 * Integrates React Flow with palette, toolbar, and node types.
 * Based on NexusCanvas.tsx pattern.
 */

import { useCallback, useMemo } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type NodeTypes,
  type EdgeTypes,
  type OnDragOverEventHandler,
  type OnDropEventHandler,
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

export function FlowDesignerCanvas() {
  const { nodes, edges, addNode, viewport } = useFlowDesignerStore()

  const onDragOver: OnDragOverEventHandler = useCallback((event) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop: OnDropEventHandler = useCallback(
    (event) => {
      event.preventDefault()

      const type = event.dataTransfer.getData('application/reactflow') as NodeType
      if (!type) return

      const position = {
        x: event.dataTransfer.offsetX,
        y: event.dataTransfer.offsetY,
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
    [addNode]
  )

  return (
    <div className="flex flex-col h-screen">
      <FlowToolbar />

      <div className="flex flex-1 overflow-hidden">
        <FlowPalette />

        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={NODE_TYPES}
            edgeTypes={EDGE_TYPES}
            onDragOver={onDragOver}
            onDrop={onDrop}
            fitView
            defaultViewport={viewport}
            minZoom={0.2}
            maxZoom={2}
            className="bg-background"
          >
            <Background />
            <Controls />
            <MiniMap
              nodeColor={() => 'var(--color-primary)'}
              maskColor="var(--color-surface)"
            />
          </ReactFlow>
        </div>
      </div>
    </div>
  )
}
