/**
 * useCostWebSocket Hook Tests
 *
 * **Context:** Phase 17-04 - Task 5c
 *
 * **Tests:**
 * - WebSocket subscription lifecycle
 * - Debouncing prevents re-render flood
 * - Connection status updates
 * - Cleanup on unmount
 * - Error handling with retry
 */

import { renderHook, act, waitFor } from '@testing-library/react'
import { useCostWebSocket } from '../useCostWebSocket'
import { useCostStore } from '@/stores/costStore'
import { subscribeToCostUpdates } from '@/stores/wsStore'

// Mock wsStore
vi.mock('@/stores/wsStore', () => ({
  subscribeToCostUpdates: vi.fn(),
}))

describe('useCostWebSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    // Reset costStore state before each test
    const { resetMetrics } = useCostStore.getState()
    resetMetrics()
  })

  afterEach(() => {
    vi.runOnlyPendingTimers()
    vi.useRealTimers()
  })

  it('should subscribe to cost updates on mount', () => {
    const unsubscribe = vi.fn()
    vi.mocked(subscribeToCostUpdates).mockReturnValue(unsubscribe)

    renderHook(() => useCostWebSocket())

    // Verify subscription was created
    expect(subscribeToCostUpdates).toHaveBeenCalledTimes(1)
    expect(subscribeToCostUpdates).toHaveBeenCalledWith(expect.any(Function))
  })

  it('should set connection status to connected on mount', async () => {
    const unsubscribe = vi.fn()
    vi.mocked(subscribeToCostUpdates).mockReturnValue(unsubscribe)

    renderHook(() => useCostWebSocket())

    // Connection status should be set immediately
    const status = useCostStore.getState().connectionStatus
    expect(status).toBe('connected')
  })

  it('should debounce cost updates (100ms)', async () => {
    const mockCallback = vi.fn()
    vi.mocked(subscribeToCostUpdates).mockImplementation((callback) => {
      mockCallback.mockImplementation(callback)
      return vi.fn()
    })

    renderHook(() => useCostWebSocket())

    // Trigger 5 rapid updates within 50ms
    act(() => {
      for (let i = 0; i < 5; i++) {
        mockCallback({
          brainId: 'brain-01',
          totalTokens: 100 + i,
          totalDuration: 10 + i,
          totalCost: 1 + i,
          lastActivityAt: new Date().toISOString(),
          successRate: 0.9,
        })
      }
    })

    // Advance timer by 50ms (before debounce window)
    act(() => {
      vi.advanceTimersByTime(50)
    })

    // Should NOT have updated yet (debounce still active)
    const metricBefore = useCostStore.getState().metrics['brain-01']
    expect(metricBefore).toBeUndefined()

    // Advance timer past debounce window (100ms)
    act(() => {
      vi.advanceTimersByTime(60)
    })

    // Now should have updated once (debounced)
    const metricAfter = useCostStore.getState().metrics['brain-01']
    expect(metricAfter).toBeDefined()
    // Should have the LAST update, not all 5
    expect(metricAfter?.totalTokens).toBe(104)
  })

  it('should update cost metric after debounce', async () => {
    const mockCallback = vi.fn()
    vi.mocked(subscribeToCostUpdates).mockImplementation((callback) => {
      mockCallback.mockImplementation(callback)
      return vi.fn()
    })

    renderHook(() => useCostWebSocket())

    const testData = {
      brainId: 'brain-02',
      totalTokens: 500,
      totalDuration: 60,
      totalCost: 5.23,
      lastActivityAt: '2026-04-10T12:00:00Z',
      successRate: 0.85,
    }

    act(() => {
      mockCallback(testData)
    })

    // Advance past debounce window
    act(() => {
      vi.advanceTimersByTime(150)
    })

    const metric = useCostStore.getState().metrics['brain-02']
    expect(metric).toEqual(testData)
  })

  it('should unsubscribe and set disconnected status on unmount', () => {
    const unsubscribe = vi.fn()
    vi.mocked(subscribeToCostUpdates).mockReturnValue(unsubscribe)

    const { unmount } = renderHook(() => useCostWebSocket())

    // Clear any pending timers
    act(() => {
      vi.runAllTimers()
    })

    unmount()

    // Verify cleanup
    expect(unsubscribe).toHaveBeenCalledTimes(1)

    const status = useCostStore.getState().connectionStatus
    expect(status).toBe('disconnected')
  })

  it('should clear timeout on unmount', () => {
    const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout')
    const mockCallback = vi.fn()
    vi.mocked(subscribeToCostUpdates).mockImplementation((callback) => {
      mockCallback.mockImplementation(callback)
      return vi.fn()
    })

    const { unmount } = renderHook(() => useCostWebSocket())

    // Trigger a cost update to create a timeout
    act(() => {
      mockCallback({
        brainId: 'brain-01',
        totalTokens: 100,
        totalDuration: 10,
        totalCost: 1,
        lastActivityAt: new Date().toISOString(),
        successRate: 0.9,
      })
    })

    unmount()

    // Verify timeout was cleared
    expect(clearTimeoutSpy).toHaveBeenCalled()
  })

  it('should handle websocket errors with retry', async () => {
    const unsubscribe = vi.fn()
    vi.mocked(subscribeToCostUpdates).mockReturnValue(unsubscribe)

    // Mock window.addEventListener for error handling
    const addEventListenerSpy = vi.spyOn(window, 'addEventListener')
    const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')

    renderHook(() => useCostWebSocket())

    // Verify error listener was added
    expect(addEventListenerSpy).toHaveBeenCalledWith(
      'websocket-error',
      expect.any(Function)
    )

    // Simulate error event
    const errorHandler = addEventListenerSpy.mock.calls.find(
      call => call[0] === 'websocket-error'
    )?.[1] as EventListener

    if (errorHandler) {
      act(() => {
        errorHandler(new Event('websocket-error'))
      })
    }

    // Connection status should be error
    let status = useCostStore.getState().connectionStatus
    expect(status).toBe('error')

    // Fast-forward past retry delay (1000ms)
    act(() => {
      vi.advanceTimersByTime(1100)
    })

    // Should retry and set back to connected
    status = useCostStore.getState().connectionStatus
    expect(status).toBe('connected')

    // Cleanup
    const { unmount } = renderHook(() => useCostWebSocket())
    unmount()

    expect(removeEventListenerSpy).toHaveBeenCalledWith(
      'websocket-error',
      expect.any(Function)
    )
  })

  it('should handle multiple rapid updates without cascade re-renders', async () => {
    const mockCallback = vi.fn()
    vi.mocked(subscribeToCostUpdates).mockImplementation((callback) => {
      mockCallback.mockImplementation(callback)
      return vi.fn()
    })

    renderHook(() => useCostWebSocket())

    // Track how many times store is updated
    let updateCount = 0
    const unsubscribe = useCostStore.subscribe(() => {
      updateCount++
    })

    // Trigger 24 rapid updates (simulating 24-brain burst)
    act(() => {
      for (let i = 0; i < 24; i++) {
        mockCallback({
          brainId: `brain-${String(i).padStart(2, '0')}`,
          totalTokens: 100 + i * 10,
          totalDuration: 10 + i,
          totalCost: 1 + i * 0.5,
          lastActivityAt: new Date().toISOString(),
          successRate: 0.9,
        })
      }
    })

    // Advance past debounce window
    act(() => {
      vi.advanceTimersByTime(150)
    })

    // Should batch into single update (debounce prevents flood)
    // Note: May be 2-3 updates due to React batching, but NOT 24
    expect(updateCount).toBeLessThan(5)

    unsubscribe()
  })
})
