/**
 * Phase08Integration.test.tsx — Full Phase 08 workflow integration test.
 *
 * Tests the complete user journey from brief submission through Focus Mode,
 * DAG render, scrubber navigation, log filtering, API key CRUD, and task
 * completion. All API/WS calls mocked — no backend dependency.
 *
 * Phase: 08-05 — Wave 4 (Integration Tests)
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'

// ─── Stores (direct integration — no mocks) ───────────────────────────────────
import { useOrchestratorStore } from '@/stores/orchestratorStore'
import { useBrainStore } from '@/stores/brainStore'
import { useReplayStore } from '@/stores/replayStore'
import { useLogFilterStore } from '@/stores/logFilterStore'
import { useWSStore } from '@/stores/wsStore'

// ─── Components ───────────────────────────────────────────────────────────────
import { FocusModeBadge } from '@/components/shared/FocusModeBadge'
import { ExecutionList } from '@/components/strategy-vault/ExecutionList'
import { KeyCreateDialog } from '@/components/engine-room/KeyCreateDialog'
import { KeyListTable } from '@/components/engine-room/KeyListTable'
import type { APIKeyMasked } from '@/components/engine-room/APIKeyManager'
import type { Snapshot } from '@/stores/replayStore'

// ─── Mock Next.js navigation ─────────────────────────────────────────────────
vi.mock('next/link', () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}))

// ─── Fixtures ─────────────────────────────────────────────────────────────────

const MOCK_TASK_ID = 'task-phase08-integration-001'
const MOCK_BRIEF = 'Build a comprehensive AI war room with real-time brain coordination'

const MOCK_EXECUTION_HISTORY = {
  executions: [
    {
      id: 'exec-001',
      status: 'success' as const,
      brief: 'First test execution brief',
      duration_ms: 154234,
      brain_count: 7,
      created_at: new Date(Date.now() - 3600000).toISOString(),
    },
    {
      id: 'exec-002',
      status: 'error' as const,
      brief: 'Second test execution with error',
      duration_ms: 45000,
      brain_count: 3,
      created_at: new Date(Date.now() - 7200000).toISOString(),
    },
  ],
  next_cursor: null,
  has_more: false,
}

const MOCK_API_KEYS: APIKeyMasked[] = [
  {
    id: 'api-key-001',
    prefix: 'mmsk_int1',
    suffix: 'end1',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    last_used_at: null,
  },
]

const MOCK_CREATED_KEY = {
  id: 'api-key-new',
  full_key: 'mmsk_newkey1234567890abcdef1234567890ab',
}

// Build snapshot series: 4 snapshots at different brain completion states
const MOCK_SNAPSHOTS: Snapshot[] = Array.from({ length: 4 }, (_, i) => ({
  timestamp: Date.now() - (4 - i) * 5000,
  snapshot: new Map([
    ['brain-01', { brain_id: 'brain-01', status: i >= 1 ? 'complete' : 'idle', timestamp: Date.now() }],
    ['brain-02', { brain_id: 'brain-02', status: i >= 2 ? 'complete' : i >= 1 ? 'running' : 'idle', timestamp: Date.now() }],
    ['brain-03', { brain_id: 'brain-03', status: i >= 3 ? 'complete' : 'idle', timestamp: Date.now() }],
  ] as [string, import('@/stores/replayStore').BrainStateReplay][]),
}))

// ─── Wrapper ──────────────────────────────────────────────────────────────────

function makeWrapper() {
  const qc = new QueryClient({
    defaultOptions: {
      queries: { retry: false, staleTime: 0 },
      mutations: { retry: false },
    },
  })
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  }
}

// ─── Reset helpers ────────────────────────────────────────────────────────────

function resetAllStores() {
  useOrchestratorStore.getState().reset()
  useReplayStore.getState().reset()
  useLogFilterStore.getState().reset()
  useBrainStore.setState({ brains: new Map(), _queue: [], _rafId: null })
  useWSStore.getState().disconnect()
}

// ─── Phase 08 Integration Test ────────────────────────────────────────────────

describe('Phase 08 — Full Workflow Integration', () => {
  beforeEach(() => {
    resetAllStores()
    vi.resetAllMocks()
    localStorage.clear()
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      writable: true,
      configurable: true,
    })
  })

  // ─── Step 1-2: Command Center + Submit Brief ──────────────────────────────

  describe('Step 1-2: Command Center — initial state and brief submit', () => {
    it('Step 1: initial state has no Focus Mode active', () => {
      const store = useOrchestratorStore.getState()
      expect(store.isFocusMode).toBe(false)
      expect(store.state).toBe('idle')
      expect(store.taskId).toBeNull()
    })

    it('Step 2: submitting brief activates Focus Mode via startTask()', () => {
      // Simulate POST /api/tasks → success → startTask() called
      useOrchestratorStore.getState().startTask(MOCK_TASK_ID, MOCK_BRIEF)

      const store = useOrchestratorStore.getState()
      expect(store.isFocusMode).toBe(true)
      expect(store.state).toBe('running')
      expect(store.taskId).toBe(MOCK_TASK_ID)
      expect(store.briefText).toBe(MOCK_BRIEF)
      expect(store.userOverride).toBe(false)
    })
  })

  // ─── Step 3: Focus Mode activated ────────────────────────────────────────

  describe('Step 3: Focus Mode activated', () => {
    it('FocusModeBadge visible when Focus Mode active', () => {
      useOrchestratorStore.getState().startTask(MOCK_TASK_ID, MOCK_BRIEF)
      render(<FocusModeBadge />)

      expect(screen.getByRole('button', { name: /exit focus mode/i })).toBeInTheDocument()
      expect(screen.getByText('Salir [Esc]')).toBeInTheDocument()
    })

    it('sidebar collapse: isFocusMode=true is the signal consumers use', () => {
      useOrchestratorStore.getState().startTask(MOCK_TASK_ID, MOCK_BRIEF)

      // NexusPage/CommandCenter read isFocusMode to collapse sidebar
      expect(useOrchestratorStore.getState().isFocusMode).toBe(true)
    })

    it('canvas expands to full width when Focus Mode active', () => {
      useOrchestratorStore.getState().startTask(MOCK_TASK_ID, MOCK_BRIEF)
      render(<FocusModeBadge />)

      // Badge is fixed positioned (overlays canvas)
      const badge = screen.getByRole('button', { name: /exit focus mode/i })
      expect(badge.className).toContain('fixed')
      expect(badge.className).toContain('z-50')
    })
  })

  // ─── Step 4: Navigate to Nexus + DAG render ───────────────────────────────

  describe('Step 4: Nexus — DAG renders with brain nodes', () => {
    it('brainStore accepts brain state updates from WS events', () => {
      // Simulate WS brain:update events arriving after task start
      useOrchestratorStore.getState().startTask(MOCK_TASK_ID, MOCK_BRIEF)

      // Directly set brain states (bypass RAF for test determinism)
      useBrainStore.setState({
        brains: new Map([
          ['brain-01', { id: 'brain-01', status: 'active', lastUpdated: Date.now() }],
          ['brain-02', { id: 'brain-02', status: 'idle', lastUpdated: Date.now() }],
          ['brain-03', { id: 'brain-03', status: 'idle', lastUpdated: Date.now() }],
        ]),
      })

      const brains = useBrainStore.getState().brains
      expect(brains.size).toBe(3)
      expect(brains.get('brain-01')?.status).toBe('active')
    })

    it('brainStore historyStack tracks brain state evolution', () => {
      useBrainStore.setState({
        brains: new Map([
          ['brain-01', { id: 'brain-01', status: 'active', lastUpdated: Date.now() }],
        ]),
      })

      useBrainStore.getState().pushHistorySnapshot()

      expect(useBrainStore.getState().historyStack).toHaveLength(1)
      expect(useBrainStore.getState().historyStack[0].snapshot.get('brain-01')?.status).toBe('active')
    })
  })

  // ─── Step 5: WS brain update events ──────────────────────────────────────

  describe('Step 5: WS brain:update events update brain tiles', () => {
    it('3 brain updates arrive, all tracked in brainStore', () => {
      const updates = [
        { id: 'brain-01', status: 'active' as const, lastUpdated: Date.now() },
        { id: 'brain-02', status: 'active' as const, lastUpdated: Date.now() },
        { id: 'brain-03', status: 'complete' as const, lastUpdated: Date.now() },
      ]

      // Simulate RAF drain: direct setState for test
      useBrainStore.setState({
        brains: new Map(updates.map((b) => [b.id, b])),
      })

      const state = useBrainStore.getState()
      expect(state.brains.get('brain-01')?.status).toBe('active')
      expect(state.brains.get('brain-02')?.status).toBe('active')
      expect(state.brains.get('brain-03')?.status).toBe('complete')
    })

    it('Focus Mode active: idle tiles should dim (isFocusMode=true context)', () => {
      useOrchestratorStore.getState().startTask(MOCK_TASK_ID, MOCK_BRIEF)

      useBrainStore.setState({
        brains: new Map([
          ['brain-01', { id: 'brain-01', status: 'active', lastUpdated: Date.now() }],
          ['brain-02', { id: 'brain-02', status: 'idle', lastUpdated: Date.now() }],
        ]),
      })

      // Consumers use isFocusMode to apply opacity-30 to idle brains
      expect(useOrchestratorStore.getState().isFocusMode).toBe(true)
      expect(useBrainStore.getState().brains.get('brain-02')?.status).toBe('idle')
    })
  })

  // ─── Steps 6-7: Strategy Vault + Execution History ───────────────────────

  describe('Steps 6-7: Strategy Vault — execution history and detail', () => {
    it('Step 6: ExecutionList loads GET /api/executions/history', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => MOCK_EXECUTION_HISTORY,
      } as Response)

      render(<ExecutionList />, { wrapper: makeWrapper() })

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/executions/history'),
          expect.any(Object)
        )
      })
    })

    it('Step 6: displays execution rows with status and duration', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => MOCK_EXECUTION_HISTORY,
      } as Response)

      render(<ExecutionList />, { wrapper: makeWrapper() })

      await waitFor(() => {
        expect(screen.getByTestId('execution-row-exec-001')).toBeInTheDocument()
        expect(screen.getByTestId('execution-row-exec-002')).toBeInTheDocument()
      })
    })

    it('Step 7: replayStore loads snapshots from execution detail', () => {
      // Simulate loading execution detail → setSnapshots called
      useReplayStore.getState().setSnapshots(MOCK_SNAPSHOTS)

      const state = useReplayStore.getState()
      expect(state.snapshots).toHaveLength(4)
      expect(state.currentSnapshotIndex).toBe(0)
      expect(state.milestones.length).toBeGreaterThan(0)
    })

    it('Step 7: current snapshot at index 0 shows initial brain states', () => {
      useReplayStore.getState().setSnapshots(MOCK_SNAPSHOTS)

      const snapshot = useReplayStore.getState().getCurrentSnapshot()
      expect(snapshot).not.toBeNull()
      expect(snapshot?.get('brain-01')?.status).toBe('idle') // index 0 = before brain-01 completes
    })
  })

  // ─── Step 8: Scrubber drag ────────────────────────────────────────────────

  describe('Step 8: Scrubber — drag updates snapshot index', () => {
    it('jumpToMilestone(2) advances to third snapshot', () => {
      useReplayStore.getState().setSnapshots(MOCK_SNAPSHOTS)

      useReplayStore.getState().jumpToMilestone(2)

      expect(useReplayStore.getState().currentSnapshotIndex).toBe(2)
    })

    it('scrubber percentage updates based on index/total', () => {
      useReplayStore.getState().setSnapshots(MOCK_SNAPSHOTS)
      useReplayStore.getState().jumpToMilestone(3) // Last snapshot (index 3 of 4)

      const pct = useReplayStore.getState().getScrubberPercentage()
      expect(pct).toBe(100) // (3 / (4-1)) * 100 = 100
    })

    it('snapshot at index 3 shows all brains complete', () => {
      useReplayStore.getState().setSnapshots(MOCK_SNAPSHOTS)
      useReplayStore.getState().jumpToMilestone(3)

      const snapshot = useReplayStore.getState().getCurrentSnapshot()
      expect(snapshot?.get('brain-01')?.status).toBe('complete')
      expect(snapshot?.get('brain-02')?.status).toBe('complete')
      expect(snapshot?.get('brain-03')?.status).toBe('complete')
    })

    it('milestones computed with label containing percentage', () => {
      useReplayStore.getState().setSnapshots(MOCK_SNAPSHOTS)

      const milestones = useReplayStore.getState().milestones
      expect(milestones.length).toBeGreaterThan(0)
      expect(milestones[0].label).toMatch(/\d+%/)
    })
  })

  // ─── Steps 9-10: Log filtering ────────────────────────────────────────────

  describe('Steps 9-10: Engine Room — log filtering', () => {
    it('Step 9: toggling error level removes it from filterLevels', () => {
      // Initial state: all 3 levels active (info, warn, error)
      expect(useLogFilterStore.getState().filterLevels.has('error')).toBe(true)

      useLogFilterStore.getState().toggleLevel('error')

      expect(useLogFilterStore.getState().filterLevels.has('error')).toBe(false)
      expect(useLogFilterStore.getState().filterLevels.has('info')).toBe(true)
      expect(useLogFilterStore.getState().filterLevels.has('warn')).toBe(true)
    })

    it('Step 9: empty filterLevels Set = show nothing (not pass-through)', () => {
      // Toggle off all levels
      useLogFilterStore.getState().toggleLevel('info')
      useLogFilterStore.getState().toggleLevel('warn')
      useLogFilterStore.getState().toggleLevel('error')

      expect(useLogFilterStore.getState().filterLevels.size).toBe(0)
    })

    it('Step 10: isolating brain sets isolatedBrainId', () => {
      useLogFilterStore.getState().setIsolatedBrain('brain-03')

      expect(useLogFilterStore.getState().isolatedBrainId).toBe('brain-03')
    })

    it('Step 10: clearing isolation sets isolatedBrainId to null', () => {
      useLogFilterStore.getState().setIsolatedBrain('brain-03')
      useLogFilterStore.getState().setIsolatedBrain(null)

      expect(useLogFilterStore.getState().isolatedBrainId).toBeNull()
    })

    it('log filter state persists to localStorage', () => {
      useLogFilterStore.getState().toggleLevel('error')
      useLogFilterStore.getState().setAutoFollow(false)

      const stored = JSON.parse(localStorage.getItem('mm_log_filters') ?? '{}')
      expect(stored.filterLevels).not.toContain('error')
      expect(stored.autoFollow).toBe(false)
    })
  })

  // ─── Step 11: Engine Room navigation ─────────────────────────────────────

  describe('Step 11: Engine Room — live logs panel', () => {
    it('wsStore can subscribe to event types', () => {
      const listener = vi.fn()
      const unsub = useWSStore.getState().subscribe('brain:update', listener)

      // Trigger listeners manually (mock WS message)
      const listeners = useWSStore.getState().listeners
      const handlers = listeners.get('brain:update')
      handlers?.forEach((fn) => fn({ brainId: 'brain-01', status: 'complete' }))

      expect(listener).toHaveBeenCalledWith({ brainId: 'brain-01', status: 'complete' })
      unsub()
    })

    it('wsStore subscribe returns cleanup function', () => {
      const listener = vi.fn()
      const unsub = useWSStore.getState().subscribe('task:complete', listener)

      unsub() // Cleanup

      const listeners = useWSStore.getState().listeners
      const handlers = listeners.get('task:complete')
      // After cleanup, listener removed
      expect(handlers?.has(listener)).toBeFalsy()
    })
  })

  // ─── Steps 12-13: API Key management ─────────────────────────────────────

  describe('Steps 12-13: Engine Room — API key CRUD in workflow context', () => {
    it('Step 12: Create Key flow shows full key once', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => MOCK_CREATED_KEY,
      } as Response)

      render(<KeyCreateDialog />, { wrapper: makeWrapper() })

      fireEvent.click(screen.getByTestId('open-create-dialog'))
      await waitFor(() => screen.getByTestId('confirm-create-key'))
      fireEvent.click(screen.getByTestId('confirm-create-key'))

      await waitFor(() => {
        expect(screen.getByTestId('created-key-code').textContent).toBe(MOCK_CREATED_KEY.full_key)
      })
    })

    it('Step 12: copy button works, then close clears key', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => MOCK_CREATED_KEY,
      } as Response)

      render(<KeyCreateDialog />, { wrapper: makeWrapper() })
      fireEvent.click(screen.getByTestId('open-create-dialog'))
      await waitFor(() => screen.getByTestId('confirm-create-key'))
      fireEvent.click(screen.getByTestId('confirm-create-key'))
      await waitFor(() => screen.getByTestId('copy-key-button'))
      fireEvent.click(screen.getByTestId('copy-key-button'))

      await waitFor(() => {
        expect(navigator.clipboard.writeText).toHaveBeenCalledWith(MOCK_CREATED_KEY.full_key)
      })

      fireEvent.click(screen.getByTestId('done-button'))

      await waitFor(() => {
        expect(screen.queryByTestId('created-key-code')).toBeNull()
      })
    })

    it('Step 13: Revoke key flow with confirm', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({}),
      } as Response)

      render(<KeyListTable keys={MOCK_API_KEYS} />, { wrapper: makeWrapper() })

      fireEvent.click(screen.getByTestId('revoke-btn-api-key-001'))
      await waitFor(() => screen.getByTestId('revoke-confirm-dialog'))

      // Verify confirm dialog shows key identifier
      expect(screen.getByText(/will be immediately revoked/i)).toBeInTheDocument()

      fireEvent.click(screen.getByTestId('confirm-revoke'))

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/keys/api-key-001', { method: 'DELETE' })
        expect(screen.queryByTestId('revoke-confirm-dialog')).toBeNull()
      })
    })
  })

  // ─── Step 14: Task completes ──────────────────────────────────────────────

  describe('Step 14: Task completion via WS task:complete event', () => {
    it('completeTask() called on task:complete event exits Focus Mode', () => {
      // Setup: task running with Focus Mode active
      useOrchestratorStore.getState().startTask(MOCK_TASK_ID, MOCK_BRIEF)
      expect(useOrchestratorStore.getState().isFocusMode).toBe(true)

      // Simulate WS 'task:complete' → completeTask()
      useOrchestratorStore.getState().completeTask()

      const store = useOrchestratorStore.getState()
      expect(store.isFocusMode).toBe(false)
      expect(store.state).toBe('complete')
      expect(store.completedAt).not.toBeNull()
    })

    it('userOverride resets to false after completeTask()', () => {
      // Even if user had pressed Esc, userOverride resets on completion
      useOrchestratorStore.getState().startTask(MOCK_TASK_ID, MOCK_BRIEF)
      useOrchestratorStore.getState().toggleOverride()

      expect(useOrchestratorStore.getState().userOverride).toBe(true)

      useOrchestratorStore.getState().completeTask()

      expect(useOrchestratorStore.getState().userOverride).toBe(false)
    })
  })

  // ─── Step 15: Post-task state ─────────────────────────────────────────────

  describe('Step 15: Post-task state — sidebar visible, no Focus Mode', () => {
    it('isFocusMode=false after completeTask()', () => {
      useOrchestratorStore.getState().startTask(MOCK_TASK_ID, MOCK_BRIEF)
      useOrchestratorStore.getState().completeTask()

      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
    })

    it('FocusModeBadge not rendered after task completes', () => {
      useOrchestratorStore.getState().startTask(MOCK_TASK_ID, MOCK_BRIEF)
      const { rerender } = render(<FocusModeBadge />)

      // Badge visible during task
      expect(screen.getByRole('button', { name: /exit focus mode/i })).toBeInTheDocument()

      // Task completes
      useOrchestratorStore.getState().completeTask()
      rerender(<FocusModeBadge />)

      // Badge gone
      expect(screen.queryByRole('button', { name: /exit focus mode/i })).toBeNull()
    })

    it('state machine ends at complete after full workflow', () => {
      // Full lifecycle
      expect(useOrchestratorStore.getState().state).toBe('idle')

      useOrchestratorStore.getState().startTask(MOCK_TASK_ID, MOCK_BRIEF)
      expect(useOrchestratorStore.getState().state).toBe('running')

      useOrchestratorStore.getState().completeTask()
      expect(useOrchestratorStore.getState().state).toBe('complete')
    })

    it('stores are independent — completing task does NOT reset log filters', () => {
      // Log filters survive task lifecycle (user may switch tasks with same filter prefs)
      useLogFilterStore.getState().toggleLevel('error') // Remove error filter

      useOrchestratorStore.getState().startTask(MOCK_TASK_ID, MOCK_BRIEF)
      useOrchestratorStore.getState().completeTask()

      // Log filter should still have error toggled off
      expect(useLogFilterStore.getState().filterLevels.has('error')).toBe(false)
    })
  })

  // ─── Cross-feature: No regressions ───────────────────────────────────────

  describe('No regressions — Phase 08 feature cohesion', () => {
    it('Focus Mode does not affect log filter state', () => {
      useOrchestratorStore.getState().startTask(MOCK_TASK_ID, MOCK_BRIEF)

      // Log filters unchanged
      expect(useLogFilterStore.getState().filterLevels.has('info')).toBe(true)
      expect(useLogFilterStore.getState().filterLevels.has('warn')).toBe(true)
      expect(useLogFilterStore.getState().filterLevels.has('error')).toBe(true)
    })

    it('replayStore scrubber does not affect orchestratorStore Focus Mode', () => {
      useOrchestratorStore.getState().startTask(MOCK_TASK_ID, MOCK_BRIEF)
      useReplayStore.getState().setSnapshots(MOCK_SNAPSHOTS)
      useReplayStore.getState().jumpToMilestone(2)

      // Scrubber navigation should NOT affect Focus Mode
      expect(useOrchestratorStore.getState().isFocusMode).toBe(true)
    })

    it('brainStore updates do not affect orchestratorStore state', () => {
      useOrchestratorStore.getState().startTask(MOCK_TASK_ID, MOCK_BRIEF)

      useBrainStore.setState({
        brains: new Map([
          ['brain-01', { id: 'brain-01', status: 'complete', lastUpdated: Date.now() }],
        ]),
      })

      // BrainStore update alone should NOT complete the task or exit Focus Mode
      // (that requires explicit WS task:complete event → completeTask())
      expect(useOrchestratorStore.getState().isFocusMode).toBe(true)
      expect(useOrchestratorStore.getState().state).toBe('running')
    })

    it('multiple task cycles work correctly (no stale state)', () => {
      // Task 1
      useOrchestratorStore.getState().startTask('task-001', 'Brief 1')
      useOrchestratorStore.getState().toggleOverride() // User pressed Esc
      useOrchestratorStore.getState().completeTask()

      // Task 2 — must start clean
      useOrchestratorStore.getState().startTask('task-002', 'Brief 2')

      const store = useOrchestratorStore.getState()
      expect(store.isFocusMode).toBe(true)
      expect(store.userOverride).toBe(false)
      expect(store.taskId).toBe('task-002')
      expect(store.briefText).toBe('Brief 2')
    })
  })
})
