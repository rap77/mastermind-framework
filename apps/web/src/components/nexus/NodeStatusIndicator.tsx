import type { BrainStatus } from '@/stores/brainStore'
import { Loader2, CheckCircle2, AlertTriangle, Circle } from 'lucide-react'
import { cn } from '@/lib/utils'

export type NodeVisualStatus = 'blueprint' | BrainStatus

interface NodeStatusIndicatorProps {
  status: NodeVisualStatus
  className?: string
}

/**
 * NodeStatusIndicator
 *
 * Pure display component. Shows icon + color for 5 brain states.
 * Always pairs color with icon for accessibility (redundant state communication).
 * Motion guards prevent animation for users with reduced-motion preference.
 *
 * States:
 *   blueprint — dashed border, 20% opacity (Ghost Architecture idle canvas)
 *   idle      — muted slate gray
 *   active    — neon cyan (#64FFDA) with spin
 *   complete  — emerald green (#10B981) with checkmark
 *   error     — red-orange pulsing with AlertTriangle (colorblind accessible)
 */
export const NodeStatusIndicator = ({
  status,
  className,
}: NodeStatusIndicatorProps) => {
  const base = cn('flex items-center gap-1 text-xs font-medium', className)

  switch (status) {
    case 'blueprint':
      return (
        <span className={cn(base, 'text-muted-foreground/40')}>
          <Circle className="size-3 opacity-40" aria-hidden="true" />
          <span className="sr-only">Blueprint</span>
        </span>
      )

    case 'idle':
      return (
        <span className={cn(base, 'text-slate-400')}>
          <Circle className="size-3" aria-hidden="true" />
          <span>Idle</span>
        </span>
      )

    case 'active':
      return (
        <span
          className={cn(base)}
          style={{ color: 'var(--color-brain-active, #64FFDA)' }}
        >
          <Loader2
            className="size-3 animate-spin motion-reduce:animate-none"
            aria-hidden="true"
          />
          <span>Active</span>
        </span>
      )

    case 'complete':
      return (
        <span
          className={cn(base)}
          style={{ color: 'var(--color-brain-complete, #10B981)' }}
        >
          <CheckCircle2 className="size-3" aria-hidden="true" />
          <span>Complete</span>
        </span>
      )

    case 'error':
      return (
        <span
          className={cn(base, 'animate-pulse motion-reduce:animate-none')}
          style={{ color: 'var(--color-brain-error, #EF4444)' }}
        >
          <AlertTriangle className="size-3" aria-hidden="true" />
          <span>Error</span>
        </span>
      )

    default:
      return null
  }
}
