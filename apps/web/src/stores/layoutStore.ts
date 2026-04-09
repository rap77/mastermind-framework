import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { enableMapSet } from 'immer'
import { persist } from 'zustand/middleware'

// Enable Immer MapSet plugin — required for Map.get/set/iteration inside set() callbacks
enableMapSet()

export type DensityMode = 'compact' | 'normal' | 'detailed'

interface LayoutState {
  companyRailCollapsed: boolean
  sidebarCollapsed: boolean
  propertiesPanelOpen: boolean
  densityMode: DensityMode
}

interface LayoutStoreState extends LayoutState {
  toggleCompanyRail: () => void
  toggleSidebar: () => void
  togglePropertiesPanel: () => void
  setDensityMode: (mode: DensityMode) => void
}

/**
 * useLayoutStore — Zustand store for layout state management.
 *
 * Uses Immer middleware for immutable updates and persist middleware for
 * localStorage persistence (layout state survives page refreshes).
 *
 * Follows same pattern as brainStore.ts: Immer + targeted selectors for performance.
 */
export const useLayoutStore = create<LayoutStoreState>()(
  immer(
    persist(
      (set) => ({
        companyRailCollapsed: false,
        sidebarCollapsed: false,
        propertiesPanelOpen: false,
        densityMode: 'normal',

        toggleCompanyRail: () => {
          set(state => {
            state.companyRailCollapsed = !state.companyRailCollapsed
          })
        },

        toggleSidebar: () => {
          set(state => {
            state.sidebarCollapsed = !state.sidebarCollapsed
          })
        },

        togglePropertiesPanel: () => {
          set(state => {
            state.propertiesPanelOpen = !state.propertiesPanelOpen
          })
        },

        setDensityMode: (mode) => {
          set(state => {
            state.densityMode = mode
          })
        },
      }),
      {
        name: 'mastermind-layout', // localStorage key
        partialize: (state) => ({
          companyRailCollapsed: state.companyRailCollapsed,
          sidebarCollapsed: state.sidebarCollapsed,
          densityMode: state.densityMode,
          // propertiesPanelOpen is NOT persisted — reset on page load
        }),
      }
    )
  )
)

/**
 * useCompanyRailCollapsed — targeted selector for CompanyRail collapse state.
 *
 * Prevents cascade re-renders: only re-renders when CompanyRail state changes.
 */
export const useCompanyRailCollapsed = () =>
  useLayoutStore(state => state.companyRailCollapsed)

/**
 * useSidebarCollapsed — targeted selector for Sidebar collapse state.
 *
 * Prevents cascade re-renders: only re-renders when Sidebar state changes.
 */
export const useSidebarCollapsed = () =>
  useLayoutStore(state => state.sidebarCollapsed)

/**
 * useDensityMode — targeted selector for density mode.
 *
 * Prevents cascade re-renders: only re-renders when density mode changes.
 */
export const useDensityMode = () =>
  useLayoutStore(state => state.densityMode)
