/**
 * Mock data generation utilities for testing
 */

import type { Thread } from '@/components/messaging/ThreadList'

/**
 * Generate a mock thread for testing
 */
export function generateMockThread(overrides?: Partial<Thread>): Thread {
  return {
    id: `thread-${Math.random().toString(36).substring(7)}`,
    channel: 'whatsapp',
    subject: `Test thread ${Math.floor(Math.random() * 1000)}`,
    preview: 'This is a preview message content for testing...',
    timestamp: Date.now() - Math.floor(Math.random() * 86400000), // Random time in last 24h
    unread: Math.random() > 0.5,
    status: 'active',
    ...overrides,
  }
}

/**
 * Generate multiple mock threads for testing
 */
export function generateMockThreads(count: number, overrides?: Partial<Thread>): Thread[] {
  return Array.from({ length: count }, (_, i) =>
    generateMockThread({
      ...overrides,
      id: `thread-${i}`,
      subject: `Test thread ${i}`,
    })
  )
}
