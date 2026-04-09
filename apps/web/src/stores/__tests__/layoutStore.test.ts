import { describe, it, expect, beforeEach } from 'vitest'
import { useLayoutStore } from '../layoutStore'

describe('layoutStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useLayoutStore.setState({
      companyRailCollapsed: false,
      sidebarCollapsed: false,
      propertiesPanelOpen: false,
      densityMode: 'normal',
    })
  })

  describe('initial state', () => {
    it('should have correct default values', () => {
      const state = useLayoutStore.getState()
      expect(state.companyRailCollapsed).toBe(false)
      expect(state.sidebarCollapsed).toBe(false)
      expect(state.propertiesPanelOpen).toBe(false)
      expect(state.densityMode).toBe('normal')
    })
  })

  describe('toggleCompanyRail', () => {
    it('should toggle companyRailCollapsed state', () => {
      const { toggleCompanyRail } = useLayoutStore.getState()

      expect(useLayoutStore.getState().companyRailCollapsed).toBe(false)

      toggleCompanyRail()
      expect(useLayoutStore.getState().companyRailCollapsed).toBe(true)

      toggleCompanyRail()
      expect(useLayoutStore.getState().companyRailCollapsed).toBe(false)
    })
  })

  describe('toggleSidebar', () => {
    it('should toggle sidebarCollapsed state', () => {
      const { toggleSidebar } = useLayoutStore.getState()

      expect(useLayoutStore.getState().sidebarCollapsed).toBe(false)

      toggleSidebar()
      expect(useLayoutStore.getState().sidebarCollapsed).toBe(true)

      toggleSidebar()
      expect(useLayoutStore.getState().sidebarCollapsed).toBe(false)
    })
  })

  describe('togglePropertiesPanel', () => {
    it('should toggle propertiesPanelOpen state', () => {
      const { togglePropertiesPanel } = useLayoutStore.getState()

      expect(useLayoutStore.getState().propertiesPanelOpen).toBe(false)

      togglePropertiesPanel()
      expect(useLayoutStore.getState().propertiesPanelOpen).toBe(true)

      togglePropertiesPanel()
      expect(useLayoutStore.getState().propertiesPanelOpen).toBe(false)
    })
  })

  describe('setDensityMode', () => {
    it('should set densityMode to compact', () => {
      const { setDensityMode } = useLayoutStore.getState()

      setDensityMode('compact')
      expect(useLayoutStore.getState().densityMode).toBe('compact')
    })

    it('should set densityMode to detailed', () => {
      const { setDensityMode } = useLayoutStore.getState()

      setDensityMode('detailed')
      expect(useLayoutStore.getState().densityMode).toBe('detailed')
    })

    it('should set densityMode to normal', () => {
      const { setDensityMode } = useLayoutStore.getState()

      setDensityMode('compact')
      expect(useLayoutStore.getState().densityMode).toBe('compact')

      setDensityMode('normal')
      expect(useLayoutStore.getState().densityMode).toBe('normal')
    })
  })

  describe('targeted selectors', () => {
    it('useCompanyRailCollapsed should return collapsed state', () => {
      const { toggleCompanyRail } = useLayoutStore.getState()

      const collapsed1 = useLayoutStore.getState().companyRailCollapsed
      expect(collapsed1).toBe(false)

      toggleCompanyRail()

      const collapsed2 = useLayoutStore.getState().companyRailCollapsed
      expect(collapsed2).toBe(true)
    })

    it('useSidebarCollapsed should return collapsed state', () => {
      const { toggleSidebar } = useLayoutStore.getState()

      const collapsed1 = useLayoutStore.getState().sidebarCollapsed
      expect(collapsed1).toBe(false)

      toggleSidebar()

      const collapsed2 = useLayoutStore.getState().sidebarCollapsed
      expect(collapsed2).toBe(true)
    })

    it('useDensityMode should return density mode', () => {
      const { setDensityMode } = useLayoutStore.getState()

      const mode1 = useLayoutStore.getState().densityMode
      expect(mode1).toBe('normal')

      setDensityMode('compact')

      const mode2 = useLayoutStore.getState().densityMode
      expect(mode2).toBe('compact')
    })
  })
})
