/**
 * APIKeyManager tests — Task 5 Phase 08-04
 *
 * Tests: tab switching, keys list renders, loading state, error state.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { APIKeyManager } from '../APIKeyManager'
import type { APIKeyMasked } from '../APIKeyManager'

// Mock subcomponents — tested independently
vi.mock('../KeyCreateDialog', () => ({
  KeyCreateDialog: () => <div data-testid="key-create-dialog">KeyCreateDialog</div>,
}))

vi.mock('../KeyListTable', () => ({
  KeyListTable: ({ keys }: { keys: APIKeyMasked[] }) => (
    <div data-testid="key-list-table">KeyListTable ({keys.length} keys)</div>
  ),
}))

const MOCK_KEYS: APIKeyMasked[] = [
  {
    id: 'key-1',
    prefix: 'mmsk_abc1',
    suffix: 'xyz1',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    last_used_at: null,
  },
]

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  }
}

describe('APIKeyManager', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  // ─── Tab navigation ──────────────────────────────────────────────────────

  describe('tab navigation', () => {
    it('renders My Keys tab by default', () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ keys: MOCK_KEYS }),
      } as Response)

      render(<APIKeyManager />, { wrapper: makeWrapper() })

      const myKeysTab = screen.getByRole('tab', { name: /my keys/i })
      expect(myKeysTab).toHaveAttribute('aria-selected', 'true')
    })

    it('switches to Create Key tab when clicked', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ keys: [] }),
      } as Response)

      render(<APIKeyManager />, { wrapper: makeWrapper() })

      const createTab = screen.getByRole('tab', { name: /create key/i })
      fireEvent.click(createTab)

      expect(createTab).toHaveAttribute('aria-selected', 'true')
      await waitFor(() => {
        expect(screen.getByTestId('key-create-dialog')).toBeInTheDocument()
      })
    })

    it('defaultTab=create starts on Create Key tab', () => {
      render(<APIKeyManager defaultTab="create" />, { wrapper: makeWrapper() })

      const createTab = screen.getByRole('tab', { name: /create key/i })
      expect(createTab).toHaveAttribute('aria-selected', 'true')
    })
  })

  // ─── Data loading ────────────────────────────────────────────────────────

  describe('data loading', () => {
    it('shows loading state while fetching', () => {
      global.fetch = vi.fn().mockReturnValue(new Promise(() => {})) // Never resolves

      render(<APIKeyManager />, { wrapper: makeWrapper() })

      expect(screen.getByText(/loading api keys/i)).toBeInTheDocument()
    })

    it('shows KeyListTable with keys on success', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ keys: MOCK_KEYS }),
      } as Response)

      render(<APIKeyManager />, { wrapper: makeWrapper() })

      await waitFor(() => {
        expect(screen.getByTestId('key-list-table')).toBeInTheDocument()
      })
      expect(screen.getByText(/1 keys/)).toBeInTheDocument()
    })

    it('shows error state when fetch fails', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({ error: 'Server error' }),
      } as Response)

      render(<APIKeyManager />, { wrapper: makeWrapper() })

      await waitFor(() => {
        expect(screen.getByText(/failed to load api keys/i)).toBeInTheDocument()
      })
    })

    it('shows retry button on error', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        json: async () => {},
      } as Response)

      render(<APIKeyManager />, { wrapper: makeWrapper() })

      await waitFor(() => {
        expect(screen.getByText(/retry/i)).toBeInTheDocument()
      })
    })
  })
})
