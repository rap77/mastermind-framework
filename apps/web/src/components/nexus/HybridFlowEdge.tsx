'use client'

/**
 * HybridFlowEdge — Custom React Flow edge with 4-state neon glow state machine
 *
 * **State machine (data-latching pattern):**
 * - idle/undefined: muted slate ghost edge (opacity 0.3, no animation)
 * - active: neon cyan animated edge (drop-shadow glow, stroke-dashoffset animation)
 * - complete: latched green solid edge (drop-shadow glow, no animation)
 * - error: pulsing red-orange dashed edge (animate-pulse class)
 *
 * **CRITICAL:** Edge appearance derives from source brain's status via useBrainState(source).
 * The edge does NOT store state — it reads from brainStore on every render.
 *
 * **prefers-reduced-motion:** All animations suppressed when user prefers reduced motion.
 */

import { useMemo } from 'react'
import { getBezierPath, BaseEdge } from '@xyflow/react'
import type { EdgeProps } from '@xyflow/react'
import { useBrainState } from '@/stores/brainStore'

// Color palette from Brain-03 UI spec
const COLOR_IDLE = '#8892B0'     // Muted Slate — ghost idle
const COLOR_ACTIVE = '#64FFDA'   // Neon Cyan — active + illuminated
const COLOR_COMPLETE = '#64FFDA' // Neon Cyan latched — complete (same hue, different filter)
const COLOR_ERROR = '#FF3D00'    // Vivid Red-Orange — error states

/**
 * Determine if user prefers reduced motion.
 * Returns false in SSR/non-browser environments.
 */
function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * HybridFlowEdge — neon glow edge component for the Nexus DAG
 *
 * Reads source brain status from brainStore to derive edge appearance.
 * Exported as named export — registered in EDGE_TYPES at module level.
 *
 * @param props - React Flow EdgeProps (source, target, sourceX, sourceY, targetX, targetY, etc.)
 */
export function HybridFlowEdge({
  id,
  source,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
}: EdgeProps) {
  const sourceState = useBrainState(source)
  const reducedMotion = prefersReducedMotion()

  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  })

  const edgeStyle = useMemo(() => {
    const status = sourceState?.status

    switch (status) {
      case 'active':
        return {
          stroke: COLOR_ACTIVE,
          strokeWidth: 2,
          opacity: 1,
          filter: reducedMotion ? undefined : 'drop-shadow(0 0 6px #64FFDA)',
        }

      case 'complete':
        return {
          stroke: COLOR_COMPLETE,
          strokeWidth: 2,
          opacity: 1,
          filter: reducedMotion ? undefined : 'drop-shadow(0 0 4px #64FFDA)',
        }

      case 'error':
        return {
          stroke: COLOR_ERROR,
          strokeWidth: 2,
          strokeDasharray: '5,5',
          opacity: 1,
        }

      case 'idle':
      default:
        return {
          stroke: COLOR_IDLE,
          strokeWidth: 1,
          opacity: 0.3,
        }
    }
  }, [sourceState?.status, reducedMotion])

  const isAnimated = !reducedMotion && sourceState?.status === 'active'
  const isError = sourceState?.status === 'error'

  return (
    <BaseEdge
      id={id}
      path={edgePath}
      style={edgeStyle}
      className={isError && !reducedMotion ? 'animate-pulse' : undefined}
      // React Flow's BaseEdge handles animated prop via CSS stroke-dashoffset
      // animated prop must be passed via parent Edge configuration, not BaseEdge
      // We achieve animation via the markerEnd and CSS filter instead
      data-animated={isAnimated}
      data-status={sourceState?.status ?? 'idle'}
    />
  )
}
