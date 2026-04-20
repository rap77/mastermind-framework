'use client'

import React from 'react'
import { cn } from '@/lib/utils'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
  TooltipPortal,
} from '@/components/ui/tooltip'

// ─── Props ────────────────────────────────────────────────────────────────────

export interface HelpTooltipProps {
  className?: string
}

// ─── Component ────────────────────────────────────────────────────────────────

/**
 * HelpTooltip — keyboard shortcuts documentation for TimelineScrubber.
 *
 * **Features:**
 * - Shows keyboard shortcuts in a tooltip
 * - Arrow keys (←/→) for navigation
 * - Space for play/pause
 * - Keyboard key icons with clear labels
 * - Integrated with TimelineScrubber
 *
 * @example
 * ```tsx
 * <HelpTooltip />
 * ```
 */
export default function HelpTooltip({ className }: HelpTooltipProps) {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger>
          <span
            className={cn(
              'inline-flex items-center justify-center',
              'w-6 h-6 rounded',
              'text-xs font-medium',
              'transition-colors cursor-pointer',
              'hover:bg-muted',
              'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1',
              className
            )}
            data-testid="keyboard-shortcuts-help"
          >
            ?
          </span>
        </TooltipTrigger>
        <TooltipPortal>
          <TooltipContent side="top" className="max-w-xs">
            <div className="space-y-2">
              <div className="font-semibold">Keyboard Shortcuts</div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">←</kbd>
                  <kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">→</kbd>
                  <span className="text-xs">Navigate milestones</span>
                </div>
                <div className="flex items-center gap-2">
                  <kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">Space</kbd>
                  <span className="text-xs">Play / Pause</span>
                </div>
              </div>
            </div>
          </TooltipContent>
        </TooltipPortal>
      </Tooltip>
    </TooltipProvider>
  )
}

export { HelpTooltip }
