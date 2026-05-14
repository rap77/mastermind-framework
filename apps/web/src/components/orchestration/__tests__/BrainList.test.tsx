/**
 * BrainList.test.tsx — D1.09
 *
 * Tests that BrainList:
 * 1. Renders all brains from the registry
 * 2. Shows the selected brain highlighted
 * 3. Reflects live WS event state from wsEventsStore
 * 4. Calls onSelect when a brain item is clicked
 */

import { render, screen, fireEvent, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { Brain } from '@/lib/api'

// ─── Mock NodeStatusIndicator ─────────────────────────────────────────────────
// Must be top-level before importing the component under test

vi.mock('@/components/nexus/NodeStatusIndicator', () => ({
  NodeStatusIndicator: ({ status }: { status: string }) => (
    <span data-testid="node-status-indicator" data-status={status}>
      {status}
    </span>
  ),
}))

// Import stores and component AFTER mocks are registered
import { useWsEventsStore } from '@/stores/wsEventsStore'
import { useBrainStore } from '@/stores/brainStore'
import { BrainList } from '../BrainList'

// ─── Fixtures ─────────────────────────────────────────────────────────────────

const MOCK_BRAINS: Brain[] = [
  {
    id: 'brain-01',
    name: 'Product Strategy',
    niche: 'software-development',
    status: 'idle',
    uptime: 0,
    last_called_at: null,
  },
  {
    id: 'brain-02',
    name: 'UX Research',
    niche: 'software-development',
    status: 'idle',
    uptime: 0,
    last_called_at: null,
  },
  {
    id: 'brain-07',
    name: 'Growth/Data',
    niche: 'universal',
    status: 'idle',
    uptime: 0,
    last_called_at: null,
  },
]

// ─── Tests ─────────────────────────────────────────────────────────────────────

describe('BrainList (D1.09)', () => {
  beforeEach(() => {
    // Reset stores between tests
    useWsEventsStore.getState().clearAll()
    useBrainStore.setState({ brains: new Map(), _queue: [], _rafId: null })
  })

  it('renders all brains from the registry', () => {
    render(
      <BrainList brains={MOCK_BRAINS} selectedBrainId={null} onSelect={vi.fn()} />,
    )

    expect(screen.getByTestId('brain-list')).toBeInTheDocument()
    expect(screen.getByTestId('brain-list-item-brain-01')).toBeInTheDocument()
    expect(screen.getByTestId('brain-list-item-brain-02')).toBeInTheDocument()
    expect(screen.getByTestId('brain-list-item-brain-07')).toBeInTheDocument()

    expect(screen.getByText('Product Strategy')).toBeInTheDocument()
    expect(screen.getByText('UX Research')).toBeInTheDocument()
    expect(screen.getByText('Growth/Data')).toBeInTheDocument()
  })

  it('shows brain count in header', () => {
    render(
      <BrainList brains={MOCK_BRAINS} selectedBrainId={null} onSelect={vi.fn()} />,
    )

    expect(screen.getByText('3 brains')).toBeInTheDocument()
  })

  it('calls onSelect when a brain item is clicked', () => {
    const onSelect = vi.fn()

    render(
      <BrainList brains={MOCK_BRAINS} selectedBrainId={null} onSelect={onSelect} />,
    )

    fireEvent.click(screen.getByTestId('brain-list-item-brain-01'))
    expect(onSelect).toHaveBeenCalledWith('brain-01')
  })

  it('marks selected brain with aria-pressed=true', () => {
    render(
      <BrainList
        brains={MOCK_BRAINS}
        selectedBrainId="brain-01"
        onSelect={vi.fn()}
      />,
    )

    const selectedItem = screen.getByTestId('brain-list-item-brain-01')
    expect(selectedItem).toHaveAttribute('aria-pressed', 'true')

    const nonSelected = screen.getByTestId('brain-list-item-brain-02')
    expect(nonSelected).toHaveAttribute('aria-pressed', 'false')
  })

  it('updates latest event display when WS event arrives', async () => {
    render(
      <BrainList brains={MOCK_BRAINS} selectedBrainId={null} onSelect={vi.fn()} />,
    )

    // No events yet — no latest event shown
    expect(screen.queryByTestId('brain-event-latest-brain-01')).not.toBeInTheDocument()

    // Dispatch a WS event for brain-01
    act(() => {
      useWsEventsStore.getState().appendEvent({
        trace_id: 'trace-abc',
        brain_id: 'brain-01',
        status: 'running',
        timestamp: new Date().toISOString(),
      })
    })

    // Latest event should now appear under brain-01
    expect(screen.getByTestId('brain-event-latest-brain-01')).toBeInTheDocument()
    expect(screen.getByTestId('brain-event-latest-brain-01')).toHaveTextContent('running')
  })

  it('shows status from brainStore for each brain', () => {
    // Put brain-01 in active state before render
    useBrainStore.setState((state) => ({
      ...state,
      brains: new Map([['brain-01', { id: 'brain-01', status: 'active', lastUpdated: Date.now() }]]),
    }))

    render(
      <BrainList brains={MOCK_BRAINS} selectedBrainId={null} onSelect={vi.fn()} />,
    )

    // NodeStatusIndicator for brain-01 should reflect active status
    const indicators = screen.getAllByTestId('node-status-indicator')
    const activeIndicator = indicators.find(
      (el) => el.getAttribute('data-status') === 'active',
    )
    expect(activeIndicator).toBeDefined()
  })
})
