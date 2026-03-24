/**
 * KeyListTable tests — Task 7 Phase 08-04
 *
 * Tests: renders keys, masking, empty state, revoke flow.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { KeyListTable, formatRelativeTime } from '../KeyListTable'
import type { APIKeyMasked } from '../APIKeyManager'

const MOCK_KEYS: APIKeyMasked[] = [
  {
    id: 'key-1',
    prefix: 'mmsk_abc1',
    suffix: 'xyz1',
    created_at: new Date(Date.now() - 86400000 * 14).toISOString(), // 14 days ago
    last_used_at: null,
  },
  {
    id: 'key-2',
    prefix: 'mmsk_def2',
    suffix: 'uvw2',
    created_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
    last_used_at: new Date(Date.now() - 1800000).toISOString(), // 30 min ago
  },
]

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  }
}

describe('KeyListTable', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  // ─── Rendering ───────────────────────────────────────────────────────────

  describe('rendering', () => {
    it('shows empty state when no keys', () => {
      render(<KeyListTable keys={[]} />, { wrapper: makeWrapper() })
      expect(screen.getByTestId('empty-state')).toBeInTheDocument()
    })

    it('renders all provided keys', () => {
      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })
      expect(screen.getByTestId('key-row-key-1')).toBeInTheDocument()
      expect(screen.getByTestId('key-row-key-2')).toBeInTheDocument()
    })

    it('masks key correctly (prefix...suffix)', () => {
      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })
      const maskedKeys = screen.getAllByTestId('key-masked')
      expect(maskedKeys[0].textContent).toBe('mmsk_abc1...xyz1')
      expect(maskedKeys[1].textContent).toBe('mmsk_def2...uvw2')
    })

    it('shows "Never" for last_used_at = null', () => {
      render(<KeyListTable keys={[MOCK_KEYS[0]]} />, { wrapper: makeWrapper() })
      expect(screen.getByText('Never')).toBeInTheDocument()
    })

    it('shows relative time for last_used_at when set', () => {
      render(<KeyListTable keys={[MOCK_KEYS[1]]} />, { wrapper: makeWrapper() })
      // 30 min ago → "30m ago"
      expect(screen.getByText('30m ago')).toBeInTheDocument()
    })

    it('renders Revoke button for each key', () => {
      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })
      expect(screen.getByTestId('revoke-btn-key-1')).toBeInTheDocument()
      expect(screen.getByTestId('revoke-btn-key-2')).toBeInTheDocument()
    })
  })

  // ─── Revoke flow ─────────────────────────────────────────────────────────

  describe('revoke flow', () => {
    it('opens confirm dialog when Revoke is clicked', async () => {
      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })

      fireEvent.click(screen.getByTestId('revoke-btn-key-1'))

      await waitFor(() => {
        expect(screen.getByTestId('revoke-confirm-dialog')).toBeInTheDocument()
      })
    })

    it('shows key identifier in confirm dialog', async () => {
      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('revoke-btn-key-1'))

      await waitFor(() => {
        // Dialog contains "will be immediately revoked" text (unique to dialog)
        expect(screen.getByText(/will be immediately revoked/i)).toBeInTheDocument()
      })
    })

    it('closes dialog when Cancel is clicked', async () => {
      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('revoke-btn-key-1'))

      await waitFor(() => {
        screen.getByTestId('cancel-revoke')
      })
      fireEvent.click(screen.getByTestId('cancel-revoke'))

      await waitFor(() => {
        expect(screen.queryByTestId('revoke-confirm-dialog')).toBeNull()
      })
    })

    it('calls DELETE /api/keys/{id} when confirmed', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({}),
      } as Response)

      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('revoke-btn-key-1'))

      await waitFor(() => {
        screen.getByTestId('confirm-revoke')
      })
      fireEvent.click(screen.getByTestId('confirm-revoke'))

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/keys/key-1', { method: 'DELETE' })
      })
    })
  })

  // ─── formatRelativeTime helper ───────────────────────────────────────────

  describe('formatRelativeTime', () => {
    it('returns "just now" for < 60 seconds', () => {
      const now = new Date().toISOString()
      expect(formatRelativeTime(now)).toBe('just now')
    })

    it('returns minutes for < 1 hour', () => {
      const tenMinutesAgo = new Date(Date.now() - 10 * 60 * 1000).toISOString()
      expect(formatRelativeTime(tenMinutesAgo)).toBe('10m ago')
    })

    it('returns hours for < 1 day', () => {
      const twoHoursAgo = new Date(Date.now() - 2 * 3600 * 1000).toISOString()
      expect(formatRelativeTime(twoHoursAgo)).toBe('2h ago')
    })

    it('returns days for < 1 month', () => {
      const fiveDaysAgo = new Date(Date.now() - 5 * 86400 * 1000).toISOString()
      expect(formatRelativeTime(fiveDaysAgo)).toBe('5d ago')
    })
  })
})
