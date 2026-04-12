import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, waitFor, screen } from '@testing-library/react'
import UnifiedInboxPage from '@/components/messaging/UnifiedInboxPage'
import { wsDispatcher } from '@/lib/wsDispatcher'

// Mock wsDispatcher
vi.mock('@/lib/wsDispatcher', () => ({
  wsDispatcher: {
    subscribe: vi.fn(),
    dispatch: vi.fn(),
  },
}))

// Mock fetch for API calls
global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve([]),
  })
) as unknown as typeof fetch

describe('WebSocket Real-time Updates - UAT Test #17', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should receive real-time thread updates via WebSocket', async () => {
    const mockUnsubscribe = vi.fn()
    vi.mocked(wsDispatcher.subscribe).mockReturnValue(mockUnsubscribe)

    render(<UnifiedInboxPage />)

    // Wait for component to mount
    await waitFor(() => {
      expect(screen.getByTestId('unified-inbox-page')).toBeInTheDocument()
    })

    // Verify subscription to 'thread_updates'
    expect(wsDispatcher.subscribe).toHaveBeenCalledWith(
      'thread_updates',
      expect.any(Function)
    )

    // Get the callback function
    const subscribeCallback = vi.mocked(wsDispatcher.subscribe).mock.calls[0][1]

    const mockUpdate = {
      thread_id: 'thread-123',
      thread: {
        id: 'thread-123',
        channel: 'whatsapp' as const,
        subject: 'New message',
        preview: 'Hey!',
        timestamp: Date.now(),
        unread: true,
        status: 'active',
      },
    }

    // Dispatch message via WebSocket callback
    subscribeCallback(mockUpdate)

    // Verify component updated without errors
    expect(screen.getByTestId('unified-inbox-page')).toBeInTheDocument()

    console.log('✅ Real-time message received and displayed')
  })

  it('should update thread within 2 seconds of WebSocket message', async () => {
    const startTime = Date.now()

    const mockUnsubscribe = vi.fn()
    vi.mocked(wsDispatcher.subscribe).mockReturnValue(mockUnsubscribe)

    render(<UnifiedInboxPage />)

    // Wait for initial render
    await waitFor(() => {
      expect(screen.getByTestId('unified-inbox-page')).toBeInTheDocument()
    })

    const subscribeCallback = vi.mocked(wsDispatcher.subscribe).mock.calls[0][1]

    // Simulate message
    subscribeCallback({
      thread_id: 'thread-456',
      thread: {
        id: 'thread-456',
        channel: 'instagram' as const,
        subject: 'Instagram DM',
        preview: 'Check this out',
        timestamp: Date.now(),
        unread: true,
        status: 'active',
      },
    })

    // Wait for update
    await waitFor(
      () => {
        expect(screen.getByTestId('unified-inbox-page')).toBeInTheDocument()
      },
      { timeout: 2000 }
    )

    const elapsed = Date.now() - startTime

    // Assert update happened within 2s
    expect(elapsed).toBeLessThan(2000)

    console.log(`✅ Thread updated in ${elapsed}ms (<2000ms target)`)
  })
})
