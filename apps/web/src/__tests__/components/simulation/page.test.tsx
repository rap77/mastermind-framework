/**
 * Tests for simulation/page.tsx — Loading and error states
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import SimulationPage from '@/app/(protected)/simulation/page'
import { useSimulationStore } from '@/stores/simulationStore'

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

// Mock the execution data to control loading/error states
vi.mock('@/mocks/mock-execution', () => ({
  mockExecution: {
    id: 'test-exec-1',
    task_id: 'task-1',
    brief: 'Test execution',
    status: 'success' as const,
    duration_ms: 5000,
    brain_count: 3,
    created_at: '2026-04-17T00:00:00Z',
    milestones: [
      { index: 0, timestamp: 0, label: 'Start', brain_count: 0 },
      { index: 1, timestamp: 5000, label: 'End', brain_count: 3 },
    ],
    brain_outputs: {},
    graph_snapshot: { nodes: [], edges: [] },
  },
}))

// Mock the components to focus on page-level logic
vi.mock('@/components/simulation/ErrorSummary', () => ({
  ErrorSummary: () => <div data-testid="error-summary">Error Summary</div>,
}))

vi.mock('@/components/simulation/ReplayControls', () => ({
  ReplayControls: () => <div data-testid="replay-controls">Replay Controls</div>,
}))

vi.mock('@/components/simulation/SimulationCanvas', () => ({
  SimulationCanvas: () => <div data-testid="simulation-canvas">Canvas</div>,
}))

vi.mock('@/components/simulation/TimelineScrubber', () => ({
  TimelineScrubber: () => <div data-testid="timeline-scrubber">Timeline</div>,
}))

vi.mock('@/components/simulation/EventLog', () => ({
  __esModule: true,
  default: () => <div data-testid="event-log">Event Log</div>,
}))

describe('SimulationPage - Loading and Error States', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset store state
    useSimulationStore.getState().reset()
  })

  describe('Loading State', () => {
    it('should complete loading and show content', async () => {
      render(<SimulationPage />)

      // Wait for loading to complete and content to appear
      await waitFor(() => {
        expect(screen.getByTestId('error-summary')).toBeInTheDocument()
      })

      // Should show main components
      expect(screen.getByTestId('replay-controls')).toBeInTheDocument()
      expect(screen.getByTestId('simulation-canvas')).toBeInTheDocument()
    })
  })

  describe('Normal State', () => {
    it('should render all components after loading', async () => {
      render(<SimulationPage />)

      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.getByTestId('error-summary')).toBeInTheDocument()
      })

      // Verify all components are rendered
      expect(screen.getByTestId('error-summary')).toBeInTheDocument()
      expect(screen.getByTestId('replay-controls')).toBeInTheDocument()
      expect(screen.getByTestId('simulation-canvas')).toBeInTheDocument()
      expect(screen.getByTestId('timeline-scrubber')).toBeInTheDocument()
      expect(screen.getByTestId('event-log')).toBeInTheDocument()
    })

    it('should hide loading indicator after successful load', async () => {
      render(<SimulationPage />)

      // Wait for content to appear (loading is done)
      await waitFor(() => {
        expect(screen.getByTestId('error-summary')).toBeInTheDocument()
      })

      // Loading indicator should not be present
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument()
    })
  })
})
