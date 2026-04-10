'use client'

import { useEffect, useRef } from 'react'
import { useLayoutStore } from '@/stores/layoutStore'

const MOBILE_BREAKPOINT = 768 // pixels

/**
 * useDensityModeSync — Auto-switch density mode based on viewport.
 *
 * Per Brain #7 Condition 2:
 * - When viewport changes from desktop to mobile → auto-switch to compact mode
 * - When viewport changes back to desktop → restore previous mode
 *
 * This prevents detailed mode from breaking mobile UI.
 */
export function useDensityModeSync() {
  const densityMode = useLayoutStore(state => state.densityMode)
  const setDensityMode = useLayoutStore(state => state.setDensityMode)
  const previousModeRef = useRef<'compact' | 'normal' | null>(null)

  useEffect(() => {
    const handleResize = () => {
      const isMobile = window.innerWidth < MOBILE_BREAKPOINT

      if (isMobile && densityMode !== 'compact') {
        // Save current mode before switching to compact
        previousModeRef.current = densityMode
        setDensityMode('compact')
      } else if (!isMobile && previousModeRef.current) {
        // Restore previous mode when returning to desktop
        setDensityMode(previousModeRef.current)
        previousModeRef.current = null
      }
    }

    // Initial check
    handleResize()

    // Listen for viewport changes
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }, [densityMode, setDensityMode])
}
