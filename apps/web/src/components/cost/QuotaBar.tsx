/**
 * QuotaBar Component
 *
 * **Purpose:** Display budget vs spent progress bar with color coding
 * **Context:** Phase 17-04 - Task 3
 *
 * **Architecture:**
 * - Color coding: green (< 80%), yellow (80-99%), red (≥ 100%)
 * - Brain #2 fix: percentage text + icons (✓, ⚠, ⚠)
 * - Brain #3 fix: cubic-bezier easing for smooth animation
 * - ARIA live region for screen readers
 * - Tooltip on hover for detailed info
 */

'use client'

import { memo } from 'react'
import type { QuotaBarProps } from './types'

export const QuotaBar = memo(function QuotaBar({
  spent,
  budget,
  threshold = 0.8,
}: QuotaBarProps) {
  const percent = Math.min((spent / budget) * 100, 100)

  /**
   * Get color class and icon based on percentage
   * Green: < 80%, Yellow: 80-99%, Red: ≥ 100%
   */
  const getColorConfig = () => {
    if (percent >= 100) {
      return {
        colorClass: 'bg-red-500',
        textClass: 'text-red-500',
        icon: '⚠',
        label: 'Budget exceeded',
      }
    }
    if (percent >= threshold * 100) {
      return {
        colorClass: 'bg-yellow-500',
        textClass: 'text-yellow-500',
        icon: '⚠',
        label: 'Approaching limit',
      }
    }
    return {
      colorClass: 'bg-green-500',
      textClass: 'text-green-500',
      icon: '✓',
      label: 'Within budget',
    }
  }

  const config = getColorConfig()

  return (
    <div className="quota-bar-container">
      {/* Progress Bar */}
      <div
        role="progressbar"
        aria-valuenow={Math.round(percent)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-live="polite"
        aria-label={config.label}
        title={`$${spent.toFixed(2)} / $${budget.toFixed(2)}`}
        className={`
          relative
          w-full
          h-3
          bg-gray-200
          dark:bg-gray-700
          rounded-full
          overflow-hidden
        `}
      >
        {/* Fill Bar */}
        <div
          className={`
            quota-bar-fill
            h-full
            ${config.colorClass}
            transition-all
            duration-200
            ease-in-out
          `}
          style={{
            width: `${percent}%`,
            transitionTimingFunction: 'cubic-bezier(0.645, 0.045, 0.355, 1)',
          }}
        />
      </div>

      {/* Percentage Text + Icon (Brain #2 fix) */}
      <div className="flex items-center gap-2 mt-1">
        <span
          className={`
            text-sm
            font-medium
            ${config.textClass}
          `}
          aria-label={`quota status: ${config.label}`}
        >
          {config.icon}
        </span>
        <span className="text-sm font-medium text-foreground">
          {Math.round(percent)}%
        </span>
      </div>
    </div>
  )
})
