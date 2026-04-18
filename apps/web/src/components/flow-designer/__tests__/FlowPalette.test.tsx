/**
 * FlowPalette Tests
 *
 * Tests for the node types palette including hover behavior.
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { FlowPalette } from '../FlowPalette'

describe('FlowPalette', () => {
  describe('rendering', () => {
    it('should render all node types', () => {
      render(<FlowPalette />)

      expect(screen.getByText('Brain')).toBeDefined()
      expect(screen.getByText('Gateway')).toBeDefined()
      expect(screen.getByText('Adapter')).toBeDefined()
      expect(screen.getByText('Router')).toBeDefined()
      expect(screen.getByText('Condition')).toBeDefined()
    })

    it('should render node type icons', () => {
      const { container } = render(<FlowPalette />)

      expect(container.textContent).toContain('🧠')
      expect(container.textContent).toContain('🚪')
      expect(container.textContent).toContain('🔌')
      expect(container.textContent).toContain('↗️')
      expect(container.textContent).toContain('❓')
    })
  })

  describe('hover behavior', () => {
    it('should use CSS hover instead of onMouseEnter/onMouseLeave', () => {
      // This test verifies the component source code doesn't use JS hover handlers
      // We need to check the actual implementation, not just the rendered DOM

      // Read the component file
      const fs = require('fs')
      const componentPath = require.resolve('../FlowPalette.tsx')
      const componentCode = fs.readFileSync(componentPath, 'utf-8')

      // Should NOT have onMouseEnter in the code
      expect(componentCode).not.toContain('onMouseEnter')

      // Should NOT have onMouseLeave in the code
      expect(componentCode).not.toContain('onMouseLeave')

      // Should have CSS hover class
      expect(componentCode).toContain('hover:')
    })

    it('should apply hover styles via CSS classes only', () => {
      const { container } = render(<FlowPalette />)

      const nodeElements = container.querySelectorAll('[draggable="true"]')

      nodeElements.forEach((element) => {
        // Style attribute should only have static properties, not borderColor
        const style = element.getAttribute('style') || ''
        // Should only have backgroundColor and borderColor set statically
        expect(style).toContain('border-color')
        // But borderColor should be the default color, not changed by JS
        expect(style).toContain('var(--color-border)')

        // Should have hover class for shadow
        const classList = Array.from(element.classList)
        expect(classList.some(cls => cls.includes('hover'))).toBe(true)
      })
    })
  })

  describe('drag behavior', () => {
    it('should have draggable elements', () => {
      const { container } = render(<FlowPalette />)

      const draggableElements = container.querySelectorAll('[draggable="true"]')
      expect(draggableElements.length).toBe(5) // 5 node types
    })
  })
})
