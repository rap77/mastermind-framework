/**
 * LiveLogPanel Component Tests
 *
 * **Purpose:** Verify virtual log viewer with WS integration and filtering
 * **Context:** Phase 08-03 — Task 8 (LiveLogPanel tests)
 */

import { render, screen, fireEvent, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { LiveLogPanel } from '../LiveLogPanel'
import { useWSStore } from '@/stores/wsStore'
import { useLogFilterStore } from '@/stores/logFilterStore'
import type { LogLine } from '@/lib/log-parser'

// ─── Mocks ────────────────────────────────────────────────────────────────────

// Mock react-virtuoso to avoid complex virtualization in tests
vi.mock('react-virtuoso', () => ({
  Virtuoso: ({
    data,
    itemContent,
    'aria-label': ariaLabel,
  }: {
    data: LogLine[]
    itemContent: (index: number, item: LogLine) => React.ReactNode
    'aria-label'?: string
  }) => (
    <div role="list" aria-label={ariaLabel ?? 'log list'}>
      {data.map((item, index) => (
        <div key={item.id} role="listitem">
          {itemContent(index, item)}
        </div>
      ))}
    </div>
  ),
}))

// ─── WS Store mock setup ───────────────────────────────────────────────────────

type Listener = (data: unknown) => void

let wsListeners: Map<string, Set<Listener>> = new Map()

const mockSubscribe = vi.fn((event: string, listener: Listener) => {
  if (!wsListeners.has(event)) wsListeners.set(event, new Set())
  wsListeners.get(event)!.add(listener)
  return () => wsListeners.get(event)?.delete(listener)
})

function emitWSEvent(event: string, data: unknown) {
  wsListeners.get(event)?.forEach((fn) => fn(data))
}

beforeEach(() => {
  wsListeners = new Map()
  mockSubscribe.mockClear()

  useWSStore.setState({
    subscribe: mockSubscribe,
    connected: true,
    socket: null,
    taskId: null,
    token: null,
    error: null,
    reconnectAttempts: 0,
    listeners: new Map(),
  } as Parameters<typeof useWSStore.setState>[0])

  useLogFilterStore.getState().reset()
})

afterEach(() => {
  vi.clearAllMocks()
})

// ─── Fixtures ─────────────────────────────────────────────────────────────────

const makeLog = (overrides: Partial<LogLine> = {}): LogLine => ({
  id: Math.random().toString(36).slice(2),
  timestamp: Date.now(),
  brainId: 'marketing-01',
  brainName: 'Marketing Strategist',
  level: 'info',
  message: 'Test log message',
  ...overrides,
})

// ─── Tests ────────────────────────────────────────────────────────────────────

describe('LiveLogPanel static mode', () => {
  it('renders log rows from static logs prop', () => {
    const logs = [
      makeLog({ message: 'First log' }),
      makeLog({ message: 'Second log' }),
    ]
    render(<LiveLogPanel logs={logs} />)
    expect(screen.getByText('First log')).toBeInTheDocument()
    expect(screen.getByText('Second log')).toBeInTheDocument()
  })

  it('shows empty state when no static logs', () => {
    render(<LiveLogPanel logs={[]} />)
    expect(screen.getByText('No logs yet')).toBeInTheDocument()
  })

  it('does not subscribe to WS in static mode', () => {
    render(<LiveLogPanel logs={[makeLog()]} />)
    expect(mockSubscribe).not.toHaveBeenCalled()
  })
})

describe('LiveLogPanel live mode', () => {
  it('subscribes to WS log:line events', () => {
    render(<LiveLogPanel />)
    expect(mockSubscribe).toHaveBeenCalledWith('log:line', expect.any(Function))
  })

  it('renders incoming WS log events', async () => {
    render(<LiveLogPanel />)

    await act(async () => {
      emitWSEvent('log:line', {
        ts: Date.now(),
        brain_id: 'marketing-01',
        brain_name: 'Marketing Strategist',
        level: 'info',
        msg: 'Live log arrived',
      })
      // Flush RAF — jsdom RAF fires via setTimeout ~16ms
      await new Promise((resolve) => setTimeout(resolve, 50))
    })

    expect(screen.getByText('Live log arrived')).toBeInTheDocument()
  })

  it('shows WS disconnected banner when not connected', () => {
    useWSStore.setState({ connected: false } as Parameters<typeof useWSStore.setState>[0])
    render(<LiveLogPanel />)
    expect(screen.getByText(/Logs paused \(WS disconnected\)/)).toBeInTheDocument()
  })

  it('hides WS disconnected banner when connected', () => {
    useWSStore.setState({ connected: true } as Parameters<typeof useWSStore.setState>[0])
    render(<LiveLogPanel />)
    expect(screen.queryByText(/Logs paused/)).not.toBeInTheDocument()
  })
})

describe('LiveLogPanel filtering', () => {
  it('shows only selected level logs', async () => {
    // Disable warn logs
    useLogFilterStore.getState().toggleLevel('warn')

    const logs = [
      makeLog({ level: 'info', message: 'Info message' }),
      makeLog({ level: 'warn', message: 'Warn message' }),
    ]
    render(<LiveLogPanel logs={logs} />)

    expect(screen.getByText('Info message')).toBeInTheDocument()
    expect(screen.queryByText('Warn message')).not.toBeInTheDocument()
  })

  it('shows no-match message when all filtered', () => {
    useLogFilterStore.getState().toggleLevel('info')
    useLogFilterStore.getState().toggleLevel('warn')
    useLogFilterStore.getState().toggleLevel('error')

    const logs = [makeLog({ level: 'info', message: 'Some log' })]
    render(<LiveLogPanel logs={logs} />)
    expect(screen.getByText('No logs match current filters')).toBeInTheDocument()
  })
})

describe('LiveLogPanel isolation mode', () => {
  it('shows only isolated brain logs', () => {
    useLogFilterStore.getState().setIsolatedBrain('marketing-01')

    const logs = [
      makeLog({ brainId: 'marketing-01', brainName: 'Marketing', message: 'Marketing log' }),
      makeLog({ brainId: 'product-01', brainName: 'Product', message: 'Product log' }),
    ]
    render(<LiveLogPanel logs={logs} />)

    expect(screen.getByText('Marketing log')).toBeInTheDocument()
    expect(screen.queryByText('Product log')).not.toBeInTheDocument()
  })

  it('clears isolation on badge click when same brain', () => {
    useLogFilterStore.getState().setIsolatedBrain('marketing-01')

    const logs = [makeLog({ brainId: 'marketing-01', brainName: 'Marketing Strategist', message: 'Test' })]
    render(<LiveLogPanel logs={logs} />)

    // Click the badge — should clear isolation
    const badge = screen.getByLabelText('Brain: Marketing Strategist (marketing-01), level: info')
    fireEvent.click(badge)

    expect(useLogFilterStore.getState().isolatedBrainId).toBeNull()
  })

  it('sets isolation on badge click for different brain', () => {
    const logs = [makeLog({ brainId: 'marketing-01', brainName: 'Marketing Strategist', message: 'Test' })]
    render(<LiveLogPanel logs={logs} />)

    const badge = screen.getByLabelText('Brain: Marketing Strategist (marketing-01), level: info')
    fireEvent.click(badge)

    expect(useLogFilterStore.getState().isolatedBrainId).toBe('marketing-01')
  })
})

describe('LiveLogPanel log row rendering', () => {
  it('renders timestamp, badge, and message for each log', () => {
    const logs = [makeLog({ message: 'Test message', level: 'warn' })]
    render(<LiveLogPanel logs={logs} />)

    expect(screen.getByText('Test message')).toBeInTheDocument()
    // Badge should be present
    expect(screen.getByRole('button', { name: /Brain: Marketing Strategist/ })).toBeInTheDocument()
  })
})
