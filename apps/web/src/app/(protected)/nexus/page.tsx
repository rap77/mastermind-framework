import { Suspense } from 'react'
import { fetchBrains } from '@/lib/api'
import { NexusCanvas } from '@/components/nexus/NexusCanvas'
import { NexusSkeleton } from '@/components/nexus/NexusSkeleton'

// Force dynamic rendering — no build-time fetch (avoids ECONNREFUSED)
export const dynamic = 'force-dynamic'

/**
 * NexusPage — The Nexus screen
 *
 * Server Component fetches Ghost Architecture from GET /api/brains.
 * Passes blueprintBrains to NexusCanvas (Client Component).
 * NexusSkeleton shows while data loads.
 * Route is protected by AuthGuardLayout (automatic from (protected) folder).
 *
 * Data flow:
 * 1. Server fetches all 24 brains (Ghost Architecture)
 * 2. NexusCanvas builds dagre layout once (positions locked)
 * 3. BrainNode reads live status from brainStore via useBrainState(id)
 * 4. WS events update brainStore → BrainNode re-renders in isolation
 */
async function NexusCanvasLoader() {
  let brainsData = null

  try {
    brainsData = await fetchBrains(1, 24)
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-2">Failed to load Ghost Architecture</p>
          <p className="text-sm text-muted-foreground">Error: {errorMessage}</p>
        </div>
      </div>
    )
  }

  if (!brainsData || brainsData.brains.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-muted-foreground">No brains available</p>
      </div>
    )
  }

  return <NexusCanvas blueprintBrains={brainsData.brains} />
}

export default function NexusPage() {
  return (
    <div className="h-screen w-full">
      <Suspense fallback={<NexusSkeleton />}>
        <NexusCanvasLoader />
      </Suspense>
    </div>
  )
}
