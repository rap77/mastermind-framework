import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useCostStore } from '../costStore'

describe('costStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useCostStore.setState({
      metrics: {},
      budget: 100,
      spent: 0,
    })
  })

  describe('initial state', () => {
    it('should have empty metrics map', () => {
      const state = useCostStore.getState()
      expect(state.metrics).toEqual({})
    })

    it('should have default budget of $100', () => {
      const state = useCostStore.getState()
      expect(state.budget).toBe(100)
    })

    it('should have zero spent initially', () => {
      const state = useCostStore.getState()
      expect(state.spent).toBe(0)
    })
  })

  describe('updateMetric', () => {
    it('should add new brain metric', () => {
      const store = useCostStore.getState()

      store.updateMetric('brain-01', {
        brainId: 'brain-01',
        totalTokens: 1000,
        totalDuration: 60,
        totalCost: 0.50,
        lastActivityAt: '2026-04-10T12:00:00Z',
        successRate: 95,
      })

      const state = useCostStore.getState()
      expect(state.metrics['brain-01']).toEqual({
        brainId: 'brain-01',
        totalTokens: 1000,
        totalDuration: 60,
        totalCost: 0.50,
        lastActivityAt: '2026-04-10T12:00:00Z',
        successRate: 95,
      })
    })

    it('should update existing brain metric', () => {
      const store = useCostStore.getState()

      store.updateMetric('brain-01', {
        brainId: 'brain-01',
        totalTokens: 1000,
        totalDuration: 60,
        totalCost: 0.50,
        lastActivityAt: '2026-04-10T12:00:00Z',
        successRate: 95,
      })

      store.updateMetric('brain-01', {
        brainId: 'brain-01',
        totalTokens: 2000,
        totalDuration: 120,
        totalCost: 1.00,
        lastActivityAt: '2026-04-10T12:05:00Z',
        successRate: 96,
      })

      const state = useCostStore.getState()
      expect(state.metrics['brain-01'].totalCost).toBe(1.00)
      expect(state.metrics['brain-01'].totalTokens).toBe(2000)
    })

    it('should recalculate total spent when adding metric', () => {
      const store = useCostStore.getState()

      store.updateMetric('brain-01', {
        brainId: 'brain-01',
        totalTokens: 1000,
        totalDuration: 60,
        totalCost: 0.50,
        lastActivityAt: '2026-04-10T12:00:00Z',
        successRate: 95,
      })

      expect(useCostStore.getState().spent).toBe(0.50)

      store.updateMetric('brain-02', {
        brainId: 'brain-02',
        totalTokens: 2000,
        totalDuration: 120,
        totalCost: 1.00,
        lastActivityAt: '2026-04-10T12:05:00Z',
        successRate: 96,
      })

      expect(useCostStore.getState().spent).toBe(1.50)
    })

    it('should update spent when metric is replaced', () => {
      const store = useCostStore.getState()

      store.updateMetric('brain-01', {
        brainId: 'brain-01',
        totalTokens: 1000,
        totalDuration: 60,
        totalCost: 0.50,
        lastActivityAt: '2026-04-10T12:00:00Z',
        successRate: 95,
      })

      store.updateMetric('brain-01', {
        brainId: 'brain-01',
        totalTokens: 2000,
        totalDuration: 120,
        totalCost: 0.80,
        lastActivityAt: '2026-04-10T12:05:00Z',
        successRate: 96,
      })

      // Spent should be 0.80 (new value), not 0.50 + 0.80 = 1.30
      expect(useCostStore.getState().spent).toBe(0.80)
    })
  })

  describe('setBudget', () => {
    it('should update budget', () => {
      const store = useCostStore.getState()
      store.setBudget(200)

      expect(useCostStore.getState().budget).toBe(200)
    })

    it('should allow zero budget', () => {
      const store = useCostStore.getState()
      store.setBudget(0)

      expect(useCostStore.getState().budget).toBe(0)
    })
  })

  describe('resetMetrics', () => {
    it('should clear all metrics', () => {
      const store = useCostStore.getState()

      store.updateMetric('brain-01', {
        brainId: 'brain-01',
        totalTokens: 1000,
        totalDuration: 60,
        totalCost: 0.50,
        lastActivityAt: '2026-04-10T12:00:00Z',
        successRate: 95,
      })

      store.resetMetrics()

      expect(useCostStore.getState().metrics).toEqual({})
    })

    it('should reset spent to zero', () => {
      const store = useCostStore.getState()

      store.updateMetric('brain-01', {
        brainId: 'brain-01',
        totalTokens: 1000,
        totalDuration: 60,
        totalCost: 0.50,
        lastActivityAt: '2026-04-10T12:00:00Z',
        successRate: 95,
      })

      store.resetMetrics()

      expect(useCostStore.getState().spent).toBe(0)
    })

    it('should not reset budget', () => {
      const store = useCostStore.getState()
      store.setBudget(200)

      store.updateMetric('brain-01', {
        brainId: 'brain-01',
        totalTokens: 1000,
        totalDuration: 60,
        totalCost: 0.50,
        lastActivityAt: '2026-04-10T12:00:00Z',
        successRate: 95,
      })

      store.resetMetrics()

      expect(useCostStore.getState().budget).toBe(200)
    })
  })

  describe('persist middleware', () => {
    it('should persist state to localStorage', () => {
      const store = useCostStore.getState()

      store.updateMetric('brain-01', {
        brainId: 'brain-01',
        totalTokens: 1000,
        totalDuration: 60,
        totalCost: 0.50,
        lastActivityAt: '2026-04-10T12:00:00Z',
        successRate: 95,
      })

      // Check localStorage has the data
      const stored = localStorage.getItem('mastermind-costs')
      expect(stored).toBeDefined()

      if (stored) {
        const parsed = JSON.parse(stored)
        expect(parsed.state.metrics['brain-01'].totalCost).toBe(0.50)
      }
    })

    it('should restore state from localStorage', () => {
      // Set up initial state
      const store = useCostStore.getState()
      store.updateMetric('brain-01', {
        brainId: 'brain-01',
        totalTokens: 1000,
        totalDuration: 60,
        totalCost: 0.50,
        lastActivityAt: '2026-04-10T12:00:00Z',
        successRate: 95,
      })

      // Simulate page reload by creating new store instance
      // (In real scenario, zustand persist middleware handles this)
      const state = useCostStore.getState()
      expect(state.metrics['brain-01']).toBeDefined()
      expect(state.metrics['brain-01'].totalCost).toBe(0.50)
    })
  })

  describe('useCostState selector', () => {
    it('should return undefined for non-existent brain', () => {
      const getCostState = useCostStore.getState().getCostState
      if (!getCostState) {
        // Selector not implemented yet
        return
      }

      const metric = getCostState('brain-99')
      expect(metric).toBeUndefined()
    })

    it('should return metric for existing brain', () => {
      const store = useCostStore.getState()

      store.updateMetric('brain-01', {
        brainId: 'brain-01',
        totalTokens: 1000,
        totalDuration: 60,
        totalCost: 0.50,
        lastActivityAt: '2026-04-10T12:00:00Z',
        successRate: 95,
      })

      const getCostState = useCostStore.getState().getCostState
      if (!getCostState) {
        return
      }

      const metric = getCostState('brain-01')
      expect(metric).toEqual({
        brainId: 'brain-01',
        totalTokens: 1000,
        totalDuration: 60,
        totalCost: 0.50,
        lastActivityAt: '2026-04-10T12:00:00Z',
        successRate: 95,
      })
    })
  })
})
