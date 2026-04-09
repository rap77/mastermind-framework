import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { AppSidebar } from '../AppSidebar'
import { useLayoutStore } from '@/stores/layoutStore'
import { usePathname } from 'next/navigation'

// Mock next/navigation
vi.mock('next/navigation', () => ({
  usePathname: vi.fn(),
}))

describe('AppSidebar', () => {
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
    it('should render all 4 navigation items', () => {
      ;(usePathname as vi.Mock).mockReturnValue('/command-center')

      render(<AppSidebar />)

      expect(screen.getByText('Command Center')).toBeInTheDocument()
      expect(screen.getByText('The Nexus')).toBeInTheDocument()
      expect(screen.getByText('Strategy Vault')).toBeInTheDocument()
      expect(screen.getByText('Engine Room')).toBeInTheDocument()
    })

    it('should render Navigation label when expanded', () => {
      ;(usePathname as vi.Mock).mockReturnValue('/command-center')

      render(<AppSidebar />)

      expect(screen.getByText('Navigation')).toBeInTheDocument()
    })

    it('should render collapse button', () => {
      ;(usePathname as vi.Mock).mockReturnValue('/command-center')

      render(<AppSidebar />)

      const button = screen.getByLabelText('Collapse Sidebar')
      expect(button).toBeInTheDocument()
    })
  })

  describe('active route highlighting', () => {
    it('should highlight Command Center when on /command-center', () => {
      ;(usePathname as vi.Mock).mockReturnValue('/command-center')

      const { container } = render(<AppSidebar />)

      const activeLink = container.querySelector('[data-testid="nav-item-command-center"]')
      expect(activeLink).toHaveClass('bg-primary', 'text-primary-foreground')
    })

    it('should highlight The Nexus when on /nexus', () => {
      ;(usePathname as vi.Mock).mockReturnValue('/nexus')

      const { container } = render(<AppSidebar />)

      const activeLink = container.querySelector('[data-testid="nav-item-the-nexus"]')
      expect(activeLink).toHaveClass('bg-primary', 'text-primary-foreground')
    })

    it('should not highlight inactive routes', () => {
      ;(usePathname as vi.Mock).mockReturnValue('/command-center')

      const { container } = render(<AppSidebar />)

      const inactiveLink = container.querySelector('[data-testid="nav-item-the-nexus"]')
      expect(inactiveLink).not.toHaveClass('bg-primary', 'text-primary-foreground')
      expect(inactiveLink).toHaveClass('text-muted-foreground')
    })
  })

  describe('collapse behavior', () => {
    it('should collapse when toggle button is clicked', () => {
      ;(usePathname as vi.Mock).mockReturnValue('/command-center')

      render(<AppSidebar />)

      const button = screen.getByLabelText('Collapse Sidebar')
      fireEvent.click(button)

      // Navigation label should disappear when collapsed
      expect(screen.queryByText('Navigation')).not.toBeInTheDocument()
      // Nav item labels should also disappear
      expect(screen.queryByText('Command Center')).not.toBeInTheDocument()
    })

    it('should expand when toggle button is clicked while collapsed', () => {
      useLayoutStore.setState({ sidebarCollapsed: true })

      ;(usePathname as vi.Mock).mockReturnValue('/command-center')

      render(<AppSidebar />)

      const button = screen.getByLabelText('Expand Sidebar')
      fireEvent.click(button)

      // Navigation label should appear when expanded
      expect(screen.getByText('Navigation')).toBeInTheDocument()
      // Nav item labels should also appear
      expect(screen.getByText('Command Center')).toBeInTheDocument()
    })
  })

  describe('width transitions', () => {
    it('should have 240px width when expanded', () => {
      useLayoutStore.setState({ sidebarCollapsed: false })

      ;(usePathname as vi.Mock).mockReturnValue('/command-center')

      const { container } = render(<AppSidebar />)

      const sidebar = container.querySelector('[data-testid="app-sidebar"]')
      expect(sidebar).toHaveClass('w-[240px]')
    })

    it('should have 60px width when collapsed', () => {
      useLayoutStore.setState({ sidebarCollapsed: true })

      ;(usePathname as vi.Mock).mockReturnValue('/command-center')

      const { container } = render(<AppSidebar />)

      const sidebar = container.querySelector('[data-testid="app-sidebar"]')
      expect(sidebar).toHaveClass('w-[60px]')
    })
  })

  describe('keyboard navigation', () => {
    it('should render links with proper href attributes', () => {
      ;(usePathname as vi.Mock).mockReturnValue('/command-center')

      const { container } = render(<AppSidebar />)

      expect(container.querySelector('a[href="/command-center"]')).toBeInTheDocument()
      expect(container.querySelector('a[href="/nexus"]')).toBeInTheDocument()
      expect(container.querySelector('a[href="/strategy-vault"]')).toBeInTheDocument()
      expect(container.querySelector('a[href="/engine-room"]')).toBeInTheDocument()
    })
  })
})
