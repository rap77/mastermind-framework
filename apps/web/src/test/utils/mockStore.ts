/**
 * Mock Store Helper
 *
 * Generic utility for creating mock Zustand stores in tests.
 * Provides type-safe mock store creation with selector support.
 *
 * @example
 * import { createMockStore } from '@/test/utils/mockStore'
 *
 * // Simple store
 * const mockStore = createMockStore({ count: 0, name: 'test' })
 * const { useCountStore } = mockStore
 *
 * // With selector support
 * vi.mocked(useCountStore).mockReturnValue({ count: 5 })
 *
 * // Direct state access
 * const currentState = mockStore.getState()
 */

import { vi } from 'vitest'

/**
 * Creates a mock Zustand store for testing
 *
 * @template T - The store state type
 * @param initialState - Initial state for the mock store
 * @returns Mock store object with:
 *   - useStore hook that supports selectors
 *   - getState method for direct state access
 *
 * @example
 * // Basic usage
 * const mockStore = createMockStore({ count: 0, name: 'test' })
 * const { useCountStore } = mockStore
 *
 * // In tests - mock return value
 * vi.mocked(useCountStore).mockReturnValue({ count: 5 })
 *
 * // In tests - with selector
 * vi.mocked(useCountStore).mockImplementation((selector) =>
 *   selector(mockStore.getState())
 * )
 *
 * // Access current state
 * const currentState = mockStore.getState()
 */
export function createMockStore<T extends Record<string, unknown>>(initialState: T) {
  const mockState = initialState

  const useStore = vi.fn((selector) => {
    if (selector) {
      return selector(mockState)
    }
    return mockState
  })

  // Add getState method for direct state access
  ;(useStore as any).getState = () => mockState

  return {
    useStore,
    getState: () => mockState,
  }
}

/**
 * Creates a mock store with action functions
 *
 * Use this when your store has actions that need to be mocked as vi.fn().
 *
 * @template T - The store state type including actions
 * @param initialState - Initial state with mocked actions
 * @returns Mock store object with useStore hook and getState method
 *
 * @example
 * const mockStore = createMockStoreWithActions({
 *   count: 0,
 *   increment: vi.fn(),
 *   decrement: vi.fn(),
 * })
 *
 * // Test that action was called
 * expect(mockStore.getState().increment).toHaveBeenCalled()
 */
export function createMockStoreWithActions<
  T extends Record<string, unknown>
>(initialState: T) {
  const mockState = initialState

  const useStore = vi.fn((selector) => {
    if (selector) {
      return selector(mockState)
    }
    return mockState
  })

  // Add getState method for direct state access
  ;(useStore as any).getState = () => mockState

  return {
    useStore,
    getState: () => mockState,
  }
}
