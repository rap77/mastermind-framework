/**
 * API Client Functions
 *
 * **Purpose:** Centralized API calls with proper error handling and typing
 * **Context:** Phase 06-02 - Command Center Bento Grid
 *
 * **Architecture:**
 * - Uses native fetch (no axios dependency)
 * - Server-side only (uses 'server-only')
 * - Proper error handling with typed responses
 */

import 'server-only'

/**
 * Brain data structure from API
 *
 * Matches FastAPI backend response from GET /api/brains
 */
export interface Brain {
  id: string
  name: string
  niche: 'master' | 'software' | 'marketing' | string
  status: 'idle' | 'active' | 'complete' | 'error'
  uptime: number
  last_called_at: string | null
  description?: string
}

/**
 * Paginated brains response
 *
 * Matches FastAPI pagination format
 */
export interface BrainsResponse {
  brains: Brain[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

/**
 * Get API base URL from environment
 *
 * @returns API URL (defaults to localhost:8000 for development)
 */
function getApiUrl(): string {
  return process.env.API_URL || 'http://localhost:8000'
}

/**
 * Fetch all brains with pagination
 *
 * **N+1 Prevention:** Single query fetches ALL brain data including cluster metadata.
 * Frontend groups by niche using useMemo (no additional queries).
 *
 * @param page - Page number (default: 1)
 * @param pageSize - Items per page (default: 24 for all brains)
 * @returns Paginated brains response
 * @throws Error if fetch fails or returns non-OK status
 *
 * **Example:**
 * ```typescript
 * import { fetchBrains } from '@/lib/api'
 *
 * const data = await fetchBrains(1, 24)
 * console.log(data.brains) // Array<Brain>
 * ```
 */
export async function fetchBrains(
  page: number = 1,
  pageSize: number = 24
): Promise<BrainsResponse> {
  const apiUrl = getApiUrl()
  const url = `${apiUrl}/api/brains?page=${page}&page_size=${pageSize}`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    // Next.js caching: cache for 30 seconds, revalidate in background
    next: { revalidate: 30 },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch brains: ${response.status} ${response.statusText}`)
  }

  const data: BrainsResponse = await response.json()
  return data
}

/**
 * Fetch a single brain by ID
 *
 * **Note:** Used for brain detail views (Phase 07)
 *
 * @param brainId - Brain ID (e.g., 'brain-01')
 * @returns Brain data
 * @throws Error if brain not found
 */
export async function fetchBrain(brainId: string): Promise<Brain> {
  const apiUrl = getApiUrl()
  const url = `${apiUrl}/api/brains/${brainId}`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    next: { revalidate: 30 },
  })

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Brain not found: ${brainId}`)
    }
    throw new Error(`Failed to fetch brain: ${response.status} ${response.statusText}`)
  }

  const data: Brain = await response.json()
  return data
}

/**
 * Phase 06-02 Notes
 *
 * **Eager Loading Strategy:**
 * - GET /api/brains returns all brains with niche field pre-populated
 * - Single query fetches everything needed for Bento Grid
 * - No N+1 queries: TanStack Query caches response, no duplicate calls
 *
 * **Caching:**
 * - Next.js fetch cache: 30 seconds
 * - TanStack Query cache: configured in page.tsx (staleTime: 30s)
 * - Refetch on window focus: disabled (avoid unnecessary calls)
 *
 * **Server-Side Only:**
 * - These functions run on server (Next.js Server Components)
 * - No client-side secrets exposed
 * - Leverages Next.js server-side caching
 */
