/**
 * ReplayControls — Playback controls for simulation replay
 *
 * Provides play/pause toggle, reset, and speed selection for execution replay.
 * Uses simulationStore for state management and follows FlowToolbar pattern.
 */

import { useCallback } from 'react'
import { useSimulationStore } from '@/stores/simulationStore'

export function ReplayControls() {
  const { play, pause, reset, setPlaybackSpeed } = useSimulationStore()
  const isPlaying = useSimulationStore((state) => state.isPlaying)
  const playbackSpeed = useSimulationStore((state) => state.playbackSpeed)

  const handlePlayPause = useCallback(() => {
    if (isPlaying) {
      pause()
    } else {
      play()
    }
  }, [isPlaying, play, pause])

  const handleReset = useCallback(() => {
    reset()
  }, [reset])

  const handleSpeedChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      const speed = parseFloat(e.target.value) as 0.5 | 1 | 2 | 5
      setPlaybackSpeed(speed)
    },
    [setPlaybackSpeed],
  )

  return (
    <div
      className="flex items-center gap-2 px-4 py-2 border-b"
      style={{
        backgroundColor: 'var(--color-surface)',
        borderColor: 'var(--color-border)',
      }}
    >
      {/* Play/Pause Button */}
      <button
        onClick={handlePlayPause}
        className="px-3 py-1 rounded text-sm flex items-center gap-2"
        style={{
          backgroundColor: 'var(--color-primary)',
          color: 'var(--color-primary-foreground)',
        }}
        aria-label={isPlaying ? 'Pause' : 'Play'}
      >
        {isPlaying ? (
          <>
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="currentColor"
              xmlns="http://www.w3.org/2000/svg"
            >
              <rect x="6" y="4" width="4" height="16" />
              <rect x="14" y="4" width="4" height="16" />
            </svg>
            Pause
          </>
        ) : (
          <>
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="currentColor"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M8 5v14l11-7z" />
            </svg>
            Play
          </>
        )}
      </button>

      {/* Reset Button */}
      <button
        onClick={handleReset}
        className="px-3 py-1 rounded text-sm flex items-center gap-2"
        style={{
          backgroundColor: 'var(--color-surface)',
          color: 'var(--color-text-primary)',
          border: '1px solid var(--color-border)',
        }}
        aria-label="Reset"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
          <path d="M3 3v5h5" />
        </svg>
        Reset
      </button>

      <div className="flex-1" />

      {/* Speed Selector */}
      <div className="flex items-center gap-2">
        <label
          htmlFor="playback-speed"
          className="text-sm"
          style={{ color: 'var(--color-text-primary)' }}
        >
          Speed:
        </label>
        <select
          id="playback-speed"
          value={playbackSpeed}
          onChange={handleSpeedChange}
          className="px-2 py-1 rounded text-sm"
          style={{
            backgroundColor: 'var(--color-surface)',
            color: 'var(--color-text-primary)',
            border: '1px solid var(--color-border)',
          }}
        >
          <option value="0.5">0.5x</option>
          <option value="1">1x</option>
          <option value="2">2x</option>
          <option value="5">5x</option>
        </select>
      </div>
    </div>
  )
}
