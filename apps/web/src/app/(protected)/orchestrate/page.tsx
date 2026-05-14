import { Suspense } from 'react'
import { fetchBrains } from '@/lib/api'
import { OrchestratePage } from '@/components/orchestration/OrchestratePage'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'

// Force dynamic rendering — no build-time fetch (avoids ECONNREFUSED)
export const dynamic = 'force-dynamic'

export const metadata = {
  title: 'Orchestration Canvas — MasterMind',
}

/**
 * OrchestrateLoader — Server Component that fetches brain registry.
 *
 * Passes blueprintBrains to the client-side OrchestratePage, which renders
 * the three-column layout: [BrainList | OrchestrationCanvas | OutputPanel].
 */
async function OrchestrateLoader() {
  let brainsData = null

  try {
    brainsData = await fetchBrains(1, 24)
  } catch (error) {
    const msg = error instanceof Error ? error.message : 'Unknown error'
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <p className="text-destructive mb-2">Failed to load brain registry</p>
          <p className="text-sm text-muted-foreground">{msg}</p>
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

  return <OrchestratePage blueprintBrains={brainsData.brains} />
}

export default function OrchestrateRoute() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center">
          <LoadingSpinner />
        </div>
      }
    >
      <OrchestrateLoader />
    </Suspense>
  )
}
