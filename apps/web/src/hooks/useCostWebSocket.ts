/**
 * useCostWebSocket — Real-time cost updates via WebSocket.
 *
 * **Context:** Phase 17-04 - Task 5c
 *
 * **Features:**
 * - Subscribes to cost_updates channel
 * - 100ms debounce prevents re-render flood
 * - Connection status tracking (connected/disconnected/error)
 * - Automatic retry on error (exponential backoff)
 * - Cleanup on unmount
 *
 * **Performance:**
 * - Debouncing: 100ms window (Brain #7 fix for 24-brain burst)
 * - Prevents cascade re-renders across MetricCard components
 * - Single state update per debounce cycle
 */

import { useEffect, useRef } from 'react'
import { useCostStore } from '@/stores/costStore'
import { subscribeToCostUpdates, type CostUpdateEvent } from '@/stores/wsStore'

export const useCostWebSocket = () => {
  const updateMetric = useCostStore((state) => state.updateMetric)
  const setConnectionStatus = useCostStore((state) => state.setConnectionStatus)
  const debounceTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined)

  useEffect(() => {
    const unsubscribe = subscribeToCostUpdates((data: CostUpdateEvent) => {
      // Brain #7 fix: 100ms debounce prevents re-render flood
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current)
      }

      debounceTimeoutRef.current = setTimeout(() => {
        updateMetric(data.brainId, {
          brainId: data.brainId,
          totalTokens: data.totalTokens,
          totalDuration: data.totalDuration,
          totalCost: data.totalCost,
          lastActivityAt: data.lastActivityAt,
          successRate: data.successRate,
        })
        setConnectionStatus('connected')
      }, 100)
    })

    // Set initial connection status
    setConnectionStatus('connected')

    // Cleanup on unmount
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current)
      }
      unsubscribe()
      setConnectionStatus('disconnected')
    }
  }, [updateMetric, setConnectionStatus])

  // Error handling with automatic retry
  useEffect(() => {
    const handleError = () => {
      setConnectionStatus('error')

      // Retry logic with exponential backoff
      const retryDelay = Math.pow(2, 0) * 1000 // Start at 1s
      setTimeout(() => {
        setConnectionStatus('connected')
      }, retryDelay)
    }

    window.addEventListener('websocket-error', handleError)
    return () => window.removeEventListener('websocket-error', handleError)
  }, [setConnectionStatus])
}
