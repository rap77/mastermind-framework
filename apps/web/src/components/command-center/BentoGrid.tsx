/**
 * BentoGrid Component
 *
 * **Purpose:** Main grid layout with semantic clustering by niche
 * **Context:** Phase 06-02 - Task 2
 *
 * **Architecture:**
 * - Data-driven clustering using CLUSTER_CONFIGS
 * - Maps CLUSTER_CONFIGS to ClusterGroup components
 * - CSS Grid with auto-fit for responsive layout
 * - No hardcoded niche logic (extensible)
 */

import { Brain } from '@/lib/api'
import { CLUSTER_CONFIGS } from '@/config/clusters'
import { ClusterGroup } from './ClusterGroup'

interface BentoGridProps {
  brains: Brain[]
}

/**
 * BentoGrid Component
 *
 * **Features:**
 * - Renders clusters from CLUSTER_CONFIGS (data-driven)
 * - Each cluster contains brains filtered by niche
 * - CSS Grid with auto-fit for responsive layout
 * - Extensible: Add new nichos via config only
 *
 * **Extensibility:**
 * - New cluster = Add to CLUSTER_CONFIGS array
 * - No BentoGrid code changes needed
 *
 * @param brains - All brains array from TanStack Query
 * @returns BentoGrid component
 */
export function BentoGrid({ brains }: BentoGridProps) {
  return (
    <div className="bento-grid grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 p-6" data-testid="bento-grid">
      {CLUSTER_CONFIGS.map((clusterConfig) => (
        <ClusterGroup key={clusterConfig.id} clusterConfig={clusterConfig} brains={brains} />
      ))}
    </div>
  )
}

/**
 * Phase 06-02 Notes
 *
 * **Data-Driven Architecture:**
 * - CLUSTER_CONFIGS defines all clusters
 * - BentoGrid maps configs to ClusterGroup components
 * - No hardcoded niche logic
 *
 * **Extensibility:**
 * - Add new cluster to config → renders automatically
 * - Future-proof for nichos beyond software/development
 *
 * **CSS Grid Layout:**
 * - auto-fit with minmax for responsive behavior
 * - 1 column on mobile, 2 on lg, 3 on xl screens
 * - Consistent spacing with gap-6
 */
