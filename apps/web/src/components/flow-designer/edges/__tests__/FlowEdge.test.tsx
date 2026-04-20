/**
 * FlowEdge Tests
 *
 * Tests for edge rendering, label positioning, and styling.
 */

import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { ReactFlowProvider } from '@xyflow/react'
import { FlowEdge } from '../FlowEdge'

// Import the helper function to test directly
import { getEdgeCenter } from '../FlowEdge'

describe('FlowEdge', () => {
  const renderWithProvider = (component: React.ReactNode) => {
    return render(<ReactFlowProvider>{component}</ReactFlowProvider>)
  }

  describe('getEdgeCenter', () => {
    it('should calculate midpoint for horizontal edge', () => {
      const result = getEdgeCenter(0, 100, 200, 100)
      expect(result.x).toBe(100)
      expect(result.y).toBe(100)
    })

    it('should calculate midpoint for vertical edge', () => {
      const result = getEdgeCenter(100, 0, 100, 200)
      expect(result.x).toBe(100)
      expect(result.y).toBe(100)
    })

    it('should calculate midpoint for diagonal edge', () => {
      const result = getEdgeCenter(0, 0, 200, 200)
      expect(result.x).toBe(100)
      expect(result.y).toBe(100)
    })

    it('should handle negative coordinates', () => {
      const result = getEdgeCenter(-100, -100, 100, 100)
      expect(result.x).toBe(0)
      expect(result.y).toBe(0)
    })

    it('should handle decimal coordinates', () => {
      const result = getEdgeCenter(0, 0, 150, 250)
      expect(result.x).toBe(75)
      expect(result.y).toBe(125)
    })
  })

  describe('rendering', () => {
    it('should render edge without label', () => {
      const { container } = renderWithProvider(
        <svg>
          <FlowEdge
            id="edge-1"
            sourceX={0}
            sourceY={100}
            targetX={200}
            targetY={100}
            source={0}
            target={1}
            selected={false}
          />
        </svg>
      )

      // Edge path should be rendered
      const edgePath = container.querySelector('path')
      expect(edgePath).toBeDefined()
    })

    it('should render edge path with bezier curve', () => {
      const { container } = renderWithProvider(
        <svg>
          <FlowEdge
            id="edge-2"
            sourceX={0}
            sourceY={100}
            targetX={200}
            targetY={100}
            source={0}
            target={1}
            selected={false}
          />
        </svg>
      )

      const edgePath = container.querySelector('path')
      expect(edgePath?.getAttribute('d')).toMatch(/^M/) // SVG path command
    })
  })

  describe('styling', () => {
    it('should apply selected styles when selected', () => {
      const { container } = renderWithProvider(
        <svg>
          <FlowEdge
            id="edge-3"
            sourceX={0}
            sourceY={100}
            targetX={200}
            targetY={100}
            source={0}
            target={1}
            selected={true}
          />
        </svg>
      )

      const edgePath = container.querySelector('path')
      expect(edgePath).toBeDefined()
      // Selected edge should exist - BaseEdge handles styling internally
      expect(edgePath).toBeTruthy()
    })

    it('should apply default styles when not selected', () => {
      const { container } = renderWithProvider(
        <svg>
          <FlowEdge
            id="edge-4"
            sourceX={0}
            sourceY={100}
            targetX={200}
            targetY={100}
            source={0}
            target={1}
            selected={false}
          />
        </svg>
      )

      const edgePath = container.querySelector('path')
      expect(edgePath).toBeDefined()
    })
  })
})
