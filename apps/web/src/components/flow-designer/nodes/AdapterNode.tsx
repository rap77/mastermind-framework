/**
 * AdapterNode — Adapter node for Flow Designer
 *
 * Represents integration nodes (APIs, databases, external services, etc.)
 * Uses semantic tokens with purple color scheme.
 */

import { Handle, Position, NodeProps } from '@xyflow/react'
import type { FlowNodeData } from '../types'

export function AdapterNode({ data, selected }: NodeProps<FlowNodeData>) {
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
        backgroundColor: 'var(--color-node-adapter-bg, hsl(var(--color-purple) / 0.1))',
        borderColor: selected
          ? 'var(--color-node-adapter-border, hsl(var(--color-purple)))'
          : 'var(--color-node-adapter-border, hsl(var(--color-purple) / 0.5))',
      }}
    >
      {/* Input handle (left) */}
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 !bg-[var(--color-node-adapter-handle, hsl(var(--color-purple)))]"
      />

      {/* Node content */}
      <div className="flex flex-col gap-1">
        {/* Icon and label row */}
        <div className="flex items-center gap-2">
          {data.icon && (
            <span className="text-lg" role="img" aria-label="adapter icon">
              {data.icon}
            </span>
          )}
          <div className="flex-1">
            <div className="font-semibold text-sm text-[var(--color-text-primary)]">
              {data.label}
            </div>
            {data.adapterType && (
              <div className="text-xs text-[var(--color-text-secondary)] uppercase">
                {data.adapterType}
              </div>
            )}
          </div>
        </div>

        {/* Description (if provided) */}
        {data.description && (
          <div className="text-xs text-[var(--color-text-tertiary)] mt-1">
            {data.description}
          </div>
        )}

        {/* Status indicator */}
        {data.status && (
          <div className="flex items-center gap-1 mt-1">
            <div
              className={`
                w-2 h-2 rounded-full
                ${data.status === 'running' ? 'animate-pulse' : ''}
              `}
              style={{
                backgroundColor:
                  data.status === 'success' ? 'var(--color-status-success, var(--status-success))' :
                  data.status === 'error' ? 'var(--color-status-error, var(--status-error))' :
                  data.status === 'running' ? 'var(--color-status-warning, var(--status-warning))' :
                  'var(--color-status-idle, var(--status-idle))',
              }}
            />
            <span className="text-xs text-[var(--color-text-secondary)] capitalize">
              {data.status}
            </span>
          </div>
        )}
      </div>

      {/* Output handle (right) */}
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 !bg-[var(--color-node-adapter-handle, hsl(var(--color-purple)))]"
      />
    </div>
  )
}
