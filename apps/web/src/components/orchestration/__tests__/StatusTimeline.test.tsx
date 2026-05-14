/**
 * StatusTimeline.test.tsx — D2.06
 *
 * Component test: StatusTimeline renders a list of mocked events in
 * chronological order with correct icons per status.
 */

import { render, screen, within } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { BrainStateEvent } from '@/stores/wsEventsStore'
import { StatusTimeline } from '../StatusTimeline'

// lucide-react mock — simple SVG stubs with accessible labels
vi.mock('lucide-react', () => ({
  CheckCircle: ({ className, 'aria-label': label, 'data-testid': testId }: { className?: string; 'aria-label'?: string; 'data-testid'?: string }) => (
    <svg className={className} aria-label={label} data-testid={testId} />
  ),
  XCircle: ({ className, 'aria-label': label, 'data-testid': testId }: { className?: string; 'aria-label'?: string; 'data-testid'?: string }) => (
    <svg className={className} aria-label={label} data-testid={testId} />
  ),
  Loader2: ({ className, 'aria-label': label, 'data-testid': testId }: { className?: string; 'aria-label'?: string; 'data-testid'?: string }) => (
    <svg className={className} aria-label={label} data-testid={testId} />
  ),
  Circle: ({ className, 'aria-label': label, 'data-testid': testId }: { className?: string; 'aria-label'?: string; 'data-testid'?: string }) => (
    <svg className={className} aria-label={label} data-testid={testId} />
  ),
}))

// ─── Fixtures ─────────────────────────────────────────────────────────────────

const MOCK_EVENTS: BrainStateEvent[] = [
  {
    trace_id: 'trace-001',
    brain_id: 'brain-01',
    status: 'dispatched',
    timestamp: '2026-05-14T10:00:00.000Z',
  },
  {
    trace_id: 'trace-001',
    brain_id: 'brain-01',
    status: 'running',
    timestamp: '2026-05-14T10:00:01.000Z',
  },
  {
    trace_id: 'trace-001',
    brain_id: 'brain-01',
    status: 'completed',
    timestamp: '2026-05-14T10:00:05.000Z',
  },
  {
    trace_id: 'trace-001',
    brain_id: 'brain-02',
    status: 'failed',
    timestamp: '2026-05-14T10:00:06.000Z',
  },
]

// ─── Tests ─────────────────────────────────────────────────────────────────────

describe('StatusTimeline (D2.06)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the timeline container', () => {
    render(<StatusTimeline events={[]} />)
    expect(screen.getByTestId('status-timeline')).toBeInTheDocument()
  })

  it('shows empty state message when no events', () => {
    render(<StatusTimeline events={[]} />)
    expect(screen.getByText(/no events yet/i)).toBeInTheDocument()
  })

  it('renders one timeline item per event', () => {
    render(<StatusTimeline events={MOCK_EVENTS} />)
    const items = screen.getAllByTestId('timeline-item')
    expect(items).toHaveLength(4)
  })

  it('renders events in the order provided (chronological when passed sorted events)', () => {
    // StatusTimeline is a pure presentational component — it renders the array
    // in the order it receives it. Sorting is the hook's (useOrchestrationStream)
    // responsibility. Here we pass events already in chronological order.
    render(<StatusTimeline events={MOCK_EVENTS} />)
    const items = screen.getAllByTestId('timeline-item')

    // First item should be the earliest event (dispatched)
    expect(items[0]).toHaveAttribute('data-status', 'dispatched')
    // Last item should be the latest event (failed)
    expect(items[3]).toHaveAttribute('data-status', 'failed')
  })

  it('renders correct brain_id labels', () => {
    render(<StatusTimeline events={MOCK_EVENTS} />)
    const brainOneItems = screen
      .getAllByTestId('timeline-item')
      .filter((el) => el.getAttribute('data-brain-id') === 'brain-01')
    expect(brainOneItems).toHaveLength(3)
  })

  it('renders CheckCircle icon for completed status', () => {
    const event: BrainStateEvent = {
      trace_id: 't1',
      brain_id: 'b1',
      status: 'completed',
      timestamp: '2026-05-14T10:00:00.000Z',
    }
    render(<StatusTimeline events={[event]} />)
    expect(screen.getByTestId('icon-completed')).toBeInTheDocument()
  })

  it('renders Loader2 icon for running status', () => {
    const event: BrainStateEvent = {
      trace_id: 't1',
      brain_id: 'b1',
      status: 'running',
      timestamp: '2026-05-14T10:00:00.000Z',
    }
    render(<StatusTimeline events={[event]} />)
    expect(screen.getByTestId('icon-running')).toBeInTheDocument()
  })

  it('renders XCircle icon for failed status', () => {
    const event: BrainStateEvent = {
      trace_id: 't1',
      brain_id: 'b1',
      status: 'failed',
      timestamp: '2026-05-14T10:00:00.000Z',
    }
    render(<StatusTimeline events={[event]} />)
    expect(screen.getByTestId('icon-failed')).toBeInTheDocument()
  })

  it('renders Circle icon for dispatched status', () => {
    const event: BrainStateEvent = {
      trace_id: 't1',
      brain_id: 'b1',
      status: 'dispatched',
      timestamp: '2026-05-14T10:00:00.000Z',
    }
    render(<StatusTimeline events={[event]} />)
    expect(screen.getByTestId('icon-dispatched')).toBeInTheDocument()
  })

  it('shows event count in header when events exist', () => {
    render(<StatusTimeline events={MOCK_EVENTS} />)
    expect(screen.getByText('4 events')).toBeInTheDocument()
  })

  it('renders custom label prop', () => {
    render(<StatusTimeline events={[]} label="brain-01 activity" />)
    expect(screen.getByText('brain-01 activity')).toBeInTheDocument()
  })

  it('renders scroll container', () => {
    render(<StatusTimeline events={MOCK_EVENTS} />)
    expect(screen.getByTestId('timeline-scroll-container')).toBeInTheDocument()
  })

  it('all items carry data-brain-id and data-status attributes', () => {
    const events: BrainStateEvent[] = [
      {
        trace_id: 't1',
        brain_id: 'brain-03',
        status: 'running',
        timestamp: '2026-05-14T10:00:00.000Z',
      },
    ]
    render(<StatusTimeline events={events} />)
    const item = screen.getByTestId('timeline-item')
    expect(item).toHaveAttribute('data-brain-id', 'brain-03')
    expect(item).toHaveAttribute('data-status', 'running')
  })

  it('renders timeline items inside an accessible list', () => {
    render(<StatusTimeline events={MOCK_EVENTS} />)
    const list = screen.getByRole('list', { name: /brain activity timeline/i })
    const items = within(list).getAllByRole('listitem')
    expect(items).toHaveLength(4)
  })
})
