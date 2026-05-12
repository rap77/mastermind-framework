import { describe, it, expect } from 'vitest'
import { getTraceId } from '../trace'

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

describe('getTraceId()', () => {
  it('returns a non-empty string', () => {
    const id = getTraceId()
    expect(typeof id).toBe('string')
    expect(id.length).toBeGreaterThan(0)
  })

  it('returns a 36-character UUID v4 format string', () => {
    const id = getTraceId()
    expect(id).toHaveLength(36)
    expect(UUID_REGEX.test(id)).toBe(true)
  })

  it('generates a unique value on each call', () => {
    const id1 = getTraceId()
    const id2 = getTraceId()
    expect(id1).not.toBe(id2)
  })
})
