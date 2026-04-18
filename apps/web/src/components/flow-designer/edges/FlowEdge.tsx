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

/**
 * getEdgeCenter — Calculate the midpoint of an edge
 *
 * @param sourceX - Source node X coordinate
 * @param sourceY - Source node Y coordinate
 * @param targetX - Target node X coordinate
 * @param targetY - Target node Y coordinate
 * @returns Object with x, y coordinates of the midpoint
 */
export function getEdgeCenter(
  sourceX: number,
  sourceY: number,
  targetX: number,
  targetY: number
): { x: number; y: number } {
  return {
    x: (sourceX + targetX) / 2,
    y: (sourceY + targetY) / 2,
  }
}

export const FlowEdge = memo(
  ({ id, sourceX, sourceY, targetX, targetY, label, selected }: EdgeProps<FlowEdge>) => {
    const [edgePath] = getBezierPath({
      sourceX,
      sourceY,
      targetX,
      targetY,
    })

    // Calculate midpoint for label positioning
    const { x: labelX, y: labelY } = getEdgeCenter(sourceX, sourceY, targetX, targetY)

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
                position: 'absolute',
                transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
                backgroundColor: 'var(--color-surface)',
                color: 'var(--color-text-primary)',
                border: '1px solid var(--color-border)',
                pointerEvents: 'all',
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
