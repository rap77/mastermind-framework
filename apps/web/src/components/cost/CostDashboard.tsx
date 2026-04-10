/**
 * CostDashboard Component
 *
 * **Purpose:** Display all brain cost metrics with budget controls
 * **Context:** Phase 17-04 - Task 4 + Task 5d
 *
 * **Architecture:**
 * - Header: Total spent/budget with QuotaBar + Connection Status
 * - Grid: 24 MetricCards (responsive: 1 col mobile, 6 cols desktop)
 * - Budget slider adjusts allocation
 * - Export CSV button downloads data
 * - Brain #7 simplified: Per brain + total ONLY (2 levels)
 * - NO "per company" toggle
 * - WebSocket connection status indicator (Task 5d)
 */

'use client'

import { startTransition, useDeferredValue, memo } from 'react'
import { useCostStore } from '@/stores/costStore'
import { useCostWebSocket } from '@/hooks/useCostWebSocket'
import { MetricCard } from './MetricCard'
import { QuotaBar } from './QuotaBar'
import type { Brain } from './types'

interface CostDashboardProps {
  brains: Brain[]
}

export const CostDashboard = memo(function CostDashboard({ brains }: CostDashboardProps) {
  const { metrics, budget, spent, setBudget, connectionStatus } = useCostStore()

  // Activate WebSocket subscription (Task 5d)
  useCostWebSocket()

  // Defer brain list for performance (React 19 concurrent feature)
  const brainList = useDeferredValue(brains)

  /**
   * Handle budget slider change
   * Uses startTransition to keep UI responsive during state updates
   */
  const handleBudgetChange = (newBudget: number) => {
    startTransition(() => {
      setBudget(newBudget)
    })
  }

  /**
   * Export metrics as CSV
   */
  const handleExportCSV = () => {
    const csvContent = [
      ['Brain ID', 'Brain Name', 'Tokens', 'Duration (s)', 'Cost ($)', 'Success Rate (%)'],
      ...Object.values(metrics).map(m => [
        m.brainId,
        brains.find(b => b.id === m.brainId)?.name || m.brainId,
        m.totalTokens.toString(),
        m.totalDuration.toString(),
        m.totalCost.toFixed(2),
        m.successRate.toString(),
      ]),
    ]
      .map(row => row.join(','))
      .join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `cost-metrics-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Empty state
  if (brainList.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">No cost data available</p>
      </div>
    )
  }

  return (
    <div className="cost-dashboard space-y-6">
      {/* Header: Total spent/budget with QuotaBar */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-foreground">Total Spent</h2>
            <p className="text-3xl font-bold text-primary">${spent.toFixed(2)}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-muted-foreground">Budget</p>
            <p className="text-xl font-semibold text-foreground">${budget.toFixed(2)}</p>
          </div>

          {/* Connection Status Indicator (Task 5d) */}
          <div className={`status-indicator ${connectionStatus}`}>
            <div className={`status-dot ${connectionStatus}`}></div>
            <span className="status-text">
              {connectionStatus === 'connected' && 'Live'}
              {connectionStatus === 'disconnected' && 'Offline'}
              {connectionStatus === 'error' && 'Error'}
            </span>
          </div>
        </div>

        {/* QuotaBar */}
        <QuotaBar spent={spent} budget={budget} />

        {/* Budget Slider */}
        <div className="mt-4">
          <label htmlFor="budget-slider" className="block text-sm font-medium text-foreground mb-2">
            Adjust Budget: ${budget}
          </label>
          <input
            id="budget-slider"
            type="range"
            min="0"
            max="1000"
            step="10"
            value={budget}
            onChange={(e) => handleBudgetChange(Number(e.target.value))}
            className="w-full"
            aria-label="Adjust budget"
          />
        </div>

        {/* Export CSV Button */}
        <button
          onClick={handleExportCSV}
          className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors"
          aria-label="Export cost metrics as CSV"
        >
          Export CSV
        </button>
      </div>

      {/* Grid: 24 MetricCards */}
      <div className="metrics-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6 gap-4">
        {brainList.map((brain) => {
          const brainMetrics = metrics[brain.id]
          if (!brainMetrics) return null

          return (
            <MetricCard
              key={brain.id}
              brain={brain}
              metrics={brainMetrics}
              densityMode="normal"
            />
          )
        })}
      </div>
    </div>
  )
})
