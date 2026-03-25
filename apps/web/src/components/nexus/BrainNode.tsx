import { memo } from 'react'
import { Handle, Position } from '@xyflow/react'
import type { NodeProps } from '@xyflow/react'
import { Card, CardContent } from '@/components/ui/card'
import { NodeStatusIndicator } from './NodeStatusIndicator'
import { useBrainState, useBrainStore } from '@/stores/brainStore'
import { useOrchestratorStore } from '@/stores/orchestratorStore'
import { cn } from '@/lib/utils'

export interface BrainNodeData {
  label: string
  niche: string
  onSelect: (id: string) => void
}

/**
 * BrainNode — Custom React Flow node component
 *
 * CRITICAL: Wrapped in React.memo to prevent cascade re-renders.
 * Brain state is read via useBrainState(id) — O(1) Map lookup.
 * All interactive children MUST have nodrag AND nopan classes (NEX-03).
 *
 * Ghost Architecture: when brainState is undefined (no active task),
 * renders with opacity-20 and dashed border.
 */
const BrainNodeComponent = ({ id, data }: NodeProps) => {
  const nodeData = data as unknown as BrainNodeData
  const brainState = useBrainState(id)
  const invocations = useBrainStore((s) => s.sessionInvocationCounts.get(id) ?? 0)

  const isGhost = brainState === undefined
  const status = isGhost ? 'blueprint' : brainState.status
  const isFocusMode = useOrchestratorStore((s) => s.isFocusMode)

  // In Focus Mode: idle brains dim to 30% opacity (active/complete/error remain full)
  const isIdleInFocusMode =
    isFocusMode && !isGhost && (status === 'idle' || status === 'blueprint')

  const handleSelect = () => {
    nodeData.onSelect(id)
  }

  return (
    <>
      {/* React Flow connection handles — not interactive so no nodrag/nopan needed */}
      <Handle type="target" position={Position.Top} />

      <Card
        size="sm"
        className={cn(
          'w-[160px] transition-all duration-200',
          isGhost
            ? 'border-dashed opacity-20'
            : isIdleInFocusMode
              ? 'border-solid opacity-30'
              : 'border-solid opacity-100',
          status === 'active' && 'ring-2 ring-[var(--color-brain-active,#64FFDA)]',
          status === 'error' && 'ring-2 ring-[var(--color-brain-error,#EF4444)]',
          status === 'complete' && 'ring-2 ring-[var(--color-brain-complete,#10B981)]',
        )}
        style={isGhost ? { boxShadow: 'var(--shadow-ghost, none)' } : undefined}
      >
        <CardContent className="p-2 flex flex-col gap-1">
          {/* CRITICAL: nodrag + nopan on ALL interactive elements (NEX-03) */}
          <div className="flex items-center gap-1 justify-between">
            <button
              type="button"
              className={cn(
                'nodrag nopan',
                'text-left text-xs font-semibold leading-tight truncate flex-1',
                'hover:text-primary transition-colors cursor-pointer',
                'bg-transparent border-0 p-0'
              )}
              onClick={handleSelect}
              aria-label={nodeData.label}
            >
              {nodeData.label}
            </button>
            {/* Checkmark badge for completed tasks */}
            {status === 'complete' && (
              <span className="nodrag nopan text-[12px] text-[var(--color-brain-complete,#10B981)] font-bold">
                ✓
              </span>
            )}
          </div>

          <div className="flex items-center justify-between">
            <NodeStatusIndicator status={status} />
            <span className="text-[10px] text-muted-foreground tabular-nums">
              ×{invocations}
            </span>
          </div>
        </CardContent>
      </Card>

      <Handle type="source" position={Position.Bottom} />
    </>
  )
}

BrainNodeComponent.displayName = 'BrainNode'

export const BrainNode = memo(BrainNodeComponent)
// Preserve displayName after memo wrapping
BrainNode.displayName = 'BrainNode'
