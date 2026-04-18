'use client'

import React, { useState, useRef, useCallback, useEffect, useMemo } from 'react'
import { cn } from '@/lib/utils'
import { useSimulationStore } from '@/stores/simulationStore'
import type { SnapshotMilestone } from '@/stores/simulationStore'
import { HelpTooltip } from './HelpTooltip'

// ─── Props ────────────────────────────────────────────────────────────────────

export interface TimelineScrubberProps {
  className?: string
}

// ─── Component ────────────────────────────────────────────────────────────────

/**
 * TimelineScrubber — timeline scrubber for simulation replay navigation.
 *
 * **Features:**
 * - Horizontal track with milestone markers
 * - Click track to jump to nearest milestone
 * - Drag scrubber handle to navigate timeline
 * - Keyboard navigation: ArrowLeft/ArrowRight between milestones
 * - Min hitbox 44px for mobile accessibility
 * - Milestone tooltips showing label and brain count
 * - Integrated with useSimulationStore via jumpToMilestone action
 *
 * @example
 * ```tsx
 * <TimelineScrubber />
 * ```
 */
export default function TimelineScrubber({ className }: TimelineScrubberProps) {
  // Store integration
  const currentExecution = useSimulationStore((state) => state.currentExecution)
  const currentMilestoneIndex = useSimulationStore((state) => state.currentMilestoneIndex)
  const jumpToMilestone = useSimulationStore((state) => state.jumpToMilestone)

  // Local state
  const [dragging, setDragging] = useState(false)
  const [hoveredMilestone, setHoveredMilestone] = useState<SnapshotMilestone | null>(null)
  const trackRef = useRef<HTMLDivElement>(null)

  // Refs to track latest handlers for event listener cleanup
  const handleMouseMoveRef = useRef<((e: MouseEvent) => void) | null>(null)
  const handleMouseUpRef = useRef<(() => void) | null>(null)

  // ── Position calculation ──────────────────────────────────────────────────
  const milestones = currentExecution?.milestones ?? []
  const milestoneCount = milestones.length

  // Memoize milestone positions to avoid recalculating on every render
  // This improves performance during playback and dragging
  const milestonePositions = useMemo(() => {
    if (milestoneCount <= 1) {
      return { positions: [], currentPositionPercent: 0, currentMilestoneArrayIndex: 0 }
    }

    const positions = milestones.map((_, index) => (index / (milestoneCount - 1)) * 100)

    // Find the current milestone's array index
    const currentMilestoneArrayIndex = milestones.findIndex((m) => m.index === currentMilestoneIndex)
    const validIndex = currentMilestoneArrayIndex === -1 ? 0 : currentMilestoneArrayIndex

    return {
      positions,
      currentPositionPercent: positions[validIndex] || 0,
      currentMilestoneArrayIndex: validIndex,
    }
  }, [milestones, milestoneCount, currentMilestoneIndex])

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
      jumpToMilestone(index)
    },
    [getIndexFromMouseEvent, jumpToMilestone]
  )

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!dragging) return
      const index = getIndexFromMouseEvent(e.clientX)
      jumpToMilestone(index)
    },
    [dragging, getIndexFromMouseEvent, jumpToMilestone]
  )

  const handleMouseUp = useCallback(() => {
    setDragging(false)
  }, [])

  // Attach global mouse events for drag-out-of-element scenarios
  useEffect(() => {
    // Update refs with latest handlers
    handleMouseMoveRef.current = handleMouseMove
    handleMouseUpRef.current = handleMouseUp

    if (dragging) {
      const mouseMoveHandler = (e: MouseEvent) => {
        handleMouseMoveRef.current?.(e)
      }
      const mouseUpHandler = () => {
        handleMouseUpRef.current?.()
      }

      window.addEventListener('mousemove', mouseMoveHandler)
      window.addEventListener('mouseup', mouseUpHandler)

      // Cleanup function - removes the specific listeners added in this effect
      return () => {
        window.removeEventListener('mousemove', mouseMoveHandler)
        window.removeEventListener('mouseup', mouseUpHandler)
      }
    }

    // Cleanup when not dragging (in case dragging state changes during render)
    return () => {
      // No-op - listeners are cleaned up by the return above when dragging was true
    }
  }, [dragging, handleMouseMove, handleMouseUp])

  // ── Keyboard navigation ───────────────────────────────────────────────────
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (!milestones.length) return

      const currentMilestoneIdx = milestones.findIndex((m) => m.index === currentMilestoneIndex)
      const idx = currentMilestoneIdx === -1 ? 0 : currentMilestoneIdx

      if (e.key === 'ArrowRight') {
        e.preventDefault()
        const next = milestones[Math.min(idx + 1, milestones.length - 1)]
        jumpToMilestone(next.index)
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault()
        const prev = milestones[Math.max(idx - 1, 0)]
        jumpToMilestone(prev.index)
      }
    },
    [milestones, currentMilestoneIndex, jumpToMilestone]
  )

  // ── Derived values ────────────────────────────────────────────────────────
  const currentMilestone = milestones.find((m) => m.index === currentMilestoneIndex)
  const thumbPercent = milestonePositions.currentPositionPercent

  // Dynamic aria-valuetext with milestone label and brain count for accessibility
  const ariaValueText = currentMilestone
    ? `${currentMilestone.label} (${currentMilestone.brain_count} ${currentMilestone.brain_count === 1 ? 'brain' : 'brains'})`
    : 'Start'

  // ── Render ────────────────────────────────────────────────────────────────
  if (milestoneCount === 0) {
    return (
      <div
        className={cn(
          'flex items-center justify-center px-4 py-3 bg-muted rounded-lg text-sm text-muted-foreground',
          className
        )}
        data-testid="timeline-scrubber-empty"
      >
        No milestones available
      </div>
    )
  }

  return (
    <div
      className={cn('flex flex-col gap-2 px-4 py-3 bg-muted rounded-lg', className)}
      data-testid="timeline-scrubber"
    >
      {/* Track area — min 44px height for mobile accessibility */}
      <div
        ref={trackRef}
        role="slider"
        aria-label="Simulation timeline scrubber"
        aria-valuemin={0}
        aria-valuemax={milestoneCount - 1}
        aria-valuenow={milestones.findIndex((m) => m.index === currentMilestoneIndex)}
        aria-valuetext={ariaValueText}
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
        <div
          className="absolute inset-x-0 h-1 rounded-full"
          style={{ backgroundColor: 'var(--color-secondary)' }}
        />

        {/* Filled progress bar */}
        <div
          className="absolute left-0 h-1 rounded-full transition-all"
          style={{
            width: `${thumbPercent}%`,
            backgroundColor: 'var(--color-primary)',
            opacity: '0.5',
          }}
        />

        {/* Milestone markers */}
        {milestones.map((milestone, idx) => (
          <button
            key={milestone.index}
            type="button"
            className={cn(
              'absolute w-2.5 h-2.5 rounded-full transition-all',
              'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1'
            )}
            style={{
              left: `${milestonePositions.positions[idx]}%`,
              transform: 'translate(-50%, -50%)',
              top: '50%',
              backgroundColor:
                milestone.index === currentMilestoneIndex
                  ? 'var(--color-primary)'
                  : 'var(--color-primary)',
              opacity: milestone.index === currentMilestoneIndex ? '1' : '0.4',
              transform: `translate(-50%, -50%) ${milestone.index === currentMilestoneIndex ? 'scale(1.25)' : 'scale(1)'}`,
              boxShadow: milestone.index === currentMilestoneIndex ? 'var(--shadow-md)' : 'none',
            }}
            onMouseEnter={() => setHoveredMilestone(milestone)}
            onMouseLeave={() => setHoveredMilestone(null)}
            onClick={(e) => {
              e.stopPropagation()
              jumpToMilestone(milestone.index)
            }}
            aria-label={`Jump to: ${milestone.label} (Brain ${milestone.brain_count})`}
            title={`${milestone.label} (Brain ${milestone.brain_count})`}
            data-testid={`milestone-${milestone.index}`}
          />
        ))}

        {/* Draggable thumb */}
        <div
          className={cn(
            'absolute w-4 h-4 rounded-full shadow-lg',
            'transition-[left] duration-100 ease-out'
          )}
          style={{
            left: `${thumbPercent}%`,
            transform: 'translate(-50%, -50%)',
            top: '50%',
            backgroundColor: 'var(--color-primary)',
            cursor: dragging ? 'grabbing' : 'grab',
            transform: `translate(-50%, -50%) ${dragging ? 'scale(1.1)' : 'scale(1)'}`,
          }}
          data-testid="scrubber-thumb"
        />
      </div>

      {/* Status label row */}
      <div
        className="flex justify-between items-center text-xs"
        style={{ color: 'var(--color-muted-foreground)' }}
      >
        <span data-testid="scrubber-label">
          {hoveredMilestone
            ? `${hoveredMilestone.label} (Brain ${hoveredMilestone.brain_count})`
            : currentMilestone
              ? `${currentMilestone.label} (Brain ${currentMilestone.brain_count})`
              : 'Start'}
        </span>
        <div className="flex items-center gap-2">
          <HelpTooltip />
          <span data-testid="scrubber-percentage">{Math.round(thumbPercent)}%</span>
        </div>
      </div>
    </div>
  )
}

export { TimelineScrubber }
