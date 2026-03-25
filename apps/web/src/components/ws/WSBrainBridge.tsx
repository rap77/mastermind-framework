'use client'

import { useEffect, useState } from 'react'
import { useWSStore } from '@/stores/wsStore'
import { useBrainStore } from '@/stores/brainStore'
import { WSMessageSchema } from '@/types/api'

/**
 * WebSocket bridge component for real-time brain updates.
 * Fetches auth token server-side, establishes WS connection, and routes
 * validated events to the brain store. Invisible event router (renders null).
 * @param taskId - Task ID for WS subscription, or null for connection only.
 */
export function WSBrainBridge({ taskId }: { taskId: string | null }) {
  const [token, setToken] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const subscribe = useWSStore(state => state.subscribe)
  const connect = useWSStore(state => state.connect)
  const disconnect = useWSStore(state => state.disconnect)
  const updateBrain = useBrainStore(state => state.updateBrain)
  const pushHistorySnapshot = useBrainStore(state => state.pushHistorySnapshot)
  const incrementInvocationCount = useBrainStore(state => state.incrementInvocationCount)

  // Fetch token from /api/auth/token endpoint (server-side cookie read)
  useEffect(() => {
    async function fetchToken() {
      try {
        const response = await fetch('/api/auth/token')
        if (!response.ok) {
          setError('Failed to fetch authentication token')
          return
        }
        const data = await response.json()
        setToken(data.access_token)
        setError(null)
      } catch {
        setError('Network error fetching token')
      }
    }

    fetchToken()
  }, [])

  // Connect to WS when taskId and token are available.
  // CRITICAL: only disconnect on cleanup if WE initiated the connection.
  // If taskId is null, we never connected — calling disconnect() would kill
  // a connection started by CommandCenterWrapper (race condition).
  useEffect(() => {
    if (!taskId || !token) return
    connect(taskId, token)
    return () => disconnect()
  }, [taskId, token, connect, disconnect])

  // Subscribe to WS events and validate with Zod before updating store
  useEffect(() => {
    const unsubscribe = subscribe('task_update_batch', (data) => {
      // Validate with Zod BEFORE updating Zustand (CONTEXT.md requirement)
      const result = WSMessageSchema.safeParse(data)
      if (!result.success) {
        // Silent fail for invalid messages - Zod validation catches malformed data
        return
      }

      // Process each brain event
      for (const event of result.data.data) {
        updateBrain({
          id: event.brain_id,
          status: event.status,
          lastUpdated: event.timestamp,
        })
        // Ghost Trace: capture snapshot after each WS event (Phase 08 replay prep)
        pushHistorySnapshot()
        // Track per-brain activation count for BrainNode ×N display
        if (event.status === 'active') {
          incrementInvocationCount(event.brain_id)
        }
      }
    })
    return unsubscribe
  }, [subscribe, updateBrain, pushHistorySnapshot, incrementInvocationCount])

  // Log error in development for debugging
  useEffect(() => {
    if (error && process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console -- Development-only error logging
      console.error('[WSBrainBridge]', error)
    }
  }, [error])

  return null  // No render output — invisible event router
}
