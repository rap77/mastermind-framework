import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

// Mock ResizeObserver for React Flow
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

// jsdom does not implement scrollIntoView — stub it globally so components
// that call el.scrollIntoView() (e.g. StatusTimeline auto-scroll) don't throw.
Element.prototype.scrollIntoView = vi.fn()

afterEach(() => {
  cleanup()
})
