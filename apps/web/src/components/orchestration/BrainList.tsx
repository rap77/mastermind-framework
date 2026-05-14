'use client'

/**
 * BrainList — Left column of the Orchestration Canvas.
 *
 * Displays all brains from the registry with their live status.
 * Status comes from two sources:
 *   1. brainStore (WS-driven runtime status: idle/active/complete/error)
 *   2. wsEventsStore (latest event per brain in the active trace)
 *
 * Uses useBrainState(id) selector for O(1) lookup — no cascade re-renders.
 * Live events feed beneath each brain when the trace is active.
 */

import type { Brain } from '@/lib/api'
import { useBrainState } from '@/stores/brainStore'
import { useWsEventsStore } from '@/stores/wsEventsStore'
import { NodeStatusIndicator } from '@/components/nexus/NodeStatusIndicator'
import { cn } from '@/lib/utils'

// ─── Types ─────────────────────────────────────────────────────────────────────

interface BrainListProps {
  brains: Brain[]
  selectedBrainId: string | null
  onSelect: (brainId: string) => void
}

// ─── Component ─────────────────────────────────────────────────────────────────

export function BrainList({ brains, selectedBrainId, onSelect }: BrainListProps) {
  return (
    <div className="flex flex-col gap-0" data-testid="brain-list">
      <div className="px-4 py-3 border-b border-border">
        <h2 className="text-sm font-semibold text-foreground">Brain Registry</h2>
        <p className="text-xs text-muted-foreground mt-0.5">{brains.length} brains</p>
      </div>

      <ul className="flex flex-col">
        {brains.map((brain) => (
          <BrainListItem
            key={brain.id}
            brain={brain}
            isSelected={brain.id === selectedBrainId}
            onSelect={onSelect}
          />
        ))}
      </ul>
    </div>
  )
}

// ─── BrainListItem ─────────────────────────────────────────────────────────────

interface BrainListItemProps {
  brain: Brain
  isSelected: boolean
  onSelect: (brainId: string) => void
}

function BrainListItem({ brain, isSelected, onSelect }: BrainListItemProps) {
  // Live status from brainStore — reactive to WS events
  const brainState = useBrainState(brain.id)
  const status = brainState?.status ?? 'idle'

  // Latest WS event for this brain across all active traces
  const allEvents = useWsEventsStore((s) => s.events)
  const latestEvent = getLatestEventForBrain(allEvents, brain.id)

  return (
    <li>
      <button
        type="button"
        onClick={() => onSelect(brain.id)}
        data-testid={`brain-list-item-${brain.id}`}
        className={cn(
          'w-full text-left px-4 py-3 transition-colors',
          'border-b border-border/50 last:border-b-0',
          'hover:bg-muted/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
          isSelected && 'bg-primary/10 border-l-2 border-l-primary',
        )}
        aria-pressed={isSelected}
        aria-label={`Select ${brain.name}`}
      >
        {/* Brain name + status indicator */}
        <div className="flex items-center justify-between gap-2">
          <span
            className={cn(
              'text-xs font-medium truncate',
              isSelected ? 'text-primary' : 'text-foreground',
            )}
          >
            {brain.name}
          </span>
          <NodeStatusIndicator status={status} className="flex-shrink-0" />
        </div>

        {/* Niche tag */}
        <span className="text-[10px] text-muted-foreground mt-0.5 block">
          {brain.niche}
        </span>

        {/* Latest WS event — shown only when an event is present */}
        {latestEvent && (
          <div
            className="mt-1 text-[10px] font-mono text-muted-foreground truncate"
            data-testid={`brain-event-latest-${brain.id}`}
          >
            {latestEvent.status}{' '}
            <span className="text-gray-500">
              {new Date(latestEvent.timestamp).toLocaleTimeString()}
            </span>
          </div>
        )}
      </button>
    </li>
  )
}

// ─── Helpers ───────────────────────────────────────────────────────────────────

/**
 * getLatestEventForBrain — scan all traces for the most recent event for a brain.
 *
 * O(traces × events-per-trace). Fine for 7 brains and <50 events per trace.
 */
function getLatestEventForBrain(
  events: Map<string, import('@/stores/wsEventsStore').BrainStateEvent[]>,
  brainId: string,
): import('@/stores/wsEventsStore').BrainStateEvent | null {
  let latest: import('@/stores/wsEventsStore').BrainStateEvent | null = null

  for (const [, traceEvents] of events.entries()) {
    for (const evt of traceEvents) {
      if (evt.brain_id === brainId) {
        if (!latest || evt.timestamp > latest.timestamp) {
          latest = evt
        }
      }
    }
  }

  return latest
}
