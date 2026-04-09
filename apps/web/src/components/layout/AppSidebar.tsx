'use client'

import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { useLayoutStore } from '@/stores/layoutStore'
import {
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  Network,
  Vault,
  Wrench,
} from 'lucide-react'

interface NavItem {
  label: string
  href: string
  icon: React.ComponentType<{ className?: string }>
}

const navItems: NavItem[] = [
  { label: 'Command Center', href: '/command-center', icon: LayoutDashboard },
  { label: 'The Nexus', href: '/nexus', icon: Network },
  { label: 'Strategy Vault', href: '/strategy-vault', icon: Vault },
  { label: 'Engine Room', href: '/engine-room', icon: Wrench },
]

/**
 * AppSidebar — Center column for navigation.
 *
 * Features:
 * - Collapsible (240px expanded, 60px collapsed)
 * - Active route highlighting
 * - Keyboard navigation support
 * - Icons for each nav item (Lucide React)
 */
export function AppSidebar() {
  const pathname = usePathname()
  const collapsed = useLayoutStore((state) => state.sidebarCollapsed)
  const toggleSidebar = useLayoutStore((state) => state.toggleSidebar)

  return (
    <div
      className={`
        flex flex-col border-r border-border bg-background
        transition-all duration-200 ease-in-out
        ${collapsed ? 'w-[60px]' : 'w-[240px]'}
      `}
      data-testid="app-sidebar"
    >
      {/* Header with collapse button */}
      <div className="flex items-center justify-between p-2 border-b border-border">
        {!collapsed && (
          <span className="text-sm font-medium text-foreground">Navigation</span>
        )}
        <button
          onClick={toggleSidebar}
          className="p-1 rounded hover:bg-muted transition-colors"
          aria-label={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          data-testid="sidebar-toggle"
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Navigation items */}
      <nav className="flex-1 py-2">
        <ul className="space-y-1 px-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={`
                    flex items-center gap-3 px-3 py-2 rounded-md
                    transition-colors duration-150
                    ${isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                    }
                  `}
                  data-testid={`nav-item-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  {!collapsed && (
                    <span className="text-sm font-medium truncate">
                      {item.label}
                    </span>
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
    </div>
  )
}
