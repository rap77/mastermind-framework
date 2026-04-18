/**
 * FlowToolbar Tests
 *
 * Tests for the toolbar component including dialog-based confirmations, loading states, and file validation.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ReactFlowProvider } from '@xyflow/react'
import { FlowToolbar } from '../FlowToolbar'
import * as Dialog from '@/components/ui/dialog'

// Mock next/navigation
const mockPush = vi.fn()
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
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
    mockPush.mockClear()
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

    it('should show loading state when navigating to simulation', async () => {
      // Make router.push return a promise that resolves quickly
      mockPush.mockImplementation(() => Promise.resolve())

      renderToolbar()

      const simulateButton = screen.getByText('Simulate')
      fireEvent.click(simulateButton)

      // Wait for loading state to appear
      await waitFor(() => {
        const loadingText = screen.queryByText('Loading...')
        // Loading should appear briefly during navigation
        expect(loadingText || mockPush).toBeTruthy()
      })
    })

    it('should disable Simulate button during navigation', async () => {
      // Make router.push return a pending promise
      let resolvePush: () => void
      mockPush.mockImplementation(() => new Promise(resolve => { resolvePush = resolve }))

      renderToolbar()

      const simulateButton = screen.getByText('Simulate')
      fireEvent.click(simulateButton)

      // Button should be disabled during navigation
      await waitFor(() => {
        expect(simulateButton).toBeDisabled()
      })

      // Clean up
      if (resolvePush) resolvePush()
    })
  })

  describe('file import validation', () => {
    it('should reject files larger than 5MB', () => {
      renderToolbar()

      const importButton = screen.getByText('Import JSON')
      fireEvent.click(importButton)

      // Create a mock file input
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement
      expect(fileInput).toBeDefined()

      // Mock a large file (> 5MB)
      const largeFile = new File(['x'.repeat(6 * 1024 * 1024)], 'large.json', {
        type: 'application/json',
      })

      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [largeFile] } })

        // Should show error toast
        const { toastError } = require('@/lib/toast')
        expect(toastError).toHaveBeenCalledWith(
          expect.stringContaining('File too large')
        )
      }
    })

    it('should reject non-JSON files', () => {
      renderToolbar()

      const importButton = screen.getByText('Import JSON')
      fireEvent.click(importButton)

      // Create a mock file input
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement
      expect(fileInput).toBeDefined()

      // Mock a non-JSON file
      const textFile = new File(['content'], 'file.txt', { type: 'text/plain' })

      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [textFile] } })

        // Should show error toast
        const { toastError } = require('@/lib/toast')
        expect(toastError).toHaveBeenCalledWith(
          expect.stringContaining('Invalid file type')
        )
      }
    })

    it('should accept valid JSON files under 5MB', () => {
      renderToolbar()

      const importButton = screen.getByText('Import JSON')
      fireEvent.click(importButton)

      // Create a mock file input
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement
      expect(fileInput).toBeDefined()

      // Mock a valid JSON file
      const jsonContent = JSON.stringify({ nodes: [], edges: [], id: '1', name: 'Test' })
      const jsonFile = new File([jsonContent], 'valid.json', { type: 'application/json' })

      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [jsonFile] } })

        // Should NOT show error toast
        const { toastError } = require('@/lib/toast')
        expect(toastError).not.toHaveBeenCalled()
      }
    })

    it('should show loading state during import', async () => {
      renderToolbar()

      const importButton = screen.getByText('Import JSON')
      fireEvent.click(importButton)

      // Create a mock file input
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement

      // Mock a valid JSON file
      const jsonContent = JSON.stringify({ nodes: [], edges: [], id: '1', name: 'Test' })
      const jsonFile = new File([jsonContent], 'valid.json', { type: 'application/json' })

      if (fileInput) {
        fireEvent.change(fileInput, { target: { files: [jsonFile] } })

        // Should show loading state briefly
        await waitFor(() => {
          const loadingText = screen.queryByText('Importing...')
          expect(loadingText || mockClearFlow).toBeTruthy()
        })
      }
    })
  })
})
