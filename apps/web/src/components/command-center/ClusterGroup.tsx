/**
 * ClusterGroup Component
 *
 * **Purpose:** Niche-level grouping component for Bento Grid
 * **Context:** Phase 06-02 - Task 2
 *
 * **Architecture:**
 * - Accepts clusterConfig prop (data-driven)
 * - Filters brains by niche
 * - Collapse/expand functionality
 * - Applies cluster color and animation themes
 * - Renders BrainTile components for each brain
 */

'use client'

import { useState } from 'react'
import { BrainTile } from './BrainTile'
import type { ClusterConfig } from '@/config/clusters'
import type { Brain } from '@/lib/api'
import { ChevronDown, ChevronUp } from 'lucide-react'

interface ClusterGroupProps {
  /** Cluster configuration from CLUSTER_CONFIGS */
  clusterConfig: ClusterConfig

  /** All brains array (filtered by niche internally) */
  brains: Brain[]
}

/**
 * ClusterGroup Component
 *
 * **Features:**
 * - Displays cluster name and brain count
 * - Collapse/expand toggle (default: expanded)
 * - Filters brains by cluster niche
 * - Applies cluster color theme
 * - Grid layout for brain tiles
 *
 * **Extensibility:**
 * - New cluster = add config to CLUSTER_CONFIGS
 * - No code changes needed
 *
 * @param clusterConfig - Cluster configuration
 * @param brains - All brains array
 * @returns ClusterGroup component
 */
export function ClusterGroup({ clusterConfig, brains }: ClusterGroupProps) {
  const [isExpanded, setIsExpanded] = useState(true)

  /**
   * Filter brains by cluster niche
   *
   * **Performance:** O(n) filter, acceptable for 24 brains
   */
  const clusterBrains = brains.filter((brain) => brain.niche === clusterConfig.niche)

  /**
   * Toggle collapse/expand state
   */
  const toggleExpanded = () => setIsExpanded((prev) => !prev)

  return (
    <div
      className={`cluster-group cluster-${clusterConfig.id} bg-${clusterConfig.color}-50 dark:bg-${clusterConfig.color}-950 rounded-lg border border-${clusterConfig.color}-200 dark:border-${clusterConfig.color}-800 p-4`}
      data-testid={`cluster-${clusterConfig.id}`}
    >
      {/* Cluster Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-foreground">{clusterConfig.name}</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">{clusterBrains.length} brains</span>
          <button
            onClick={toggleExpanded}
            aria-label={isExpanded ? 'Collapse cluster' : 'Expand cluster'}
            className="p-1 hover:bg-accent rounded transition-colors"
            type="button"
          >
            {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Brain Tiles Grid */}
      {isExpanded && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {clusterBrains.map((brain) => (
            <BrainTile key={brain.id} brain={brain} />
          ))}
        </div>
      )}
    </div>
  )
}

/**
 * Phase 06-02 Notes
 *
 * **Data-Driven Architecture:**
 * - clusterConfig prop provides all cluster metadata
 * - Color, animation, brains all from config
 * - No hardcoded niche logic
 *
 * **Extensibility:**
 * - Add new cluster to CLUSTER_CONFIGS → renders automatically
 * - No component code changes needed
 *
 * **Performance:**
 * - Filter runs on every render (acceptable for small datasets)
 * - For 100+ brains, consider memoization with useMemo
 *
 * **Accessibility:**
 * - Aria labels on collapse button
 * - Keyboard navigation support
 */
