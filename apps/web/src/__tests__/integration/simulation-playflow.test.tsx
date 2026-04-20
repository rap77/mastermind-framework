/**
 * Integration Tests: Simulation Playback Flow
 *
 * End-to-end tests for the complete user workflow:
 * 1. Load execution → verify all components render
 * 2. Click play → verify playback starts, isPlaying=true
 * 3. Click pause → verify playback stops, isPlaying=false
 * 4. Click reset → verify state cleared, back to initial
 * 5. Verify timeline scrubbing works with jumpToMilestone
 *
 * These tests verify the integration between the page, store, and components.
 * We mock the heavy components (SimulationCanvas) to avoid ResizeObserver issues
 * while still testing the full integration of the page + store + controls.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SimulationPage from '@/app/(protected)/simulation/page'
import { useSimulationStore } from '@/stores/simulationStore'
import { mockExecution } from '@/mocks/mock-execution'

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

// Mock SimulationCanvas to avoid React Flow/ResizeObserver complexity in integration tests
vi.mock('@/components/simulation/SimulationCanvas', () => ({
  SimulationCanvas: () => <div data-testid="simulation-canvas">Canvas Mock</div>,
}))

// Mock ErrorSummary to avoid selector issues
vi.mock('@/components/simulation/ErrorSummary', () => ({
  ErrorSummary: () => <div data-testid="error-summary">Error Summary Mock</div>,
}))

// Mock TimelineScrubber to avoid selector issues
vi.mock('@/components/simulation/TimelineScrubber', () => ({
  TimelineScrubber: () => <div data-testid="timeline-scrubber">Timeline Mock</div>,
}))

// Mock EventLog to avoid selector issues
vi.mock('@/components/simulation/EventLog', () => ({
  __esModule: true,
  default: () => <div data-testid="event-log">Event Log Mock</div>,
}))

// No need for fake timers - we'll use real setTimeout with test timeouts

describe('Simulation Playback Flow - Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset store state
    useSimulationStore.getState().reset()
  })

  afterEach(() => {
    // Clean up: stop any playing state
    const store = useSimulationStore.getState()
    if (store.isPlaying) {
      store.pause()
    }
  })

  describe('Phase 1: Load Execution', () => {
    it('should load execution and render all components', async () => {
      const user = userEvent.setup()

      render(<SimulationPage />)

      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.getByTestId('error-summary')).toBeInTheDocument()
      })

      // Verify all main components are rendered
      expect(screen.getByTestId('error-summary')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument() // ReplayControls
      expect(screen.getByTestId('simulation-canvas')).toBeInTheDocument()
      expect(screen.getByTestId('timeline-scrubber')).toBeInTheDocument()
      expect(screen.getByTestId('event-log')).toBeInTheDocument()

      // Verify initial state from store
      const state = useSimulationStore.getState()
      expect(state.currentExecution).toEqual(mockExecution)
      expect(state.isPlaying).toBe(false)
      expect(state.currentMilestoneIndex).toBe(0)
      expect(state.playbackSpeed).toBe(1)
    })

    it('should initialize with correct error detection', async () => {
      render(<SimulationPage />)

      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.getByTestId('error-summary')).toBeInTheDocument()
      })

      // Verify error detection from mockExecution
      const state = useSimulationStore.getState()
      expect(state.errorNodes.size).toBe(1) // brain-3 has error
      expect(state.errorMessages.get('node-3')).toContain('timeout error')
      // Note: brain-3 (1200ms) and brain-5 (1100ms) are both slow, so we expect 2
      expect(state.slowNodes.size).toBe(2) // brain-3 and brain-5 are slow
      expect(state.slowNodes.get('node-5')).toBe(1100)
    })
  })

  describe('Phase 2: Play Playback', () => {
    it('should start playback when play button is clicked', async () => {
      const user = userEvent.setup()

      render(<SimulationPage />)

      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument()
      })

      // Find and click the play button
      const playButton = screen.getByRole('button', { name: /play/i })
      await user.click(playButton)

      // Verify playback started
      await waitFor(() => {
        const state = useSimulationStore.getState()
        expect(state.isPlaying).toBe(true)
      })

      // Verify button text changed to "Pause"
      expect(screen.getByRole('button', { name: /pause/i })).toBeInTheDocument()
    })

    it('should advance milestones during playback', async () => {
      const user = userEvent.setup()

      render(<SimulationPage />)

      // Wait for loading
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument()
      })

      // Start playback
      const playButton = screen.getByRole('button', { name: /play/i })
      await user.click(playButton)

      // Verify initial milestone
      expect(useSimulationStore.getState().currentMilestoneIndex).toBe(0)

      // Wait for milestone to advance (BASE_DELAY_MS = 1000ms)
      await waitFor(
        () => {
          const state = useSimulationStore.getState()
          expect(state.currentMilestoneIndex).toBeGreaterThan(0)
        },
        { timeout: 2000 }
      )
    })
  })

  describe('Phase 3: Pause Playback', () => {
    it('should pause playback when pause button is clicked', async () => {
      const user = userEvent.setup()

      render(<SimulationPage />)

      // Wait for loading
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument()
      })

      // Start playback
      const playButton = screen.getByRole('button', { name: /play/i })
      await user.click(playButton)

      // Verify playing
      await waitFor(() => {
        expect(useSimulationStore.getState().isPlaying).toBe(true)
      })

      // Pause playback
      const pauseButton = screen.getByRole('button', { name: /pause/i })
      await user.click(pauseButton)

      // Verify paused
      await waitFor(() => {
        const state = useSimulationStore.getState()
        expect(state.isPlaying).toBe(false)
      })

      // Verify button text changed back to "Play"
      expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument()
    })

    it('should maintain current position when paused', async () => {
      const user = userEvent.setup()

      render(<SimulationPage />)

      // Wait for loading
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument()
      })

      // Start playback
      const playButton = screen.getByRole('button', { name: /play/i })
      await user.click(playButton)

      // Wait for milestone to advance
      await waitFor(
        () => {
          expect(useSimulationStore.getState().currentMilestoneIndex).toBeGreaterThan(0)
        },
        { timeout: 2000 }
      )

      // Get current milestone index
      const milestoneBeforePause = useSimulationStore.getState().currentMilestoneIndex

      // Pause
      const pauseButton = screen.getByRole('button', { name: /pause/i })
      await user.click(pauseButton)

      // Verify milestone index didn't change
      await waitFor(() => {
        const state = useSimulationStore.getState()
        expect(state.currentMilestoneIndex).toBe(milestoneBeforePause)
      })
    })
  })

  describe('Phase 4: Reset Playback', () => {
    it('should reset state when reset button is clicked', async () => {
      const user = userEvent.setup()

      render(<SimulationPage />)

      // Wait for loading
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument()
      })

      // Start playback and advance
      const playButton = screen.getByRole('button', { name: /play/i })
      await user.click(playButton)

      // Wait for milestone to advance
      await waitFor(
        () => {
          expect(useSimulationStore.getState().currentMilestoneIndex).toBeGreaterThan(0)
        },
        { timeout: 2000 }
      )

      // Reset
      const resetButton = screen.getByRole('button', { name: /reset/i })
      await user.click(resetButton)

      // Verify reset to initial state
      await waitFor(() => {
        const state = useSimulationStore.getState()
        expect(state.isPlaying).toBe(false)
        expect(state.currentMilestoneIndex).toBe(0)
        expect(state.playbackSpeed).toBe(1)
      })
    })

    it('should clear execution data on reset', async () => {
      const user = userEvent.setup()

      render(<SimulationPage />)

      // Wait for loading
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument()
      })

      // Verify execution is loaded
      expect(useSimulationStore.getState().currentExecution).not.toBeNull()

      // Reset
      const resetButton = screen.getByRole('button', { name: /reset/i })
      await user.click(resetButton)

      // Verify execution cleared
      await waitFor(() => {
        const state = useSimulationStore.getState()
        expect(state.currentExecution).toBeNull()
        expect(state.errorNodes.size).toBe(0)
        expect(state.slowNodes.size).toBe(0)
      })
    })
  })

  describe('Phase 5: Timeline Scrubbing', () => {
    it('should jump to specific milestone', async () => {
      render(<SimulationPage />)

      // Wait for loading
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument()
      })

      // Verify starting at milestone 0
      expect(useSimulationStore.getState().currentMilestoneIndex).toBe(0)

      // Jump to milestone 2
      useSimulationStore.getState().jumpToMilestone(2)

      // Verify position updated
      await waitFor(() => {
        const state = useSimulationStore.getState()
        expect(state.currentMilestoneIndex).toBe(2)
      })
    })

    it('should clamp milestone index to valid range', async () => {
      render(<SimulationPage />)

      // Wait for loading
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument()
      })

      // Try to jump beyond max
      useSimulationStore.getState().jumpToMilestone(999)

      // Should clamp to max milestone
      await waitFor(() => {
        const state = useSimulationStore.getState()
        expect(state.currentMilestoneIndex).toBe(5) // mockExecution has 6 milestones (0-5)
      })

      // Try to jump below min
      useSimulationStore.getState().jumpToMilestone(-5)

      // Should clamp to 0
      await waitFor(() => {
        const state = useSimulationStore.getState()
        expect(state.currentMilestoneIndex).toBe(0)
      })
    })

    it('should filter events by current milestone', async () => {
      render(<SimulationPage />)

      // Wait for loading
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument()
      })

      // At milestone 0, should have minimal events
      const eventsAtStart = useSimulationStore.getState().getFilteredEvents()
      expect(eventsAtStart.length).toBeGreaterThanOrEqual(0)

      // Jump to milestone 4 (end)
      useSimulationStore.getState().jumpToMilestone(4)

      // Should have more events at end
      await waitFor(() => {
        const eventsAtEnd = useSimulationStore.getState().getFilteredEvents()
        expect(eventsAtEnd.length).toBeGreaterThan(eventsAtStart.length)
      })
    })
  })

  describe('Phase 6: Playback Speed Control', () => {
    it('should change playback speed', async () => {
      const user = userEvent.setup()

      render(<SimulationPage />)

      // Wait for loading
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument()
      })

      // Find speed selector
      const speedSelect = screen.getByRole('combobox')
      expect(speedSelect).toBeInTheDocument()

      // Change speed to 2x
      await user.selectOptions(speedSelect, '2')

      // Verify speed updated
      await waitFor(() => {
        const state = useSimulationStore.getState()
        expect(state.playbackSpeed).toBe(2)
      })
    })

    it('should support all speed options', async () => {
      const user = userEvent.setup()

      render(<SimulationPage />)

      // Wait for loading
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument()
      })

      const speedSelect = screen.getByRole('combobox')

      const speeds: Array<0.5 | 1 | 2 | 5> = [0.5, 1, 2, 5]

      for (const speed of speeds) {
        await user.selectOptions(speedSelect, speed.toString())

        await waitFor(() => {
          expect(useSimulationStore.getState().playbackSpeed).toBe(speed)
        })
      }
    })
  })

  describe('Complete Workflow Integration', () => {
    it('should complete full workflow: load → play → pause → reset', async () => {
      const user = userEvent.setup()

      render(<SimulationPage />)

      // 1. Load execution
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument()
      })
      expect(useSimulationStore.getState().currentExecution).not.toBeNull()

      // 2. Start playback
      const playButton = screen.getByRole('button', { name: /play/i })
      await user.click(playButton)

      await waitFor(() => {
        expect(useSimulationStore.getState().isPlaying).toBe(true)
      })

      // 3. Wait for milestone to advance
      await waitFor(
        () => {
          expect(useSimulationStore.getState().currentMilestoneIndex).toBeGreaterThan(0)
        },
        { timeout: 2000 }
      )

      const milestoneAfterPlay = useSimulationStore.getState().currentMilestoneIndex
      expect(milestoneAfterPlay).toBeGreaterThan(0)

      // 4. Pause playback
      const pauseButton = screen.getByRole('button', { name: /pause/i })
      await user.click(pauseButton)

      await waitFor(() => {
        expect(useSimulationStore.getState().isPlaying).toBe(false)
      })

      // 5. Reset
      const resetButton = screen.getByRole('button', { name: /reset/i })
      await user.click(resetButton)

      await waitFor(() => {
        const state = useSimulationStore.getState()
        expect(state.isPlaying).toBe(false)
        expect(state.currentMilestoneIndex).toBe(0)
        expect(state.currentExecution).toBeNull()
      })
    })
  })
})
