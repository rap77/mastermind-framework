/**
 * KeyCreateDialog tests — Task 6 Phase 08-04
 *
 * Tests: dialog opens/closes, create key button, show-once pattern,
 * copy-to-clipboard, warning displayed.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { KeyCreateDialog } from '../KeyCreateDialog'

const MOCK_KEY_RESPONSE = {
  id: 'key-123',
  full_key: 'mmsk_abcdef1234567890abcdef1234567890',
}

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  }
}

describe('KeyCreateDialog', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    // Mock clipboard API
    Object.defineProperty(navigator, 'clipboard', {
      value: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
      writable: true,
      configurable: true,
    })
  })

  // ─── Initial state ───────────────────────────────────────────────────────

  it('shows Create API Key button by default', () => {
    render(<KeyCreateDialog />, { wrapper: makeWrapper() })
    expect(screen.getByTestId('open-create-dialog')).toBeInTheDocument()
  })

  it('dialog is not visible until button is clicked', () => {
    render(<KeyCreateDialog />, { wrapper: makeWrapper() })
    expect(screen.queryByTestId('key-create-dialog-content')).toBeNull()
  })

  // ─── Dialog open/close ───────────────────────────────────────────────────

  it('opens dialog when Create API Key button is clicked', async () => {
    render(<KeyCreateDialog />, { wrapper: makeWrapper() })

    fireEvent.click(screen.getByTestId('open-create-dialog'))

    await waitFor(() => {
      // Dialog contains the confirm-create-key button (unique to dialog)
      expect(screen.getByTestId('confirm-create-key')).toBeInTheDocument()
    })
  })

  it('shows confirmation text before creating', async () => {
    render(<KeyCreateDialog />, { wrapper: makeWrapper() })
    fireEvent.click(screen.getByTestId('open-create-dialog'))

    await waitFor(() => {
      // Look for the dialog-specific description (unique text about storing securely)
      expect(screen.getByText(/cannot be retrieved later/i)).toBeInTheDocument()
    })
  })

  it('closes dialog when Cancel is clicked', async () => {
    render(<KeyCreateDialog />, { wrapper: makeWrapper() })
    fireEvent.click(screen.getByTestId('open-create-dialog'))

    await waitFor(() => {
      screen.getByText(/cancel/i)
    })

    fireEvent.click(screen.getByText(/cancel/i))

    await waitFor(() => {
      expect(screen.queryByTestId('key-create-dialog-content')).toBeNull()
    })
  })

  // ─── Key creation ────────────────────────────────────────────────────────

  it('shows full key in code block after successful creation', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => MOCK_KEY_RESPONSE,
    } as Response)

    render(<KeyCreateDialog />, { wrapper: makeWrapper() })
    fireEvent.click(screen.getByTestId('open-create-dialog'))

    await waitFor(() => {
      screen.getByTestId('confirm-create-key')
    })
    fireEvent.click(screen.getByTestId('confirm-create-key'))

    await waitFor(() => {
      const keyCode = screen.getByTestId('created-key-code')
      expect(keyCode.textContent).toBe(MOCK_KEY_RESPONSE.full_key)
    })
  })

  it('shows security warning after key creation', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => MOCK_KEY_RESPONSE,
    } as Response)

    render(<KeyCreateDialog />, { wrapper: makeWrapper() })
    fireEvent.click(screen.getByTestId('open-create-dialog'))

    await waitFor(() => {
      screen.getByTestId('confirm-create-key')
    })
    fireEvent.click(screen.getByTestId('confirm-create-key'))

    await waitFor(() => {
      expect(screen.getByText(/won't be able to see it again/i)).toBeInTheDocument()
    })
  })

  it('shows copy button after key creation', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => MOCK_KEY_RESPONSE,
    } as Response)

    render(<KeyCreateDialog />, { wrapper: makeWrapper() })
    fireEvent.click(screen.getByTestId('open-create-dialog'))

    await waitFor(() => {
      screen.getByTestId('confirm-create-key')
    })
    fireEvent.click(screen.getByTestId('confirm-create-key'))

    await waitFor(() => {
      expect(screen.getByTestId('copy-key-button')).toBeInTheDocument()
    })
  })

  it('copy button calls clipboard.writeText with full key', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => MOCK_KEY_RESPONSE,
    } as Response)

    render(<KeyCreateDialog />, { wrapper: makeWrapper() })
    fireEvent.click(screen.getByTestId('open-create-dialog'))

    await waitFor(() => {
      screen.getByTestId('confirm-create-key')
    })
    fireEvent.click(screen.getByTestId('confirm-create-key'))

    await waitFor(() => {
      screen.getByTestId('copy-key-button')
    })
    fireEvent.click(screen.getByTestId('copy-key-button'))

    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(MOCK_KEY_RESPONSE.full_key)
    })
  })

  it('closes dialog and clears key when Done is clicked', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => MOCK_KEY_RESPONSE,
    } as Response)

    render(<KeyCreateDialog />, { wrapper: makeWrapper() })
    fireEvent.click(screen.getByTestId('open-create-dialog'))

    await waitFor(() => {
      screen.getByTestId('confirm-create-key')
    })
    fireEvent.click(screen.getByTestId('confirm-create-key'))

    await waitFor(() => {
      screen.getByTestId('done-button')
    })
    fireEvent.click(screen.getByTestId('done-button'))

    await waitFor(() => {
      expect(screen.queryByTestId('created-key-code')).toBeNull()
    })
  })

  // ─── Error handling ──────────────────────────────────────────────────────

  it('shows error message when key creation fails', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({ error: 'Server error' }),
    } as Response)

    render(<KeyCreateDialog />, { wrapper: makeWrapper() })
    fireEvent.click(screen.getByTestId('open-create-dialog'))

    await waitFor(() => {
      screen.getByTestId('confirm-create-key')
    })
    fireEvent.click(screen.getByTestId('confirm-create-key'))

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument()
    })
  })
})
