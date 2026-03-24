/**
 * NexusPage — Client wrapper for the Nexus canvas with Focus Mode layout.
 *
 * **Purpose:** Responds to Focus Mode state to collapse sidebar and expand canvas.
 * NexusCanvas remains the core React Flow graph; this wrapper handles layout shifts.
 *
 * **Focus Mode layout:**
 * - Active (isFocusMode=true): Canvas expands full width, sidebar/panel hidden
 * - Inactive (isFocusMode=false): Canvas at ~70% width, panels visible
 *
 * **Animation:** CSS transition on width/opacity (no framer-motion dep).
 *
 * **Phase:** 08-04 — Wave 3 (Focus Mode layout)
 */

'use client'

import { useOrchestratorStore } from '@/stores/orchestratorStore'
import { FocusModeBadge } from '@/components/shared/FocusModeBadge'

// ─── Types ────────────────────────────────────────────────────────────────────

export interface NexusPageLayoutProps {
  /** The NexusCanvas (or NexusCanvasLoader Suspense wrapper) */
  canvas: React.ReactNode
  /** Optional sidebar panel (not visible in Focus Mode) */
  sidebar?: React.ReactNode
  /** Optional right panel (not visible in Focus Mode) */
  panel?: React.ReactNode
}

// ─── Component ────────────────────────────────────────────────────────────────

/**
 * NexusPage layout wrapper — manages sidebar collapse in Focus Mode.
 *
 * When isFocusMode=true:
 * - Sidebar slides out (hidden, opacity 0)
 * - Canvas expands to full width
 * - FocusModeBadge appears in top-right corner
 *
 * @example
 * ```tsx
 * <NexusPage
 *   canvas={<NexusCanvas blueprintBrains={brains} />}
 *   sidebar={<Sidebar />}
 * />
 * ```
 */
export function NexusPage({ canvas, sidebar, panel }: NexusPageLayoutProps) {
  const isFocusMode = useOrchestratorStore((s) => s.isFocusMode)

  return (
    <div className="relative flex h-screen overflow-hidden">
      {/* Sidebar — hidden in Focus Mode */}
      {sidebar && (
        <div
          className={`flex-shrink-0 border-r overflow-hidden transition-all duration-300 ${
            isFocusMode
              ? 'w-0 opacity-0 pointer-events-none'
              : 'w-[250px] opacity-100'
          }`}
          aria-hidden={isFocusMode}
          data-testid="nexus-sidebar"
        >
          {sidebar}
        </div>
      )}

      {/* Canvas — expands in Focus Mode */}
      <div
        className="flex-1 overflow-hidden transition-all duration-300"
        data-testid="nexus-canvas-container"
      >
        {canvas}
      </div>

      {/* Right panel — hidden in Focus Mode */}
      {panel && (
        <div
          className={`flex-shrink-0 border-l overflow-hidden transition-all duration-300 ${
            isFocusMode
              ? 'w-0 opacity-0 pointer-events-none'
              : 'w-[300px] opacity-100'
          }`}
          aria-hidden={isFocusMode}
          data-testid="nexus-panel"
        >
          {panel}
        </div>
      )}

      {/* Focus Mode badge — visible when active, keyboard shortcut to exit */}
      <FocusModeBadge />
    </div>
  )
}
