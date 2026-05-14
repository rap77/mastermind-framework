/**
 * SessionEvaluatedBadge — Command Center badge showing Brain #7 quality score.
 *
 * Displays the quality score from the last completed brain session, as evaluated
 * by Brain #7 (Growth/Data). Updates in real-time via WebSocket without a page reload.
 *
 * Badge text: "Última sesión: score 0.87"
 *
 * Score color coding:
 *   - >= 0.75 (high)    → green  (high_value session)
 *   - >= 0.50 (medium)  → yellow
 *   - < 0.50  (low)     → red
 */

"use client"

import { useSessionEvaluated } from "@/hooks/useSessionEvaluated"

function getScoreColor(score: number): string {
  if (score >= 0.75) return "bg-green-100 text-green-800 border-green-200"
  if (score >= 0.50) return "bg-yellow-100 text-yellow-800 border-yellow-200"
  return "bg-red-100 text-red-800 border-red-200"
}

function formatScore(score: number): string {
  return score.toFixed(2)
}

/**
 * Badge component that shows the latest Brain #7 session quality score.
 *
 * Renders nothing until the first session_evaluated event is received.
 * Updates in real-time via WebSocket without page reload.
 *
 * @example
 * ```tsx
 * // In CommandCenterWrapper or CommandCenter header:
 * <SessionEvaluatedBadge />
 * ```
 */
export function SessionEvaluatedBadge() {
  const { lastScore, hasScore, lastBrainIds } = useSessionEvaluated()

  if (!hasScore || lastScore === null) {
    return null
  }

  const colorClass = getScoreColor(lastScore)
  const brainCount = lastBrainIds.length
  const brainLabel = brainCount === 1 ? "brain" : "brains"

  return (
    <div
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-colors ${colorClass}`}
      title={`Brain #7 evaluation: ${lastScore.toFixed(4)} across ${brainCount} ${brainLabel}`}
      data-testid="session-evaluated-badge"
    >
      <span className="size-1.5 rounded-full bg-current opacity-75" />
      <span>
        Última sesión: score {formatScore(lastScore)}
      </span>
    </div>
  )
}
