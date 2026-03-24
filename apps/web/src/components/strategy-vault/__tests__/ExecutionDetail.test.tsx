/**
 * ExecutionDetail Component Tests
 *
 * **Purpose:** Verify execution detail view with accordion, scrubber, and replay
 * **Context:** Phase 08-02 - Task 5
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ExecutionDetail } from '../ExecutionDetail'
import type { ExecutionDetail as ExecutionDetailType } from '../ExecutionDetail'
import { useReplayStore } from '@/stores/replayStore'

// ─── Mocks ────────────────────────────────────────────────────────────────────

const mockRouterPush = vi.fn()

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockRouterPush }),
}))

vi.mock('lucide-react', () => ({
  ChevronDown: () => <svg data-testid="chevron-icon" />,
  Copy: () => <svg data-testid="copy-icon" />,
  Download: () => <svg data-testid="download-icon" />,
  XCircle: () => <svg data-testid="xcircle-icon" />,
  AlertCircle: () => <svg data-testid="alert-icon" />,
}))

// Mock SmartMarkdown (tested separately)
vi.mock('../SmartMarkdown', () => ({
  SmartMarkdown: ({ markdown }: { markdown: string }) => (
    <div data-testid="smart-markdown">{markdown.slice(0, 50)}</div>
  ),
}))

// Mock SnapshotScrubber (tested separately)
vi.mock('../SnapshotScrubber', () => ({
  SnapshotScrubber: ({ onScrub, milestones }: { onScrub: (i: number) => void; milestones: unknown[] }) => (
    <div data-testid="snapshot-scrubber">
      <button onClick={() => onScrub(1)} data-testid="scrubber-milestone-1">
        Milestone 1
      </button>
      <span>Milestones: {milestones.length}</span>
    </div>
  ),
}))

// ─── Fixtures ─────────────────────────────────────────────────────────────────

const MOCK_EXECUTION: ExecutionDetailType = {
  id: 'exec-001',
  task_id: 'task-abc',
  brief: 'Build a scalable REST API',
  status: 'success',
  duration_ms: 154234,
  brain_count: 3,
  created_at: '2026-03-24T04:00:00Z',
  milestones: [
    { index: 0, timestamp: 1000, label: '0% (0 active)', brainCount: 0 },
    { index: 1, timestamp: 2000, label: '50% (2 active)', brainCount: 2 },
    { index: 2, timestamp: 3000, label: '100% (3 active)', brainCount: 3 },
  ],
  brain_outputs: {
    'brain-01': {
      brain_id: 'brain-01',
      status: 'complete',
      output: '# Product Strategy\n\nBuild a REST API with these features:\n- Authentication\n- Rate limiting',
      duration_ms: 5000,
      timestamp: 1500,
    },
    'brain-02': {
      brain_id: 'brain-02',
      status: 'complete',
      output: '## UX Research\n\nUser needs analysis for the API.',
      duration_ms: 3000,
      timestamp: 2000,
    },
    'brain-03': {
      brain_id: 'brain-03',
      status: 'error',
      output: '### Error occurred during analysis',
      duration_ms: 1000,
      timestamp: 2500,
    },
  },
  graph_snapshot: {
    nodes: [
      { id: 'brain-01', data: { name: 'Product Strategy' } },
      { id: 'brain-02', data: { name: 'UX Research' } },
      { id: 'brain-03', data: { name: 'UI Design' } },
    ],
    edges: [
      { id: 'e1', source: 'brain-01', target: 'brain-02' },
    ],
  },
}

// ─── Wrapper ──────────────────────────────────────────────────────────────────

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

// ─── Tests ────────────────────────────────────────────────────────────────────

describe('ExecutionDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.stubGlobal('fetch', vi.fn())
    // Reset replay store between tests to avoid state bleed
    useReplayStore.getState().reset()
  })

  it('renders loading skeleton while fetching', () => {
    vi.mocked(fetch).mockImplementation(() => new Promise(() => {}))

    render(<ExecutionDetail executionId="exec-001" />, { wrapper: createWrapper() })

    expect(screen.getByTestId('execution-detail-loading')).toBeInTheDocument()
  })

  it('renders execution detail after data loads', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_EXECUTION),
    } as Response)

    render(<ExecutionDetail executionId="exec-001" />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('execution-detail')).toBeInTheDocument()
    })
    expect(screen.getByText('Build a scalable REST API')).toBeInTheDocument()
  })

  it('renders ReplayNexus with REPLAY MODE banner', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_EXECUTION),
    } as Response)

    render(<ExecutionDetail executionId="exec-001" />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('replay-mode-banner')).toBeInTheDocument()
    })
    expect(screen.getByTestId('replay-mode-banner')).toHaveTextContent('REPLAY MODE')
  })

  it('renders all brain output accordion items', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_EXECUTION),
    } as Response)

    render(<ExecutionDetail executionId="exec-001" />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('brain-outputs-accordion')).toBeInTheDocument()
    })

    expect(screen.getByTestId('accordion-item-brain-01')).toBeInTheDocument()
    expect(screen.getByTestId('accordion-item-brain-02')).toBeInTheDocument()
    expect(screen.getByTestId('accordion-item-brain-03')).toBeInTheDocument()
  })

  it('expands accordion item to show SmartMarkdown on click', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_EXECUTION),
    } as Response)

    render(<ExecutionDetail executionId="exec-001" />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('accordion-header-brain-01')).toBeInTheDocument()
    })

    // Content should not be visible initially
    expect(screen.queryByTestId('accordion-content-brain-01')).not.toBeInTheDocument()

    // Click to expand
    fireEvent.click(screen.getByTestId('accordion-header-brain-01'))

    // Content should now be visible
    expect(screen.getByTestId('accordion-content-brain-01')).toBeInTheDocument()
    expect(screen.getByTestId('smart-markdown')).toBeInTheDocument()
  })

  it('shows copy button on accordion item', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_EXECUTION),
    } as Response)

    render(<ExecutionDetail executionId="exec-001" />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getAllByTestId('copy-button')[0]).toBeInTheDocument()
    })
  })

  it('shows download button for full execution', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_EXECUTION),
    } as Response)

    render(<ExecutionDetail executionId="exec-001" />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('download-button')).toBeInTheDocument()
    })
  })

  it('renders logs panel', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_EXECUTION),
    } as Response)

    render(<ExecutionDetail executionId="exec-001" />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('logs-panel')).toBeInTheDocument()
    })
  })

  it('renders snapshot scrubber when milestones available', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_EXECUTION),
    } as Response)

    render(<ExecutionDetail executionId="exec-001" />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('snapshot-scrubber')).toBeInTheDocument()
    })
  })

  it('shows error state on fetch failure', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 500,
    } as Response)

    render(<ExecutionDetail executionId="exec-001" />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('execution-detail-error')).toBeInTheDocument()
    })
  })

  it('redirects to /strategy-vault on 404', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ detail: 'Not found' }),
    } as Response)

    render(<ExecutionDetail executionId="exec-not-found" />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(mockRouterPush).toHaveBeenCalledWith('/strategy-vault')
    })
  })

  it('logs panel shows brain activity entries', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_EXECUTION),
    } as Response)

    render(<ExecutionDetail executionId="exec-001" />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('log-entry-brain-01')).toBeInTheDocument()
    })
    expect(screen.getByTestId('log-entry-brain-02')).toBeInTheDocument()
    expect(screen.getByTestId('log-entry-brain-03')).toBeInTheDocument()
  })

  it('ReplayNexus shows graph nodes', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_EXECUTION),
    } as Response)

    render(<ExecutionDetail executionId="exec-001" />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('replay-nexus')).toBeInTheDocument()
    })
    expect(screen.getByTestId('replay-node-brain-01')).toBeInTheDocument()
  })
})
