import type { Metadata } from 'next'
import { ExecutionList } from '@/components/strategy-vault/ExecutionList'

// Force dynamic rendering — execution list is real-time, never cached at build
export const dynamic = 'force-dynamic'

export const metadata: Metadata = {
  title: 'Strategy Vault | MasterMind',
  description: 'Audit past AI brain executions and trace workflow history',
}

/**
 * StrategyVaultPage — execution history list page.
 *
 * **Route:** /strategy-vault
 * **Auth:** Protected by AuthGuardLayout (automatic from (protected) folder)
 *
 * Shows paginated list of all past task executions.
 * User can click any execution to view detailed brain outputs.
 *
 * **Data flow:**
 * Client component (ExecutionList) fetches GET /api/executions/history
 * via TanStack Query with cursor pagination.
 */
export default function StrategyVaultPage() {
  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Strategy Vault</h1>
        <p className="text-muted-foreground mt-1">
          Audit past executions and learn from brain outputs
        </p>
      </div>
      <ExecutionList />
    </div>
  )
}
