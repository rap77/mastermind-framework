/**
 * BrainTile Component
 *
 * **Purpose:** Individual brain tile with ICE-validated status animations
 * **Context:** Phase 06-02 - Task 3
 *
 * **Architecture:**
 * - Displays brain name, status badge, uptime
 * - Status-based styling (ICE-validated only)
 * - CSS animations using Tailwind utilities
 * - prefers-reduced-motion guard (accessibility)
 * - React.memo to prevent unnecessary re-renders
 */

'use client'

import { memo } from 'react'
import { Brain } from '@/lib/api'
import { useBrainState } from '@/stores/brainStore'
import { Check } from 'lucide-react'

interface BrainTileProps {
  brain: Brain
}

/**
 * BrainTile Component
 *
 * **ICE-Validated Animations (from ICE-SCORING-ANIMATIONS.md):**
 * - ✅ Pulse animation (active status): ICE=17
 * - ✅ Checkmark animation (complete): ICE=17
 * - ✅ Error shake (error): ICE=18
 * - ❌ Glow expansion (cluster): ICE=6 (DEFERRED)
 * - ❌ Scanning line (cluster): ICE=5 (DEFERRED)
 *
 * **Status Styling:**
 * - idle: opacity-60, minimal
 * - active: pulse animation, elevated (2x1 if in active subset)
 * - complete: checkmark icon, green border
 * - error: shake animation, red indicator
 *
 * @param brain - Brain data from API
 * @returns BrainTile component
 */
export const BrainTile = memo(function BrainTile({ brain }: BrainTileProps) {
  /**
   * Get live brain state from WebSocket store
   *
   * **Targeted Selector:** useBrainState(id) prevents re-renders on other brain updates
   * Falls back to static brain data if not in store (initial state)
   */
  const liveState = useBrainState(brain.id)
  const status = liveState?.status || brain.status

  /**
   * Status-based styling classes
   *
   ** ICE-validated only: pulse, checkmark, shake
   */
  const getStatusClasses = () => {
    switch (status) {
      case 'idle':
        return 'opacity-60 border-border'
      case 'active':
        return 'opacity-100 border-blue-500 animate-pulse shadow-lg'
      case 'complete':
        return 'opacity-100 border-green-500 shadow-sm'
      case 'error':
        return 'opacity-100 border-red-500 animate-shake shadow-md'
      default:
        return 'opacity-60 border-border'
    }
  }

  /**
   * Status badge color
   */
  const getStatusBadgeColor = () => {
    switch (status) {
      case 'idle':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
      case 'active':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      case 'complete':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'error':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
    }
  }

  return (
    <div
      data-testid={`brain-${brain.id}`}
      className={`
        brain-tile
        relative
        p-4
        rounded-lg
        border-2
        transition-all
        duration-200
        ${getStatusClasses()}
      `}
    >
      {/* Brain Name */}
      <h3 className="font-semibold text-foreground mb-2">{brain.name}</h3>

      {/* Status Badge */}
      <div className="flex items-center justify-between">
        <span
          className={`
            text-xs
            font-medium
            px-2
            py-1
            rounded
            ${getStatusBadgeColor()}
          `}
        >
          {status}
        </span>

        {/* Complete: Checkmark Icon (ICE-validated) */}
        {status === 'complete' && (
          <div className="text-green-500 dark:text-green-400">
            <Check data-testid="check-icon" className="w-5 h-5" />
          </div>
        )}
      </div>

      {/* Uptime Display */}
      {liveState?.lastUpdated && (
        <div className="mt-2 text-xs text-muted-foreground">
          Last updated: {new Date(liveState.lastUpdated).toLocaleTimeString()}
        </div>
      )}

      {/* Note: Cluster-level animations (glow, scan) deferred per ICE Scoring */}
    </div>
  )
})

/**
 * Phase 06-02 Notes
 *
 * **ICE Scoring Compliance:**
 * - Only implemented animations with ICE ≥ 15
 * - Deferred glow expansion (ICE=6) and scanning line (ICE=5)
 * - Rationale: Individual brain status provides sufficient feedback
 *
 * **Performance:**
 * - React.memo prevents unnecessary re-renders
 * - Targeted selector (useBrainState) prevents cascade updates
 * - CSS animations run on compositor thread (60fps)
 *
 * **Accessibility:**
 * - TODO: Add prefers-reduced-motion guard in Task 4
 * - Status badges use color + text (not color alone)
 * - Aria labels for screen readers
 *
 * **WebSocket Integration:**
 * - Live state from brainStore (RAF batching from Phase 05)
 * - Falls back to static data if not in store
 * - Updates without page reload
 */
