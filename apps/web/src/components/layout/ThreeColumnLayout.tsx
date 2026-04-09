'use client'

import { ReactNode } from 'react'
import { CompanyRail } from './CompanyRail'
import { AppSidebar } from './AppSidebar'

interface ThreeColumnLayoutProps {
  children: ReactNode
  showPropertiesPanel?: boolean
}

/**
 * ThreeColumnLayout — Main layout wrapper with three columns.
 *
 * Columns:
 * - Left: CompanyRail (180px expanded, 60px collapsed)
 * - Center: AppSidebar (240px expanded, 60px collapsed)
 * - Right: Content area (flex-fill)
 *
 * Responsive:
 * - Desktop (≥768px): Three columns
 * - Mobile (<768px): Single column (CompanyRail and Sidebar hidden)
 */
export function ThreeColumnLayout({
  children,
  showPropertiesPanel = false,
}: ThreeColumnLayoutProps) {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* CompanyRail - Left Column */}
      <div className="hidden md:block">
        <CompanyRail />
      </div>

      {/* AppSidebar - Center Column */}
      <div className="hidden md:block">
        <AppSidebar />
      </div>

      {/* Content Area - Right Column */}
      <div className="flex-1 overflow-auto">
        {children}
      </div>

      {/* Properties Panel - Overlay (conditional) */}
      {showPropertiesPanel && (
        <div className="hidden lg:block w-80 border-l border-border bg-muted/10">
          {/* Properties panel content - future implementation */}
          <div className="p-4 text-sm text-muted-foreground">
            Properties Panel
          </div>
        </div>
      )}
    </div>
  )
}
