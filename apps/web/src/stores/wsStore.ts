import { create } from 'zustand'

type Listener = (data: unknown) => void

interface WSState {
  socket: WebSocket | null
  taskId: string | null
  token: string | null
  connected: boolean
  listeners: Map<string, Set<Listener>>
  connect: (taskId: string, token: string) => void
  disconnect: () => void
  reconnect: (clearState: boolean) => void  // Brain #7: WS reconciliation
  subscribe: (event: string, listener: Listener) => () => void
}

export const useWSStore = create<WSState>((set, get) => ({
  socket: null,
  taskId: null,
  token: null,
  connected: false,
  listeners: new Map(),

  connect: (taskId, token) => {
    // CRITICAL: Guard for SSR — this action must only run in browser (Pitfall 2)
    if (typeof window === 'undefined') return

    const { socket, disconnect } = get()
    if (socket && get().taskId === taskId) return  // Already connected to same task

    disconnect()

    const ws = new WebSocket(
      `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/tasks/${taskId}?token=${token}`
    )

    ws.onopen = () => set({ connected: true })
    ws.onclose = () => set({ socket: null, connected: false, taskId: null, token: null })
    ws.onerror = (error) => console.error('WebSocket error:', error)

    ws.onmessage = (event) => {
      // RAF batching handled in brainStore — raw dispatch here (Pitfall 4)
      const msg = JSON.parse(event.data)
      const { listeners } = get()
      const handlers = listeners.get(msg.type)
      if (handlers) handlers.forEach(fn => fn(msg.data))
    }

    set({ socket: ws, taskId, token, connected: false })
  },

  disconnect: () => {
    const { socket } = get()
    socket?.close()
    set({ socket: null, connected: false, taskId: null, token: null })
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
    get().connect(taskId, token)
  },

  subscribe: (event, listener) => {
    const { listeners } = get()
    if (!listeners.has(event)) listeners.set(event, new Set())
    listeners.get(event)!.add(listener)
    return () => listeners.get(event)?.delete(listener)
  },
}))
