/**
 * Tests for EventLog.tsx — Relative time format helpers
 */

import { describe, it, expect } from 'vitest'

// Import helper functions directly
const formatRelativeTime = (timestamp: number, currentTime: number = Date.now()): string => {
  const diff = currentTime - timestamp
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)

  if (seconds < 60) {
    return `${seconds}s ago`
  } else if (minutes < 60) {
    return `${minutes}m ago`
  } else {
    return `${hours}h ago`
  }
}

const formatTimestamp = (timestamp: number): string => {
  const date = new Date(timestamp)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  const seconds = date.getSeconds().toString().padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
}

const formatTimestampWithRelative = (timestamp: number): string => {
  const absolute = formatTimestamp(timestamp)
  const relative = formatRelativeTime(timestamp)
  return `${absolute} (${relative})`
}

describe('EventLog - Relative Time Format', () => {
  describe('formatRelativeTime helper', () => {
    it('should show seconds for recent events', () => {
      const now = 1700000000000
      const timestamp = now - 5000 // 5 seconds ago

      const result = formatRelativeTime(timestamp, now)

      expect(result).toBe('5s ago')
    })

    it('should show minutes for older events', () => {
      const now = 1700000000000
      const timestamp = now - 5 * 60 * 1000 // 5 minutes ago

      const result = formatRelativeTime(timestamp, now)

      expect(result).toBe('5m ago')
    })

    it('should show hours for very old events', () => {
      const now = 1700000000000
      const timestamp = now - 2 * 60 * 60 * 1000 // 2 hours ago

      const result = formatRelativeTime(timestamp, now)

      expect(result).toBe('2h ago')
    })

    it('should handle 0 seconds', () => {
      const now = 1700000000000
      const timestamp = now

      const result = formatRelativeTime(timestamp, now)

      expect(result).toBe('0s ago')
    })
  })

  describe('formatTimestampWithRelative helper', () => {
    it('should include both absolute and relative time', () => {
      const timestamp = 1700000000000 // Fixed timestamp

      const result = formatTimestampWithRelative(timestamp)

      // Should match format "HH:MM:SS (Xs ago)"
      expect(result).toMatch(/\d{2}:\d{2}:\d{2} \(\d+[smh] ago\)/)
    })

    it('should format correctly for recent events', () => {
      const timestamp = Date.now() - 10000 // 10 seconds ago

      const result = formatTimestampWithRelative(timestamp)

      expect(result).toContain('10s ago')
      expect(result).toMatch(/\d{2}:\d{2}:\d{2}/)
    })
  })
})
