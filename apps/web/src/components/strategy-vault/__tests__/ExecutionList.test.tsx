/**
 * ExecutionList Component Tests
 *
 * **Purpose:** Verify paginated execution list table with status badges
 * **Context:** Phase 08-02 - Task 4
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ExecutionList } from '../ExecutionList'
import type { ExecutionSummary, ExecutionHistoryResponse } from '../ExecutionList'

// ─── Mock next/link ───────────────────────────────────────────────────────────
vi.mock('next/link', () => ({
  default: ({ href, children, ...props }: { href: string; children: React.ReactNode; [key: string]: unknown }) => (
    <a href={href} {...props}>{children}</a>
  ),
}))

// ─── Mock lucide-react ────────────────────────────────────────────────────────
vi.mock('lucide-react', () => ({
  CheckCircle: () => <svg data-testid="icon-check" />,
  XCircle: () => <svg data-testid="icon-x" />,
  Loader2: () => <svg data-testid="icon-loader" />,
  Clock: () => <svg data-testid="icon-clock" />,
  Brain: () => <svg data-testid="icon-brain" />,
  ArrowRight: () => <svg data-testid="icon-arrow" />,
}))

// ─── Fixtures ─────────────────────────────────────────────────────────────────

const MOCK_EXECUTIONS: ExecutionSummary[] = [
  {
    id: 'exec-001',
    status: 'success',
    brief: 'Build a REST API for user management with JWT authentication',
    duration_ms: 154234,
    brain_count: 12,
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2h ago
  },
  {
    id: 'exec-002',
    status: 'error',
    brief: 'Design a scalable microservices architecture for e-commerce',
    duration_ms: 45000,
    brain_count: 8,
    created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1d ago
  },
  {
    id: 'exec-003',
    status: 'running',
    brief: 'Create a product launch strategy for B2B SaaS',
    duration_ms: 12000,
    brain_count: 6,
    created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(), // 5m ago
  },
]

const MOCK_RESPONSE_PAGE1: ExecutionHistoryResponse = {
  executions: MOCK_EXECUTIONS,
  next_cursor: 'cursor-page2',
  has_more: true,
}

const MOCK_RESPONSE_PAGE2: ExecutionHistoryResponse = {
  executions: [
    {
      id: 'exec-004',
      status: 'success',
      brief: 'Second page execution',
      duration_ms: 30000,
      brain_count: 5,
      created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    },
  ],
  next_cursor: null,
  has_more: false,
}

// ─── Test Wrapper ─────────────────────────────────────────────────────────────

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

// ─── Tests ────────────────────────────────────────────────────────────────────

describe('ExecutionList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.stubGlobal('fetch', vi.fn())
  })

  it('renders table skeleton while loading', async () => {
    vi.mocked(fetch).mockImplementation(() => new Promise(() => {})) // never resolves

    render(<ExecutionList />, { wrapper: createWrapper() })

    // Skeleton rows should be visible (pulse animation div)
    const container = screen.getByTestId('execution-list')
    expect(container).toBeInTheDocument()
  })

  it('renders execution rows after data loads', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_RESPONSE_PAGE1),
    } as Response)

    render(<ExecutionList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('execution-row-exec-001')).toBeInTheDocument()
    })

    expect(screen.getByTestId('execution-row-exec-002')).toBeInTheDocument()
    expect(screen.getByTestId('execution-row-exec-003')).toBeInTheDocument()
  })

  it('renders success status badge with green styling', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_RESPONSE_PAGE1),
    } as Response)

    render(<ExecutionList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getAllByTestId('status-badge-success')[0]).toBeInTheDocument()
    })
    expect(screen.getAllByTestId('status-badge-success')[0]).toHaveClass('bg-green-100')
  })

  it('renders error status badge with red styling', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_RESPONSE_PAGE1),
    } as Response)

    render(<ExecutionList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('status-badge-error')).toBeInTheDocument()
    })
    expect(screen.getByTestId('status-badge-error')).toHaveClass('bg-red-100')
  })

  it('renders running status badge with yellow styling', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_RESPONSE_PAGE1),
    } as Response)

    render(<ExecutionList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('status-badge-running')).toBeInTheDocument()
    })
    expect(screen.getByTestId('status-badge-running')).toHaveClass('bg-yellow-100')
  })

  it('truncates brief text over 100 chars', async () => {
    const longBrief = 'A'.repeat(150)
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        executions: [{ ...MOCK_EXECUTIONS[0], brief: longBrief }],
        next_cursor: null,
        has_more: false,
      }),
    } as Response)

    render(<ExecutionList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('execution-row-exec-001')).toBeInTheDocument()
    })

    // Should show truncated text (100 chars + ellipsis)
    const briefText = screen.getByTitle(longBrief)
    expect(briefText.textContent?.length).toBeLessThanOrEqual(102) // 100 chars + ellipsis
  })

  it('shows view link for each execution row', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_RESPONSE_PAGE1),
    } as Response)

    render(<ExecutionList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('view-link-exec-001')).toBeInTheDocument()
    })

    expect(screen.getByTestId('view-link-exec-001')).toHaveAttribute(
      'href',
      '/strategy-vault/exec-001'
    )
  })

  it('shows empty state when no executions', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ executions: [], next_cursor: null, has_more: false }),
    } as Response)

    render(<ExecutionList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('empty-state')).toBeInTheDocument()
    })
    expect(screen.getByTestId('empty-state')).toHaveTextContent('No executions yet')
  })

  it('shows error state with retry button on fetch failure', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 500,
    } as Response)

    render(<ExecutionList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('execution-list-error')).toBeInTheDocument()
    })
    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument()
  })

  it('shows pagination controls when executions are present', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_RESPONSE_PAGE1),
    } as Response)

    render(<ExecutionList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('pagination-controls')).toBeInTheDocument()
    })
    expect(screen.getByTestId('pagination-prev')).toBeInTheDocument()
    expect(screen.getByTestId('pagination-next')).toBeInTheDocument()
  })

  it('prev button disabled on first page', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_RESPONSE_PAGE1),
    } as Response)

    render(<ExecutionList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('pagination-prev')).toBeInTheDocument()
    })
    expect(screen.getByTestId('pagination-prev')).toBeDisabled()
  })

  it('navigates to next page and loads new executions', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_RESPONSE_PAGE1),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_RESPONSE_PAGE2),
      } as Response)

    render(<ExecutionList />, { wrapper: createWrapper() })

    // Wait for first page
    await waitFor(() => {
      expect(screen.getByTestId('execution-row-exec-001')).toBeInTheDocument()
    })

    // Click next
    fireEvent.click(screen.getByTestId('pagination-next'))

    // Should load second page
    await waitFor(() => {
      expect(screen.getByTestId('execution-row-exec-004')).toBeInTheDocument()
    })

    // Prev button should now be enabled
    expect(screen.getByTestId('pagination-prev')).not.toBeDisabled()
  })

  it('next button disabled when has_more is false', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ ...MOCK_RESPONSE_PAGE1, has_more: false }),
    } as Response)

    render(<ExecutionList />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByTestId('pagination-next')).toBeInTheDocument()
    })
    expect(screen.getByTestId('pagination-next')).toBeDisabled()
  })
})
