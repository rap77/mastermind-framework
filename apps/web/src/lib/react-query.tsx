/**
 * TanStack Query Provider Configuration
 *
 * **Purpose:** Configure TanStack Query for server state management
 * **Context:** Phase 06-02 - Command Center Bento Grid
 *
 * **Architecture:**
 * - Client component (uses 'use client')
 * - Wraps app with QueryClientProvider
 * - Optimized for Next.js 16 + React 19
 */

'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState, type ReactNode } from 'react'

/**
 * QueryClient provider props
 */
interface QueryProviderProps {
  children: ReactNode
}

/**
 * TanStack Query Provider Component
 *
 * **Configuration:**
 * - staleTime: 30s (reduce refetches)
 * - refetchOnWindowFocus: false (avoid unnecessary calls)
 * - retry: 1 (avoid infinite retries on auth errors)
 * - DevTools: enabled in development only
 *
 * **Example:**
 * ```tsx
 * import { QueryProvider } from '@/lib/react-query'
 *
 * export default function RootLayout({ children }) {
 *   return (
 *     <html>
 *       <body>
 *         <QueryProvider>{children}</QueryProvider>
 *       </body>
 *     </html>
 *   )
 * }
 * ```
 */
export function QueryProvider({ children }: QueryProviderProps) {
  /**
   * Create QueryClient instance
   *
   * **Important:** Create inside component to avoid SSR cache sharing
   * https://tanstack.com/query/latest/docs/framework/react/guides/ssr
   */
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            /**
             * staleTime: Data remains fresh for 30 seconds
             *
             * Reduces unnecessary refetches while ensuring data isn't too stale.
             * Matches Next.js fetch cache duration (30s).
             */
            staleTime: 30 * 1000,

            /**
             * refetchOnWindowFocus: Disabled
             *
             * Avoid unnecessary API calls when user returns to tab.
             * Brains data doesn't change that frequently.
             */
            refetchOnWindowFocus: false,

            /**
             * retry: 1 attempt
             *
             * Avoid infinite retries on auth errors (401/403).
             * Auth errors should be handled by auth guards, not retry logic.
             */
            retry: 1,

            /**
             * gcTime: 5 minutes (formerly cacheTime)
             *
             * Keep unused data in cache for 5 minutes before garbage collection.
             * Allows instant navigation back to Command Center.
             */
            gcTime: 5 * 60 * 1000,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  )
}

/**
 * Phase 06-02 Notes
 *
 * **Integration:**
 * - Add QueryProvider to app/layout.tsx (wrap children)
 * - Use useQuery hook in Command Center page
 *
 * **SSR Considerations:**
 * - QueryClient created inside component (not singleton)
 * - Prevents cache sharing between users on server
 * - Next.js 16 hydration handles state transfer correctly
 *
 * **Performance:**
 * - Stale data acceptable for 30s (brains metadata changes infrequently)
 * - WebSocket updates provide real-time status (overrides cached data)
 * - Reduced network calls = better performance
 */
