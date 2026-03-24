/**
 * logFilterStore Tests
 *
 * **Purpose:** Verify Zustand log filter store with localStorage persistence
 * **Context:** Phase 08-03 — Task 2
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { useLogFilterStore } from '../logFilterStore'

// ─── Mock localStorage ────────────────────────────────────────────────────────

const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key]
    }),
    clear: vi.fn(() => {
      store = {}
    }),
    get length() {
      return Object.keys(store).length
    },
    key: vi.fn((index: number) => Object.keys(store)[index] ?? null),
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
})

// ─── Reset store before each test ─────────────────────────────────────────────

beforeEach(() => {
  localStorageMock.clear()
  localStorageMock.getItem.mockClear()
  localStorageMock.setItem.mockClear()
  useLogFilterStore.getState().reset()
})

afterEach(() => {
  vi.clearAllMocks()
})

// ─── Initial state ─────────────────────────────────────────────────────────────

describe('logFilterStore initial state', () => {
  it('initializes with all levels enabled', () => {
    const { filterLevels } = useLogFilterStore.getState()
    expect(filterLevels.has('info')).toBe(true)
    expect(filterLevels.has('warn')).toBe(true)
    expect(filterLevels.has('error')).toBe(true)
  })

  it('initializes with autoFollow enabled', () => {
    const { autoFollow } = useLogFilterStore.getState()
    expect(autoFollow).toBe(true)
  })

  it('initializes with no isolation', () => {
    const { isolatedBrainId } = useLogFilterStore.getState()
    expect(isolatedBrainId).toBeNull()
  })
})

// ─── toggleLevel ───────────────────────────────────────────────────────────────

describe('toggleLevel', () => {
  it('removes an active level on toggle', () => {
    useLogFilterStore.getState().toggleLevel('warn')
    const { filterLevels } = useLogFilterStore.getState()
    expect(filterLevels.has('warn')).toBe(false)
    expect(filterLevels.has('info')).toBe(true)
    expect(filterLevels.has('error')).toBe(true)
  })

  it('adds an inactive level on toggle', () => {
    useLogFilterStore.getState().toggleLevel('warn') // remove warn
    useLogFilterStore.getState().toggleLevel('warn') // add warn back
    const { filterLevels } = useLogFilterStore.getState()
    expect(filterLevels.has('warn')).toBe(true)
  })

  it('persists to localStorage on toggle', () => {
    useLogFilterStore.getState().toggleLevel('error')
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'mm_log_filters',
      expect.stringContaining('"filterLevels"')
    )
    const saved = JSON.parse(localStorageMock.setItem.mock.calls.at(-1)?.[1] ?? '{}')
    expect(saved.filterLevels).not.toContain('error')
  })
})

// ─── setAutoFollow ─────────────────────────────────────────────────────────────

describe('setAutoFollow', () => {
  it('disables auto-follow', () => {
    useLogFilterStore.getState().setAutoFollow(false)
    expect(useLogFilterStore.getState().autoFollow).toBe(false)
  })

  it('enables auto-follow', () => {
    useLogFilterStore.getState().setAutoFollow(false)
    useLogFilterStore.getState().setAutoFollow(true)
    expect(useLogFilterStore.getState().autoFollow).toBe(true)
  })

  it('persists autoFollow to localStorage', () => {
    useLogFilterStore.getState().setAutoFollow(false)
    const saved = JSON.parse(localStorageMock.setItem.mock.calls.at(-1)?.[1] ?? '{}')
    expect(saved.autoFollow).toBe(false)
  })
})

// ─── setIsolatedBrain ─────────────────────────────────────────────────────────

describe('setIsolatedBrain', () => {
  it('sets isolated brain id', () => {
    useLogFilterStore.getState().setIsolatedBrain('marketing-01')
    expect(useLogFilterStore.getState().isolatedBrainId).toBe('marketing-01')
  })

  it('clears isolation when set to null', () => {
    useLogFilterStore.getState().setIsolatedBrain('marketing-01')
    useLogFilterStore.getState().setIsolatedBrain(null)
    expect(useLogFilterStore.getState().isolatedBrainId).toBeNull()
  })

  it('persists isolation to localStorage', () => {
    useLogFilterStore.getState().setIsolatedBrain('product-01')
    const saved = JSON.parse(localStorageMock.setItem.mock.calls.at(-1)?.[1] ?? '{}')
    expect(saved.isolatedBrainId).toBe('product-01')
  })
})

// ─── reset ─────────────────────────────────────────────────────────────────────

describe('reset', () => {
  it('restores default state', () => {
    useLogFilterStore.getState().toggleLevel('warn')
    useLogFilterStore.getState().setAutoFollow(false)
    useLogFilterStore.getState().setIsolatedBrain('product-01')

    useLogFilterStore.getState().reset()

    const state = useLogFilterStore.getState()
    expect(state.filterLevels.has('warn')).toBe(true)
    expect(state.autoFollow).toBe(true)
    expect(state.isolatedBrainId).toBeNull()
  })
})
