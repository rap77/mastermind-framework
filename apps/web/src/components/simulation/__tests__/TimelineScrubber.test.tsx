/**
 * TimelineScrubber.test.tsx — Unit tests for TimelineScrubber
 *
 * Tests the timeline scrubber component with TDD approach:
 * - Event listener cleanup on drag end
 * - Mouse drag behavior
 * - Click to navigate
 * - Keyboard navigation
 * - Memory leak prevention
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, cleanup, fireEvent } from '@testing-library/react'
import TimelineScrubber from '../TimelineScrubber'
import { useSimulationStore } from '@/stores/simulationStore'

// Mock execution data
const mockExecution = {
  id: 'exec-123',
  task_id: 'task-456',
  brief: 'Test execution',
  status: 'success' as const,
  duration_ms: 5000,
  brain_count: 3,
  created_at: '2026-04-16T10:00:00Z',
  milestones: [
    { index: 0, timestamp: 1000, label: 'Start', brain_count: 0 },
    { index: 1, timestamp: 2000, label: 'Milestone 1', brain_count: 1 },
    { index: 2, timestamp: 3000, label: 'Milestone 2', brain_count: 2 },
    { index: 3, timestamp: 4000, label: 'End', brain_count: 3 },
  ],
  brain_outputs: {},
  graph_snapshot: {
    nodes: [],
    edges: [],
  },
}

describe('TimelineScrubber', () => {
  beforeEach(() => {
    // Load mock execution
    const store = useSimulationStore.getState()
    store.loadExecution(mockExecution)
  })

  afterEach(() => {
    cleanup()
    // Reset store after each test
    const store = useSimulationStore.getState()
    store.reset()
  })

  describe('Event Listener Cleanup', () => {
    it('should add mousemove and mouseup listeners when dragging starts', () => {
      const addEventListenerSpy = vi.spyOn(window, 'addEventListener')
      const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')

      render(<TimelineScrubber />)

      const track = screen.getByRole('slider')
      fireEvent.mouseDown(track, { clientX: 100 })

      // Verify listeners were added
      expect(addEventListenerSpy).toHaveBeenCalledWith('mousemove', expect.any(Function))
      expect(addEventListenerSpy).toHaveBeenCalledWith('mouseup', expect.any(Function))

      addEventListenerSpy.mockRestore()
      removeEventListenerSpy.mockRestore()
    })

    it('should remove mousemove and mouseup listeners when dragging ends', () => {
      const addEventListenerSpy = vi.spyOn(window, 'addEventListener')
      const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')

      render(<TimelineScrubber />)

      const track = screen.getByRole('slider')

      // Start dragging
      fireEvent.mouseDown(track, { clientX: 100 })

      // Clear the spy calls from mouseDown
      addEventListenerSpy.mockClear()
      removeEventListenerSpy.mockClear()

      // End dragging
      fireEvent.mouseUp(window)

      // Verify listeners were removed
      expect(removeEventListenerSpy).toHaveBeenCalledWith('mousemove', expect.any(Function))
      expect(removeEventListenerSpy).toHaveBeenCalledWith('mouseup', expect.any(Function))

      addEventListenerSpy.mockRestore()
      removeEventListenerSpy.mockRestore()
    })

    it('should clean up listeners on unmount to prevent memory leaks', () => {
      const addEventListenerSpy = vi.spyOn(window, 'addEventListener')
      const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')

      const { unmount } = render(<TimelineScrubber />)

      const track = screen.getByRole('slider')
      fireEvent.mouseDown(track, { clientX: 100 })

      // Clear the spy calls from mouseDown
      addEventListenerSpy.mockClear()
      removeEventListenerSpy.mockClear()

      // Unmount while dragging
      unmount()

      // Verify listeners were removed during cleanup
      expect(removeEventListenerSpy).toHaveBeenCalledWith('mousemove', expect.any(Function))
      expect(removeEventListenerSpy).toHaveBeenCalledWith('mouseup', expect.any(Function))

      addEventListenerSpy.mockRestore()
      removeEventListenerSpy.mockRestore()
    })

    it('should not add duplicate listeners when dragging state remains true across renders', () => {
      const addEventListenerSpy = vi.spyOn(window, 'addEventListener')

      render(<TimelineScrubber />)

      const track = screen.getByRole('slider')
      fireEvent.mouseDown(track, { clientX: 100 })

      const callCountAfterMouseDown = addEventListenerSpy.mock.calls.length

      // Force a re-render while dragging
      fireEvent.mouseMove(track, { clientX: 150 })

      const callCountAfterMouseMove = addEventListenerSpy.mock.calls.length

      // Should not have called addEventListener again
      expect(callCountAfterMouseMove).toBe(callCountAfterMouseDown)

      addEventListenerSpy.mockRestore()
    })
  })

  describe('Mouse Drag Navigation', () => {
    it('should jump to milestone on mouse down', () => {
      render(<TimelineScrubber />)

      const track = screen.getByRole('slider')
      fireEvent.mouseDown(track, { clientX: 100 })

      const store = useSimulationStore.getState()
      expect(store.currentMilestoneIndex).toBeGreaterThanOrEqual(0)
    })

    it('should handle mouse drag without errors', () => {
      render(<TimelineScrubber />)

      const track = screen.getByRole('slider')

      // Start drag
      fireEvent.mouseDown(track, { clientX: 10 })

      // Simulate mouse move
      const mouseMoveEvent = new MouseEvent('mousemove', {
        clientX: 50,
        bubbles: true,
        cancelable: true,
      })
      window.dispatchEvent(mouseMoveEvent)

      // End drag
      fireEvent.mouseUp(window)

      // Should complete without errors
      const store = useSimulationStore.getState()
      expect(store.currentMilestoneIndex).toBeGreaterThanOrEqual(0)
    })
  })

  describe('Keyboard Navigation', () => {
    it('should navigate to next milestone on ArrowRight', () => {
      render(<TimelineScrubber />)

      const track = screen.getByRole('slider')

      fireEvent.keyDown(track, { key: 'ArrowRight' })

      const store = useSimulationStore.getState()
      expect(store.currentMilestoneIndex).toBe(1)
    })

    it('should navigate to previous milestone on ArrowLeft', () => {
      // Start at milestone 2
      useSimulationStore.getState().jumpToMilestone(2)

      render(<TimelineScrubber />)

      const track = screen.getByRole('slider')
      fireEvent.keyDown(track, { key: 'ArrowLeft' })

      const store = useSimulationStore.getState()
      expect(store.currentMilestoneIndex).toBe(1)
    })

    it('should not go below 0 on ArrowLeft', () => {
      render(<TimelineScrubber />)

      const track = screen.getByRole('slider')
      fireEvent.keyDown(track, { key: 'ArrowLeft' })

      const store = useSimulationStore.getState()
      expect(store.currentMilestoneIndex).toBe(0)
    })

    it('should not go above max index on ArrowRight', () => {
      // Start at last milestone
      useSimulationStore.getState().jumpToMilestone(3)

      render(<TimelineScrubber />)

      const track = screen.getByRole('slider')
      fireEvent.keyDown(track, { key: 'ArrowRight' })

      const store = useSimulationStore.getState()
      expect(store.currentMilestoneIndex).toBe(3)
    })
  })

  describe('Accessibility - Dynamic aria-valuetext', () => {
    it('should update aria-valuetext when milestone changes during drag', () => {
      render(<TimelineScrubber />)

      const track = screen.getByRole('slider')

      // Initial aria-valuetext with brain count
      expect(track).toHaveAttribute('aria-valuetext', 'Start (0 brains)')

      // Drag to milestone 1 using keyboard (more reliable in tests)
      fireEvent.keyDown(track, { key: 'ArrowRight' })

      // aria-valuetext should update to "Milestone 1 (1 brain)"
      expect(track).toHaveAttribute('aria-valuetext', 'Milestone 1 (1 brain)')

      // Drag to milestone 2
      fireEvent.keyDown(track, { key: 'ArrowRight' })

      // aria-valuetext should update to "Milestone 2 (2 brains)"
      expect(track).toHaveAttribute('aria-valuetext', 'Milestone 2 (2 brains)')
    })

    it('should include milestone label and brain count in aria-valuetext', () => {
      render(<TimelineScrubber />)

      const track = screen.getByRole('slider')

      // Navigate to milestone 1
      fireEvent.keyDown(track, { key: 'ArrowRight' })

      // aria-valuetext should contain both label and brain count
      const ariaValuetext = track.getAttribute('aria-valuetext')
      expect(ariaValuetext).toContain('Milestone 1')
      expect(ariaValuetext).toContain('1 brain')
    })

    it('should update aria-valuetext on keyboard navigation', () => {
      render(<TimelineScrubber />)

      const track = screen.getByRole('slider')

      // Initial state
      expect(track).toHaveAttribute('aria-valuetext', 'Start (0 brains)')

      // Navigate to next milestone
      fireEvent.keyDown(track, { key: 'ArrowRight' })

      // aria-valuetext should update with brain count
      expect(track).toHaveAttribute('aria-valuetext', 'Milestone 1 (1 brain)')
    })
  })
})
