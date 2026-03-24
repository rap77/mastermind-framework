/**
 * Log Parser Utilities
 *
 * **Purpose:** Parse WebSocket log events into typed LogLine objects
 * **Context:** Phase 08-03 — Engine Room live log infrastructure
 */

// ─── Types ─────────────────────────────────────────────────────────────────

export interface LogLine {
  id: string // UUID for React key
  timestamp: number // Unix milliseconds
  brainId: string // e.g., "marketing-01"
  brainName: string // e.g., "Marketing Strategist"
  level: 'info' | 'warn' | 'error' // log level
  message: string // log message text
  metadata?: Record<string, unknown> // optional structured data
}

/** Raw WS event structure from log:line events */
export interface WS_LogEvent {
  ts?: number
  brain_id?: string
  brain_name?: string
  level?: string
  msg?: string
  metadata?: Record<string, unknown>
  [key: string]: unknown
}

// ─── Helpers ───────────────────────────────────────────────────────────────

function generateId(): string {
  // Use crypto.randomUUID if available (browser), fallback to Math.random
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

function isValidLevel(level: unknown): level is 'info' | 'warn' | 'error' {
  return level === 'info' || level === 'warn' || level === 'error'
}

// ─── Functions ─────────────────────────────────────────────────────────────

/**
 * Parse a raw WS log event into a typed LogLine object.
 * Returns null if the event is invalid/missing required fields.
 */
export function parseLogLine(event: WS_LogEvent): LogLine | null {
  if (!event || typeof event !== 'object') return null

  const brainId = typeof event.brain_id === 'string' && event.brain_id ? event.brain_id : null
  const message = typeof event.msg === 'string' ? event.msg : null

  // brainId and message are required
  if (!brainId || message === null) return null

  const timestamp =
    typeof event.ts === 'number' && isFinite(event.ts)
      ? event.ts
      : Date.now()

  const brainName =
    typeof event.brain_name === 'string' && event.brain_name
      ? event.brain_name
      : brainId

  const rawLevel = event.level
  const level: 'info' | 'warn' | 'error' = isValidLevel(rawLevel) ? rawLevel : 'info'

  const logLine: LogLine = {
    id: generateId(),
    timestamp,
    brainId,
    brainName,
    level,
    message,
  }

  if (event.metadata && typeof event.metadata === 'object') {
    logLine.metadata = event.metadata
  }

  return logLine
}

/**
 * Filter logs by selected levels.
 * If levels Set is empty, returns all logs.
 */
export function filterLogsByLevel(logs: LogLine[], levels: Set<string>): LogLine[] {
  if (levels.size === 0) return logs
  return logs.filter((log) => levels.has(log.level))
}

/**
 * Filter logs to a single brain (isolation mode).
 */
export function filterLogsByBrain(logs: LogLine[], brainId: string): LogLine[] {
  return logs.filter((log) => log.brainId === brainId)
}

/**
 * Format a Unix milliseconds timestamp to HH:MM:SS.mmm
 * Example: 1711234567123 → "14:23:45.123"
 */
export function formatTimestamp(timestamp: number): string {
  const date = new Date(timestamp)
  const hh = String(date.getHours()).padStart(2, '0')
  const mm = String(date.getMinutes()).padStart(2, '0')
  const ss = String(date.getSeconds()).padStart(2, '0')
  const ms = String(date.getMilliseconds()).padStart(3, '0')
  return `${hh}:${mm}:${ss}.${ms}`
}

/**
 * Get Tailwind color class for a log level.
 */
export function colorForLevel(level: string): string {
  switch (level) {
    case 'warn':
      return 'text-yellow-500'
    case 'error':
      return 'text-red-500'
    default:
      return 'text-blue-500'
  }
}
