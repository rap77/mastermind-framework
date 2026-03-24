/**
 * orchestratorStore tests — Task 1 Phase 08-04
 *
 * Tests: task lifecycle, Focus Mode computed state, userOverride idempotency,
 * reset on complete, no state leaks between tests.
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useOrchestratorStore } from '../orchestratorStore'

// Reset store state between tests
function resetStore() {
  useOrchestratorStore.getState().reset()
}

describe('orchestratorStore', () => {
  beforeEach(() => {
    resetStore()
  })

  // ─── Initial state ───────────────────────────────────────────────────────

  describe('initial state', () => {
    it('starts in idle state', () => {
      const state = useOrchestratorStore.getState()
      expect(state.state).toBe('idle')
      expect(state.taskId).toBeNull()
      expect(state.briefText).toBe('')
      expect(state.isFocusMode).toBe(false)
      expect(state.userOverride).toBe(false)
    })
  })

  // ─── startTask ───────────────────────────────────────────────────────────

  describe('startTask', () => {
    it('transitions state to running', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Build feature X')
      const state = useOrchestratorStore.getState()
      expect(state.state).toBe('running')
      expect(state.taskId).toBe('task-1')
      expect(state.briefText).toBe('Build feature X')
    })

    it('activates Focus Mode when task starts', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      expect(useOrchestratorStore.getState().isFocusMode).toBe(true)
    })

    it('resets userOverride to false on new task start', () => {
      // Simulate previous task that user escaped
      const { startTask, toggleOverride } = useOrchestratorStore.getState()
      startTask('task-1', 'Brief 1')
      toggleOverride() // user escapes
      expect(useOrchestratorStore.getState().userOverride).toBe(true)

      // Start new task — override must reset
      startTask('task-2', 'Brief 2')
      expect(useOrchestratorStore.getState().userOverride).toBe(false)
      expect(useOrchestratorStore.getState().isFocusMode).toBe(true)
    })

    it('records startedAt timestamp', () => {
      const before = Date.now()
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      const after = Date.now()
      const { startedAt } = useOrchestratorStore.getState()
      expect(startedAt).toBeGreaterThanOrEqual(before)
      expect(startedAt).toBeLessThanOrEqual(after)
    })

    it('clears completedAt on new task', () => {
      const { startTask, completeTask } = useOrchestratorStore.getState()
      startTask('task-1', 'Brief')
      completeTask()
      startTask('task-2', 'New Brief')
      expect(useOrchestratorStore.getState().completedAt).toBeNull()
    })
  })

  // ─── completeTask ────────────────────────────────────────────────────────

  describe('completeTask', () => {
    it('transitions state to complete', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      useOrchestratorStore.getState().completeTask()
      expect(useOrchestratorStore.getState().state).toBe('complete')
    })

    it('deactivates Focus Mode on complete', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      expect(useOrchestratorStore.getState().isFocusMode).toBe(true)
      useOrchestratorStore.getState().completeTask()
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
    })

    it('resets userOverride to false on complete', () => {
      const { startTask, toggleOverride, completeTask } = useOrchestratorStore.getState()
      startTask('task-1', 'Brief')
      toggleOverride() // user was in override mode
      completeTask()
      expect(useOrchestratorStore.getState().userOverride).toBe(false)
    })

    it('records completedAt timestamp', () => {
      const { startTask, completeTask } = useOrchestratorStore.getState()
      startTask('task-1', 'Brief')
      const before = Date.now()
      completeTask()
      const after = Date.now()
      const { completedAt } = useOrchestratorStore.getState()
      expect(completedAt).not.toBeNull()
      expect(completedAt!).toBeGreaterThanOrEqual(before)
      expect(completedAt!).toBeLessThanOrEqual(after)
    })
  })

  // ─── setError ────────────────────────────────────────────────────────────

  describe('setError', () => {
    it('transitions state to error', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      useOrchestratorStore.getState().setError()
      expect(useOrchestratorStore.getState().state).toBe('error')
    })

    it('deactivates Focus Mode on error', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      useOrchestratorStore.getState().setError()
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
    })
  })

  // ─── toggleOverride (Focus Mode escape hatch) ────────────────────────────

  describe('toggleOverride', () => {
    it('disables Focus Mode when task is running', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      expect(useOrchestratorStore.getState().isFocusMode).toBe(true)

      useOrchestratorStore.getState().toggleOverride()
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
      expect(useOrchestratorStore.getState().userOverride).toBe(true)
    })

    it('does not re-trap user (calling toggleOverride again re-enables)', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      useOrchestratorStore.getState().toggleOverride() // disable
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)

      // Second toggle re-enables Focus Mode (task still running)
      useOrchestratorStore.getState().toggleOverride()
      expect(useOrchestratorStore.getState().isFocusMode).toBe(true)
      expect(useOrchestratorStore.getState().userOverride).toBe(false)
    })

    it('does not activate Focus Mode if task is idle', () => {
      // State is idle (no task), toggling override should not activate Focus Mode
      useOrchestratorStore.getState().toggleOverride()
      // isFocusMode = state === 'running' && !userOverride
      // idle + override=true → still false
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
    })
  })

  // ─── isFocusMode computed property ──────────────────────────────────────

  describe('isFocusMode computed', () => {
    it('is false when idle', () => {
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
    })

    it('is true when running and no override', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      expect(useOrchestratorStore.getState().isFocusMode).toBe(true)
    })

    it('is false when running but override=true', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      useOrchestratorStore.getState().toggleOverride()
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
    })

    it('is false when complete', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      useOrchestratorStore.getState().completeTask()
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
    })

    it('is false when error', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      useOrchestratorStore.getState().setError()
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
    })
  })

  // ─── reset ───────────────────────────────────────────────────────────────

  describe('reset', () => {
    it('returns store to initial state', () => {
      const { startTask, reset } = useOrchestratorStore.getState()
      startTask('task-1', 'Brief')
      reset()

      const state = useOrchestratorStore.getState()
      expect(state.taskId).toBeNull()
      expect(state.state).toBe('idle')
      expect(state.briefText).toBe('')
      expect(state.startedAt).toBe(0)
      expect(state.completedAt).toBeNull()
      expect(state.userOverride).toBe(false)
      expect(state.isFocusMode).toBe(false)
    })
  })
})
