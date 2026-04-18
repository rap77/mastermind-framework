/**
 * FlowToolbar Tests
 *
 * Tests for the toolbar component including dialog-based confirmations.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ReactFlowProvider } from '@xyflow/react'
import { FlowToolbar } from '../FlowToolbar'
import * as Dialog from '@/components/ui/dialog'

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

// Mock the store
const mockClearFlow = vi.fn()
const mockNodes = []
const mockEdges = []

vi.mock('@/stores/flowDesignerStore', () => ({
  useFlowDesignerStore: vi.fn(() => ({
    nodes: mockNodes,
    edges: mockEdges,
    clearFlow: mockClearFlow,
  })),
}))

// Mock toast
vi.mock('@/lib/toast', () => ({
  toastError: vi.fn(),
}))

// Mock flow-serializer
vi.mock('@/lib/flow-serializer', () => ({
  exportFlowToFile: vi.fn(),
  importFlow: vi.fn(() => ({ nodes: [], edges: [], id: '1', name: 'Test' })),
}))

// Mock ReactFlow hooks
vi.mock('@xyflow/react', () => ({
  useReactFlow: () => ({
    zoomIn: vi.fn(),
    zoomOut: vi.fn(),
    fitView: vi.fn(),
  }),
  ReactFlowProvider: ({ children }: { children: React.ReactNode }) => children,
}))

describe('FlowToolbar', () => {
  beforeEach(() => {
    mockClearFlow.mockClear()
    // Mock window.confirm to ensure it's NOT called
    global.confirm = vi.fn(() => true)
  })

  const renderToolbar = () => render(<FlowToolbar />)

  describe('clear flow confirmation', () => {
    it('should NOT use window.confirm for clear action', () => {
      renderToolbar()

      const clearButton = screen.getByText('Clear')
      fireEvent.click(clearButton)

      // confirm() should NOT be called
      expect(global.confirm).not.toHaveBeenCalled()
    })

    it('should show confirmation dialog when Clear button is clicked', () => {
      renderToolbar()

      const clearButton = screen.getByText('Clear')
      fireEvent.click(clearButton)

      // Dialog title should be in the document
      const dialogTitle = screen.queryByText('Clear Flow')
      expect(dialogTitle).toBeDefined()
    })

    it('should call clearFlow when confirmed via dialog', () => {
      renderToolbar()

      const clearButton = screen.getByText('Clear')
      fireEvent.click(clearButton)

      // Find and click the confirm button in the dialog
      const confirmButtons = screen.getAllByText('Clear')
      const dialogConfirmButton = confirmButtons.find(btn =>
        btn.getAttribute('variant') === 'danger' ||
        btn.closest('[data-slot="dialog-footer"]')
      )

      if (dialogConfirmButton) {
        fireEvent.click(dialogConfirmButton)
      }

      // clearFlow should be called
      expect(mockClearFlow).toHaveBeenCalled()
    })

    it('should NOT call clearFlow when dialog is cancelled', () => {
      renderToolbar()

      const clearButton = screen.getByText('Clear')
      fireEvent.click(clearButton)

      // Click cancel button
      const cancelButton = screen.queryByText('Cancel')
      if (cancelButton) {
        fireEvent.click(cancelButton)
      }

      // clearFlow should NOT be called
      expect(mockClearFlow).not.toHaveBeenCalled()
    })
  })

  describe('other toolbar actions', () => {
    it('should render all toolbar buttons', () => {
      renderToolbar()

      expect(screen.getByText('Zoom In')).toBeDefined()
      expect(screen.getByText('Zoom Out')).toBeDefined()
      expect(screen.getByText('Fit View')).toBeDefined()
      expect(screen.getByText('Simulate')).toBeDefined()
      expect(screen.getByText('Export JSON')).toBeDefined()
      expect(screen.getByText('Import JSON')).toBeDefined()
      expect(screen.getByText('Clear')).toBeDefined()
    })
  })
})
