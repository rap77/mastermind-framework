/**
 * WebSocket event dispatcher for real-time updates.
 *
 * Provides a simple pub/sub interface for WebSocket events.
 * Components can subscribe to specific event types and receive updates.
 */

import { logger } from '@/lib/logger'

type Listener = (data: unknown) => void
type Unsubscribe = () => void

/**
 * WebSocket event dispatcher for real-time updates.
 *
 * This class provides a pub/sub interface for WebSocket events, allowing
 * components to subscribe to specific event types and receive updates.
 * Uses a singleton pattern to ensure a single dispatcher instance.
 *
 * @example
 * ```ts
 * // Subscribe to thread updates
 * const unsubscribe = wsDispatcher.subscribe('thread_updates', (data) => {
 *   console.log('Thread updated:', data)
 * })
 *
 * // Later: unsubscribe
 * unsubscribe()
 * ```
 */
class WSEventDispatcher {
  private listeners: Map<string, Set<Listener>> = new Map()

  /**
   * Subscribe to a WebSocket event.
   * @param event - Event name (e.g., 'thread_updates', 'new_message')
   * @param listener - Callback function to handle the event
   * @returns Unsubscribe function
   */
  subscribe(event: string, listener: Listener): Unsubscribe {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(listener)

    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(event)
      if (listeners) {
        listeners.delete(listener)
        if (listeners.size === 0) {
          this.listeners.delete(event)
        }
      }
    }
  }

  /**
   * Dispatch an event to all subscribers.
   * @param event - Event name
   * @param data - Event data to pass to listeners
   */
  dispatch(event: string, data: unknown): void {
    const listeners = this.listeners.get(event)
    if (listeners) {
      listeners.forEach((listener) => {
        try {
          listener(data)
        } catch (error) {
          logger.error(`Error in ${event} listener:`, error)
        }
      })
    }
  }

  /**
   * Clear all listeners for an event or all events.
   * @param event - Event name (optional, clears all if not provided)
   */
  clear(event?: string): void {
    if (event) {
      this.listeners.delete(event)
    } else {
      this.listeners.clear()
    }
  }
}

// Singleton instance
export const wsDispatcher = new WSEventDispatcher()
