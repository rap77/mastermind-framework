/**
 * StatusTimelineInteraction.test.tsx — D2.08
 *
 * Interaction test: a WS event arriving in the store causes StatusTimeline
 * (rendered via useOrchestrationStream) to add the new event item within
 * the 500ms budget.
 *
 * Approach:
 * - Render a composed component that uses useOrchestrationStream and passes
 *   the result to StatusTimeline (mirrors the actual wiring in OrchestrationCanvas).
 * - Directly call wsEventsStore.appendEvent() to simulate a WS message arriving.
 * - Assert the new item appears in the DOM within the 500ms budget.
 */

import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import type { BrainStateEvent } from '@/stores/wsEventsStore'
import { useWsEventsStore } from '@/stores/wsEventsStore'
import { useOrchestrationStream } from '@/hooks/useOrchestrationStream'
import { StatusTimeline } from '../StatusTimeline'
import { act } from 'react'

// lucide-react mock
vi.mock('lucide-react', () => ({
  CheckCircle: ({ 'data-testid': testId, 'aria-label': label, className }: { 'data-testid'?: string; 'aria-label'?: string; className?: string }) => (
    <svg data-testid={testId} aria-label={label} className={className} />
  ),
  XCircle: ({ 'data-testid': testId, 'aria-label': label, className }: { 'data-testid'?: string; 'aria-label'?: string; className?: string }) => (
    <svg data-testid={testId} aria-label={label} className={className} />
  ),
  Loader2: ({ 'data-testid': testId, 'aria-label': label, className }: { 'data-testid'?: string; 'aria-label'?: string; className?: string }) => (
    <svg data-testid={testId} aria-label={label} className={className} />
  ),
  Circle: ({ 'data-testid': testId, 'aria-label': label, className }: { 'data-testid'?: string; 'aria-label'?: string; className?: string }) => (
    <svg data-testid={testId} aria-label={label} className={className} />
  ),
}))

// ─── Composed component (mirrors OrchestrationCanvas wiring) ──────────────────

function TimelineWithStream({ brainId }: { brainId?: string | null }) {
  const { events } = useOrchestrationStream({ brainId })
  return <StatusTimeline events={events} />
}

// ─── Tests ─────────────────────────────────────────────────────────────────────

describe('StatusTimeline interaction (D2.08)', () => {
  beforeEach(() => {
    useWsEventsStore.getState().clearAll()
    vi.clearAllMocks()
  })

  it('adds a new timeline item when a WS event arrives (within 500ms)', async () => {
    render(<TimelineWithStream />)

    // Initially no items
    expect(screen.queryByTestId('timeline-item')).not.toBeInTheDocument()

    const startMs = Date.now()

    // Simulate WS event arriving (what BrainStatusFeed does on message)
    const event: BrainStateEvent = {
      trace_id: 'trace-ws-test',
      brain_id: 'brain-04',
      status: 'dispatched',
      timestamp: new Date().toISOString(),
    }

    act(() => {
      useWsEventsStore.getState().appendEvent(event)
    })

    // Timeline must show the new item within 500ms
    await waitFor(
      () => {
        expect(screen.getByTestId('timeline-item')).toBeInTheDocument()
      },
      { timeout: 500 },
    )

    const elapsed = Date.now() - startMs
    expect(elapsed).toBeLessThan(500)
  })

  it('accumulates multiple events sequentially', async () => {
    render(<TimelineWithStream />)

    const events: BrainStateEvent[] = [
      { trace_id: 'trace-001', brain_id: 'brain-01', status: 'dispatched', timestamp: '2026-05-14T10:00:01.000Z' },
      { trace_id: 'trace-001', brain_id: 'brain-01', status: 'running', timestamp: '2026-05-14T10:00:02.000Z' },
      { trace_id: 'trace-001', brain_id: 'brain-01', status: 'completed', timestamp: '2026-05-14T10:00:03.000Z' },
    ]

    for (const ev of events) {
      act(() => {
        useWsEventsStore.getState().appendEvent(ev)
      })
    }

    await waitFor(
      () => {
        expect(screen.getAllByTestId('timeline-item')).toHaveLength(3)
      },
      { timeout: 500 },
    )
  })

  it('filters by brainId — only matching events appear', async () => {
    render(<TimelineWithStream brainId="brain-02" />)

    act(() => {
      useWsEventsStore.getState().appendEvent({
        trace_id: 'trace-001',
        brain_id: 'brain-01',
        status: 'running',
        timestamp: new Date().toISOString(),
      })
      useWsEventsStore.getState().appendEvent({
        trace_id: 'trace-001',
        brain_id: 'brain-02',
        status: 'dispatched',
        timestamp: new Date().toISOString(),
      })
    })

    await waitFor(
      () => {
        const items = screen.getAllByTestId('timeline-item')
        expect(items).toHaveLength(1)
        expect(items[0]).toHaveAttribute('data-brain-id', 'brain-02')
      },
      { timeout: 500 },
    )
  })

  it('shows empty state before any events and activity after event arrives', async () => {
    render(<TimelineWithStream />)

    // Empty state visible initially
    expect(screen.getByText(/no events yet/i)).toBeInTheDocument()

    act(() => {
      useWsEventsStore.getState().appendEvent({
        trace_id: 'trace-001',
        brain_id: 'brain-05',
        status: 'running',
        timestamp: new Date().toISOString(),
      })
    })

    await waitFor(
      () => {
        expect(screen.queryByText(/no events yet/i)).not.toBeInTheDocument()
        expect(screen.getByTestId('timeline-item')).toBeInTheDocument()
      },
      { timeout: 500 },
    )
  })
})
