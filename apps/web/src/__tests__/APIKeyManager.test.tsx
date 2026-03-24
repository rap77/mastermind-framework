/**
 * APIKeyManager.test.tsx — Broader API key CRUD tests.
 *
 * Covers create (show-once security), list (masking verification), revoke
 * flow, security isolation, error handling, and tabs switching.
 * Complements co-located component tests with security-focused scenarios.
 *
 * Phase: 08-05 — Wave 4 (Integration Tests)
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { APIKeyManager } from '@/components/engine-room/APIKeyManager'
import { KeyCreateDialog } from '@/components/engine-room/KeyCreateDialog'
import { KeyListTable } from '@/components/engine-room/KeyListTable'
import type { APIKeyMasked } from '@/components/engine-room/APIKeyManager'

// ─── Fixtures ─────────────────────────────────────────────────────────────────

const MOCK_KEYS: APIKeyMasked[] = [
  {
    id: 'key-1',
    prefix: 'mmsk_abc1',
    suffix: 'xyz1',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    last_used_at: null,
  },
  {
    id: 'key-2',
    prefix: 'mmsk_def2',
    suffix: 'uvw2',
    created_at: new Date(Date.now() - 3600000).toISOString(),
    last_used_at: new Date(Date.now() - 1800000).toISOString(),
  },
  {
    id: 'key-3',
    prefix: 'mmsk_ghi3',
    suffix: 'rst3',
    created_at: new Date(Date.now() - 7200000).toISOString(),
    last_used_at: null,
  },
]

const MOCK_CREATED_KEY = {
  id: 'key-new',
  full_key: 'mmsk_abcdef1234567890abcdef1234567890ab',
}

// ─── Wrapper ──────────────────────────────────────────────────────────────────

function makeWrapper() {
  const qc = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  }
}

// ─── Tests ────────────────────────────────────────────────────────────────────

describe('APIKeyManager — CRUD security tests', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      writable: true,
      configurable: true,
    })
  })

  // ─── test_loads_key_list ──────────────────────────────────────────────────

  describe('test_loads_key_list', () => {
    it('fetches GET /api/keys and displays masked keys', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ keys: MOCK_KEYS }),
      } as Response)

      render(<APIKeyManager />, { wrapper: makeWrapper() })

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/keys')
      })
    })

    it('renders 3 masked keys from API response', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ keys: MOCK_KEYS }),
      } as Response)

      render(<APIKeyManager />, { wrapper: makeWrapper() })

      await waitFor(() => {
        // KeyListTable renders with count visible
        expect(screen.getByRole('table', { name: /api keys/i })).toBeInTheDocument()
        expect(screen.getByTestId('key-row-key-1')).toBeInTheDocument()
        expect(screen.getByTestId('key-row-key-2')).toBeInTheDocument()
        expect(screen.getByTestId('key-row-key-3')).toBeInTheDocument()
      })
    })

    it('keys display prefix+...+suffix masked format', async () => {
      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })

      const maskedKeys = screen.getAllByTestId('key-masked')
      expect(maskedKeys[0].textContent).toBe('mmsk_abc1...xyz1')
      expect(maskedKeys[1].textContent).toBe('mmsk_def2...uvw2')
      expect(maskedKeys[2].textContent).toBe('mmsk_ghi3...rst3')
    })
  })

  // ─── test_create_key_flow ─────────────────────────────────────────────────

  describe('test_create_key_flow', () => {
    it('POST /api/keys returns full key visible in dialog', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => MOCK_CREATED_KEY,
      } as Response)

      render(<KeyCreateDialog />, { wrapper: makeWrapper() })

      // Open dialog
      fireEvent.click(screen.getByTestId('open-create-dialog'))
      await waitFor(() => screen.getByTestId('confirm-create-key'))

      // Create key
      fireEvent.click(screen.getByTestId('confirm-create-key'))

      await waitFor(() => {
        expect(screen.getByTestId('created-key-code')).toBeInTheDocument()
        expect(screen.getByTestId('created-key-code').textContent).toBe(MOCK_CREATED_KEY.full_key)
      })
    })

    it('copy button visible after key creation', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => MOCK_CREATED_KEY,
      } as Response)

      render(<KeyCreateDialog />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('open-create-dialog'))
      await waitFor(() => screen.getByTestId('confirm-create-key'))
      fireEvent.click(screen.getByTestId('confirm-create-key'))

      await waitFor(() => {
        expect(screen.getByTestId('copy-key-button')).toBeInTheDocument()
      })
    })

    it('security warning "won\'t be able to see it again" shown', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => MOCK_CREATED_KEY,
      } as Response)

      render(<KeyCreateDialog />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('open-create-dialog'))
      await waitFor(() => screen.getByTestId('confirm-create-key'))
      fireEvent.click(screen.getByTestId('confirm-create-key'))

      await waitFor(() => {
        expect(screen.getByText(/won't be able to see it again/i)).toBeInTheDocument()
      })
    })
  })

  // ─── test_create_key_show_once ────────────────────────────────────────────

  describe('test_create_key_show_once', () => {
    it('full key visible in dialog', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => MOCK_CREATED_KEY,
      } as Response)

      render(<KeyCreateDialog />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('open-create-dialog'))
      await waitFor(() => screen.getByTestId('confirm-create-key'))
      fireEvent.click(screen.getByTestId('confirm-create-key'))

      await waitFor(() => {
        expect(screen.getByTestId('created-key-display')).toBeInTheDocument()
      })
    })

    it('key disappears permanently after clicking Done (show-once)', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => MOCK_CREATED_KEY,
      } as Response)

      render(<KeyCreateDialog />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('open-create-dialog'))
      await waitFor(() => screen.getByTestId('confirm-create-key'))
      fireEvent.click(screen.getByTestId('confirm-create-key'))
      await waitFor(() => screen.getByTestId('done-button'))

      // Close dialog — key should be gone
      fireEvent.click(screen.getByTestId('done-button'))

      await waitFor(() => {
        // Dialog closed: code element gone
        expect(screen.queryByTestId('created-key-code')).toBeNull()
        expect(screen.queryByTestId('created-key-display')).toBeNull()
      })
    })

    it('full key not re-accessible after dialog close', async () => {
      global.fetch = vi.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => MOCK_CREATED_KEY,
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ keys: [] }),
        } as Response)

      render(<KeyCreateDialog />, { wrapper: makeWrapper() })

      // Create + close
      fireEvent.click(screen.getByTestId('open-create-dialog'))
      await waitFor(() => screen.getByTestId('confirm-create-key'))
      fireEvent.click(screen.getByTestId('confirm-create-key'))
      await waitFor(() => screen.getByTestId('done-button'))
      fireEvent.click(screen.getByTestId('done-button'))

      // Try to re-open dialog — should start fresh, no previous key
      await waitFor(() => screen.getByTestId('open-create-dialog'))
      fireEvent.click(screen.getByTestId('open-create-dialog'))

      await waitFor(() => {
        // Confirm step visible (not key display step)
        expect(screen.queryByTestId('created-key-code')).toBeNull()
        expect(screen.getByTestId('confirm-create-key')).toBeInTheDocument()
      })
    })
  })

  // ─── test_create_key_security ─────────────────────────────────────────────

  describe('test_create_key_security', () => {
    it('full key NOT in localStorage after creation', async () => {
      const localStorageSpy = vi.spyOn(Storage.prototype, 'setItem')

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => MOCK_CREATED_KEY,
      } as Response)

      render(<KeyCreateDialog />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('open-create-dialog'))
      await waitFor(() => screen.getByTestId('confirm-create-key'))
      fireEvent.click(screen.getByTestId('confirm-create-key'))
      await waitFor(() => screen.getByTestId('created-key-code'))

      // Verify full key was never stored in localStorage
      const allSetItemCalls = localStorageSpy.mock.calls
      for (const [key, value] of allSetItemCalls) {
        expect(String(key) + String(value)).not.toContain(MOCK_CREATED_KEY.full_key)
      }
    })

    it('copy writes full key to clipboard via API', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => MOCK_CREATED_KEY,
      } as Response)

      render(<KeyCreateDialog />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('open-create-dialog'))
      await waitFor(() => screen.getByTestId('confirm-create-key'))
      fireEvent.click(screen.getByTestId('confirm-create-key'))
      await waitFor(() => screen.getByTestId('copy-key-button'))
      fireEvent.click(screen.getByTestId('copy-key-button'))

      await waitFor(() => {
        expect(navigator.clipboard.writeText).toHaveBeenCalledWith(MOCK_CREATED_KEY.full_key)
      })
    })
  })

  // ─── test_list_keys_masked ────────────────────────────────────────────────

  describe('test_list_keys_masked', () => {
    it('all 5 keys display as masked (prefix...suffix)', () => {
      const fiveKeys: APIKeyMasked[] = Array.from({ length: 5 }, (_, i) => ({
        id: `key-${i + 1}`,
        prefix: `mmsk_key${i + 1}`,
        suffix: `end${i + 1}`,
        created_at: new Date(Date.now() - 86400000 * i).toISOString(),
        last_used_at: null,
      }))

      render(<KeyListTable keys={fiveKeys} />, { wrapper: makeWrapper() })

      const maskedKeys = screen.getAllByTestId('key-masked')
      expect(maskedKeys).toHaveLength(5)

      maskedKeys.forEach((el, i) => {
        expect(el.textContent).toBe(`mmsk_key${i + 1}...end${i + 1}`)
        // Full key never in DOM
        expect(el.textContent).not.toMatch(/abcdef1234567890/)
      })
    })

    it('no full keys exposed in KeyListTable DOM', () => {
      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })

      // Iterate all masked elements and confirm they contain "..."
      const maskedKeys = screen.getAllByTestId('key-masked')
      maskedKeys.forEach((el) => {
        expect(el.textContent).toContain('...')
      })
    })
  })

  // ─── test_revoke_key_flow ─────────────────────────────────────────────────

  describe('test_revoke_key_flow', () => {
    it('clicking Revoke shows confirm dialog', async () => {
      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })

      fireEvent.click(screen.getByTestId('revoke-btn-key-1'))

      await waitFor(() => {
        expect(screen.getByTestId('revoke-confirm-dialog')).toBeInTheDocument()
        expect(screen.getByText(/revoke api key/i)).toBeInTheDocument()
      })
    })

    it('confirm calls DELETE /api/keys/{id}', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({}),
      } as Response)

      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('revoke-btn-key-1'))
      await waitFor(() => screen.getByTestId('confirm-revoke'))
      fireEvent.click(screen.getByTestId('confirm-revoke'))

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/keys/key-1', { method: 'DELETE' })
      })
    })

    it('dialog closes after successful revoke', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({}),
      } as Response)

      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('revoke-btn-key-1'))
      await waitFor(() => screen.getByTestId('confirm-revoke'))
      fireEvent.click(screen.getByTestId('confirm-revoke'))

      await waitFor(() => {
        expect(screen.queryByTestId('revoke-confirm-dialog')).toBeNull()
      })
    })
  })

  // ─── test_revoke_key_confirm ──────────────────────────────────────────────

  describe('test_revoke_key_confirm', () => {
    it('Cancel in confirm dialog does NOT call DELETE', async () => {
      global.fetch = vi.fn()

      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('revoke-btn-key-1'))
      await waitFor(() => screen.getByTestId('cancel-revoke'))
      fireEvent.click(screen.getByTestId('cancel-revoke'))

      await waitFor(() => {
        expect(screen.queryByTestId('revoke-confirm-dialog')).toBeNull()
      })

      expect(global.fetch).not.toHaveBeenCalled()
    })

    it('key row remains visible after Cancel', async () => {
      global.fetch = vi.fn()

      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('revoke-btn-key-1'))
      await waitFor(() => screen.getByTestId('cancel-revoke'))
      fireEvent.click(screen.getByTestId('cancel-revoke'))

      await waitFor(() => {
        expect(screen.queryByTestId('revoke-confirm-dialog')).toBeNull()
      })

      // Key row still present (passed as prop — parent controls list)
      expect(screen.getByTestId('key-row-key-1')).toBeInTheDocument()
    })
  })

  // ─── test_revoke_key_error ────────────────────────────────────────────────

  describe('test_revoke_key_error', () => {
    it('DELETE failure keeps dialog open for retry', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({ error: 'Server error' }),
      } as Response)

      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('revoke-btn-key-1'))
      await waitFor(() => screen.getByTestId('confirm-revoke'))
      fireEvent.click(screen.getByTestId('confirm-revoke'))

      // After failed DELETE, dialog remains open (user can retry)
      await waitFor(() => {
        expect(screen.getByTestId('confirm-revoke')).toBeInTheDocument()
      })
    })

    it('key row still present after revoke error', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({ error: 'Server error' }),
      } as Response)

      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('revoke-btn-key-1'))
      await waitFor(() => screen.getByTestId('confirm-revoke'))
      fireEvent.click(screen.getByTestId('confirm-revoke'))

      // Wait for mutation to settle
      await new Promise((r) => setTimeout(r, 50))

      // Key row still present (error = no invalidation)
      expect(screen.getByTestId('key-row-key-1')).toBeInTheDocument()
    })
  })

  // ─── test_key_isolation ───────────────────────────────────────────────────

  describe('test_key_isolation', () => {
    it('DELETE is only called for the selected key ID', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({}),
      } as Response)

      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })

      // Revoke key-2 specifically (not key-1 or key-3)
      fireEvent.click(screen.getByTestId('revoke-btn-key-2'))
      await waitFor(() => screen.getByTestId('confirm-revoke'))
      fireEvent.click(screen.getByTestId('confirm-revoke'))

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/keys/key-2', { method: 'DELETE' })
      })

      // Verify only the correct key ID was called
      const deleteCalls = (global.fetch as ReturnType<typeof vi.fn>).mock.calls
      expect(deleteCalls).toHaveLength(1)
      expect(deleteCalls[0][0]).toBe('/api/keys/key-2')
      expect(deleteCalls[0][0]).not.toBe('/api/keys/key-1')
      expect(deleteCalls[0][0]).not.toBe('/api/keys/key-3')
    })

    it('other key rows untouched after specific key revoke', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({}),
      } as Response)

      render(<KeyListTable keys={MOCK_KEYS} />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('revoke-btn-key-2'))
      await waitFor(() => screen.getByTestId('confirm-revoke'))
      fireEvent.click(screen.getByTestId('confirm-revoke'))

      await waitFor(() => {
        // Confirm dialog closes after success
        expect(screen.queryByTestId('revoke-confirm-dialog')).toBeNull()
      })

      // Keys 1 and 3 remain (parent would remove key-2 on cache invalidation)
      expect(screen.getByTestId('key-row-key-1')).toBeInTheDocument()
      expect(screen.getByTestId('key-row-key-3')).toBeInTheDocument()
    })
  })

  // ─── test_tabs_switch ─────────────────────────────────────────────────────

  describe('test_tabs_switch', () => {
    it('My Keys tab is active by default', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ keys: [] }),
      } as Response)

      render(<APIKeyManager />, { wrapper: makeWrapper() })

      const myKeysTab = screen.getByRole('tab', { name: /my keys/i })
      expect(myKeysTab).toHaveAttribute('aria-selected', 'true')
    })

    it('clicking Create Key tab switches content', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ keys: [] }),
      } as Response)

      render(<APIKeyManager />, { wrapper: makeWrapper() })

      const createTab = screen.getByRole('tab', { name: /create key/i })
      fireEvent.click(createTab)

      expect(createTab).toHaveAttribute('aria-selected', 'true')
      await waitFor(() => {
        expect(screen.getByTestId('open-create-dialog')).toBeInTheDocument()
      })
    })

    it('defaultTab=create shows Create Key panel immediately', () => {
      render(<APIKeyManager defaultTab="create" />, { wrapper: makeWrapper() })

      const createTab = screen.getByRole('tab', { name: /create key/i })
      expect(createTab).toHaveAttribute('aria-selected', 'true')
      expect(screen.getByTestId('open-create-dialog')).toBeInTheDocument()
    })

    it('switching back to My Keys shows loading state', async () => {
      global.fetch = vi.fn().mockReturnValue(new Promise(() => {})) // Never resolves

      render(<APIKeyManager />, { wrapper: makeWrapper() })

      // Switch to Create, then back to My Keys
      const createTab = screen.getByRole('tab', { name: /create key/i })
      fireEvent.click(createTab)

      const myKeysTab = screen.getByRole('tab', { name: /my keys/i })
      fireEvent.click(myKeysTab)

      // Loading state shown while fetch pending
      expect(screen.getByText(/loading api keys/i)).toBeInTheDocument()
    })
  })
})
