/**
 * API Client Functions
 *
 * **Purpose:** Centralized API calls with proper error handling and typing
 * **Context:** Phase 06-02 - Command Center Bento Grid
 *
 * **Architecture:**
 * - Server Components call FastAPI directly with cookies
 * - Client Components use Next.js API routes as proxies
 * - Proper error handling with typed responses
 *
 * **Why dual approach?**
 * - Server Components CAN read cookies with await cookies()
 * - But fetch() from Server Component to internal route loses cookies
 * - Solution: Server Components call FastAPI directly, pass token manually
 */

import 'server-only'
import { cookies } from 'next/headers'
import { PaginatedBrainsResponseSchema } from '@/types/api'

/**
 * Brain data structure from API
 *
 * Matches FastAPI backend response from GET /api/brains
 */
export interface Brain {
  id: string
  name: string
  niche: 'software-development' | 'marketing-digital' | 'universal'
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
}

/**
 * Fetch all brains with pagination
 *
 * **Architecture:** Uses Next.js route handler proxy (/api/brains)
 * - Proxy reads httpOnly cookie and adds Authorization header
 * - Proxies to FastAPI backend
 * - Returns brains data to Server Component
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
  // CRITICAL: Server Component reads cookies and calls FastAPI directly
  const apiUrl = process.env.API_URL || 'http://localhost:8001'
  const url = `${apiUrl}/api/brains?page=${page}&page_size=${pageSize}`

  // Get JWT token from httpOnly cookie
  const cookieStore = await cookies()  // CRITICAL: await in Next.js 16
  const token = cookieStore.get('access_token')?.value

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(url, {
    method: 'GET',
    headers,
    next: { revalidate: 0 },  // Disable caching
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Unauthorized - Please login first')
    }
    throw new Error(`Failed to fetch brains: ${response.status} ${response.statusText}`)
  }

  const raw = await response.json()
  const data = PaginatedBrainsResponseSchema.parse(raw)
  return data
}

/**
 * Fetch a single brain by ID
 *
 * **Architecture:** Uses Next.js route handler proxy (/api/brains/[id])
 * - Proxy reads httpOnly cookie and adds Authorization header
 * - Proxies to FastAPI backend
 * - Returns brain data to Server Component
 *
 * **Note:** Used for brain detail views (Phase 07)
 *
 * @param brainId - Brain ID (e.g., 'brain-01')
 * @returns Brain data
 * @throws Error if brain not found
 */
export async function fetchBrain(brainId: string): Promise<Brain> {
  // CRITICAL: Server Component reads cookies and calls FastAPI directly
  const apiUrl = process.env.API_URL || 'http://localhost:8001'
  const url = `${apiUrl}/api/brains/${brainId}`

  // Get JWT token from httpOnly cookie
  const cookieStore = await cookies()  // CRITICAL: await in Next.js 16
  const token = cookieStore.get('access_token')?.value

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(url, {
    method: 'GET',
    headers,
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
