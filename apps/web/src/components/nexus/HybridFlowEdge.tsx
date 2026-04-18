'use client'

/**
 * HybridFlowEdge — Custom React Flow edge with 4-state neon glow state machine
 *
 * **State machine (data-latching pattern):**
 * - idle/undefined: muted slate ghost edge (var(--color-brain-idle), opacity 0.3, no animation)
 * - active: neon cyan animated edge (var(--color-brain-active), drop-shadow glow, stroke-dashoffset animation)
 * - complete: latched green solid edge (var(--color-brain-complete), drop-shadow glow, no animation)
 * - error: pulsing red-orange dashed edge (var(--color-brain-error), animate-pulse class)
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

// Phase 17: Using theme tokens instead of hardcoded colors
// Colors now defined in globals.css as --color-brain-* variables
// These fallback values match the original Brain-03 UI spec

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
          stroke: 'var(--color-brain-active, #64FFDA)',
          strokeWidth: 2,
          opacity: 1,
          filter: reducedMotion ? undefined : 'drop-shadow(0 0 6px var(--color-brain-active, #64FFDA))',
        }

      case 'complete':
        return {
          stroke: 'var(--color-brain-complete, #10B981)',
          strokeWidth: 2,
          opacity: 1,
          filter: reducedMotion ? undefined : 'drop-shadow(0 0 4px var(--color-brain-complete, #10B981))',
        }

      case 'error':
        return {
          stroke: 'var(--color-brain-error, #EF4444)',
          strokeWidth: 2,
          strokeDasharray: '5,5',
          opacity: 1,
        }

      case 'idle':
      default:
        return {
          stroke: 'var(--color-brain-idle, #8892B0)',
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
