/**
 * FlowEdge — Custom edge component for Flow Designer
 *
 * Styled edge with label support and animation for active flows.
 * Uses semantic tokens for theming.
 */

import { memo } from 'react'
import {
  EdgeLabelRenderer,
  BaseEdge,
  type EdgeProps,
  getBezierPath,
} from '@xyflow/react'
import type { FlowEdge } from '../types'

export const FlowEdge = memo(
  ({ id, sourceX, sourceY, targetX, targetY, label, selected }: EdgeProps<FlowEdge>) => {
    const [edgePath] = getBezierPath({
      sourceX,
      sourceY,
      targetX,
      targetY,
    })

    return (
      <>
        <BaseEdge
          id={id}
          path={edgePath}
          className={`
            transition-all duration-200
            ${selected ? 'stroke-[var(--color-primary)] stroke-2' : 'stroke-[var(--color-border)]'}
          `}
        />

        {label && (
          <EdgeLabelRenderer>
            <div
              className={`
                px-2 py-1 rounded text-xs font-medium
                ${selected ? 'bg-[var(--color-primary)] text-[var(--color-primary-foreground)]' : ''}
              `}
              style={{
                backgroundColor: 'var(--color-surface)',
                color: 'var(--color-text-primary)',
                border: '1px solid var(--color-border)',
              }}
            >
              {label}
            </div>
          </EdgeLabelRenderer>
        )}
      </>
    )
  }
)

FlowEdge.displayName = 'FlowEdge'
