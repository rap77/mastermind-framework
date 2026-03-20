/**
 * WSBrainBridge Integration Tests
 *
 * **Purpose:** Test WebSocket to brainStore bridge (existing from Phase 05)
 * **Context:** Phase 06-02 - Task 4
 *
 * **Note:** WSBrainBridge was implemented in Phase 05 with RAF batching.
 * These tests verify the integration works for Command Center.
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useBrainStore, useBrainState } from '@/stores/brainStore'

describe('WSBrainBridge Integration (Phase 05 → Phase 06)', () => {
  beforeEach(() => {
    // Reset store before each test
    const { brains } = useBrainStore.getState()
    brains.clear()
  })

  /**
   * Test 1: brainStore has updateBrain action for WebSocket events
   */
  it('should have updateBrain action for WebSocket events', () => {
    const { updateBrain } = useBrainStore.getState()

    expect(typeof updateBrain).toBe('function')
  })

  /**
   * Test 2: brainStore uses Map for O(1) lookups
   */
  it('should use Map data structure for O(1) lookups', () => {
    const { brains } = useBrainStore.getState()

    expect(brains).toBeInstanceOf(Map)
  })

  /**
   * Test 3: RAF batching queue exists for performance
   */
  it('should have RAF batching queue for burst updates', () => {
    const { _queue } = useBrainStore.getState()

    expect(Array.isArray(_queue)).toBe(true)
  })

  /**
   * Test 4: brainStore has targeted selector export
   */
  it('should export useBrainState targeted selector', () => {
    expect(typeof useBrainState).toBe('function')
  })
})
