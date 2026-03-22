/**
 * Cluster Configuration
 *
 * **Purpose:** Data-driven cluster configuration for extensibility
 * **Context:** Phase 06-02 - Task 2
 *
 * **Architecture:**
 * - CLUSTER_CONFIGS array defines all clusters
 * - Add new nichos here without modifying component code
 * - Export helper functions for cluster lookups
 */

/**
 * Cluster configuration interface
 *
 * Defines structure for each cluster in the Bento Grid
 */
export interface ClusterConfig {
  /** Unique cluster ID (e.g., 'master', 'software') */
  id: string

  /** Display name for cluster header */
  name: string

  /** Niche identifier for filtering brains */
  niche: 'master' | 'software' | 'marketing' | string

  /** Tailwind color for cluster theme (e.g., 'zinc', 'cyan', 'purple') */
  color: string

  /** Animation variant for cluster (e.g., 'steady', 'scan', 'glow') */
  animation: string

  /** Array of brain IDs belonging to this cluster */
  brains: string[]
}

/**
 * Cluster configurations
 *
 * **Extensibility:** Add new nichos here without changing component code
 *
 * **Current Nichos:**
 * - Master (1): zinc-100 — Steady Pulse
 * - Software (7): cyan-400 — Scanning Line
 * - Marketing (16): purple-500 — Glow Expansion
 *
 * **Future Nichos:**
 * - Finance: Add { id: 'finance', name: 'Finance', niche: 'finance', ... }
 * - Healthcare: Add { id: 'healthcare', name: 'Healthcare', niche: 'healthcare', ... }
 */
export const CLUSTER_CONFIGS: ClusterConfig[] = [
  {
    id: 'master',
    name: 'Master',
    niche: 'universal',  // Backend uses 'universal' for master brain
    color: 'zinc',
    animation: 'steady',
    brains: ['brain-08'],
  },
  {
    id: 'software',
    name: 'Software Development',
    niche: 'software-development',  // Backend uses 'software-development'
    color: 'cyan',
    animation: 'scan',
    brains: [
      'brain-01',
      'brain-02',
      'brain-03',
      'brain-04',
      'brain-05',
      'brain-06',
      'brain-07',
    ],
  },
  {
    id: 'marketing',
    name: 'Marketing',
    niche: 'marketing-digital',  // Backend uses 'marketing-digital'
    color: 'purple',
    animation: 'glow',
    brains: [
      'brain-09',
      'brain-10',
      'brain-11',
      'brain-12',
      'brain-13',
      'brain-14',
      'brain-15',
      'brain-16',
      'brain-17',
      'brain-18',
      'brain-19',
      'brain-20',
      'brain-21',
      'brain-22',
      'brain-23',
      'brain-24',
    ],
  },
  /**
   * Future: Add new clusters here
   *
   * Example:
   * {
   *   id: 'finance',
   *   name: 'Finance',
   *   niche: 'finance',
   *   color: 'emerald',
   *   animation: 'pulse',
   *   brains: ['brain-25', 'brain-26']
   * }
   */
]

/**
 * Get cluster configuration for a specific brain
 *
 * **Performance:** O(n) lookup, acceptable for 24 brains
 *
 * @param brainId - Brain ID (e.g., 'brain-01')
 * @returns Cluster configuration or null if not found
 *
 * **Example:**
 * ```typescript
 * import { getClusterForBrain } from '@/config/clusters'
 *
 * const cluster = getClusterForBrain('brain-01')
 * // { id: 'software', name: 'Software Development', ... }
 * ```
 */
export function getClusterForBrain(brainId: string): ClusterConfig | null {
  return CLUSTER_CONFIGS.find((cluster) => cluster.brains.includes(brainId)) || null
}

/**
 * Get all brain IDs for a specific cluster
 *
 * **Performance:** O(1) lookup by cluster ID
 *
 * @param clusterId - Cluster ID (e.g., 'software')
 * @returns Array of brain IDs or empty array if cluster not found
 *
 * **Example:**
 * ```typescript
 * import { getBrainsInCluster } from '@/config/clusters'
 *
 * const brains = getBrainsInCluster('software')
 * // ['brain-01', 'brain-02', ..., 'brain-07']
 * ```
 */
export function getBrainsInCluster(clusterId: string): string[] {
  const cluster = CLUSTER_CONFIGS.find((c) => c.id === clusterId)
  return cluster?.brains || []
}

/**
 * Get cluster configuration by niche
 *
 * **Performance:** O(n) lookup, acceptable for 3-5 clusters
 *
 * @param niche - Niche identifier (e.g., 'software')
 * @returns Cluster configuration or null if not found
 *
 * **Example:**
 * ```typescript
 * import { getClusterByNiche } from '@/config/clusters'
 *
 * const cluster = getClusterByNiche('software')
 * // { id: 'software', name: 'Software Development', ... }
 * ```
 */
export function getClusterByNiche(niche: string): ClusterConfig | null {
  return CLUSTER_CONFIGS.find((cluster) => cluster.niche === niche) || null
}

/**
 * Phase 06-02 Notes
 *
 * **Extensibility Pattern:**
 * - New nicho = Add config to CLUSTER_CONFIGS array
 * - No component code changes needed
 * - BentoGrid automatically renders new cluster
 *
 * **Data-Driven Architecture:**
 * - ClusterGroup receives ClusterConfig as prop
 * - Color, animation, brains all from config
 * - Future-proof for nichos beyond software/development
 *
 * **Performance:**
 * - Helper functions are O(n) or O(1)
 * - Acceptable for small datasets (24 brains, 3-5 clusters)
 * - For 100+ clusters, consider Map-based lookup
 */
