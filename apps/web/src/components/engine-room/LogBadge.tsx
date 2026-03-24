/**
 * LogBadge Component
 *
 * **Purpose:** Display brain name + id badge with level color in log lines
 * **Context:** Phase 08-03 — Engine Room live log viewer
 */

import { colorForLevel } from '@/lib/log-parser'

// ─── Types ──────────────────────────────────────────────────────────────────

interface LogBadgeProps {
  brainId: string
  brainName: string
  level: 'info' | 'warn' | 'error'
  onClick?: () => void
}

// ─── Component ──────────────────────────────────────────────────────────────

/**
 * Badge showing brain name + id with color based on log level.
 * Optionally clickable to trigger brain isolation mode.
 */
export function LogBadge({ brainId, brainName, level, onClick }: LogBadgeProps) {
  const levelColor = colorForLevel(level)

  return (
    <span
      role="button"
      tabIndex={onClick ? 0 : -1}
      onClick={onClick}
      onKeyDown={(e) => {
        if (onClick && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault()
          onClick()
        }
      }}
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-sm bg-secondary text-xs font-mono ${levelColor} ${
        onClick ? 'cursor-pointer hover:opacity-80 transition-opacity' : 'cursor-default'
      }`}
      aria-label={`Brain: ${brainName} (${brainId}), level: ${level}`}
    >
      <span>{brainName}</span>
      <span className="text-muted-foreground opacity-70">({brainId})</span>
    </span>
  )
}
