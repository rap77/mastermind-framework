'use client'

/**
 * StatusTimeline — D2.02, D2.04, D2.05
 *
 * Chronological list of BrainStateEvent entries with per-status icons.
 * Auto-scrolls to the most recent event when the list changes.
 *
 * Status → icon mapping (D2.04):
 *   completed  → CheckCircle (Lucide)
 *   running    → Loader2    (Lucide, animated spin)
 *   dispatched → Circle     (Lucide, muted — "pending/queued")
 *   failed     → XCircle    (Lucide)
 *
 * Each row shows:
 *   [icon] brain_id · status · relative timestamp
 */

import { useEffect, useRef } from 'react'
import { CheckCircle, XCircle, Loader2, Circle } from 'lucide-react'
import type { BrainStateEvent, BrainEventStatus } from '@/stores/wsEventsStore'
import { cn } from '@/lib/utils'

// ─── Status icon helpers ───────────────────────────────────────────────────────

interface StatusIconProps {
  status: BrainEventStatus
  className?: string
}

function StatusIcon({ status, className }: StatusIconProps) {
  switch (status) {
    case 'completed':
      return (
        <CheckCircle
          className={cn('h-4 w-4 text-emerald-500 flex-shrink-0', className)}
          aria-label="completed"
          data-testid="icon-completed"
        />
      )
    case 'running':
      return (
        <Loader2
          className={cn('h-4 w-4 text-blue-500 flex-shrink-0 animate-spin', className)}
          aria-label="running"
          data-testid="icon-running"
        />
      )
    case 'failed':
      return (
        <XCircle
          className={cn('h-4 w-4 text-red-500 flex-shrink-0', className)}
          aria-label="failed"
          data-testid="icon-failed"
        />
      )
    case 'dispatched':
    default:
      return (
        <Circle
          className={cn('h-4 w-4 text-muted-foreground flex-shrink-0', className)}
          aria-label="dispatched"
          data-testid="icon-dispatched"
        />
      )
  }
}

// ─── Relative timestamp helper ─────────────────────────────────────────────────

function relativeTime(isoTimestamp: string): string {
  const then = new Date(isoTimestamp).getTime()
  const now = Date.now()
  const diffMs = now - then

  if (diffMs < 1_000) return 'just now'
  if (diffMs < 60_000) return `${Math.floor(diffMs / 1_000)}s ago`
  if (diffMs < 3_600_000) return `${Math.floor(diffMs / 60_000)}m ago`
  return `${Math.floor(diffMs / 3_600_000)}h ago`
}

// ─── StatusTimelineItem ────────────────────────────────────────────────────────

interface StatusTimelineItemProps {
  event: BrainStateEvent
}

function StatusTimelineItem({ event }: StatusTimelineItemProps) {
  return (
    <li
      className="flex items-start gap-2 px-3 py-2 text-xs border-b border-border/40 last:border-0"
      data-testid="timeline-item"
      data-brain-id={event.brain_id}
      data-status={event.status}
    >
      <StatusIcon status={event.status} />

      <div className="flex-1 min-w-0">
        <span className="font-medium text-foreground truncate block">
          {event.brain_id}
        </span>
        <span
          className={cn(
            'capitalize',
            event.status === 'completed' && 'text-emerald-600 dark:text-emerald-400',
            event.status === 'running' && 'text-blue-600 dark:text-blue-400',
            event.status === 'failed' && 'text-red-600 dark:text-red-400',
            event.status === 'dispatched' && 'text-muted-foreground',
          )}
        >
          {event.status}
        </span>
      </div>

      <time
        dateTime={event.timestamp}
        className="text-muted-foreground whitespace-nowrap flex-shrink-0"
        title={event.timestamp}
      >
        {relativeTime(event.timestamp)}
      </time>
    </li>
  )
}

// ─── StatusTimeline ────────────────────────────────────────────────────────────

export interface StatusTimelineProps {
  events: BrainStateEvent[]
  /** Optional label for the panel header. Defaults to "Activity". */
  label?: string
  className?: string
}

export function StatusTimeline({
  events,
  label = 'Activity',
  className,
}: StatusTimelineProps) {
  // D2.05 — auto-scroll ref: scroll to the sentinel div at list bottom
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (events.length > 0) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [events])

  return (
    <div
      className={cn('flex flex-col', className)}
      data-testid="status-timeline"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-border bg-background/80 flex-shrink-0">
        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
          {label}
        </span>
        {events.length > 0 && (
          <span className="text-xs text-muted-foreground">
            {events.length} event{events.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Event list — scrollable */}
      <div className="overflow-y-auto flex-1" data-testid="timeline-scroll-container">
        {events.length === 0 ? (
          <p className="text-xs text-muted-foreground text-center py-6 px-3">
            No events yet. Dispatch a brain to see activity here.
          </p>
        ) : (
          <ul role="list" aria-label="Brain activity timeline">
            {events.map((event) => (
              <StatusTimelineItem
                key={`${event.trace_id}-${event.brain_id}-${event.status}`}
                event={event}
              />
            ))}
          </ul>
        )}

        {/* D2.05 — auto-scroll sentinel */}
        <div ref={bottomRef} aria-hidden="true" />
      </div>
    </div>
  )
}
