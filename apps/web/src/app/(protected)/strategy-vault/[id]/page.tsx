import type { Metadata } from 'next'
import Link from 'next/link'
import { ExecutionDetail } from '@/components/strategy-vault/ExecutionDetail'

// Force dynamic rendering — execution details are real-time
export const dynamic = 'force-dynamic'

// ─── Props ────────────────────────────────────────────────────────────────────

interface ExecutionDetailsPageProps {
  params: Promise<{ id: string }> // CRITICAL: params is a Promise in Next.js 16
}

// ─── Metadata ─────────────────────────────────────────────────────────────────

export async function generateMetadata({
  params,
}: ExecutionDetailsPageProps): Promise<Metadata> {
  // CRITICAL: await params — required in Next.js 16 (Promise-based params)
  const { id } = await params
  return {
    title: `Execution ${id.slice(0, 8)}… | Strategy Vault`,
    description: `Detailed view of execution ${id}`,
  }
}

// ─── Page ─────────────────────────────────────────────────────────────────────

/**
 * ExecutionDetailsPage — execution detail page.
 *
 * **Route:** /strategy-vault/[id]
 * **Auth:** Protected by AuthGuardLayout (automatic from (protected) folder)
 *
 * Shows full execution audit: DAG replay, brain outputs accordion,
 * timeline scrubber, and static logs panel.
 *
 * **Data flow:**
 * Client component (ExecutionDetail) fetches GET /api/executions/{id}
 * via TanStack Query. 404 → redirects back to /strategy-vault.
 */
export default async function ExecutionDetailsPage({
  params,
}: ExecutionDetailsPageProps) {
  // CRITICAL: await params — required in Next.js 16
  const { id } = await params

  return (
    <div className="space-y-4 p-6">
      {/* Breadcrumb navigation */}
      <nav aria-label="Breadcrumb">
        <Link
          href="/strategy-vault"
          className="text-sm text-muted-foreground hover:text-foreground transition-colors inline-flex items-center gap-1"
        >
          ← Back to Strategy Vault
        </Link>
      </nav>

      {/* Execution detail view */}
      <ExecutionDetail executionId={id} />
    </div>
  )
}
