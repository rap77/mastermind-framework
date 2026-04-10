'use client'

import { memo, useState, useEffect } from 'react'
import { StatusBadge } from './StatusBadge'
import { useSwipeGesture } from '@/hooks/useSwipeGesture'
import { cn } from '@/lib/utils'

interface Brain {
  id: string
  name: string
  domain: string
  status: 'idle' | 'running' | 'completed' | 'failed'
  lastRunTime?: string
}

interface BrainCardProps {
  brain: Brain
  densityMode: 'compact' | 'normal'
}

export const BrainCard = memo(function BrainCard({ brain, densityMode }: BrainCardProps) {
  const [showActions, setShowActions] = useState(false)
  const [canHover, setCanHover] = useState(false)

  // Detect hover capability after mount (SSR-safe)
  useEffect(() => {
    setCanHover(window.matchMedia('(hover: hover)').matches)
  }, [])

  // Swipe gesture to reveal actions (mobile)
  const { onTouchStart, onTouchMove, onTouchEnd } = useSwipeGesture({
    onSwipeLeft: () => setShowActions(true),
    onSwipeRight: () => setShowActions(false)
  })

  return (
    <div
      className={cn(
        'rounded-lg border bg-card p-4 transition-all hover:shadow-md',
        'group relative'
      )}
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
    >
      {/* Header with name and status */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex-1 min-w-0">
          <h3
            className={cn(
              'font-semibold truncate',
              densityMode === 'compact' ? 'text-sm' : 'text-base'
            )}
          >
            {brain.name}
          </h3>
          {densityMode === 'normal' && (
            <p className="text-xs text-muted-foreground mt-1">
              {brain.domain}
            </p>
          )}
        </div>
        <StatusBadge
          variant={brain.status}
          showPing={brain.status === 'running'}
        />
      </div>

      {/* Additional info in normal mode */}
      {densityMode === 'normal' && brain.lastRunTime && (
        <div className="text-xs text-muted-foreground">
          Last run: {brain.lastRunTime}
        </div>
      )}

      {/* Actions on hover (desktop) or swipe (mobile) */}
      {(showActions || canHover) && (
        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            className="p-1 rounded hover:bg-muted"
            aria-label={`Actions for ${brain.name}`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
            </svg>
          </button>
        </div>
      )}
    </div>
  )
})
