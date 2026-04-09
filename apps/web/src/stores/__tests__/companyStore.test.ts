import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useCompanyStore, useActiveCompany, useCompanies, useActiveCompanyId } from '../companyStore'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

describe('companyStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useCompanyStore.setState({
      companies: [],
      activeCompanyId: null,
      ordering: [],
    })
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have empty initial state', () => {
      const { result } = renderHook(() => useCompanyStore())

      expect(result.current.companies).toEqual([])
      expect(result.current.activeCompanyId).toBeNull()
      expect(result.current.ordering).toEqual([])
    })
  })

  describe('setActiveCompany', () => {
    it('should set active company ID', () => {
      const { result } = renderHook(() => useCompanyStore())

      act(() => {
        result.current.setActiveCompany('company-1')
      })

      expect(result.current.activeCompanyId).toBe('company-1')
    })
  })

  describe('addCompany', () => {
    it('should add company to store', () => {
      const { result } = renderHook(() => useCompanyStore())
      const company = {
        id: 'company-1',
        name: 'Test Company',
        slug: 'test-company',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }

      act(() => {
        result.current.addCompany(company)
      })

      expect(result.current.companies).toHaveLength(1)
      expect(result.current.companies[0]).toEqual(company)
      expect(result.current.ordering).toEqual(['company-1'])
    })

    it('should auto-select first company as active', () => {
      const { result } = renderHook(() => useCompanyStore())
      const company = {
        id: 'company-1',
        name: 'Test Company',
        slug: 'test-company',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }

      act(() => {
        result.current.addCompany(company)
      })

      expect(result.current.activeCompanyId).toBe('company-1')
    })

    it('should not add duplicate company', () => {
      const { result } = renderHook(() => useCompanyStore())
      const company = {
        id: 'company-1',
        name: 'Test Company',
        slug: 'test-company',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }

      act(() => {
        result.current.addCompany(company)
        result.current.addCompany(company) // Add again
      })

      expect(result.current.companies).toHaveLength(1)
      expect(result.current.ordering).toEqual(['company-1'])
    })
  })

  describe('removeCompany', () => {
    it('should remove company from store', () => {
      const { result } = renderHook(() => useCompanyStore())
      const company1 = {
        id: 'company-1',
        name: 'Test Company 1',
        slug: 'test-company-1',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }
      const company2 = {
        id: 'company-2',
        name: 'Test Company 2',
        slug: 'test-company-2',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }

      act(() => {
        result.current.addCompany(company1)
        result.current.addCompany(company2)
        result.current.removeCompany('company-1')
      })

      expect(result.current.companies).toHaveLength(1)
      expect(result.current.companies[0].id).toBe('company-2')
      expect(result.current.ordering).toEqual(['company-2'])
    })

    it('should switch active company when removing active company', () => {
      const { result } = renderHook(() => useCompanyStore())
      const company1 = {
        id: 'company-1',
        name: 'Test Company 1',
        slug: 'test-company-1',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }
      const company2 = {
        id: 'company-2',
        name: 'Test Company 2',
        slug: 'test-company-2',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }

      act(() => {
        result.current.addCompany(company1)
        result.current.addCompany(company2)
        result.current.setActiveCompany('company-1')
        result.current.removeCompany('company-1')
      })

      expect(result.current.activeCompanyId).toBe('company-2')
    })

    it('should clear active company when removing last company', () => {
      const { result } = renderHook(() => useCompanyStore())
      const company = {
        id: 'company-1',
        name: 'Test Company',
        slug: 'test-company',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }

      act(() => {
        result.current.addCompany(company)
        result.current.removeCompany('company-1')
      })

      expect(result.current.activeCompanyId).toBeNull()
    })
  })

  describe('reorderCompanies', () => {
    it('should reorder companies in ordering array', () => {
      const { result } = renderHook(() => useCompanyStore())
      const company1 = {
        id: 'company-1',
        name: 'Test Company 1',
        slug: 'test-company-1',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }
      const company2 = {
        id: 'company-2',
        name: 'Test Company 2',
        slug: 'test-company-2',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }
      const company3 = {
        id: 'company-3',
        name: 'Test Company 3',
        slug: 'test-company-3',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }

      act(() => {
        result.current.addCompany(company1)
        result.current.addCompany(company2)
        result.current.addCompany(company3)
        // Move company-3 to position 1 (between company-1 and company-2)
        result.current.reorderCompanies('company-3', 'company-2')
      })

      expect(result.current.ordering).toEqual(['company-1', 'company-3', 'company-2'])
    })

    it('should handle invalid company IDs gracefully', () => {
      const { result } = renderHook(() => useCompanyStore())
      const company1 = {
        id: 'company-1',
        name: 'Test Company 1',
        slug: 'test-company-1',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }
      const company2 = {
        id: 'company-2',
        name: 'Test Company 2',
        slug: 'test-company-2',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }

      act(() => {
        result.current.addCompany(company1)
        result.current.addCompany(company2)
        result.current.reorderCompanies('invalid-id', 'company-2')
      })

      // Should not crash, ordering should remain unchanged
      expect(result.current.ordering).toEqual(['company-1', 'company-2'])
    })
  })

  describe('updateCompanyStatus', () => {
    it('should update company status', () => {
      const { result } = renderHook(() => useCompanyStore())
      const company = {
        id: 'company-1',
        name: 'Test Company',
        slug: 'test-company',
        status: 'inactive' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }

      act(() => {
        result.current.addCompany(company)
        result.current.updateCompanyStatus('company-1', 'active', 5, 10)
      })

      expect(result.current.companies[0].status).toBe('active')
      expect(result.current.companies[0].liveAgentsCount).toBe(5)
      expect(result.current.companies[0].unreadCount).toBe(10)
    })

    it('should handle updating non-existent company', () => {
      const { result } = renderHook(() => useCompanyStore())

      act(() => {
        result.current.updateCompanyStatus('non-existent', 'active', 5, 10)
      })

      // Should not crash
      expect(result.current.companies).toEqual([])
    })
  })

  describe('selectors', () => {
    it('useActiveCompany should return active company', () => {
      const { result } = renderHook(() => useActiveCompany())
      const company = {
        id: 'company-1',
        name: 'Test Company',
        slug: 'test-company',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }

      act(() => {
        useCompanyStore.getState().addCompany(company)
      })

      expect(result.current).toEqual(company)
    })

    it('useActiveCompanyId should return active company ID', () => {
      const { result } = renderHook(() => useActiveCompanyId())
      const company = {
        id: 'company-1',
        name: 'Test Company',
        slug: 'test-company',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }

      act(() => {
        useCompanyStore.getState().addCompany(company)
      })

      expect(result.current).toBe('company-1')
    })

    it('useCompanies should return companies sorted by ordering', () => {
      const { result } = renderHook(() => useCompanies())
      const company1 = {
        id: 'company-1',
        name: 'Test Company 1',
        slug: 'test-company-1',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }
      const company2 = {
        id: 'company-2',
        name: 'Test Company 2',
        slug: 'test-company-2',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }
      const company3 = {
        id: 'company-3',
        name: 'Test Company 3',
        slug: 'test-company-3',
        status: 'active' as const,
        unreadCount: 0,
        liveAgentsCount: 0,
      }

      act(() => {
        useCompanyStore.getState().addCompany(company1)
        useCompanyStore.getState().addCompany(company2)
        useCompanyStore.getState().addCompany(company3)
        useCompanyStore.getState().reorderCompanies('company-3', 'company-2')
      })

      expect(result.current).toHaveLength(3)
      expect(result.current[0].id).toBe('company-1')
      expect(result.current[1].id).toBe('company-3')
      expect(result.current[2].id).toBe('company-2')
    })
  })
})
