'use client'

import { ChevronLeft, ChevronRight, GripVertical } from 'lucide-react'
import { useLayoutStore } from '@/stores/layoutStore'

/**
 * CompanyRail — Left column for company switcher.
 *
 * Placeholder implementation (full multi-tenant switcher in Plan 02).
 * Current features:
 * - Collapsible (180px expanded, 60px collapsed)
 * - Drag handle for future reordering
 * - Border-right and bg-muted styling
 */
export function CompanyRail() {
  const collapsed = useLayoutStore((state) => state.companyRailCollapsed)
  const toggleCompanyRail = useLayoutStore((state) => state.toggleCompanyRail)

  return (
    <div
      className={`
        flex flex-col border-r border-border bg-muted/10
        transition-all duration-200 ease-in-out
        ${collapsed ? 'w-[60px]' : 'w-[180px]'}
      `}
      data-testid="company-rail"
    >
      {/* Header with collapse button */}
      <div className="flex items-center justify-between p-2 border-b border-border">
        {!collapsed && (
          <span className="text-sm font-medium text-foreground">Companies</span>
        )}
        <button
          onClick={toggleCompanyRail}
          className="p-1 rounded hover:bg-muted transition-colors"
          aria-label={collapsed ? 'Expand CompanyRail' : 'Collapse CompanyRail'}
          data-testid="company-rail-toggle"
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Drag handle (for future Plan 02 reordering) */}
      <div className="flex items-center justify-center py-2 border-b border-border">
        <GripVertical className="w-4 h-4 text-muted-foreground" />
      </div>

      {/* Placeholder content */}
      {!collapsed && (
        <div className="flex-1 flex items-center justify-center p-4">
          <p className="text-xs text-muted-foreground text-center">
            Company switcher placeholder<br />
            (Plan 02)
          </p>
        </div>
      )}
    </div>
  )
}
