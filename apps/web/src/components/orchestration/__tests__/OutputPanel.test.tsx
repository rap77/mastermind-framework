/**
 * OutputPanel.test.tsx — D1.10
 *
 * Tests that OutputPanel:
 * 1. Shows empty state when no brain is selected
 * 2. Renders structured brain metadata when a brain is selected
 * 3. Renders Brain #7 quality score from WS events
 * 4. Renders trace timeline events
 */

import { render, screen, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { Brain } from '@/lib/api'

// ─── Mock NodeStatusIndicator — must be top-level ─────────────────────────────

vi.mock('@/components/nexus/NodeStatusIndicator', () => ({
  NodeStatusIndicator: ({ status }: { status: string }) => (
    <span data-testid="node-status-indicator" data-status={status}>
      {status}
    </span>
  ),
}))

// Import stores and component AFTER mocks
import { useWsEventsStore } from '@/stores/wsEventsStore'
import { useBrainStore } from '@/stores/brainStore'
import { OutputPanel } from '../OutputPanel'

// ─── Fixtures ─────────────────────────────────────────────────────────────────

const BRAIN_01: Brain = {
  id: 'brain-01',
  name: 'Product Strategy',
  niche: 'software-development',
  status: 'idle',
  uptime: 3600,
  last_called_at: '2026-05-13T10:00:00.000Z',
  description: 'Defines product strategy and roadmap',
}

// ─── Tests ─────────────────────────────────────────────────────────────────────

describe('OutputPanel (D1.10)', () => {
  beforeEach(() => {
    useWsEventsStore.getState().clearAll()
    useBrainStore.setState({ brains: new Map(), _queue: [], _rafId: null })
  })

  describe('Empty state', () => {
    it('shows empty state message when no brain is selected', () => {
      render(<OutputPanel selectedBrain={null} />)

      expect(screen.getByTestId('output-panel-empty')).toBeInTheDocument()
      expect(screen.getByText(/select a brain/i)).toBeInTheDocument()
    })
  })

  describe('Structured output', () => {
    it('renders brain metadata panel when a brain is selected', () => {
      render(<OutputPanel selectedBrain={BRAIN_01} />)

      expect(screen.getByTestId('output-panel')).toBeInTheDocument()
      expect(screen.getByTestId('output-brain-metadata')).toBeInTheDocument()
    })

    it('displays brain name and niche in header', () => {
      render(<OutputPanel selectedBrain={BRAIN_01} />)

      expect(screen.getByText('Product Strategy')).toBeInTheDocument()
      expect(screen.getByText('software-development')).toBeInTheDocument()
    })

    it('displays brain ID', () => {
      render(<OutputPanel selectedBrain={BRAIN_01} />)

      expect(screen.getByText('brain-01')).toBeInTheDocument()
    })

    it('displays uptime when > 0', () => {
      render(<OutputPanel selectedBrain={BRAIN_01} />)

      expect(screen.getByText('3600s')).toBeInTheDocument()
    })

    it('displays description when present', () => {
      render(<OutputPanel selectedBrain={BRAIN_01} />)

      expect(screen.getByText('Defines product strategy and roadmap')).toBeInTheDocument()
    })

    it('renders live status from brainStore', () => {
      // Put brain-01 in active state
      useBrainStore.setState((state) => ({
        ...state,
        brains: new Map([
          ['brain-01', { id: 'brain-01', status: 'active', lastUpdated: Date.now() }],
        ]),
      }))

      render(<OutputPanel selectedBrain={BRAIN_01} />)

      const indicator = screen.getByTestId('node-status-indicator')
      expect(indicator).toHaveAttribute('data-status', 'active')
    })
  })

  describe('Brain #7 quality score', () => {
    it('shows "no evaluation" when no Brain #7 events', () => {
      render(<OutputPanel selectedBrain={BRAIN_01} />)

      expect(screen.getByTestId('output-brain7-score')).toBeInTheDocument()
      expect(screen.getByText(/no evaluation score available/i)).toBeInTheDocument()
    })

    it('renders quality score when Brain #7 completed event with score is present', () => {
      act(() => {
        const store = useWsEventsStore.getState()
        // brain-01 in this trace
        store.appendEvent({
          trace_id: 'trace-xyz',
          brain_id: 'brain-01',
          status: 'completed',
          timestamp: '2026-05-13T10:00:01.000Z',
        })
        // Brain #7 evaluated with quality_score:0.87
        store.appendEvent({
          trace_id: 'trace-xyz',
          brain_id: 'brain-07',
          status: 'completed',
          timestamp: '2026-05-13T10:00:02.000Z',
          model: 'quality_score:0.87',
        })
      })

      render(<OutputPanel selectedBrain={BRAIN_01} />)

      // Score section should show 87
      expect(screen.getByTestId('output-brain7-score')).toBeInTheDocument()
      expect(screen.getByText(/87/)).toBeInTheDocument()
    })
  })

  describe('Trace timeline', () => {
    it('shows empty timeline message when no events', () => {
      render(<OutputPanel selectedBrain={BRAIN_01} />)

      expect(screen.getByTestId('output-timeline-empty')).toBeInTheDocument()
    })

    it('renders timeline events for the selected brain', () => {
      act(() => {
        const store = useWsEventsStore.getState()
        store.appendEvent({
          trace_id: 'trace-abc',
          brain_id: 'brain-01',
          status: 'dispatched',
          timestamp: '2026-05-13T10:00:00.000Z',
        })
        store.appendEvent({
          trace_id: 'trace-abc',
          brain_id: 'brain-01',
          status: 'running',
          timestamp: '2026-05-13T10:00:01.000Z',
        })
        store.appendEvent({
          trace_id: 'trace-abc',
          brain_id: 'brain-01',
          status: 'completed',
          timestamp: '2026-05-13T10:00:02.000Z',
        })
      })

      render(<OutputPanel selectedBrain={BRAIN_01} />)

      expect(screen.getByTestId('output-timeline-list')).toBeInTheDocument()
      expect(screen.getAllByTestId('timeline-event-dispatched').length).toBeGreaterThan(0)
      expect(screen.getAllByTestId('timeline-event-running').length).toBeGreaterThan(0)
      expect(screen.getAllByTestId('timeline-event-completed').length).toBeGreaterThan(0)
    })

    it('does NOT show events for other brains in the timeline', () => {
      act(() => {
        const store = useWsEventsStore.getState()
        // brain-02 event — should NOT show in brain-01 output panel
        store.appendEvent({
          trace_id: 'trace-abc',
          brain_id: 'brain-02',
          status: 'running',
          timestamp: '2026-05-13T10:00:01.000Z',
        })
      })

      render(<OutputPanel selectedBrain={BRAIN_01} />)

      // Timeline should still be empty for brain-01
      expect(screen.getByTestId('output-timeline-empty')).toBeInTheDocument()
    })
  })
})
