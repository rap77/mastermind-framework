'use client'

import React, { useState, useRef, useCallback, useEffect } from 'react'
import { cn } from '@/lib/utils'
import type { SnapshotMilestone } from '@/stores/replayStore'

// ─── Props ────────────────────────────────────────────────────────────────────

export interface SnapshotScrubberProps {
  milestones: SnapshotMilestone[]
  currentIndex: number
  onScrub: (index: number) => void
  onMilestoneHover?: (milestone: SnapshotMilestone | null) => void
  className?: string
}

// ─── Component ────────────────────────────────────────────────────────────────

/**
 * SnapshotScrubber — timeline scrubber for execution replay navigation.
 *
 * **Features:**
 * - Horizontal track with milestone markers (max 7, Miller's Law)
 * - Click track to jump to nearest milestone
 * - Keyboard navigation: ArrowLeft/ArrowRight between milestones
 * - Min hitbox 44px for mobile accessibility
 * - Integrated with useReplayStore via onScrub callback
 *
 * @example
 * ```tsx
 * <SnapshotScrubber
 *   milestones={milestones}
 *   currentIndex={currentSnapshotIndex}
 *   onScrub={(index) => useReplayStore.setState({ currentSnapshotIndex: index })}
 * />
 * ```
 */
export function SnapshotScrubber({
  milestones,
  currentIndex,
  onScrub,
  onMilestoneHover,
  className,
}: SnapshotScrubberProps) {
  const [dragging, setDragging] = useState(false)
  const [hoveredMilestone, setHoveredMilestone] = useState<SnapshotMilestone | null>(null)
  const trackRef = useRef<HTMLDivElement>(null)

  // ── Position calculation ──────────────────────────────────────────────────
  const milestoneCount = milestones.length

  const getPositionPercent = (index: number): number => {
    if (milestoneCount <= 1) return 0
    return (index / (milestoneCount - 1)) * 100
  }

  const getIndexFromMouseEvent = useCallback(
    (clientX: number): number => {
      if (!trackRef.current || milestoneCount === 0) return 0
      const rect = trackRef.current.getBoundingClientRect()
      const percent = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width))
      const rawIndex = Math.round(percent * (milestoneCount - 1))

      // Snap to nearest milestone
      const nearest = milestones.reduce((prev, m) =>
        Math.abs(m.index - rawIndex) < Math.abs(prev.index - rawIndex) ? m : prev
      )
      return nearest.index
    },
    [milestones, milestoneCount]
  )

  // ── Mouse handlers ────────────────────────────────────────────────────────
  const handleTrackMouseDown = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      setDragging(true)
      const index = getIndexFromMouseEvent(e.clientX)
      onScrub(index)
    },
    [getIndexFromMouseEvent, onScrub]
  )

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!dragging) return
      const index = getIndexFromMouseEvent(e.clientX)
      onScrub(index)
    },
    [dragging, getIndexFromMouseEvent, onScrub]
  )

  const handleMouseUp = useCallback(() => {
    setDragging(false)
  }, [])

  // Attach global mouse events for drag-out-of-element scenarios
  useEffect(() => {
    if (dragging) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [dragging, handleMouseMove, handleMouseUp])

  // ── Keyboard navigation ───────────────────────────────────────────────────
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (!milestones.length) return

      const currentMilestoneIdx = milestones.findIndex((m) => m.index === currentIndex)
      const idx = currentMilestoneIdx === -1 ? 0 : currentMilestoneIdx

      if (e.key === 'ArrowRight') {
        e.preventDefault()
        const next = milestones[Math.min(idx + 1, milestones.length - 1)]
        onScrub(next.index)
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault()
        const prev = milestones[Math.max(idx - 1, 0)]
        onScrub(prev.index)
      }
    },
    [milestones, currentIndex, onScrub]
  )

  // ── Milestone hover ───────────────────────────────────────────────────────
  const handleMilestoneHover = useCallback(
    (milestone: SnapshotMilestone | null) => {
      setHoveredMilestone(milestone)
      onMilestoneHover?.(milestone)
    },
    [onMilestoneHover]
  )

  // ── Derived values ────────────────────────────────────────────────────────
  const currentMilestone = milestones.find((m) => m.index === currentIndex)
  const thumbPercent = getPositionPercent(
    milestones.findIndex((m) => m.index === currentIndex) === -1
      ? 0
      : milestones.findIndex((m) => m.index === currentIndex)
  )

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div
      className={cn('flex flex-col gap-2 px-4 py-3 bg-muted rounded-lg', className)}
      data-testid="snapshot-scrubber"
    >
      {/* Track area — min 44px height for mobile accessibility */}
      <div
        ref={trackRef}
        role="slider"
        aria-label="Execution timeline scrubber"
        aria-valuemin={0}
        aria-valuemax={milestoneCount - 1}
        aria-valuenow={milestones.findIndex((m) => m.index === currentIndex)}
        aria-valuetext={currentMilestone?.label ?? 'Start'}
        tabIndex={0}
        className={cn(
          'relative flex items-center cursor-pointer',
          'min-h-[44px]', // Accessibility: WCAG AA minimum touch target
          dragging && 'cursor-grabbing select-none'
        )}
        onMouseDown={handleTrackMouseDown}
        onKeyDown={handleKeyDown}
      >
        {/* Track line */}
        <div className="absolute inset-x-0 h-1 bg-secondary rounded-full" />

        {/* Filled progress bar */}
        <div
          className="absolute left-0 h-1 bg-primary/50 rounded-full transition-all"
          style={{ width: `${thumbPercent}%` }}
        />

        {/* Milestone markers */}
        {milestones.map((milestone, idx) => (
          <button
            key={milestone.index}
            type="button"
            className={cn(
              'absolute w-2.5 h-2.5 rounded-full transition-all',
              'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1',
              milestone.index === currentIndex
                ? 'bg-primary scale-125 shadow-md'
                : 'bg-primary/40 hover:bg-primary/80 hover:scale-110'
            )}
            style={{
              left: `${getPositionPercent(idx)}%`,
              transform: 'translate(-50%, -50%)',
              top: '50%',
            }}
            onClick={(e) => {
              e.stopPropagation()
              onScrub(milestone.index)
            }}
            onMouseEnter={() => handleMilestoneHover(milestone)}
            onMouseLeave={() => handleMilestoneHover(null)}
            aria-label={`Jump to: ${milestone.label}`}
            title={milestone.label}
            data-testid={`milestone-${milestone.index}`}
          />
        ))}

        {/* Draggable thumb */}
        <div
          className={cn(
            'absolute w-4 h-4 bg-primary rounded-full shadow-lg',
            'transition-[left] duration-100 ease-out',
            dragging ? 'cursor-grabbing scale-110' : 'cursor-grab'
          )}
          style={{
            left: `${thumbPercent}%`,
            transform: 'translate(-50%, -50%)',
            top: '50%',
          }}
          data-testid="scrubber-thumb"
        />
      </div>

      {/* Status label row */}
      <div className="flex justify-between items-center text-xs text-muted-foreground">
        <span data-testid="scrubber-label">
          {hoveredMilestone?.label ?? currentMilestone?.label ?? 'Start'}
        </span>
        <span data-testid="scrubber-percentage">
          {Math.round(thumbPercent)}%
        </span>
      </div>
    </div>
  )
}
