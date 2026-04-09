import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { enableMapSet } from 'immer'
import { persist } from 'zustand/middleware'

// Enable Immer MapSet plugin — required for Map.get/set/iteration inside set() callbacks
enableMapSet()

export type CompanyStatus = 'active' | 'inactive' | 'error'

export interface Company {
  id: string
  name: string
  slug: string
  icon?: string
  status: CompanyStatus
  unreadCount: number
  liveAgentsCount: number
}

interface CompanyState {
  companies: Company[]
  activeCompanyId: string | null
  ordering: string[] // Array of company IDs in display order
}

interface CompanyStoreState extends CompanyState {
  setActiveCompany: (companyId: string) => void
  reorderCompanies: (activeId: string, overId: string) => void
  addCompany: (company: Company) => void
  removeCompany: (companyId: string) => void
  updateCompanyStatus: (companyId: string, status: CompanyStatus, liveAgentsCount: number, unreadCount: number) => void
}

/**
 * useCompanyStore — Zustand store for multi-tenant company management.
 *
 * Uses Immer middleware for immutable updates and persist middleware for
 * localStorage persistence (company state survives page refreshes).
 *
 * Cross-tab sync: storage event listener rehydrates store when localStorage
 * changes in another tab.
 *
 * Follows same pattern as layoutStore.ts: Immer + targeted selectors for performance.
 */
export const useCompanyStore = create<CompanyStoreState>()(
  immer(
    persist(
      (set, get) => ({
        companies: [],
        activeCompanyId: null,
        ordering: [],

        setActiveCompany: (companyId: string) => {
          set(state => {
            state.activeCompanyId = companyId
          })
        },

        reorderCompanies: (activeId: string, overId: string) => {
          set(state => {
            const oldIndex = state.ordering.indexOf(activeId)
            const newIndex = state.ordering.indexOf(overId)

            if (oldIndex !== -1 && newIndex !== -1) {
              // Remove from old position and insert at new position
              state.ordering.splice(oldIndex, 1)
              state.ordering.splice(newIndex, 0, activeId)
            }
          })
        },

        addCompany: (company: Company) => {
          set(state => {
            // Check if company already exists
            const exists = state.companies.some(c => c.id === company.id)
            if (!exists) {
              state.companies.push(company)
              state.ordering.push(company.id)

              // Auto-select first company
              if (state.companies.length === 1) {
                state.activeCompanyId = company.id
              }
            }
          })
        },

        removeCompany: (companyId: string) => {
          set(state => {
            state.companies = state.companies.filter(c => c.id !== companyId)
            state.ordering = state.ordering.filter(id => id !== companyId)

            // Switch to another company if active was removed
            if (state.activeCompanyId === companyId) {
              state.activeCompanyId = state.companies.length > 0 ? state.companies[0].id : null
            }
          })
        },

        updateCompanyStatus: (companyId: string, status: CompanyStatus, liveAgentsCount: number, unreadCount: number) => {
          set(state => {
            const company = state.companies.find(c => c.id === companyId)
            if (company) {
              company.status = status
              company.liveAgentsCount = liveAgentsCount
              company.unreadCount = unreadCount
            }
          })
        },
      }),
      {
        name: 'mastermind-companies', // localStorage key
        partialize: (state) => ({
          companies: state.companies,
          activeCompanyId: state.activeCompanyId,
          ordering: state.ordering,
        }),
      }
    )
  )
)

// Cross-tab sync: Listen for storage events from other tabs
if (typeof window !== 'undefined') {
  window.addEventListener('storage', (e) => {
    if (e.key === 'mastermind-companies' && e.newValue) {
      // Rehydrate store from localStorage
      useCompanyStore.persist.rehydrate()
    }
  })
}

/**
 * useActiveCompany — targeted selector for active company.
 *
 * Prevents cascade re-renders: only re-renders when active company changes.
 */
export const useActiveCompany = () =>
  useCompanyStore(state => {
    const activeCompany = state.companies.find(c => c.id === state.activeCompanyId)
    return activeCompany || null
  })

/**
 * useCompanies — targeted selector for companies array.
 *
 * Returns companies sorted by ordering array.
 */
export const useCompanies = () => {
  const companies = useCompanyStore(state => state.companies)
  const ordering = useCompanyStore(state => state.ordering)

  // Memoize sorted companies to prevent infinite loops
  return ordering
    .map(id => companies.find(c => c.id === id))
    .filter((c): c is Company => c !== undefined)
}

/**
 * useActiveCompanyId — targeted selector for active company ID.
 *
 * Prevents cascade re-renders: only re-renders when active company ID changes.
 */
export const useActiveCompanyId = () =>
  useCompanyStore(state => state.activeCompanyId)
