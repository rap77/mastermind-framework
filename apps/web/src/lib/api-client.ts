/**
 * Client-side API fetch wrapper with distributed tracing.
 *
 * Injects an `X-Trace-ID` header into every outgoing request so that
 * logs across the frontend → Rust control plane → Python agent runtime
 * can be correlated by a single trace identifier.
 *
 * **Usage (client components and client-side actions):**
 * ```typescript
 * import { apiFetch } from '@/lib/api-client'
 *
 * const res = await apiFetch('/api/brains/product-vision/trigger', {
 *   method: 'POST',
 * })
 * ```
 *
 * **Do NOT use in server-only code** (`lib/api.ts`, route handlers, Server
 * Components) — those run on the server where `X-Trace-ID` should be
 * extracted from the inbound request, not generated anew.
 */

import { getTraceId } from './trace'

/**
 * Wrapper around `fetch` that merges an auto-generated `X-Trace-ID` header
 * with any headers provided by the caller.
 *
 * All other `RequestInit` options (method, body, cache, signal, …) are
 * forwarded unchanged.
 *
 * @param url - The URL or path to fetch.
 * @param init - Optional fetch options (headers are merged, not replaced).
 * @returns The native `fetch` promise.
 */
export function apiFetch(url: string, init?: RequestInit): Promise<Response> {
  return fetch(url, {
    ...init,
    headers: {
      ...init?.headers,
      'X-Trace-ID': getTraceId(),
    },
  })
}
