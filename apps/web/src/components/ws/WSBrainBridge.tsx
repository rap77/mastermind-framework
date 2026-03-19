'use client'

import { useEffect, useState } from 'react'
import { useWSStore } from '@/stores/wsStore'
import { useBrainStore } from '@/stores/brainStore'
import { WSMessageSchema, type BrainEvent } from '@/types/api'

export function WSBrainBridge({ taskId }: { taskId: string | null }) {
  const [token, setToken] = useState<string | null>(null)
  const subscribe = useWSStore(state => state.subscribe)
  const connect = useWSStore(state => state.connect)
  const disconnect = useWSStore(state => state.disconnect)
  const updateBrain = useBrainStore(state => state.updateBrain)

  // Fetch token from /api/auth/token endpoint (server-side cookie read)
  useEffect(() => {
    async function fetchToken() {
      try {
        const response = await fetch('/api/auth/token')
        if (!response.ok) {
          console.error('Failed to fetch token')
          return
        }
        const data = await response.json()
        setToken(data.access_token)
      } catch (error) {
        console.error('Error fetching token:', error)
      }
    }

    fetchToken()
  }, [])

  // Connect to WS when taskId and token are available
  useEffect(() => {
    if (taskId && token) {
      connect(taskId, token)
    }
    return () => disconnect()
  }, [taskId, token, connect, disconnect])

  // Subscribe to WS events and validate with Zod before updating store
  useEffect(() => {
    const unsubscribe = subscribe('task_update_batch', (data) => {
      // Validate with Zod BEFORE updating Zustand (CONTEXT.md requirement)
      const result = WSMessageSchema.safeParse(data)
      if (!result.success) {
        console.error('Invalid WS message:', result.error)
        return
      }

      // Process each brain event
      for (const event of result.data.data) {
        updateBrain({
          id: event.brain_id,
          status: event.status,
          lastUpdated: event.timestamp,
        })
      }
    })
    return unsubscribe
  }, [subscribe, updateBrain])

  return null  // No render output — invisible event router
}
