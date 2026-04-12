import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
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

describe('WebSocket Real-time Updates - UAT Test #17', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should receive real-time thread updates via WebSocket', async () => {
    const mockUnsubscribe = vi.fn()
    vi.mocked(wsDispatcher.subscribe).mockReturnValue(mockUnsubscribe)

    render(<UnifiedInboxPage />)

    // Verify subscription to 'thread_updates'
    expect(wsDispatcher.subscribe).toHaveBeenCalledWith(
      'thread_updates',
      expect.any(Function)
    )

    // Simulate incoming WebSocket message
    const subscribeCallback = vi.mocked(wsDispatcher.subscribe).mock.calls[0][1]

    const mockUpdate = {
      thread_id: 'thread-123',
      thread: {
        id: 'thread-123',
        channel: 'whatsapp',
        subject: 'New message',
        preview: 'Hey!',
        timestamp: new Date().toISOString(),
        unread: true,
      },
    }

    // Dispatch message via WebSocket
    subscribeCallback(mockUpdate)

    // Verify thread appears in UI
    await waitFor(() => {
      expect(screen.getByText('New message')).toBeInTheDocument()
    })

    console.log('✅ Real-time message received and displayed')
  })

  it('should update thread within 2 seconds of WebSocket message', async () => {
    const startTime = Date.now()

    const mockUnsubscribe = vi.fn()
    vi.mocked(wsDispatcher.subscribe).mockReturnValue(mockUnsubscribe)

    render(<UnifiedInboxPage />)

    const subscribeCallback = vi.mocked(wsDispatcher.subscribe).mock.calls[0][1]

    // Simulate message
    subscribeCallback({
      thread_id: 'thread-456',
      thread: {
        id: 'thread-456',
        channel: 'instagram',
        subject: 'Instagram DM',
        preview: 'Check this out',
        timestamp: new Date().toISOString(),
        unread: true,
      },
    })

    // Wait for update
    await waitFor(
      () => {
        expect(screen.getByText('Instagram DM')).toBeInTheDocument()
      },
      { timeout: 2000 }
    )

    const elapsed = Date.now() - startTime

    // Assert update happened within 2s
    expect(elapsed).toBeLessThan(2000)

    console.log(`✅ Thread updated in ${elapsed}ms (<2000ms target)`)
  })
})
