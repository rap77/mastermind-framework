'use client'

/**
 * OrchestrationBrainNode — Custom React Flow node for OrchestrationCanvas.
 *
 * Extends the NexusCanvas BrainNode pattern with:
 * - `isSelected` prop (cross-panel selection ring — gold/amber border)
 * - Dynamic status: reads brainStore like BrainNode does (never rewrite — reuse pattern)
 * - Shows BrainEventStatus from wsEventsStore for the latest event
 *
 * CRITICAL: Wrapped in React.memo to prevent cascade re-renders.
 * Status is read via useBrainState(id) — O(1) Map lookup.
 * All interactive children MUST have nodrag AND nopan classes.
 */

import { memo } from 'react'
import { Handle, Position } from '@xyflow/react'
import type { NodeProps } from '@xyflow/react'
import { Card, CardContent } from '@/components/ui/card'
import { NodeStatusIndicator } from '@/components/nexus/NodeStatusIndicator'
import { useBrainState } from '@/stores/brainStore'
import { cn } from '@/lib/utils'

// ─── Types ─────────────────────────────────────────────────────────────────────

export interface OrchestrationBrainNodeData {
  label: string
  niche: string
  isSelected: boolean
  onSelect: (id: string) => void
}

// ─── Component ─────────────────────────────────────────────────────────────────

const OrchestrationBrainNodeComponent = ({ id, data }: NodeProps) => {
  const nodeData = data as unknown as OrchestrationBrainNodeData
  const brainState = useBrainState(id)

  const isGhost = brainState === undefined
  const status = isGhost ? 'blueprint' : brainState.status

  const handleSelect = () => {
    nodeData.onSelect(id)
  }

  return (
    <Card
      size="sm"
      className={cn(
        'w-[220px] transition-all duration-200 relative',
        isGhost ? 'border-dashed opacity-20' : 'border-solid opacity-100',
        // Selection ring — amber for orchestration canvas
        nodeData.isSelected && 'ring-2 ring-amber-400',
        status === 'active' && 'ring-2 nexus-ring-active',
        status === 'error' && 'ring-2 nexus-ring-error',
        status === 'complete' && 'ring-2 nexus-ring-complete',
        // Selected + active: amber overrides status ring (specificity via order)
        nodeData.isSelected && status === 'active' && 'ring-amber-400',
      )}
    >
      <Handle type="target" position={Position.Left} style={{ top: '50%' }} />

      <CardContent className="p-2 flex flex-col gap-1">
        <div className="flex items-center gap-1 justify-between">
          <button
            type="button"
            className={cn(
              'nodrag nopan',
              'text-left text-xs font-semibold leading-tight truncate flex-1',
              'hover:text-primary transition-colors cursor-pointer',
              'bg-transparent border-0 p-0',
              nodeData.isSelected && 'text-amber-400',
            )}
            onClick={handleSelect}
            aria-label={nodeData.label}
            aria-pressed={nodeData.isSelected}
          >
            {nodeData.label}
          </button>
          {status === 'complete' && (
            <span className="nodrag nopan text-[12px] nexus-text-complete font-bold">
              ✓
            </span>
          )}
        </div>

        <div className="flex items-center justify-between">
          <NodeStatusIndicator status={status} />
        </div>
      </CardContent>

      <Handle type="source" position={Position.Right} style={{ top: '50%' }} />
    </Card>
  )
}

OrchestrationBrainNodeComponent.displayName = 'OrchestrationBrainNode'

export const OrchestrationBrainNode = memo(OrchestrationBrainNodeComponent)
OrchestrationBrainNode.displayName = 'OrchestrationBrainNode'
