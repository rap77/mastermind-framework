import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { CompanyRail } from '../CompanyRail'
import { useLayoutStore } from '@/stores/layoutStore'
import { useCompanyStore } from '@/stores/companyStore'

describe('CompanyRail', () => {
  beforeEach(() => {
    // Reset layout state before each test
    useLayoutStore.setState({
      companyRailCollapsed: false,
      sidebarCollapsed: false,
      propertiesPanelOpen: false,
      densityMode: 'normal',
    })
    // Reset company state before each test
    useCompanyStore.setState({
      companies: [],
      activeCompanyId: null,
      ordering: [],
    })
  })

  describe('rendering', () => {
    it('should render Companies label when expanded', () => {
      render(<CompanyRail />)

      expect(screen.getByText('Companies')).toBeInTheDocument()
    })

    it('should show empty state when no companies exist', () => {
      render(<CompanyRail />)

      expect(screen.getByText('No companies yet')).toBeInTheDocument()
    })

    it('should render collapse button', () => {
      render(<CompanyRail />)

      const button = screen.getByLabelText('Collapse CompanyRail')
      expect(button).toBeInTheDocument()
    })

    it('should render companies when they exist', () => {
      const company = {
        id: 'company-1',
        name: 'Test Company',
        slug: 'test-company',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }

      useCompanyStore.getState().addCompany(company)
      render(<CompanyRail />)

      expect(screen.getByText('Test Company')).toBeInTheDocument()
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

  describe('company selection', () => {
    it('should highlight active company', () => {
      const company = {
        id: 'company-1',
        name: 'Test Company',
        slug: 'test-company',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }

      useCompanyStore.getState().addCompany(company)
      const { container } = render(<CompanyRail />)

      const companyCard = container.querySelector('[data-testid="company-test-company"]')
      expect(companyCard).toHaveClass('bg-accent')
    })

    it('should select company when clicked', () => {
      const company = {
        id: 'company-1',
        name: 'Test Company',
        slug: 'test-company',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }

      useCompanyStore.getState().addCompany(company)
      const { container } = render(<CompanyRail />)

      const companyCard = container.querySelector('[data-testid="company-test-company"]')
      fireEvent.click(companyCard!)

      expect(useCompanyStore.getState().activeCompanyId).toBe('company-1')
    })
  })
})
