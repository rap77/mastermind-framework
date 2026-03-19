import { create } from 'zustand'

type Listener = (data: unknown) => void

interface WSState {
  socket: WebSocket | null
  taskId: string | null
  token: string | null
  connected: boolean
  error: string | null
  reconnectAttempts: number
  listeners: Map<string, Set<Listener>>
  connect: (taskId: string, token: string) => void
  disconnect: () => void
  reconnect: (clearState: boolean) => void  // Brain #7: WS reconciliation
  subscribe: (event: string, listener: Listener) => () => void
  setError: (error: string | null) => void
}

// Reconnect configuration
const MAX_RECONNECT_ATTEMPTS = 5
const RECONNECT_DELAY_MS = 1000

export const useWSStore = create<WSState>((set, get) => ({
  socket: null,
  taskId: null,
  token: null,
  connected: false,
  error: null,
  reconnectAttempts: 0,
  listeners: new Map(),

  connect: (taskId, token) => {
    // CRITICAL: Guard for SSR — this action must only run in browser (Pitfall 2)
    if (typeof window === 'undefined') return

    const { socket, disconnect } = get()
    if (socket && get().taskId === taskId) return  // Already connected to same task

    disconnect()

    try {
      const ws = new WebSocket(
        `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/tasks/${taskId}?token=${token}`
      )

      ws.onopen = () => {
        set({ connected: true, error: null, reconnectAttempts: 0 })
      }

      ws.onclose = (event) => {
        set({ socket: null, connected: false, taskId: null, token: null })

        // Auto-reconnect with exponential backoff if not intentionally closed
        if (!event.wasClean && get().reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          const delay = RECONNECT_DELAY_MS * Math.pow(2, get().reconnectAttempts)
          setTimeout(() => {
            const { taskId, token } = get()
            if (taskId && token) {
              set({ reconnectAttempts: get().reconnectAttempts + 1 })
              get().connect(taskId, token)
            }
          }, delay)
        }
      }

      ws.onerror = () => {
        // WebSocket error is always followed by onclose - handle there
        set({ error: 'WebSocket connection error' })
      }

      ws.onmessage = (event) => {
        // RAF batching handled in brainStore — raw dispatch here (Pitfall 4)
        const msg = JSON.parse(event.data)
        const { listeners } = get()
        const handlers = listeners.get(msg.type)
        if (handlers) handlers.forEach(fn => fn(msg.data))
      }

      set({ socket: ws, taskId, token, connected: false })
    } catch (err) {
      set({ error: 'Failed to create WebSocket connection' })
    }
  },

  disconnect: () => {
    const { socket } = get()
    socket?.close()
    set({ socket: null, connected: false, taskId: null, token: null, reconnectAttempts: 0 })
  },

  reconnect: (clearState = false) => {
    // Brain #7: WS reconciliation after drop — clear stale state
    const { taskId, token } = get()
    if (!taskId || !token) return

    get().disconnect()

    if (clearState) {
      // Signal brainStore to clear stale data
      const clearEvent = { type: 'ws:reconnect', data: null }
      const { listeners } = get()
      const handlers = listeners.get('ws:reconnect')
      if (handlers) handlers.forEach(fn => fn(clearEvent))
    }

    // Reconnect with same credentials
    set({ reconnectAttempts: 0 })
    get().connect(taskId, token)
  },

  subscribe: (event, listener) => {
    const { listeners } = get()
    if (!listeners.has(event)) listeners.set(event, new Set())
    listeners.get(event)!.add(listener)
    return () => listeners.get(event)?.delete(listener)
  },

  setError: (error) => set({ error }),
}))
