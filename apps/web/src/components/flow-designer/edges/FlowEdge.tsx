/**
 * FlowEdge — Custom edge component for Flow Designer
 *
 * Styled edge with n8n-inspired aesthetics:
 * - Smooth step path with rounded corners (like n8n)
 * - Thicker stroke (2px default, 2.5px selected)
 * - Animated dashed line on hover/selected
 * - Label support with badge styling
 */

import { memo } from 'react'
import {
  EdgeLabelRenderer,
  BaseEdge,
  type EdgeProps,
  getSmoothStepPath,
} from '@xyflow/react'
import type { FlowEdge } from '../types'

/**
 * Calculates the midpoint of an edge for label positioning
 *
 * @param sourceX - Source node X coordinate
 * @param sourceY - Source node Y coordinate
 * @param targetX - Target node X coordinate
 * @param targetY - Target node Y coordinate
 * @returns Object with x, y coordinates of the midpoint
 * @example
 * const center = getEdgeCenter(0, 0, 100, 100)
 * // Returns: { x: 50, y: 50 }
 */
export const getEdgeCenter = (
  sourceX: number,
  sourceY: number,
  targetX: number,
  targetY: number
): { x: number; y: number } => {
  return {
    x: (sourceX + targetX) / 2,
    y: (sourceY + targetY) / 2,
  }
}

export const FlowEdge = memo(
  ({ id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, label, selected }: EdgeProps<FlowEdge>) => {
    const [edgePath] = getSmoothStepPath({
      sourceX,
      sourceY,
      targetX,
      targetY,
      sourcePosition,
      targetPosition,
      borderRadius: 16,
    })

    // Calculate midpoint for label positioning
    const { x: labelX, y: labelY } = getEdgeCenter(sourceX, sourceY, targetX, targetY)

    return (
      <>
        {/* Background wider path for better hover target */}
        <path
          d={edgePath}
          fill="none"
          strokeWidth={12}
          stroke="transparent"
        />

        <BaseEdge
          id={id}
          path={edgePath}
          style={{
            strokeWidth: selected ? 2.5 : 2,
            stroke: selected
              ? 'var(--color-primary)'
              : 'var(--color-border)',
            transition: 'stroke 0.2s, stroke-width 0.2s',
          }}
        />

        {label && (
          <EdgeLabelRenderer>
            <div
              className={`
                px-2 py-0.5 rounded text-xs font-medium
                pointer-events: all
              `}
              style={{
                position: 'absolute',
                transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
                backgroundColor: selected
                  ? 'var(--color-primary)'
                  : 'var(--color-surface)',
                color: selected
                  ? 'var(--color-primary-foreground)'
                  : 'var(--color-text-secondary)',
                border: `1px solid ${selected ? 'var(--color-primary)' : 'var(--color-border)'}`,
                pointerEvents: 'all',
                fontSize: '11px',
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
