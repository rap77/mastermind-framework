/**
 * ErrorSummary — Execution statistics display for simulation replay
 *
 * Shows three key metrics at a glance:
 * - Total Errors: Number of nodes with error status (red badge)
 * - Slow Nodes: Number of nodes with duration > 1000ms (yellow badge)
 * - Total Time: Overall execution duration in seconds (formatted)
 *
 * Uses simulationStore's getErrorSummary() selector and follows
 * ReplayControls pattern with theme tokens for all colors.
 */

import { useCallback, useMemo } from 'react'
import { useSimulationStore } from '@/stores/simulationStore'
import { Badge } from '@/components/ui/badge'

export function ErrorSummary() {
  const getErrorSummary = useSimulationStore((state) => state.getErrorSummary)

  const errorSummary = useMemo(() => getErrorSummary(), [getErrorSummary])

  const formatTime = useCallback((ms: number): string => {
    return `${(ms / 1000).toFixed(3)}s`
  }, [])

  return (
    <div
      className="flex items-center gap-4 px-4 py-2 border-b"
      style={{
        backgroundColor: 'var(--color-surface)',
        borderColor: 'var(--color-border)',
      }}
    >
      {/* Total Errors Badge */}
      <div className="flex items-center gap-2">
        <span
          className="text-sm font-medium"
          style={{ color: 'var(--color-text-primary)' }}
        >
          Errors:
        </span>
        <Badge variant="destructive">
          {errorSummary.totalErrors}
        </Badge>
      </div>

      {/* Slow Nodes Badge */}
      <div className="flex items-center gap-2">
        <span
          className="text-sm font-medium"
          style={{ color: 'var(--color-text-primary)' }}
        >
          Slow Nodes:
        </span>
        <Badge variant="warning">
          {errorSummary.slowNodes}
        </Badge>
      </div>

      {/* Total Time Badge */}
      <div className="flex items-center gap-2">
        <span
          className="text-sm font-medium"
          style={{ color: 'var(--color-text-primary)' }}
        >
          Total Time:
        </span>
        <Badge variant="default">
          {formatTime(errorSummary.totalTime)}
        </Badge>
      </div>
    </div>
  )
}
