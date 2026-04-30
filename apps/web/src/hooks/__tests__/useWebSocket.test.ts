/**
 * useWebSocket Hook Tests — B2.11
 *
 * Verifies:
 *   1. Hook starts in 'connecting' when URL is provided
 *   2. Transitions to 'connected' on socket open
 *   3. onMessage fires and state update < 500ms (B2.11 spec)
 *   4. Reconnect attempts capped at maxReconnectAttempts (3)
 *   5. disconnect() stops reconnect loop
 *   6. null URL leaves hook in 'disconnected' state
 */

import { act, renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { useWebSocket } from '../useWebSocket'

// ------------------------------------------------------------------ mock WS

type MockWS = InstanceType<typeof MockWebSocket>

let lastInstance: MockWS | null = null
const instanceHistory: MockWS[] = []
let constructorCallCount = 0

class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  onopen: (() => void) | null = null
  onclose: ((e: Partial<CloseEvent>) => void) | null = null
  onmessage: ((e: MessageEvent) => void) | null = null
  onerror: ((e: Event) => void) | null = null
  readyState: number = MockWebSocket.CONNECTING
  send = vi.fn()
  close = vi.fn(() => {
    this.readyState = MockWebSocket.CLOSED
    this.onclose?.({ wasClean: true, code: 1000 } as CloseEvent)
  })

  constructor(_url: string) {
    constructorCallCount++
    lastInstance = this
    instanceHistory.push(this)
  }

  // Test helpers
  _open() {
    this.readyState = MockWebSocket.OPEN
    this.onopen?.()
  }

  _message(data: string) {
    this.onmessage?.(new MessageEvent('message', { data }))
  }

  _close(wasClean = false) {
    this.readyState = MockWebSocket.CLOSED
    this.onclose?.({ wasClean, code: wasClean ? 1000 : 1006 } as CloseEvent)
  }

  _error() {
    this.onerror?.(new Event('error'))
  }
}

// ------------------------------------------------------------------ setup

beforeEach(() => {
  lastInstance = null
  instanceHistory.length = 0
  constructorCallCount = 0
  vi.stubGlobal('WebSocket', MockWebSocket)
  vi.useFakeTimers()
})

afterEach(() => {
  vi.runOnlyPendingTimers()
  vi.useRealTimers()
  vi.unstubAllGlobals()
  vi.clearAllMocks()
})

// ------------------------------------------------------------------ tests

describe('useWebSocket', () => {
  describe('initial connection', () => {
    it('starts in connecting state when URL provided', () => {
      const { result } = renderHook(() =>
        useWebSocket('ws://localhost:8002/ws/events'),
      )
      expect(result.current.status).toBe('connecting')
      expect(constructorCallCount).toBe(1)
    })

    it('stays disconnected when URL is null', () => {
      const { result } = renderHook(() => useWebSocket(null))
      expect(result.current.status).toBe('disconnected')
      expect(constructorCallCount).toBe(0)
    })

    it('transitions to connected when socket opens', () => {
      const { result } = renderHook(() =>
        useWebSocket('ws://localhost:8002/ws/events'),
      )

      act(() => { lastInstance!._open() })

      expect(result.current.status).toBe('connected')
    })

    it('resets reconnectCount to 0 after successful open', () => {
      const { result } = renderHook(() =>
        useWebSocket('ws://localhost:8002/ws/events'),
      )

      act(() => { lastInstance!._open() })

      expect(result.current.reconnectCount).toBe(0)
    })
  })

  describe('message handling', () => {
    it('calls onMessage callback when server sends data', () => {
      const onMessage = vi.fn()
      renderHook(() =>
        useWebSocket('ws://localhost:8002/ws/events', { onMessage }),
      )

      act(() => {
        lastInstance!._open()
        lastInstance!._message('{"trace_id":"t1","status":"dispatched"}')
      })

      expect(onMessage).toHaveBeenCalledOnce()
      const event: MessageEvent = onMessage.mock.calls[0][0]
      expect(event.data).toContain('trace_id')
    })

    it('B2.11: state update from WS message occurs < 500ms', () => {
      const received: string[] = []
      renderHook(() =>
        useWebSocket('ws://localhost:8002/ws/events', {
          onMessage: (e: MessageEvent) => received.push(e.data),
        }),
      )

      act(() => { lastInstance!._open() })

      const before = performance.now()
      act(() => {
        lastInstance!._message('{"trace_id":"perf","status":"completed"}')
      })
      const elapsed = performance.now() - before

      // Synchronous dispatch — always well under 500ms
      expect(elapsed).toBeLessThan(500)
      expect(received).toHaveLength(1)
      expect(received[0]).toContain('perf')
    })
  })

  describe('reconnect logic', () => {
    it('attempts to reconnect on unexpected close', () => {
      renderHook(() =>
        useWebSocket('ws://localhost:8002/ws/events', {
          maxReconnectAttempts: 3,
          reconnectBaseDelayMs: 100,
        }),
      )

      act(() => {
        lastInstance!._open()
        lastInstance!._close(false) // unexpected
      })

      // Advance past first reconnect delay (100ms × 2^0 = 100ms)
      act(() => { vi.advanceTimersByTime(200) })

      expect(instanceHistory).toHaveLength(2)
    })

    it('increments reconnectCount after unexpected close', () => {
      const { result } = renderHook(() =>
        useWebSocket('ws://localhost:8002/ws/events', {
          maxReconnectAttempts: 3,
          reconnectBaseDelayMs: 10,
        }),
      )

      act(() => {
        lastInstance!._open()
        lastInstance!._close(false)
      })

      // reconnectCount is synchronously incremented before the timer fires
      expect(result.current.reconnectCount).toBe(1)
    })

    it('stops reconnecting after maxReconnectAttempts (3)', () => {
      const { result } = renderHook(() =>
        useWebSocket('ws://localhost:8002/ws/events', {
          maxReconnectAttempts: 3,
          reconnectBaseDelayMs: 10,
        }),
      )

      // Each _close triggers timer; advance + trigger again until exhausted
      for (let i = 0; i < 3; i++) {
        act(() => {
          lastInstance!._close(false)
          vi.advanceTimersByTime(200) // triggers next reconnect
        })
      }
      // Final close — no more reconnects remaining
      act(() => {
        lastInstance!._close(false)
      })

      // Status is set synchronously inside onclose handler
      expect(result.current.status).toBe('disconnected')
      // No more than 4 total instances (1 initial + 3 reconnects)
      expect(instanceHistory.length).toBeLessThanOrEqual(4)
    })

    it('does NOT reconnect on intentional close', () => {
      const { result } = renderHook(() =>
        useWebSocket('ws://localhost:8002/ws/events'),
      )

      act(() => { lastInstance!._open() })

      act(() => { result.current.disconnect() })

      act(() => { vi.advanceTimersByTime(5_000) })

      // Only 1 WebSocket ever created
      expect(instanceHistory).toHaveLength(1)
    })
  })

  describe('disconnect', () => {
    it('closes the socket and sets status to disconnected', () => {
      const { result } = renderHook(() =>
        useWebSocket('ws://localhost:8002/ws/events'),
      )

      act(() => { lastInstance!._open() })

      const ws = lastInstance!

      act(() => { result.current.disconnect() })

      expect(result.current.status).toBe('disconnected')
      expect(ws.close).toHaveBeenCalled()
    })

    it('resets reconnectCount to 0 on disconnect', () => {
      const { result } = renderHook(() =>
        useWebSocket('ws://localhost:8002/ws/events', {
          maxReconnectAttempts: 3,
          reconnectBaseDelayMs: 10,
        }),
      )

      // Trigger one reconnect attempt
      act(() => {
        lastInstance!._close(false)
        vi.advanceTimersByTime(20)
      })

      // Now disconnect intentionally
      act(() => { result.current.disconnect() })

      expect(result.current.reconnectCount).toBe(0)
    })
  })

  describe('send', () => {
    it('sends data when socket is open', () => {
      const { result } = renderHook(() =>
        useWebSocket('ws://localhost:8002/ws/events'),
      )

      act(() => { lastInstance!._open() })

      const ws = lastInstance!

      act(() => { result.current.send('{"ping":true}') })

      expect(ws.send).toHaveBeenCalledWith('{"ping":true}')
    })

    it('is a no-op when URL is null (no socket created)', () => {
      const { result } = renderHook(() => useWebSocket(null))

      act(() => { result.current.send('hello') })

      // No WebSocket was ever created
      expect(constructorCallCount).toBe(0)
    })
  })
})
