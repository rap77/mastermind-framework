/**
 * FilterBar Component
 *
 * **Purpose:** Log filter controls — level toggles, auto-follow, isolation display
 * **Context:** Phase 08-03 — Engine Room filter bar
 */

'use client'

import { useLogFilterStore } from '@/stores/logFilterStore'

// ─── Types ──────────────────────────────────────────────────────────────────

interface FilterBarProps {
  onFilterChange?: () => void // optional callback when filter changes
}

const LOG_LEVELS = ['info', 'warn', 'error'] as const
type LogLevel = (typeof LOG_LEVELS)[number]

const LEVEL_LABELS: Record<LogLevel, string> = {
  info: 'INFO',
  warn: 'WARN',
  error: 'ERROR',
}

// ─── Component ──────────────────────────────────────────────────────────────

/**
 * Horizontal filter bar for the Engine Room log panel.
 * Controls: level toggles (info/warn/error), auto-follow, isolation clear.
 */
export function FilterBar({ onFilterChange }: FilterBarProps) {
  const {
    filterLevels,
    autoFollow,
    isolatedBrainId,
    toggleLevel,
    setAutoFollow,
    setIsolatedBrain,
  } = useLogFilterStore()

  const handleToggleLevel = (level: LogLevel) => {
    toggleLevel(level)
    onFilterChange?.()
  }

  return (
    <div
      className="flex gap-3 items-center px-4 py-2 bg-secondary border-b text-sm"
      role="toolbar"
      aria-label="Log filters"
    >
      {/* Level toggles */}
      <div className="flex gap-2" role="group" aria-label="Log level filters">
        {LOG_LEVELS.map((level) => (
          <button
            key={level}
            onClick={() => handleToggleLevel(level)}
            aria-pressed={filterLevels.has(level)}
            aria-label={`Toggle ${level} logs`}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              filterLevels.has(level)
                ? 'bg-blue-600 text-white'
                : 'bg-slate-700 text-slate-400'
            }`}
          >
            {LEVEL_LABELS[level]}
          </button>
        ))}
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Auto-follow toggle */}
      <label className="flex items-center gap-2 text-xs cursor-pointer select-none">
        <input
          type="checkbox"
          checked={autoFollow}
          onChange={(e) => setAutoFollow(e.target.checked)}
          aria-label="Auto-follow newest log"
          className="cursor-pointer"
        />
        Auto-follow
      </label>

      {/* Isolation display */}
      {isolatedBrainId && (
        <div
          className="text-xs text-muted-foreground flex items-center gap-2 ml-2 px-2 py-1 bg-muted rounded"
          role="status"
          aria-live="polite"
        >
          <span>Viewing: {isolatedBrainId}</span>
          <button
            onClick={() => {
              setIsolatedBrain(null)
              onFilterChange?.()
            }}
            aria-label="Clear brain isolation"
            className="hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  )
}
