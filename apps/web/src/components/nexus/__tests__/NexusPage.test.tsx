/**
 * NexusPage layout tests — Task 4 Phase 08-04
 *
 * Tests: sidebar collapse in Focus Mode, canvas expansion, panel hide,
 * FocusModeBadge integration.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { NexusPage } from '../NexusPage'
import { useOrchestratorStore } from '@/stores/orchestratorStore'

// Mock FocusModeBadge — don't test its internals here (tested separately)
vi.mock('@/components/shared/FocusModeBadge', () => ({
  FocusModeBadge: () => <div data-testid="focus-mode-badge" />,
}))

function resetStore() {
  useOrchestratorStore.getState().reset()
}

describe('NexusPage', () => {
  beforeEach(() => {
    resetStore()
  })

  const mockCanvas = <div data-testid="canvas">Canvas</div>
  const mockSidebar = <div data-testid="sidebar">Sidebar</div>
  const mockPanel = <div data-testid="panel">Panel</div>

  // ─── Default state (not in Focus Mode) ──────────────────────────────────

  describe('default state (not in Focus Mode)', () => {
    it('renders canvas', () => {
      render(<NexusPage canvas={mockCanvas} />)
      expect(screen.getByTestId('canvas')).toBeInTheDocument()
    })

    it('renders sidebar when provided', () => {
      render(<NexusPage canvas={mockCanvas} sidebar={mockSidebar} />)
      expect(screen.getByTestId('sidebar')).toBeInTheDocument()
    })

    it('renders panel when provided', () => {
      render(<NexusPage canvas={mockCanvas} panel={mockPanel} />)
      expect(screen.getByTestId('panel')).toBeInTheDocument()
    })

    it('sidebar container is visible (not w-0) when not in Focus Mode', () => {
      render(<NexusPage canvas={mockCanvas} sidebar={mockSidebar} />)
      const sidebarContainer = screen.getByTestId('nexus-sidebar')
      expect(sidebarContainer.className).toContain('w-[250px]')
      expect(sidebarContainer.className).not.toContain('w-0')
    })
  })

  // ─── Focus Mode active ───────────────────────────────────────────────────

  describe('Focus Mode active', () => {
    beforeEach(() => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
    })

    it('sidebar container collapses to w-0 in Focus Mode', () => {
      render(<NexusPage canvas={mockCanvas} sidebar={mockSidebar} />)
      const sidebarContainer = screen.getByTestId('nexus-sidebar')
      expect(sidebarContainer.className).toContain('w-0')
      expect(sidebarContainer.className).not.toContain('w-[250px]')
    })

    it('sidebar is aria-hidden in Focus Mode', () => {
      render(<NexusPage canvas={mockCanvas} sidebar={mockSidebar} />)
      const sidebarContainer = screen.getByTestId('nexus-sidebar')
      expect(sidebarContainer).toHaveAttribute('aria-hidden', 'true')
    })

    it('panel container collapses in Focus Mode', () => {
      render(<NexusPage canvas={mockCanvas} panel={mockPanel} />)
      const panelContainer = screen.getByTestId('nexus-panel')
      expect(panelContainer.className).toContain('w-0')
    })

    it('canvas container remains visible in Focus Mode', () => {
      render(<NexusPage canvas={mockCanvas} sidebar={mockSidebar} />)
      expect(screen.getByTestId('canvas')).toBeInTheDocument()
    })

    it('FocusModeBadge is rendered', () => {
      render(<NexusPage canvas={mockCanvas} />)
      expect(screen.getByTestId('focus-mode-badge')).toBeInTheDocument()
    })
  })

  // ─── Focus Mode toggle ───────────────────────────────────────────────────

  describe('Focus Mode toggle', () => {
    it('sidebar re-expands when userOverride disables Focus Mode', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      const { rerender } = render(<NexusPage canvas={mockCanvas} sidebar={mockSidebar} />)

      // In Focus Mode
      expect(screen.getByTestId('nexus-sidebar').className).toContain('w-0')

      // User escapes
      useOrchestratorStore.getState().toggleOverride()
      rerender(<NexusPage canvas={mockCanvas} sidebar={mockSidebar} />)

      // Sidebar re-expands
      expect(screen.getByTestId('nexus-sidebar').className).toContain('w-[250px]')
    })
  })

  // ─── Optional children ───────────────────────────────────────────────────

  describe('optional children', () => {
    it('renders without sidebar (no sidebar container)', () => {
      render(<NexusPage canvas={mockCanvas} />)
      expect(screen.queryByTestId('nexus-sidebar')).toBeNull()
    })

    it('renders without panel (no panel container)', () => {
      render(<NexusPage canvas={mockCanvas} />)
      expect(screen.queryByTestId('nexus-panel')).toBeNull()
    })
  })
})
