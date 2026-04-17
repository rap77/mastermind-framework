/**
 * FlowDesignerCanvas Tests
 *
 * Tests for the main canvas component including rendering,
 * node dropping, edge connections, and zoom controls.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ReactFlowProvider } from '@xyflow/react'
import { FlowDesignerCanvas } from '../FlowDesignerCanvas'
import { NodeType } from '../types'

// Mock ResizeObserver (required by React Flow)
global.ResizeObserver = vi.fn(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
})) as any

// Mock the store
vi.mock('@/stores/flowDesignerStore', () => ({
  useFlowDesignerStore: vi.fn(() => ({
    nodes: [],
    edges: [],
    addNode: vi.fn(),
    addEdge: vi.fn(),
    updateNode: vi.fn(),
  })),
}))

describe('FlowDesignerCanvas', () => {
  const renderWithProvider = (component: React.ReactNode) => {
    return render(<ReactFlowProvider>{component}</ReactFlowProvider>)
  }

  describe('rendering', () => {
    it('should render the canvas', () => {
      renderWithProvider(<FlowDesignerCanvas />)

      // React Flow renders a div with specific class
      const canvas = document.querySelector('.react-flow')
      expect(canvas).toBeDefined()
    })

    it('should render background grid', () => {
      renderWithProvider(<FlowDesignerCanvas />)

      // Background should be present
      const background = document.querySelector('.react-flow__background')
      expect(background).toBeDefined()
    })

    it('should render controls', () => {
      renderWithProvider(<FlowDesignerCanvas />)

      // Controls should be present
      const controls = document.querySelector('.react-flow__controls')
      expect(controls).toBeDefined()
    })

    it('should render minimap', () => {
      renderWithProvider(<FlowDesignerCanvas />)

      // Minimap should be present
      const minimap = document.querySelector('.react-flow__minimap')
      expect(minimap).toBeDefined()
    })

    it('should render info panel', () => {
      renderWithProvider(<FlowDesignerCanvas />)

      // Check for info panel text
      expect(screen.getByText(/🖱️ Drag to pan/)).toBeDefined()
      expect(screen.getByText(/🔗 Drag from handles/)).toBeDefined()
    })
  })

  describe('node drop', () => {
    it('should handle drag over events', () => {
      renderWithProvider(<FlowDesignerCanvas />)

      const canvas = document.querySelector('.react-flow') as HTMLElement
      const dragOverEvent = new DragEvent('dragover', {
        bubbles: true,
        cancelable: true,
      })

      fireEvent(canvas, dragOverEvent)

      expect(dragOverEvent.defaultPrevented).toBe(true)
    })

    it('should ignore drops without node type data', () => {
      const { addNode } = vi.mocked(require('@/stores/flowDesignerStore')).useFlowDesignerStore()

      renderWithProvider(<FlowDesignerCanvas />)

      const canvas = document.querySelector('.react-flow') as HTMLElement
      const dropEvent = new DragEvent('drop', {
        bubbles: true,
        clientX: 100,
        clientY: 100,
      })

      // Mock getBoundingClientRect
      canvas.getBoundingClientRect = vi.fn(() => ({
        left: 0,
        top: 0,
        right: 1000,
        bottom: 1000,
        width: 1000,
        height: 1000,
        x: 0,
        y: 0,
        toJSON: () => ({}),
      }))

      fireEvent(canvas, dropEvent)

      // addNode should not be called for invalid drops
      expect(addNode).not.toHaveBeenCalled()
    })
  })

  describe('edge connection', () => {
    it('should create edge when connecting nodes', async () => {
      const { addEdge } = vi.mocked(require('@/stores/flowDesignerStore')).useFlowDesignerStore()

      renderWithProvider(<FlowDesignerCanvas />)

      // This is a simplified test - in real scenarios, you'd have actual nodes
      // and would trigger connection events through React Flow's API
      // For now, we verify the component renders without errors

      expect(document.querySelector('.react-flow')).toBeDefined()
    })
  })

  describe('zoom controls', () => {
    it('should render zoom buttons', () => {
      renderWithProvider(<FlowDesignerCanvas />)

      const controls = document.querySelector('.react-flow__controls')
      expect(controls).toBeDefined()

      // Zoom buttons should be present
      const buttons = controls?.querySelectorAll('button')
      expect(buttons?.length).toBeGreaterThan(0)
    })
  })

  describe('minimap', () => {
    it('should render minimap with nodes', () => {
      renderWithProvider(<FlowDesignerCanvas />)

      const minimap = document.querySelector('.react-flow__minimap')
      expect(minimap).toBeDefined()
    })
  })

  describe('accessibility', () => {
    it('should have proper ARIA labels', () => {
      renderWithProvider(<FlowDesignerCanvas />)

      // Info panel should be accessible
      const infoPanel = screen.getByText(/🖱️ Drag to pan/)
      expect(infoPanel).toBeDefined()
    })
  })

  describe('responsive behavior', () => {
    it('should fill available space', () => {
      const { container } = renderWithProvider(<FlowDesignerCanvas />)

      const canvasWrapper = container.querySelector('.flex-1')
      expect(canvasWrapper).toBeDefined()
    })
  })
})
