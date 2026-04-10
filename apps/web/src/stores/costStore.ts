import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

export interface CostMetric {
  brainId: string
  totalTokens: number
  totalDuration: number // seconds
  totalCost: number // USD
  lastActivityAt: string
  successRate: number
}

interface CostState {
  metrics: Record<string, CostMetric>
  budget: number
  spent: number
  connectionStatus: 'connected' | 'disconnected' | 'error'

  // Actions
  updateMetric: (brainId: string, metric: CostMetric) => void
  setBudget: (budget: number) => void
  resetMetrics: () => void
  getCostState: (brainId: string) => CostMetric | undefined
  setConnectionStatus: (status: 'connected' | 'disconnected' | 'error') => void
}

export const useCostStore = create<CostState>()(
  persist(
    immer((set, get) => ({
      metrics: {},
      budget: 100, // Default $100 budget
      spent: 0,
      connectionStatus: 'disconnected',

      updateMetric: (brainId, metric) =>
        set((state) => {
          state.metrics[brainId] = metric
          // Recalculate total spent from all metrics
          state.spent = Object.values(state.metrics)
            .reduce((sum, m) => sum + m.totalCost, 0)
        }),

      setBudget: (budget) =>
        set((state) => {
          state.budget = budget
        }),

      setConnectionStatus: (status) =>
        set((state) => {
          state.connectionStatus = status
        }),

      resetMetrics: () =>
        set((state) => {
          state.metrics = {}
          state.spent = 0
        }),

      getCostState: (brainId) => {
        return get().metrics[brainId]
      },
    })),
    {
      name: 'mastermind-costs',
      // Only persist these fields (not getCostState function)
      partialize: (state) => ({
        metrics: state.metrics,
        budget: state.budget,
        spent: state.spent,
        // Don't persist connectionStatus — it's transient
      }),
    }
  )
)

/**
 * useCostState — targeted selector for a single brain's cost metrics.
 *
 * Prevents cascade re-renders: only re-renders consumers when the specific
 * brain's cost metrics change (O(1) object lookup via Zustand selector).
 *
 * @param brainId - Brain ID to select (e.g. 'brain-01')
 * @returns CostMetric for the given brainId, or undefined if not yet tracked
 */
export const useCostState = (brainId: string) =>
  useCostStore((state) => state.metrics[brainId])
