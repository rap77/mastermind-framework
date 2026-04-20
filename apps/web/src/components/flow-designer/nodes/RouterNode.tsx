/**
 * RouterNode — Conditional routing nodes
 *
 * Orange theme using var(--color-warning).
 */

import { Handle, Position, type NodeProps } from '@xyflow/react'
import type { FlowNodeData } from '../types'

export function RouterNode({ data, selected }: NodeProps<FlowNodeData>) {
  return (
    <div
      className={`
        px-4 py-3 rounded-lg border-2 min-w-[220px]
        transition-all duration-200
        ${selected ? 'ring-2 ring-warning ring-offset-2' : ''}
      `}
      style={{
        backgroundColor: 'var(--color-surface)',
        borderColor: 'var(--color-warning)',
        color: 'var(--color-warning)',
      }}
    >
      <Handle type="target" position={Position.Top} className="!bg-warning" />

      <div className="flex items-center gap-2">
        <div
          className="w-6 h-6 rounded flex items-center justify-center text-xs"
          style={{
            backgroundColor: 'var(--color-warning)',
            color: 'var(--color-warning-foreground)',
          }}
        >
          ↗️
        </div>
        <div className="flex-1">
          <div className="font-semibold text-sm truncate">{data.label}</div>
          {data.description && (
            <div className="text-xs opacity-70 truncate">{data.description}</div>
          )}
        </div>
      </div>

      <Handle type="source" position={Position.Bottom} className="!bg-warning" />
    </div>
  )
}
