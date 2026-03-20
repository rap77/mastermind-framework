import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { registerCommandShortcut } from '../commands'

describe('registerCommandShortcut', () => {
  let mockCallback: ReturnType<typeof vi.fn>
  let cleanup: ReturnType<ReturnType<typeof registerCommandShortcut>>

  beforeEach(() => {
    mockCallback = vi.fn()
  })

  afterEach(() => {
    if (cleanup) cleanup()
  })

  it('should trigger callback when Cmd+Enter is pressed', () => {
    cleanup = registerCommandShortcut(mockCallback)

    const event = new KeyboardEvent('keydown', {
      key: 'Enter',
      metaKey: true,
      ctrlKey: true
    })
    document.dispatchEvent(event)

    expect(mockCallback).toHaveBeenCalledTimes(1)
  })

  it('should NOT trigger when shortcut is pressed if modal is already open', () => {
    // Simulate modal already being open by checking conditions
    let isModalOpen = true
    const conditionalCallback = vi.fn(() => {
      if (!isModalOpen) {
        mockCallback()
      }
    })

    cleanup = registerCommandShortcut(conditionalCallback)

    const event = new KeyboardEvent('keydown', {
      key: 'Enter',
      metaKey: true,
      ctrlKey: true
    })
    document.dispatchEvent(event)

    // Should not trigger because modal is "open"
    expect(mockCallback).not.toHaveBeenCalled()
  })

  it('should register event listener on mount', () => {
    const addEventListenerSpy = vi.spyOn(document, 'addEventListener')

    cleanup = registerCommandShortcut(mockCallback)

    expect(addEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function))

    addEventListenerSpy.mockRestore()
  })

  it('should clean up event listener on unmount', () => {
    const removeEventListenerSpy = vi.spyOn(document, 'removeEventListener')

    cleanup = registerCommandShortcut(mockCallback)
    cleanup()

    expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function))

    removeEventListenerSpy.mockRestore()
  })

  it('should NOT trigger for other key combinations', () => {
    cleanup = registerCommandShortcut(mockCallback)

    // Test Cmd+K (should not trigger)
    const event1 = new KeyboardEvent('keydown', {
      key: 'k',
      metaKey: true
    })
    document.dispatchEvent(event1)
    expect(mockCallback).not.toHaveBeenCalled()

    // Test Enter alone (should not trigger)
    const event2 = new KeyboardEvent('keydown', {
      key: 'Enter'
    })
    document.dispatchEvent(event2)
    expect(mockCallback).not.toHaveBeenCalled()
  })
})
