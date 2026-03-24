/**
 * log-parser Tests
 *
 * **Purpose:** Verify log parsing, filtering, formatting utilities
 * **Context:** Phase 08-03 — Task 1
 */

import { describe, it, expect } from 'vitest'
import {
  parseLogLine,
  filterLogsByLevel,
  filterLogsByBrain,
  formatTimestamp,
  colorForLevel,
  type LogLine,
  type WS_LogEvent,
} from '../log-parser'

// ─── parseLogLine ──────────────────────────────────────────────────────────

describe('parseLogLine', () => {
  it('returns null for null input', () => {
    expect(parseLogLine(null as unknown as WS_LogEvent)).toBeNull()
  })

  it('returns null for non-object input', () => {
    expect(parseLogLine('string' as unknown as WS_LogEvent)).toBeNull()
  })

  it('returns null when brainId is missing', () => {
    const event: WS_LogEvent = { ts: Date.now(), msg: 'hello', level: 'info' }
    expect(parseLogLine(event)).toBeNull()
  })

  it('returns null when message is missing', () => {
    const event: WS_LogEvent = { ts: Date.now(), brain_id: 'marketing-01', level: 'info' }
    expect(parseLogLine(event)).toBeNull()
  })

  it('parses a valid event correctly', () => {
    const ts = 1711234567123
    const event: WS_LogEvent = {
      ts,
      brain_id: 'marketing-01',
      brain_name: 'Marketing Strategist',
      level: 'info',
      msg: 'Task started',
    }
    const result = parseLogLine(event)
    expect(result).not.toBeNull()
    expect(result!.timestamp).toBe(ts)
    expect(result!.brainId).toBe('marketing-01')
    expect(result!.brainName).toBe('Marketing Strategist')
    expect(result!.level).toBe('info')
    expect(result!.message).toBe('Task started')
    expect(result!.id).toBeTruthy()
  })

  it('uses brainId as brainName when brain_name is missing', () => {
    const event: WS_LogEvent = {
      ts: Date.now(),
      brain_id: 'marketing-01',
      level: 'info',
      msg: 'Task started',
    }
    const result = parseLogLine(event)
    expect(result!.brainName).toBe('marketing-01')
  })

  it('defaults to info level when level is missing', () => {
    const event: WS_LogEvent = {
      ts: Date.now(),
      brain_id: 'marketing-01',
      msg: 'Task started',
    }
    const result = parseLogLine(event)
    expect(result!.level).toBe('info')
  })

  it('defaults to info level when level is invalid', () => {
    const event: WS_LogEvent = {
      ts: Date.now(),
      brain_id: 'marketing-01',
      level: 'debug',
      msg: 'Task started',
    }
    const result = parseLogLine(event)
    expect(result!.level).toBe('info')
  })

  it('uses Date.now() when ts is missing', () => {
    const before = Date.now()
    const event: WS_LogEvent = {
      brain_id: 'marketing-01',
      msg: 'Task started',
      level: 'warn',
    }
    const result = parseLogLine(event)
    const after = Date.now()
    expect(result!.timestamp).toBeGreaterThanOrEqual(before)
    expect(result!.timestamp).toBeLessThanOrEqual(after)
  })

  it('includes metadata when present', () => {
    const event: WS_LogEvent = {
      ts: Date.now(),
      brain_id: 'marketing-01',
      msg: 'Task started',
      level: 'info',
      metadata: { confidence: 0.95 },
    }
    const result = parseLogLine(event)
    expect(result!.metadata).toEqual({ confidence: 0.95 })
  })

  it('generates unique ids for each log line', () => {
    const event: WS_LogEvent = { ts: Date.now(), brain_id: 'x', msg: 'test', level: 'info' }
    const r1 = parseLogLine(event)
    const r2 = parseLogLine(event)
    expect(r1!.id).not.toBe(r2!.id)
  })
})

// ─── filterLogsByLevel ─────────────────────────────────────────────────────

describe('filterLogsByLevel', () => {
  const logs: LogLine[] = [
    { id: '1', timestamp: 1, brainId: 'a', brainName: 'A', level: 'info', message: 'info msg' },
    { id: '2', timestamp: 2, brainId: 'a', brainName: 'A', level: 'warn', message: 'warn msg' },
    { id: '3', timestamp: 3, brainId: 'a', brainName: 'A', level: 'error', message: 'error msg' },
  ]

  it('returns all logs when levels set is empty', () => {
    expect(filterLogsByLevel(logs, new Set())).toHaveLength(3)
  })

  it('filters to info only', () => {
    const result = filterLogsByLevel(logs, new Set(['info']))
    expect(result).toHaveLength(1)
    expect(result[0].level).toBe('info')
  })

  it('filters to warn and error', () => {
    const result = filterLogsByLevel(logs, new Set(['warn', 'error']))
    expect(result).toHaveLength(2)
  })

  it('filters all levels when all selected', () => {
    const result = filterLogsByLevel(logs, new Set(['info', 'warn', 'error']))
    expect(result).toHaveLength(3)
  })
})

// ─── filterLogsByBrain ─────────────────────────────────────────────────────

describe('filterLogsByBrain', () => {
  const logs: LogLine[] = [
    { id: '1', timestamp: 1, brainId: 'marketing-01', brainName: 'Marketing', level: 'info', message: 'msg1' },
    { id: '2', timestamp: 2, brainId: 'product-01', brainName: 'Product', level: 'info', message: 'msg2' },
    { id: '3', timestamp: 3, brainId: 'marketing-01', brainName: 'Marketing', level: 'warn', message: 'msg3' },
  ]

  it('filters to specific brain only', () => {
    const result = filterLogsByBrain(logs, 'marketing-01')
    expect(result).toHaveLength(2)
    result.forEach((log) => expect(log.brainId).toBe('marketing-01'))
  })

  it('returns empty for unknown brain', () => {
    expect(filterLogsByBrain(logs, 'unknown-brain')).toHaveLength(0)
  })
})

// ─── formatTimestamp ───────────────────────────────────────────────────────

describe('formatTimestamp', () => {
  it('formats HH:MM:SS.mmm correctly', () => {
    // Use a fixed date: 2024-01-01T14:23:45.123Z — adjust for timezone
    // Test: use a timestamp, parse it back and verify format
    const ts = new Date(2024, 0, 1, 14, 23, 45, 123).getTime()
    const result = formatTimestamp(ts)
    // Format: HH:MM:SS.mmm
    expect(result).toMatch(/^\d{2}:\d{2}:\d{2}\.\d{3}$/)
  })

  it('pads single-digit hours and minutes', () => {
    const ts = new Date(2024, 0, 1, 1, 5, 3, 7).getTime()
    const result = formatTimestamp(ts)
    expect(result).toMatch(/^01:05:03\.007$/)
  })
})

// ─── colorForLevel ─────────────────────────────────────────────────────────

describe('colorForLevel', () => {
  it('returns text-blue-500 for info', () => {
    expect(colorForLevel('info')).toBe('text-blue-500')
  })

  it('returns text-yellow-500 for warn', () => {
    expect(colorForLevel('warn')).toBe('text-yellow-500')
  })

  it('returns text-red-500 for error', () => {
    expect(colorForLevel('error')).toBe('text-red-500')
  })

  it('defaults to text-blue-500 for unknown level', () => {
    expect(colorForLevel('debug')).toBe('text-blue-500')
    expect(colorForLevel('')).toBe('text-blue-500')
  })
})
