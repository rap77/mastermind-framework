/**
 * Simulation & Replay Route — Execution replay with timeline scrubbing
 *
 * Main page for the Simulation & Replay feature (B2).
 * Layout: Vertical stack with header, error summary, controls, canvas, timeline, and event log.
 *
 * Features:
 * - Load and replay past executions
 * - Timeline scrubbing with milestone markers
 * - Error detection and slow node highlighting
 * - Playback controls (play/pause, speed, reset)
 * - Real-time event log filtering
 * - Read-only graph visualization with status overlays
 *
 * Components (6 total, vertical stack):
 * 1. Header: "Simulation & Replay" title
 * 2. ErrorSummary: error statistics (errors, slow nodes, total time)
 * 3. ReplayControls: play/pause, reset, speed selector
 * 4. SimulationCanvas: read-only React Flow with node status overlays
 * 5. TimelineScrubber: horizontal timeline with milestone markers
 * 6. EventLog: scrollable event log with color-coded events
 *
 * Uses theme tokens for all colors (dark mode compatible).
 */

'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { ErrorSummary } from '@/components/simulation/ErrorSummary'
import { ReplayControls } from '@/components/simulation/ReplayControls'
import { SimulationCanvas } from '@/components/simulation/SimulationCanvas'
import { TimelineScrubber } from '@/components/simulation/TimelineScrubber'
import EventLog from '@/components/simulation/EventLog'
import { useSimulationStore } from '@/stores/simulationStore'
import { mockExecution } from '@/mocks/mock-execution'

// ─── Page Component ───────────────────────────────────────────────────────────

export default function SimulationPage() {
  const router = useRouter()
  const loadExecution = useSimulationStore((state) => state.loadExecution)

  // Loading and error states for API integration
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load mock execution on mount
  useEffect(() => {
    try {
      loadExecution(mockExecution)
      setIsLoading(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load execution')
      setIsLoading(false)
    }
  }, [loadExecution])

  return (
    <div className="flex flex-col min-h-screen bg-background">
      {/* Header */}
      <div
        className="px-6 py-4 border-b flex items-center justify-between"
        style={{ borderColor: 'var(--color-border)' }}
      >
        <div>
          <h1 className="text-2xl font-bold text-foreground">
            Simulation & Replay
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Replay and analyze past executions with timeline scrubbing
          </p>
        </div>
        <button
          onClick={() => router.push('/flow-designer')}
          className="px-4 py-2 rounded text-sm font-medium"
          style={{
            backgroundColor: 'var(--color-primary)',
            color: 'var(--color-primary-foreground)',
          }}
        >
          Edit Flow
        </button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div
          data-testid="loading-indicator"
          className="flex-1 flex items-center justify-center"
        >
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
            <p className="mt-2 text-sm text-muted-foreground">Loading execution...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div
          data-testid="error-banner"
          className="mx-6 mt-6 p-4 rounded border"
          style={{
            backgroundColor: 'var(--color-destructive-muted)',
            borderColor: 'var(--color-destructive)',
          }}
        >
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5"
                style={{ color: 'var(--color-destructive)' }}
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="flex-1">
              <h3
                className="text-sm font-medium"
                style={{ color: 'var(--color-destructive-foreground)' }}
              >
                Error loading execution
              </h3>
              <p
                className="mt-1 text-sm"
                style={{ color: 'var(--color-destructive-muted-foreground)' }}
              >
                {error}
              </p>
            </div>
            <button
              onClick={() => window.location.reload()}
              className="flex-shrink-0 px-3 py-1 text-sm font-medium rounded border"
              style={{
                backgroundColor: 'var(--color-destructive)',
                color: 'var(--color-destructive-foreground)',
                borderColor: 'var(--color-destructive)',
              }}
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Main Content - Only show when not loading and no error */}
      {!isLoading && !error && (
        <>
          {/* Error Summary */}
          <div className="px-6 py-4">
            <ErrorSummary />
          </div>

      {/* Replay Controls */}
      <ReplayControls />

      {/* Main Canvas Area */}
      <div className="flex-1 px-6 py-4 overflow-hidden">
        <SimulationCanvas />
      </div>

      {/* Bottom Section: Timeline + Event Log */}
      <div className="px-6 pb-6 space-y-4">
        {/* Timeline Scrubber */}
        <TimelineScrubber />

        {/* Event Log */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <div className="text-sm font-semibold text-foreground mb-2">
              Event Log
            </div>
            <EventLog />
          </div>
        </div>
      </div>
        </>
      )}
    </div>
  )
}
