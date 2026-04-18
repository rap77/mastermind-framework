'use client'

import React, { useState } from 'react'
import { cn } from '@/lib/utils'
import { useFilteredEvents } from '@/stores/simulationStore'
import type { SimulationEvent } from '@/stores/simulationStore'

// ─── Props ────────────────────────────────────────────────────────────────────

export interface EventLogProps {
  className?: string
}

// ─── Helpers ───────────────────────────────────────────────────────────────────

/**
 * formatTimestamp — converts timestamp to HH:MM:SS format
 */
const formatTimestamp = (timestamp: number): string => {
  const date = new Date(timestamp)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  const seconds = date.getSeconds().toString().padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
}

/**
 * formatRelativeTime — converts timestamp to relative time (e.g., "2s ago", "5m ago")
 */
const formatRelativeTime = (timestamp: number, currentTime: number = Date.now()): string => {
  const diff = currentTime - timestamp
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)

  if (seconds < 60) {
    return `${seconds}s ago`
  } else if (minutes < 60) {
    return `${minutes}m ago`
  } else {
    return `${hours}h ago`
  }
}

/**
 * formatTimestampWithRelative — shows both absolute and relative time
 */
const formatTimestampWithRelative = (timestamp: number): string => {
  const absolute = formatTimestamp(timestamp)
  const relative = formatRelativeTime(timestamp)
  return `${absolute} (${relative})`
}

/**
 * getEventColor — returns CSS variable for event type
 */
const getEventColor = (type: SimulationEvent['type']): string => {
  switch (type) {
    case 'info':
      return 'var(--color-info)'
    case 'success':
      return 'var(--color-success)'
    case 'error':
      return 'var(--color-error)'
    case 'warning':
      return 'var(--color-warning)'
    default:
      return 'var(--color-muted-foreground)'
  }
}

// ─── Component ────────────────────────────────────────────────────────────────

/**
 * EventLog — scrollable event log for simulation replay.
 *
 * **Features:**
 * - Displays filtered events in chronological order
 * - Color-coded by event type (info/success/error/warning)
 * - Timestamps formatted as HH:MM:SS
 * - Scrollable container with max-height 300px
 * - Empty state when no events available
 * - Uses theme tokens for all colors (dark mode compatible)
 *
 * **Event Types:**
 * - `info`: Blue — general information events
 * - `success`: Green — successful completions
 * - `error`: Red — failures and errors
 * - `warning`: Yellow — slow operations or warnings
 *
 * @example
 * ```tsx
 * <EventLog />
 * ```
 */
export default function EventLog({ className }: EventLogProps) {
  const events = useFilteredEvents()
  const [showRelativeTime, setShowRelativeTime] = useState(false)

  // Empty state
  if (events.length === 0) {
    return (
      <div
        className={cn(
          'flex items-center justify-center',
          'text-sm text-muted-foreground',
          'min-h-[200px]',
          className,
        )}
      >
        No events yet
      </div>
    )
  }

  return (
    <div
      className={cn(
        'flex flex-col',
        'space-y-2',
        'overflow-y-auto',
        'max-h-[300px]',
        'p-4',
        'rounded-md',
        'bg-card',
        'border border-border',
        className,
      )}
    >
      {/* Toggle button for relative time */}
      <div className="flex items-center justify-between pb-2 border-b border-border">
        <span className="text-sm font-medium text-foreground">Event Log</span>
        <button
          onClick={() => setShowRelativeTime(!showRelativeTime)}
          className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          aria-label={showRelativeTime ? 'Show absolute time' : 'Show relative time'}
        >
          {showRelativeTime ? 'Absolute' : 'Relative'}
        </button>
      </div>
      {events.map((event, index) => (
        <div
          key={`${event.timestamp}-${index}`}
          className="flex items-start gap-2 text-sm"
        >
          {/* Timestamp */}
          <span className="font-mono text-xs text-muted-foreground shrink-0">
            {showRelativeTime
              ? formatTimestampWithRelative(event.timestamp)
              : formatTimestamp(event.timestamp)}
          </span>

          {/* Event type indicator */}
          <span
            className="w-2 h-2 rounded-full shrink-0 mt-1"
            style={{ backgroundColor: getEventColor(event.type) }}
            aria-hidden="true"
          />

          {/* Message */}
          <span className="text-foreground flex-1 break-words">
            {event.message}
          </span>

          {/* Brain ID (optional) */}
          {event.brainId && (
            <span className="text-xs text-muted-foreground shrink-0">
              {event.brainId}
            </span>
          )}
        </div>
      ))}
    </div>
  )
}
