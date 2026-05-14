'use client'

/**
 * OutputPanel — Right column of the Orchestration Canvas.
 *
 * Shows for the selected brain:
 * - Structured output (description, status, niche, uptime)
 * - Brain #7 quality_score (from wsEventsStore events for this brain)
 * - Trace timeline: ordered list of WS events across all traces
 *
 * Reactive to wsEventsStore — re-renders when new events arrive.
 * No WS connection here — BrainStatusFeed (in WSBrainBridge) does that.
 */

import type { Brain } from '@/lib/api'
import { useBrainState } from '@/stores/brainStore'
import { useWsEventsStore, type BrainStateEvent } from '@/stores/wsEventsStore'
import { NodeStatusIndicator } from '@/components/nexus/NodeStatusIndicator'

// ─── Types ─────────────────────────────────────────────────────────────────────

interface OutputPanelProps {
  selectedBrain: Brain | null
}

// ─── Status color helpers ───────────────────────────────────────────────────────

const EVENT_STATUS_COLORS: Record<BrainStateEvent['status'], string> = {
  dispatched: 'text-blue-400',
  running: 'text-yellow-400',
  completed: 'text-green-400',
  failed: 'text-red-400',
}

const EVENT_STATUS_ICONS: Record<BrainStateEvent['status'], string> = {
  dispatched: '→',
  running: '⟳',
  completed: '✓',
  failed: '✗',
}

// ─── Component ─────────────────────────────────────────────────────────────────

export function OutputPanel({ selectedBrain }: OutputPanelProps) {
  if (!selectedBrain) {
    return (
      <div
        className="flex h-full items-center justify-center p-6"
        data-testid="output-panel-empty"
      >
        <p className="text-sm text-muted-foreground text-center">
          Select a brain to view output
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-0 h-full" data-testid="output-panel">
      {/* Header */}
      <div className="px-4 py-3 border-b border-border flex-shrink-0">
        <h2 className="text-sm font-semibold text-foreground truncate">
          {selectedBrain.name}
        </h2>
        <p className="text-xs text-muted-foreground mt-0.5">{selectedBrain.niche}</p>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-6">
        <BrainMetadata brain={selectedBrain} />
        <Brain7ScoreSection brainId={selectedBrain.id} />
        <TraceTimeline brainId={selectedBrain.id} />
      </div>
    </div>
  )
}

// ─── BrainMetadata ─────────────────────────────────────────────────────────────

function BrainMetadata({ brain }: { brain: Brain }) {
  const brainState = useBrainState(brain.id)
  const liveStatus = brainState?.status ?? 'idle'

  return (
    <section aria-labelledby="output-metadata-title">
      <h3
        id="output-metadata-title"
        className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2"
      >
        Brain Info
      </h3>
      <div
        className="rounded-md border border-border bg-muted/20 p-3 flex flex-col gap-2"
        data-testid="output-brain-metadata"
      >
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Status</span>
          <NodeStatusIndicator status={liveStatus} />
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">ID</span>
          <span className="text-xs font-mono text-foreground">{brain.id}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Uptime</span>
          <span className="text-xs font-mono text-foreground">
            {brain.uptime > 0 ? `${brain.uptime}s` : '—'}
          </span>
        </div>
        {brain.last_called_at && (
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Last called</span>
            <span className="text-xs font-mono text-foreground">
              {new Date(brain.last_called_at).toLocaleTimeString()}
            </span>
          </div>
        )}
        {brain.description && (
          <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
            {brain.description}
          </p>
        )}
      </div>
    </section>
  )
}

// ─── Brain7ScoreSection ────────────────────────────────────────────────────────

/**
 * Brain7ScoreSection — shows quality score from Brain #7 evaluation.
 *
 * Brain #7 (niche=universal) emits WS events with `quality_score` in the model field.
 * Convention: model field carries "quality_score:0.87" when Brain #7 evaluates.
 * Falls back to "No score available" when Brain #7 hasn't evaluated yet.
 */
function Brain7ScoreSection({ brainId }: { brainId: string }) {
  const allEvents = useWsEventsStore((s) => s.events)

  // Find the latest Brain #7 completed event for any trace that involves this brain
  let qualityScore: number | null = null

  for (const [, traceEvents] of allEvents.entries()) {
    // Check if this trace involves our selected brain
    const hasBrain = traceEvents.some((e) => e.brain_id === brainId)
    if (!hasBrain) continue

    // Find Brain #7 completed events in this trace
    const brain7Events = traceEvents.filter(
      (e) => e.brain_id === 'brain-07' && e.status === 'completed' && e.model,
    )

    for (const evt of brain7Events) {
      const match = evt.model?.match(/quality_score:([\d.]+)/)
      if (match) {
        qualityScore = parseFloat(match[1])
      }
    }
  }

  return (
    <section aria-labelledby="output-brain7-title">
      <h3
        id="output-brain7-title"
        className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2"
      >
        Brain #7 Quality Score
      </h3>
      <div
        className="rounded-md border border-border bg-muted/20 p-3"
        data-testid="output-brain7-score"
      >
        {qualityScore !== null ? (
          <div className="flex items-center gap-3">
            <ScoreBar score={qualityScore} />
            <span className="text-lg font-bold tabular-nums text-foreground">
              {(qualityScore * 100).toFixed(0)}
              <span className="text-sm font-normal text-muted-foreground">/100</span>
            </span>
          </div>
        ) : (
          <p className="text-xs text-muted-foreground italic">
            No evaluation score available
          </p>
        )}
      </div>
    </section>
  )
}

function ScoreBar({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  const color =
    pct >= 80 ? 'bg-green-500' : pct >= 50 ? 'bg-yellow-500' : 'bg-red-500'

  return (
    <div
      className="flex-1 h-2 rounded-full bg-muted overflow-hidden"
      role="meter"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Quality score: ${pct}%`}
    >
      <div
        className={`h-full rounded-full transition-all duration-500 ${color}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}

// ─── TraceTimeline ─────────────────────────────────────────────────────────────

/**
 * TraceTimeline — ordered list of WS events involving the selected brain.
 *
 * Shows events from ALL traces that include this brain_id, newest first.
 */
function TraceTimeline({ brainId }: { brainId: string }) {
  const allEvents = useWsEventsStore((s) => s.events)

  const brainEvents: (BrainStateEvent & { traceId: string })[] = []

  for (const [traceId, traceEvents] of allEvents.entries()) {
    for (const evt of traceEvents) {
      if (evt.brain_id === brainId) {
        brainEvents.push({ ...evt, traceId })
      }
    }
  }

  // Newest first
  brainEvents.sort((a, b) => b.timestamp.localeCompare(a.timestamp))

  return (
    <section aria-labelledby="output-timeline-title">
      <h3
        id="output-timeline-title"
        className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2"
      >
        Trace Timeline
      </h3>

      {brainEvents.length === 0 ? (
        <p
          className="text-xs text-muted-foreground italic"
          data-testid="output-timeline-empty"
        >
          No events recorded yet
        </p>
      ) : (
        <ul
          className="flex flex-col gap-1"
          data-testid="output-timeline-list"
        >
          {brainEvents.map((evt, idx) => (
            <li
              key={`${evt.traceId}-${evt.brain_id}-${evt.status}-${idx}`}
              className="flex items-center gap-2 text-xs font-mono py-0.5"
              data-testid={`timeline-event-${evt.status}`}
            >
              <span className={EVENT_STATUS_COLORS[evt.status]}>
                {EVENT_STATUS_ICONS[evt.status]}
              </span>
              <span className={EVENT_STATUS_COLORS[evt.status]}>{evt.status}</span>
              <span className="text-gray-500 truncate flex-1" title={evt.traceId}>
                {evt.traceId.slice(0, 8)}…
              </span>
              <span className="text-gray-600 flex-shrink-0">
                {new Date(evt.timestamp).toLocaleTimeString()}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
