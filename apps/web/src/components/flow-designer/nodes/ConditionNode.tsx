/**
 * ConditionNode — Boolean logic nodes (if/else, switches)
 *
 * Yellow theme using custom var(--color-yellow).
 */

import { Handle, Position, type NodeProps } from '@xyflow/react'
import type { FlowNodeData } from '../types'

export function ConditionNode({ data, selected }: NodeProps<FlowNodeData>) {
  return (
    <div
      className={`
        px-4 py-2 rounded-lg border-2 min-w-[180px]
        transition-all duration-200
        ${selected ? 'ring-2 ring-offset-2' : ''}
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
            color: 'black',
          }}
        >
          ❓
        </div>
        <div className="flex-1">
          <div className="font-semibold text-sm truncate">{data.label}</div>
          {data.expression && (
            <div className="text-xs opacity-70 font-mono">{data.expression}</div>
          )}
        </div>
      </div>

      <Handle type="source" position={Position.Bottom} className="!bg-warning" />
    </div>
  )
}
