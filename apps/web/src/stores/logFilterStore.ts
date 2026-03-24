/**
 * Log Filter Store
 *
 * **Purpose:** Zustand store for log filter state with localStorage persistence
 * **Context:** Phase 08-03 — Engine Room filter bar state management
 */

import { create } from 'zustand'

// ─── Types ──────────────────────────────────────────────────────────────────

type LogLevel = 'info' | 'warn' | 'error'

interface LogFilterState {
  filterLevels: Set<LogLevel> // selected levels
  autoFollow: boolean // auto-scroll to newest
  isolatedBrainId: string | null // if set, show only this brain's logs

  // Actions
  toggleLevel: (level: LogLevel) => void
  setAutoFollow: (enabled: boolean) => void
  setIsolatedBrain: (brainId: string | null) => void
  reset: () => void
}

const STORAGE_KEY = 'mm_log_filters'

// ─── Persistence helpers ─────────────────────────────────────────────────────

function loadFromStorage(): Partial<{
  filterLevels: LogLevel[]
  autoFollow: boolean
  isolatedBrainId: string | null
}> {
  if (typeof window === 'undefined') return {}
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return {}
    return JSON.parse(raw)
  } catch {
    return {}
  }
}

function saveToStorage(state: {
  filterLevels: Set<LogLevel>
  autoFollow: boolean
  isolatedBrainId: string | null
}): void {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        filterLevels: Array.from(state.filterLevels),
        autoFollow: state.autoFollow,
        isolatedBrainId: state.isolatedBrainId,
      })
    )
  } catch {
    // Ignore storage errors (private browsing, full storage, etc.)
  }
}

// ─── Default state ───────────────────────────────────────────────────────────

const DEFAULT_LEVELS: LogLevel[] = ['info', 'warn', 'error']

// ─── Store ───────────────────────────────────────────────────────────────────

export const useLogFilterStore = create<LogFilterState>((set, get) => {
  // Hydrate from localStorage on init (client only)
  const stored = loadFromStorage()

  const initialLevels: Set<LogLevel> = new Set(
    Array.isArray(stored.filterLevels) && stored.filterLevels.length > 0
      ? (stored.filterLevels.filter(
          (l): l is LogLevel => l === 'info' || l === 'warn' || l === 'error'
        ))
      : DEFAULT_LEVELS
  )

  return {
    filterLevels: initialLevels,
    autoFollow: stored.autoFollow ?? true,
    isolatedBrainId: stored.isolatedBrainId ?? null,

    toggleLevel: (level) => {
      set((state) => {
        const newSet = new Set(state.filterLevels)
        if (newSet.has(level)) {
          newSet.delete(level)
        } else {
          newSet.add(level)
        }

        saveToStorage({
          filterLevels: newSet,
          autoFollow: state.autoFollow,
          isolatedBrainId: state.isolatedBrainId,
        })

        return { filterLevels: newSet }
      })
    },

    setAutoFollow: (enabled) => {
      set((state) => {
        const next = { ...state, autoFollow: enabled }
        saveToStorage({
          filterLevels: state.filterLevels,
          autoFollow: enabled,
          isolatedBrainId: state.isolatedBrainId,
        })
        return { autoFollow: enabled }
      })
    },

    setIsolatedBrain: (brainId) => {
      set((state) => {
        saveToStorage({
          filterLevels: state.filterLevels,
          autoFollow: state.autoFollow,
          isolatedBrainId: brainId,
        })
        return { isolatedBrainId: brainId }
      })
    },

    reset: () => {
      const defaultState = {
        filterLevels: new Set<LogLevel>(DEFAULT_LEVELS),
        autoFollow: true,
        isolatedBrainId: null,
      }
      saveToStorage(defaultState)
      set(defaultState)
    },
  }
})
