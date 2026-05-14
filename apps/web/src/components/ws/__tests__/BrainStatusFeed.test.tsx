/**
 * Tests for BrainStatusFeed — C2.08
 *
 * Verifies model and provider fields are displayed when present in BrainStateEvent.
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { BrainStatusFeed } from '../BrainStatusFeed'
import { useWsEventsStore } from '@/stores/wsEventsStore'

// Mock useWebSocket so BrainStatusFeed doesn't try to create real WS connections
vi.mock('@/hooks/useWebSocket', () => ({
  useWebSocket: vi.fn(() => ({
    status: 'disconnected',
    reconnectCount: 0,
  })),
}))

beforeEach(() => {
  useWsEventsStore.setState({ events: new Map() })
})

describe('BrainStatusFeed — C2.08 model and provider display', () => {
  it('shows model field when event includes model', () => {
    const traceId = 'trace-model-test'
    useWsEventsStore.setState({
      events: new Map([
        [
          traceId,
          [
            {
              trace_id: traceId,
              brain_id: '1',
              status: 'dispatched',
              timestamp: new Date().toISOString(),
              model: 'anthropic:claude-opus-4-6',
              provider: 'anthropic',
            },
          ],
        ],
      ]),
    })

    render(<BrainStatusFeed />)

    const modelEl = screen.getByTestId('brain-event-model')
    expect(modelEl).toBeInTheDocument()
    expect(modelEl).toHaveTextContent('anthropic:claude-opus-4-6')
  })

  it('shows z_ai model correctly', () => {
    const traceId = 'trace-zai-test'
    useWsEventsStore.setState({
      events: new Map([
        [
          traceId,
          [
            {
              trace_id: traceId,
              brain_id: '7',
              status: 'running',
              timestamp: new Date().toISOString(),
              model: 'z_ai:claude-3-7-sonnet',
              provider: 'z_ai',
            },
          ],
        ],
      ]),
    })

    render(<BrainStatusFeed />)

    const modelEl = screen.getByTestId('brain-event-model')
    expect(modelEl).toHaveTextContent('z_ai:claude-3-7-sonnet')
  })

  it('shows no model element when event has no model', () => {
    const traceId = 'trace-no-model'
    useWsEventsStore.setState({
      events: new Map([
        [
          traceId,
          [
            {
              trace_id: traceId,
              brain_id: '3',
              status: 'completed',
              timestamp: new Date().toISOString(),
              // no model or provider
            },
          ],
        ],
      ]),
    })

    render(<BrainStatusFeed />)

    expect(screen.queryByTestId('brain-event-model')).not.toBeInTheDocument()
    expect(screen.queryByTestId('brain-event-provider')).not.toBeInTheDocument()
  })

  it('shows provider when only provider is present (no model)', () => {
    const traceId = 'trace-provider-only'
    useWsEventsStore.setState({
      events: new Map([
        [
          traceId,
          [
            {
              trace_id: traceId,
              brain_id: '2',
              status: 'dispatched',
              timestamp: new Date().toISOString(),
              provider: 'openrouter',
              // no model
            },
          ],
        ],
      ]),
    })

    render(<BrainStatusFeed />)

    const providerEl = screen.getByTestId('brain-event-provider')
    expect(providerEl).toBeInTheDocument()
    expect(providerEl).toHaveTextContent('openrouter')
  })
})
