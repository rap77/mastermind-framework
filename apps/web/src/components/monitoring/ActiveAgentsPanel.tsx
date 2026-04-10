'use client'

import { useState } from 'react'
import { useLayoutStore } from '@/stores/layoutStore'
import { StatusBadge } from './StatusBadge'
import { BrainCard } from './BrainCard'
import { cn } from '@/lib/utils'

interface Brain {
  id: string
  name: string
  domain: string
  status: 'idle' | 'running' | 'completed' | 'failed'
  lastRunTime?: string
}

interface ActiveAgentsPanelProps {
  brains: Brain[]
}

export function ActiveAgentsPanel({ brains }: ActiveAgentsPanelProps) {
  const densityMode = useLayoutStore(state => state.densityMode)
  const setDensityMode = useLayoutStore(state => state.setDensityMode)
  const [filter, setFilter] = useState<'all' | 'active'>('active')

  // Filter brains based on active status
  const filteredBrains = filter === 'active'
    ? brains.filter(brain => brain.status === 'running')
    : brains

  return (
    <div className="space-y-4">
      {/* Header with controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-bold">Active Agents</h2>
          <StatusBadge
            variant="idle"
            count={filteredBrains.length}
            showCount={true}
          />
        </div>

        <div className="flex items-center gap-2">
          {/* Filter toggle */}
          <button
            onClick={() => setFilter(filter === 'all' ? 'active' : 'all')}
            className={cn(
              'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
              filter === 'active' ? 'bg-primary text-primary-foreground' : 'bg-muted'
            )}
            aria-label={`Show ${filter === 'all' ? 'active only' : 'all'} agents`}
          >
            {filter === 'active' ? 'Active Only' : 'All Agents'}
          </button>

          {/* Density mode toggle */}
          <button
            onClick={() => setDensityMode(densityMode === 'compact' ? 'normal' : 'compact')}
            className={cn(
              'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
              'bg-muted hover:bg-muted-foreground/10'
            )}
            aria-label={`Switch to ${densityMode === 'compact' ? 'normal' : 'compact'} mode`}
          >
            {densityMode === 'compact' ? 'Compact' : 'Normal'}
          </button>
        </div>
      </div>

      {/* Brain cards grid */}
      <div
        className={cn(
          'grid gap-4',
          densityMode === 'compact' && 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-6',
          densityMode === 'normal' && 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'
        )}
      >
        {filteredBrains.map(brain => (
          <BrainCard
            key={brain.id}
            brain={brain}
            densityMode={densityMode}
          />
        ))}
      </div>

      {/* Empty state */}
      {filteredBrains.length === 0 && (
        <div className="text-center py-12 text-muted-foreground">
          <p>No agents to display</p>
        </div>
      )}
    </div>
  )
}
