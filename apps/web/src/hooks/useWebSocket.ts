/**
 * useWebSocket — Generic WebSocket hook with reconnect logic.
 *
 * B2.7 spec:
 *   - Accepts a URL string
 *   - Reconnects on unexpected close (max 3 attempts, exponential backoff)
 *   - Exposes connection status and last received message
 *   - Cleans up on unmount
 *
 * Used by BrainStatusFeed to connect to ws://rust:8002/ws/events.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

export interface UseWebSocketOptions {
  /** Maximum reconnect attempts on unexpected disconnect (default: 3). */
  maxReconnectAttempts?: number
  /** Base delay in ms before first reconnect attempt (default: 1000). */
  reconnectBaseDelayMs?: number
  /** Called whenever a message is received. */
  onMessage?: (event: MessageEvent) => void
  /** Called when the connection opens. */
  onOpen?: () => void
  /** Called when the connection closes (clean or unexpected). */
  onClose?: (event: CloseEvent) => void
  /** Called on WebSocket error. */
  onError?: (event: Event) => void
}

export interface UseWebSocketReturn {
  status: WebSocketStatus
  /** Number of reconnect attempts made so far. */
  reconnectCount: number
  /** Send a text message over the socket (no-op when disconnected). */
  send: (data: string) => void
  /** Manually disconnect and stop reconnecting. */
  disconnect: () => void
}

const MAX_RECONNECT_ATTEMPTS = 3
const RECONNECT_BASE_DELAY_MS = 1_000

export function useWebSocket(
  url: string | null,
  options: UseWebSocketOptions = {},
): UseWebSocketReturn {
  const {
    maxReconnectAttempts = MAX_RECONNECT_ATTEMPTS,
    reconnectBaseDelayMs = RECONNECT_BASE_DELAY_MS,
    onMessage,
    onOpen,
    onClose,
    onError,
  } = options

  const [status, setStatus] = useState<WebSocketStatus>('disconnected')
  const [reconnectCount, setReconnectCount] = useState(0)

  const socketRef = useRef<WebSocket | null>(null)
  const reconnectCountRef = useRef(0)
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const intentionalCloseRef = useRef(false)

  const clearReconnectTimer = () => {
    if (reconnectTimerRef.current !== null) {
      clearTimeout(reconnectTimerRef.current)
      reconnectTimerRef.current = null
    }
  }

  const connect = useCallback(
    (connectUrl: string) => {
      // Guard: never connect in SSR context
      if (typeof window === 'undefined') return

      intentionalCloseRef.current = false
      setStatus('connecting')

      const ws = new WebSocket(connectUrl)
      socketRef.current = ws

      ws.onopen = () => {
        reconnectCountRef.current = 0
        setReconnectCount(0)
        setStatus('connected')
        onOpen?.()
      }

      ws.onmessage = (event: MessageEvent) => {
        onMessage?.(event)
      }

      ws.onerror = (event: Event) => {
        setStatus('error')
        onError?.(event)
        // onclose fires after onerror — reconnect logic lives there
      }

      ws.onclose = (event: CloseEvent) => {
        socketRef.current = null
        onClose?.(event)

        if (intentionalCloseRef.current) {
          setStatus('disconnected')
          return
        }

        const attempt = reconnectCountRef.current
        if (attempt < maxReconnectAttempts) {
          const delay = reconnectBaseDelayMs * Math.pow(2, attempt)
          reconnectCountRef.current = attempt + 1
          setReconnectCount(attempt + 1)
          setStatus('connecting')

          reconnectTimerRef.current = setTimeout(() => {
            connect(connectUrl)
          }, delay)
        } else {
          setStatus('disconnected')
        }
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [maxReconnectAttempts, reconnectBaseDelayMs],
  )

  const disconnect = useCallback(() => {
    intentionalCloseRef.current = true
    clearReconnectTimer()
    socketRef.current?.close()
    socketRef.current = null
    setStatus('disconnected')
    reconnectCountRef.current = 0
    setReconnectCount(0)
  }, [])

  const send = useCallback((data: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(data)
    }
  }, [])

  useEffect(() => {
    if (!url) {
      disconnect()
      return
    }

    connect(url)

    return () => {
      intentionalCloseRef.current = true
      clearReconnectTimer()
      socketRef.current?.close()
      socketRef.current = null
    }
    // connect is stable; url change triggers reconnect
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url])

  return { status, reconnectCount, send, disconnect }
}
