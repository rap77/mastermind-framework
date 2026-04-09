import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ThreeColumnLayout } from '../ThreeColumnLayout'
import { useLayoutStore } from '@/stores/layoutStore'

describe('ThreeColumnLayout', () => {
  beforeEach(() => {
    // Reset layout state before each test
    useLayoutStore.setState({
      companyRailCollapsed: false,
      sidebarCollapsed: false,
      propertiesPanelOpen: false,
      densityMode: 'normal',
    })
  })

  describe('rendering', () => {
    it('should render children content', () => {
      render(
        <ThreeColumnLayout>
          <div>Test Content</div>
        </ThreeColumnLayout>
      )

      expect(screen.getByText('Test Content')).toBeInTheDocument()
    })

    it('should not show properties panel by default', () => {
      render(
        <ThreeColumnLayout>
          <div>Content</div>
        </ThreeColumnLayout>
      )

      expect(screen.queryByText('Properties Panel')).not.toBeInTheDocument()
    })

    it('should show properties panel when showPropertiesPanel is true', () => {
      render(
        <ThreeColumnLayout showPropertiesPanel={true}>
          <div>Content</div>
        </ThreeColumnLayout>
      )

      expect(screen.getByText('Properties Panel')).toBeInTheDocument()
    })
  })

  describe('responsive layout', () => {
    it('should render CompanyRail and Sidebar with responsive classes', () => {
      render(
        <ThreeColumnLayout>
          <div>Content</div>
        </ThreeColumnLayout>
      )

      // CompanyRail and Sidebar should be in the document with responsive classes
      const companyRail = screen.getByText('Companies')
      const sidebar = screen.getByText('Navigation')

      expect(companyRail).toBeInTheDocument()
      expect(sidebar).toBeInTheDocument()
    })
  })
})
