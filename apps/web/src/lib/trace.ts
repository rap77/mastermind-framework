/**
 * Distributed trace ID utilities.
 *
 * Provides a pure function that generates a fresh UUID v4 on every call.
 * This is intentionally stateless — no caching, no singleton.
 */

/**
 * Generate a new UUID v4 trace identifier.
 *
 * Uses `crypto.randomUUID()` when available (all modern browsers and
 * Node.js 19+). Falls back to a manual Math.random()-based UUID v4
 * generator that is RFC 4122 compliant.
 *
 * @returns A 36-character UUID v4 string, e.g. `"110e8400-e29b-41d4-a716-446655440000"`
 */
export function getTraceId(): string {
  if (
    typeof crypto !== 'undefined' &&
    typeof crypto.randomUUID === 'function'
  ) {
    return crypto.randomUUID()
  }

  // RFC 4122 §4.4 — version 4, variant 10xx
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}
