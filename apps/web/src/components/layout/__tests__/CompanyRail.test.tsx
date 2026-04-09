import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { CompanyRail } from '../CompanyRail'
import { useLayoutStore } from '@/stores/layoutStore'

describe('CompanyRail', () => {
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
    it('should render Companies label when expanded', () => {
      render(<CompanyRail />)

      expect(screen.getByText('Companies')).toBeInTheDocument()
    })

    it('should show placeholder content when expanded', () => {
      render(<CompanyRail />)

      expect(screen.getByText(/Company switcher placeholder/)).toBeInTheDocument()
      expect(screen.getByText(/Plan 02/)).toBeInTheDocument()
    })

    it('should render collapse button', () => {
      render(<CompanyRail />)

      const button = screen.getByLabelText('Collapse CompanyRail')
      expect(button).toBeInTheDocument()
    })
  })

  describe('collapse behavior', () => {
    it('should collapse when toggle button is clicked', () => {
      render(<CompanyRail />)

      const button = screen.getByLabelText('Collapse CompanyRail')
      fireEvent.click(button)

      // Label should disappear when collapsed
      expect(screen.queryByText('Companies')).not.toBeInTheDocument()
    })

    it('should expand when toggle button is clicked while collapsed', () => {
      useLayoutStore.setState({ companyRailCollapsed: true })

      render(<CompanyRail />)

      const button = screen.getByLabelText('Expand CompanyRail')
      fireEvent.click(button)

      // Label should appear when expanded
      expect(screen.getByText('Companies')).toBeInTheDocument()
    })
  })

  describe('width transitions', () => {
    it('should have 180px width when expanded', () => {
      useLayoutStore.setState({ companyRailCollapsed: false })

      const { container } = render(<CompanyRail />)

      const rail = container.querySelector('[data-testid="company-rail"]')
      expect(rail).toHaveClass('w-[180px]')
    })

    it('should have 60px width when collapsed', () => {
      useLayoutStore.setState({ companyRailCollapsed: true })

      const { container } = render(<CompanyRail />)

      const rail = container.querySelector('[data-testid="company-rail"]')
      expect(rail).toHaveClass('w-[60px]')
    })
  })
})
