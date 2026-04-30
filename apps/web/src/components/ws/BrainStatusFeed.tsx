'use client'

/**
 * BrainStatusFeed — Real-time brain lifecycle event display.
 *
 * B2.9 spec:
 *   - Connects to ws://rust:8002/ws/events via useWebSocket
 *   - Parses incoming JSON as BrainStateEvent
 *   - Appends events to wsEventsStore keyed by trace_id
 *   - Renders a live list of brain status updates grouped by trace
 *   - Shows connection status badge
 *
 * The component is intentionally display-only.  No brain actions are
 * dispatched from here — this is a pure read path.
 */

import { useEffect } from 'react'

import { useWebSocket } from '@/hooks/useWebSocket'
import {
  type BrainStateEvent,
  useWsEventsStore,
} from '@/stores/wsEventsStore'

// ------------------------------------------------------------------ config

/** Returns the Rust hub WS URL — evaluated at call-site so it's safe in SSR. */
function getRustWsUrl(): string | null {
  if (typeof window === 'undefined') return null
  return process.env.NEXT_PUBLIC_RUST_WS_URL ?? 'ws://localhost:8002/ws/events'
}

// ------------------------------------------------------------------ helpers

const STATUS_COLORS: Record<BrainStateEvent['status'], string> = {
  dispatched: 'text-blue-400',
  running: 'text-yellow-400',
  completed: 'text-green-400',
  failed: 'text-red-400',
}

const STATUS_ICONS: Record<BrainStateEvent['status'], string> = {
  dispatched: '→',
  running: '⟳',
  completed: '✓',
  failed: '✗',
}

// ------------------------------------------------------------------ component

interface BrainStatusFeedProps {
  /** Restrict the feed to events from a specific trace_id. Pass null to show all. */
  traceId?: string | null
  /** Maximum number of events to display (default: 50). */
  maxItems?: number
  /** CSS class applied to the container. */
  className?: string
}

export function BrainStatusFeed({
  traceId = null,
  maxItems = 50,
  className = '',
}: BrainStatusFeedProps) {
  const appendEvent = useWsEventsStore((s) => s.appendEvent)
  const allEvents = useWsEventsStore((s) => s.events)

  const { status, reconnectCount } = useWebSocket(getRustWsUrl(), {
    onMessage: (event) => {
      try {
        const parsed = JSON.parse(event.data) as BrainStateEvent
        // Basic shape validation before storing
        if (parsed.trace_id && parsed.brain_id && parsed.status && parsed.timestamp) {
          appendEvent(parsed)
        }
      } catch {
        // Malformed JSON — ignore silently (logged in dev via console)
        if (process.env.NODE_ENV === 'development') {
          console.warn('[BrainStatusFeed] failed to parse WS message:', event.data)
        }
      }
    },
  })

  // Clean up stale entries when component unmounts
  useEffect(() => {
    return () => {
      // We intentionally do NOT clear the store on unmount so that
      // parent components can still read the accumulated history.
    }
  }, [])

  // Flatten events — filter by traceId if provided
  const displayEvents: (BrainStateEvent & { _traceId: string })[] = []
  for (const [tid, evts] of allEvents.entries()) {
    if (traceId && tid !== traceId) continue
    for (const evt of evts) {
      displayEvents.push({ ...evt, _traceId: tid })
    }
  }

  // Most-recent first, capped at maxItems
  const visibleEvents = displayEvents.slice(-maxItems).reverse()

  return (
    <div className={`flex flex-col gap-2 ${className}`} data-testid="brain-status-feed">
      {/* Connection status badge */}
      <div className="flex items-center gap-2 text-xs font-mono">
        <span
          className={
            status === 'connected'
              ? 'text-green-400'
              : status === 'connecting'
                ? 'text-yellow-400'
                : 'text-red-400'
          }
          data-testid="ws-status-badge"
        >
          {status === 'connected' && '● Connected'}
          {status === 'connecting' &&
            `● Connecting${reconnectCount > 0 ? ` (retry ${reconnectCount}/3)` : ''}...`}
          {status === 'disconnected' && '○ Disconnected'}
          {status === 'error' && '● Error'}
        </span>
        <span className="text-gray-500">/ws/events</span>
      </div>

      {/* Event list */}
      {visibleEvents.length === 0 ? (
        <p className="text-xs text-gray-500 italic" data-testid="no-events-message">
          Waiting for brain events…
        </p>
      ) : (
        <ul className="space-y-1" data-testid="events-list">
          {visibleEvents.map((evt, idx) => (
            <li
              key={`${evt._traceId}-${evt.brain_id}-${evt.status}-${idx}`}
              className="flex items-center gap-2 text-xs font-mono"
              data-testid={`brain-event-${evt.status}`}
            >
              <span className={STATUS_COLORS[evt.status]}>
                {STATUS_ICONS[evt.status]}
              </span>
              <span className="text-gray-300">brain-{evt.brain_id}</span>
              <span className={STATUS_COLORS[evt.status]}>{evt.status}</span>
              <span className="text-gray-600 truncate max-w-[120px]" title={evt._traceId}>
                {evt._traceId.slice(0, 8)}…
              </span>
              <span className="text-gray-600">
                {new Date(evt.timestamp).toLocaleTimeString()}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
