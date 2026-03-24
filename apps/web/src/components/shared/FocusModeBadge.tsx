/**
 * FocusModeBadge — Floating escape hatch for Focus Mode.
 *
 * **Purpose:** Gives user a visible affordance to exit Focus Mode via click
 * or keyboard shortcut ([F] / [Esc]).
 *
 * **Visibility:** Only rendered when isFocusMode === true.
 * **Position:** Configurable corner (default: top-right — Fitts's Law high-access).
 *
 * **Animation:** CSS transition via data-visible attribute (no framer-motion dep).
 *
 * **Phase:** 08-04 — Wave 3
 */

'use client'

import { useEffect } from 'react'
import { useOrchestratorStore } from '@/stores/orchestratorStore'

// ─── Types ────────────────────────────────────────────────────────────────────

export interface FocusModeBadgeProps {
  /** Corner position of the badge. Default: 'top-right' (Fitts's Law) */
  position?: 'top-left' | 'top-right' | 'bottom-right'
}

const POSITION_CLASSES: Record<NonNullable<FocusModeBadgeProps['position']>, string> = {
  'top-left': 'top-4 left-4',
  'top-right': 'top-4 right-4',
  'bottom-right': 'bottom-4 right-4',
}

// ─── Component ────────────────────────────────────────────────────────────────

/**
 * FocusModeBadge — floating button to exit Focus Mode.
 *
 * Keyboard shortcuts:
 * - [F] — toggle Focus Mode
 * - [Esc] — exit Focus Mode (sets userOverride=true)
 *
 * @example
 * ```tsx
 * // In root layout or NexusPage
 * <FocusModeBadge />
 * ```
 */
export function FocusModeBadge({ position = 'top-right' }: FocusModeBadgeProps) {
  const { isFocusMode, toggleOverride } = useOrchestratorStore()

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't interfere with form inputs or text areas
      const target = e.target as HTMLElement
      if (target.tagName === 'TEXTAREA' || target.tagName === 'INPUT') return

      if (e.key.toLowerCase() === 'f') {
        e.preventDefault()
        toggleOverride()
      }
      if (e.key === 'Escape') {
        // Only intercept Escape when Focus Mode is active to avoid modal conflicts
        if (isFocusMode) {
          e.preventDefault()
          toggleOverride()
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [toggleOverride, isFocusMode])

  if (!isFocusMode) return null

  const positionClass = POSITION_CLASSES[position]

  return (
    <button
      onClick={toggleOverride}
      className={`fixed ${positionClass} z-50 px-3 py-1.5 rounded-md bg-blue-600 text-white text-xs font-semibold shadow-lg hover:bg-blue-700 transition-colors cursor-pointer`}
      aria-label="Exit Focus Mode"
      title="Exit Focus Mode (Esc)"
    >
      Salir [Esc]
    </button>
  )
}
