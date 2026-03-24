/**
 * Engine Room Page
 *
 * **Purpose:** Live execution monitoring and brain configuration management
 * **Route:** /engine-room
 * **Auth:** Protected by AuthGuardLayout (automatic from (protected) folder)
 *
 * **Phase 08-03 scope:**
 * - Logs tab: LiveLogPanel (fully functional, WS-connected, filters, isolation)
 * - Config tab: Placeholder (API key management wired in 08-04)
 *
 * **Note:** `metadata` cannot be exported from a 'use client' component.
 * Route-level metadata is handled in a separate layout or the parent layout.
 */

'use client'

import { useState } from 'react'
import { LiveLogPanel } from '@/components/engine-room/LiveLogPanel'
import { APIKeyManager } from '@/components/engine-room/APIKeyManager'

// ─── Tab types ───────────────────────────────────────────────────────────────

type TabId = 'logs' | 'config'

const TABS: { id: TabId; label: string }[] = [
  { id: 'logs', label: 'Live Logs' },
  { id: 'config', label: 'Configuration' },
]

// ─── Component ───────────────────────────────────────────────────────────────

/**
 * Engine Room — tabbed interface for execution monitoring and brain config.
 *
 * Logs tab: Live log stream with virtual scrolling, level filtering, brain isolation.
 * Config tab: Placeholder for API key management (Phase 08-04).
 */
export default function EngineRoomPage() {
  const [activeTab, setActiveTab] = useState<TabId>('logs')

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="border-b px-6 py-4 shrink-0">
        <h1 className="text-2xl font-bold">Engine Room</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Monitor execution and manage integrations
        </p>
      </div>

      {/* Tab navigation */}
      <div className="border-b px-6 shrink-0">
        <nav className="flex gap-0" role="tablist" aria-label="Engine Room sections">
          {TABS.map(({ id, label }) => (
            <button
              key={id}
              role="tab"
              aria-selected={activeTab === id}
              aria-controls={`tabpanel-${id}`}
              id={`tab-${id}`}
              onClick={() => setActiveTab(id)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === id
                  ? 'border-primary text-foreground'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab panels */}
      <div className="flex-1 overflow-hidden">
        {/* Logs tab — LiveLogPanel with FilterBar and WS integration */}
        <div
          id="tabpanel-logs"
          role="tabpanel"
          aria-labelledby="tab-logs"
          hidden={activeTab !== 'logs'}
          className="h-full"
        >
          {activeTab === 'logs' && <LiveLogPanel />}
        </div>

        {/* Config tab — API key management */}
        <div
          id="tabpanel-config"
          role="tabpanel"
          aria-labelledby="tab-config"
          hidden={activeTab !== 'config'}
          className="h-full overflow-auto"
        >
          {activeTab === 'config' && (
            <div className="p-6 max-w-2xl">
              <div className="mb-6">
                <h2 className="text-xl font-bold">Configuration</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  Manage API keys for external integrations.
                </p>
              </div>
              <APIKeyManager />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
