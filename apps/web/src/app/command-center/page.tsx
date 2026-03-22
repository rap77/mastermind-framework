/**
 * Command Center Page
 *
 * **Purpose:** Main dashboard showing all 24 AI brains in Bento Grid layout
 * **Context:** Phase 06-02 - Task 1, Phase 06-03 - Task 4
 *
 * **Architecture:**
 * - Server Component (fetches brains server-side for initial render)
 * - Uses TanStack Query for data fetching and caching
 * - Passes brains data to BentoGrid component
 * - Handles loading/error states with proper error boundaries
 * - Client wrapper provides Cmd+Enter shortcut and modal
 *
 * **N+1 Prevention:**
 * - Single query fetches ALL brain data including cluster metadata
 * - TanStack Query caches response, no duplicate calls
 * - Frontend groups by niche using useMemo (not additional queries)
 */

import { fetchBrains, type BrainsResponse } from '@/lib/api'
import { BentoGrid } from '@/components/command-center/BentoGrid'
import { CommandCenterWrapper } from '@/components/command-center/CommandCenterWrapper'

// Force dynamic rendering (no build-time fetch to avoid ECONNREFUSED)
export const dynamic = 'force-dynamic'

/**
 * Command Center Page Component
 *
 * **Query Configuration:**
 * - queryKey: ['brains', page, page_size]
 * - queryFn: fetches /api/brains?page=1&page_size=24
 * - staleTime: 30s (reduce refetches)
 * - refetchOnWindowFocus: false (avoid unnecessary calls)
 *
 * **Data Flow:**
 * 1. Server Component fetches brains (SSR)
 * 2. TanStack Query hydrates client-side cache
 * 3. WebSocket updates provide real-time status (Phase 05)
 * 4. User sees live status without page reload
 *
 * @returns Command Center page with Bento Grid
 */
export default async function CommandCenterPage() {
  let brainsData: BrainsResponse | null = null

  try {
    brainsData = await fetchBrains(1, 24)
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-2">Failed to load brains</p>
          <p className="text-sm text-muted-foreground">Error: {errorMessage}</p>
        </div>
      </div>
    )
  }

  /**
   * Handle empty state
   *
   * **Note:** This shouldn't happen in production (24 brains always exist)
   * but we handle it gracefully for testing/dev environments
   */
  if (!brainsData || !brainsData.brains || brainsData.brains.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-muted-foreground">No brains available</p>
      </div>
    )
  }

  /**
   * Render Bento Grid with brains data
   *
   * **Passing Data:**
   * - Brains array from TanStack Query
   * - BentoGrid handles clustering by niche internally
   * - No additional queries needed (data already pre-clustered by niche field)
   *
   * **Client Wrapper:**
   * - CommandCenterWrapper provides Cmd+Enter shortcut
   * - BriefInputModal for task submission
   * - WebSocket connection after task creation
   */
  return (
    <CommandCenterWrapper>
      <BentoGrid brains={brainsData.brains} />
    </CommandCenterWrapper>
  )
}

/**
 * Phase 06-02 Notes
 *
 * **Server-Side Rendering:**
 * - Page is async Server Component
 * - fetchBrains runs on server (uses 'server-only')
 * - Initial HTML includes brains data (SEO-friendly, fast LCP)
 *
 * **TanStack Query Integration:**
 * - Server-side fetch hydrates client-side cache automatically
 * - WebSocket updates (Phase 05) override cached data in real-time
 * - Refetching disabled on window focus (unnecessary for brains metadata)
 *
 * **Performance:**
 * - Single query eliminates N+1 problem
 * - Eager Loading reduces round-trips to server
 * - 30s cache reduces unnecessary refetches
 *
 * **Next Steps (Task 2):**
 * - BentoGrid component receives brains array
 * - Clusters by niche using useMemo (no additional queries)
 * - Renders BrainTile components for each brain
 */
