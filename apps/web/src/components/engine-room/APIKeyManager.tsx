/**
 * APIKeyManager — Container for API key management.
 *
 * **Purpose:** Provides tabbed interface for creating and listing API keys.
 * **Layout:** Simple tab navigation (Create Key | My Keys) using accessible button tabs.
 *
 * **Data:** GET /api/keys via TanStack Query (staleTime: 5s — user may revoke during session).
 *
 * **Phase:** 08-04 — Wave 3 (API Key Management)
 */

'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { KeyCreateDialog } from './KeyCreateDialog'
import { KeyListTable } from './KeyListTable'

// ─── Types ────────────────────────────────────────────────────────────────────

type ActiveTab = 'list' | 'create'

export interface APIKeyManagerProps {
  /** Default tab to show. Default: 'list' */
  defaultTab?: ActiveTab
}

export interface APIKeyMasked {
  id: string
  prefix: string
  suffix: string
  created_at: string
  last_used_at: string | null
}

interface APIKeysResponse {
  keys: APIKeyMasked[]
}

// ─── Tab config ───────────────────────────────────────────────────────────────

const TABS: { id: ActiveTab; label: string }[] = [
  { id: 'list', label: 'My Keys' },
  { id: 'create', label: 'Create Key' },
]

// ─── Component ────────────────────────────────────────────────────────────────

/**
 * APIKeyManager — tabbed container for API key CRUD.
 *
 * @example
 * ```tsx
 * // In Engine Room Config tab
 * <APIKeyManager />
 * ```
 */
export function APIKeyManager({ defaultTab = 'list' }: APIKeyManagerProps) {
  const [activeTab, setActiveTab] = useState<ActiveTab>(defaultTab)

  const { data, isLoading, isError, refetch } = useQuery<APIKeysResponse>({
    queryKey: ['api-keys'],
    queryFn: async () => {
      const res = await fetch('/api/keys')
      if (!res.ok) throw new Error('Failed to fetch API keys')
      return res.json() as Promise<APIKeysResponse>
    },
    staleTime: 5000,
  })

  return (
    <div className="space-y-4">
      {/* Tab navigation */}
      <nav
        role="tablist"
        aria-label="API Key Management"
        className="flex border-b"
      >
        {TABS.map(({ id, label }) => (
          <button
            key={id}
            role="tab"
            id={`tab-apikey-${id}`}
            aria-selected={activeTab === id}
            aria-controls={`tabpanel-apikey-${id}`}
            onClick={() => setActiveTab(id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px ${
              activeTab === id
                ? 'border-primary text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {label}
          </button>
        ))}
      </nav>

      {/* My Keys tab */}
      <div
        role="tabpanel"
        id="tabpanel-apikey-list"
        aria-labelledby="tab-apikey-list"
        hidden={activeTab !== 'list'}
      >
        {activeTab === 'list' && (
          <>
            {isLoading && (
              <p className="text-sm text-muted-foreground py-4">Loading API keys...</p>
            )}
            {isError && (
              <div className="space-y-2 py-4">
                <p className="text-sm text-destructive">Failed to load API keys.</p>
                <button
                  onClick={() => refetch()}
                  className="text-xs text-primary underline hover:no-underline"
                >
                  Retry
                </button>
              </div>
            )}
            {!isLoading && !isError && (
              <KeyListTable keys={data?.keys ?? []} />
            )}
          </>
        )}
      </div>

      {/* Create Key tab */}
      <div
        role="tabpanel"
        id="tabpanel-apikey-create"
        aria-labelledby="tab-apikey-create"
        hidden={activeTab !== 'create'}
      >
        {activeTab === 'create' && <KeyCreateDialog />}
      </div>
    </div>
  )
}
