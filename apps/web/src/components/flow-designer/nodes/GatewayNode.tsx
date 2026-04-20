/**
 * GatewayNode — Gateway node for Flow Designer
 *
 * Represents entry/exit points for flows (Start, End, API Gateway, etc.)
 * Uses semantic tokens with green color scheme.
 */

import { Handle, Position, NodeProps } from '@xyflow/react'
import type { FlowNodeData } from '../types'

export function GatewayNode({ data, selected }: NodeProps<FlowNodeData>) {
  const isStart = data.label?.toLowerCase().includes('start')
  const isEnd = data.label?.toLowerCase().includes('end')

  return (
    <div
      className={`
        px-4 py-3 rounded-lg border-2 min-w-[220px]
        transition-all duration-200
        ${selected
          ? 'border-[var(--color-border-primary)] shadow-lg'
          : 'border-[var(--color-border-default)]'
        }
        bg-[var(--color-surface-primary)]
        hover:border-[var(--color-border-hover)]
      `}
      style={{
        backgroundColor: 'var(--color-node-gateway-bg, hsl(var(--color-success) / 0.1))',
        borderColor: selected
          ? 'var(--color-node-gateway-border, hsl(var(--color-success)))'
          : 'var(--color-node-gateway-border, hsl(var(--color-success) / 0.5))',
      }}
    >
      {/* Input handle (only for non-start nodes) */}
      {!isStart && (
        <Handle
          type="target"
          position={Position.Left}
          className="w-3 h-3 !bg-[var(--color-node-gateway-handle, hsl(var(--color-success)))]"
        />
      )}

      {/* Node content */}
      <div className="flex flex-col gap-1">
        {/* Icon and label row */}
        <div className="flex items-center gap-2">
          {data.icon && (
            <span className="text-lg" role="img" aria-label="gateway icon">
              {data.icon}
            </span>
          )}
          <div className="flex-1">
            <div className="font-semibold text-sm text-[var(--color-text-primary)]">
              {data.label}
            </div>
          </div>
        </div>

        {/* Description (if provided) */}
        {data.description && (
          <div className="text-xs text-[var(--color-text-tertiary)] mt-1">
            {data.description}
          </div>
        )}
      </div>

      {/* Output handle (only for non-end nodes) */}
      {!isEnd && (
        <Handle
          type="source"
          position={Position.Right}
          className="w-3 h-3 !bg-[var(--color-node-gateway-handle, hsl(var(--color-success)))]"
        />
      )}
    </div>
  )
}
