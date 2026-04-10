/**
 * MetricCard Component
 *
 * **Purpose:** Display cost metrics for a single brain with trend indicators
 * **Context:** Phase 17-04 - Task 2
 *
 * **Architecture:**
 * - React.memo prevents unnecessary re-renders
 * - Density modes: compact (cost only) vs normal (3 lines)
 * - Trend indicator: ↑ red (increased), ↓ green (decreased)
 * - Drill-down button for brain detail page
 * - useCostState selector for targeted updates (O(1) lookup)
 */

'use client'

import { memo } from 'react'
import { ArrowUp, ArrowDown } from 'lucide-react'
import type { MetricCardProps } from './types'
import { useCostState } from '@/stores/costStore'

export const MetricCard = memo(function MetricCard({
  brain,
  metrics,
  densityMode = 'normal',
  onDrillDown,
}: MetricCardProps) {
  /**
   * Get previous cost from store for trend calculation
   *
   * **Targeted Selector:** useCostState(id) prevents re-renders on other brain updates
   * O(1) Map lookup via Zustand selector
   */
  const previousMetrics = useCostState(brain.id)
  const previousCost = previousMetrics?.totalCost || metrics.totalCost

  /**
   * Calculate trend (current vs previous)
   * Brain #3 fix: ↑ red (increased), ↓ green (decreased)
   */
  const getTrend = () => {
    if (metrics.totalCost > previousCost) {
      return { direction: 'up', color: 'text-red-500' }
    }
    if (metrics.totalCost < previousCost) {
      return { direction: 'down', color: 'text-green-500' }
    }
    return null // No change
  }

  const trend = getTrend()

  /**
   * Format large numbers (e.g., 1,000,000 -> 1M)
   */
  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`
    }
    return num.toString()
  }

  /**
   * Format duration (seconds -> human readable)
   */
  const formatDuration = (seconds: number): string => {
    if (seconds >= 3600) {
      return `${(seconds / 3600).toFixed(1)}h`
    }
    if (seconds >= 60) {
      return `${(seconds / 60).toFixed(0)}m`
    }
    return `${seconds}s`
  }

  return (
    <div
      data-testid={`metric-card-${brain.id}`}
      className={`
        metric-card
        bg-card
        border
        border-border
        rounded-lg
        p-4
        transition-all
        duration-200
        hover:shadow-md
        ${densityMode === 'compact' ? 'flex items-center justify-between' : ''}
      `}
    >
      {/* Brain Header */}
      <div className="flex items-center gap-2 mb-2">
        <span className="text-2xl" role="img" aria-label={`${brain.name} icon`}>
          {brain.icon}
        </span>
        <h3 className="font-semibold text-foreground">{brain.name}</h3>
      </div>

      {/* Compact Mode: Single line with cost only */}
      {densityMode === 'compact' && (
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-foreground">
            ${metrics.totalCost.toFixed(2)}
          </span>
          {trend && (
            <span className={trend.color}>
              {trend.direction === 'up' ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
            </span>
          )}
        </div>
      )}

      {/* Normal Mode: 3 lines (tokens, duration, cost) */}
      {densityMode === 'normal' && (
        <div className="space-y-2">
          {/* Tokens */}
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Tokens</span>
            <span className="font-medium text-foreground">
              {formatNumber(metrics.totalTokens)}
            </span>
          </div>

          {/* Duration */}
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Duration</span>
            <span className="font-medium text-foreground">
              {formatDuration(metrics.totalDuration)}
            </span>
          </div>

          {/* Cost with trend */}
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Cost</span>
            <div className="flex items-center gap-2">
              <span className="font-bold text-foreground">
                ${metrics.totalCost.toFixed(2)}
              </span>
              {trend && (
                <span className={trend.color} aria-label={`Cost ${trend.direction === 'up' ? 'increased' : 'decreased'}`}>
                  {trend.direction === 'up' ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
                </span>
              )}
            </div>
          </div>

          {/* Success Rate */}
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Success Rate</span>
            <span className="font-medium text-foreground">
              {metrics.successRate}%
            </span>
          </div>
        </div>
      )}

      {/* Drill-down Button */}
      {onDrillDown && (
        <button
          onClick={() => onDrillDown(brain.id)}
          className={`
            mt-2
            w-full
            px-3
            py-1.5
            text-sm
            font-medium
            text-primary
            bg-primary/10
            hover:bg-primary/20
            rounded
            transition-colors
            duration-150
          `}
          aria-label={`View details for ${brain.name}`}
        >
          View Details
        </button>
      )}
    </div>
  )
})
