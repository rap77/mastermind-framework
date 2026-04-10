/**
 * Cost Component Types
 *
 * **Purpose:** Shared types for cost tracking components
 * **Context:** Phase 17-04 - Tasks 2-7
 */

export interface Brain {
  id: string
  name: string
  icon: string
}

export interface CostMetric {
  brainId: string
  totalTokens: number
  totalDuration: number // seconds
  totalCost: number // USD
  lastActivityAt: string
  successRate: number
}

export interface MetricCardProps {
  brain: Brain
  metrics: CostMetric
  densityMode?: 'compact' | 'normal'
  onDrillDown?: (brainId: string) => void
  previousCost?: number // Optional: for trend calculation
}

export interface QuotaBarProps {
  spent: number
  budget: number
  threshold?: number
}
