/**
 * ReplayStore Tests
 *
 * **Purpose:** Verify Zustand store for Strategy Vault scrubber state
 * **Context:** Phase 08-02 - Task 1
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useReplayStore } from '../replayStore'
import type { Snapshot } from '../replayStore'

// ─── Helpers ──────────────────────────────────────────────────────────────────

function makeBrainMap(statuses: Record<string, string>) {
  const m = new Map()
  for (const [id, status] of Object.entries(statuses)) {
    m.set(id, { brain_id: id, status })
  }
  return m
}

function makeSnapshots(count: number): Snapshot[] {
  return Array.from({ length: count }, (_, i) => ({
    timestamp: 1000 + i * 100,
    snapshot: makeBrainMap({
      'brain-01': i < 3 ? 'idle' : 'complete',
      'brain-02': i < 5 ? 'running' : 'complete',
    }),
  }))
}

// ─── Tests ────────────────────────────────────────────────────────────────────

describe('useReplayStore', () => {
  beforeEach(() => {
    useReplayStore.getState().reset()
  })

  it('initializes with empty state', () => {
    const state = useReplayStore.getState()
    expect(state.snapshots).toEqual([])
    expect(state.milestones).toEqual([])
    expect(state.currentSnapshotIndex).toBe(0)
    expect(state.taskId).toBeNull()
  })

  it('setSnapshots stores snapshots and resets index', () => {
    const snapshots = makeSnapshots(5)
    useReplayStore.getState().setSnapshots(snapshots)

    const state = useReplayStore.getState()
    expect(state.snapshots).toHaveLength(5)
    expect(state.currentSnapshotIndex).toBe(0)
  })

  it('setSnapshots computes milestones automatically', () => {
    const snapshots = makeSnapshots(7)
    useReplayStore.getState().setSnapshots(snapshots)

    const state = useReplayStore.getState()
    // 7 snapshots with interval=1 → max 7 milestones
    expect(state.milestones.length).toBeGreaterThan(0)
    expect(state.milestones.length).toBeLessThanOrEqual(7)
  })

  it('computes max 7 milestones for large snapshot arrays (Miller\'s Law)', () => {
    const snapshots = makeSnapshots(100)
    useReplayStore.getState().setSnapshots(snapshots)

    const state = useReplayStore.getState()
    expect(state.milestones.length).toBeLessThanOrEqual(7)
  })

  it('milestones have correct index, timestamp, label, brainCount', () => {
    const snapshots = makeSnapshots(14)
    useReplayStore.getState().setSnapshots(snapshots)

    const { milestones } = useReplayStore.getState()
    expect(milestones[0]).toMatchObject({
      index: 0,
      timestamp: expect.any(Number),
      label: expect.any(String),
      brainCount: expect.any(Number),
    })
  })

  it('jumpToMilestone updates currentSnapshotIndex', () => {
    const snapshots = makeSnapshots(14)
    useReplayStore.getState().setSnapshots(snapshots)
    useReplayStore.getState().jumpToMilestone(7)

    expect(useReplayStore.getState().currentSnapshotIndex).toBe(7)
  })

  it('jumpToMilestone clamps to valid range', () => {
    const snapshots = makeSnapshots(5)
    useReplayStore.getState().setSnapshots(snapshots)

    useReplayStore.getState().jumpToMilestone(999)
    expect(useReplayStore.getState().currentSnapshotIndex).toBe(4)

    useReplayStore.getState().jumpToMilestone(-5)
    expect(useReplayStore.getState().currentSnapshotIndex).toBe(0)
  })

  it('getCurrentSnapshot returns correct Map at currentSnapshotIndex', () => {
    const snapshots = makeSnapshots(5)
    useReplayStore.getState().setSnapshots(snapshots)
    useReplayStore.getState().jumpToMilestone(2)

    const snap = useReplayStore.getState().getCurrentSnapshot()
    expect(snap).toBeInstanceOf(Map)
    expect(snap?.get('brain-01')).toBeDefined()
  })

  it('getCurrentSnapshot returns null when no snapshots', () => {
    const snap = useReplayStore.getState().getCurrentSnapshot()
    expect(snap).toBeNull()
  })

  it('getScrubberPercentage returns 0 for empty snapshots', () => {
    expect(useReplayStore.getState().getScrubberPercentage()).toBe(0)
  })

  it('getScrubberPercentage returns 0-100 range', () => {
    const snapshots = makeSnapshots(11)
    useReplayStore.getState().setSnapshots(snapshots)

    useReplayStore.getState().jumpToMilestone(0)
    expect(useReplayStore.getState().getScrubberPercentage()).toBe(0)

    useReplayStore.getState().jumpToMilestone(10)
    expect(useReplayStore.getState().getScrubberPercentage()).toBe(100)

    useReplayStore.getState().jumpToMilestone(5)
    expect(useReplayStore.getState().getScrubberPercentage()).toBe(50)
  })

  it('reset clears all state', () => {
    const snapshots = makeSnapshots(7)
    useReplayStore.getState().setSnapshots(snapshots)
    useReplayStore.getState().jumpToMilestone(3)
    useReplayStore.getState().reset()

    const state = useReplayStore.getState()
    expect(state.snapshots).toEqual([])
    expect(state.milestones).toEqual([])
    expect(state.currentSnapshotIndex).toBe(0)
  })
})
