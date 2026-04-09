'use client'

import { useState } from 'react'
import { ChevronLeft, ChevronRight, GripVertical, Building2 } from 'lucide-react'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { useLayoutStore } from '@/stores/layoutStore'
import { useCompanyStore, useActiveCompanyId, useCompanies } from '@/stores/companyStore'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { cn } from '@/lib/utils'

interface SortableCompanyProps {
  company: {
    id: string
    name: string
    slug: string
    icon?: string
    status: 'active' | 'inactive' | 'error'
    unreadCount: number
    liveAgentsCount: number
  }
  isActive: boolean
  collapsed: boolean
  onSelect: (companyId: string) => void
}

function SortableCompany({ company, isActive, collapsed, onSelect }: SortableCompanyProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: company.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  // Determine status badge based on company state
  const getBadgeStatus = () => {
    if (company.status === 'error') return 'error'
    if (company.liveAgentsCount > 0) return 'live'
    if (company.unreadCount > 0) return 'warning'
    return undefined
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        'group relative flex items-center gap-2 p-2 rounded-md transition-all duration-200',
        'hover:bg-muted/50 cursor-pointer',
        isActive && 'bg-accent border-l-2 border-accent-foreground',
        isDragging && 'opacity-50'
      )}
      onClick={() => onSelect(company.id)}
      data-testid={`company-${company.slug}`}
      role="button"
      tabIndex={0}
      aria-selected={isActive}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onSelect(company.id)
        }
      }}
    >
      {/* Drag handle — visible at 60% opacity, full on hover (Brain #2 HIGH priority) */}
      <button
        {...attributes}
        {...listeners}
        className={cn(
          'flex-shrink-0 p-1 rounded transition-opacity duration-200',
          'opacity-60 group-hover:opacity-100',
          'hover:bg-muted'
        )}
        aria-label={`Reorder ${company.name}`}
        tabIndex={-1}
        onClick={(e) => e.stopPropagation()}
      >
        <GripVertical className="w-4 h-4 text-muted-foreground" />
      </button>

      {/* Company icon or fallback */}
      <div
        className={cn(
          'flex-shrink-0 flex items-center justify-center rounded-md bg-primary/10 text-primary',
          collapsed ? 'w-8 h-8' : 'w-10 h-10'
        )}
      >
        {company.icon ? (
          <img src={company.icon} alt="" className="w-full h-full rounded-md object-cover" />
        ) : (
          <Building2 className={cn('w-4 h-4', collapsed && 'w-3 h-3')} />
        )}
      </div>

      {/* Company name (hidden when collapsed) */}
      {!collapsed && (
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-foreground truncate">{company.name}</p>
        </div>
      )}

      {/* Status badge */}
      <div className="flex-shrink-0">
        {getBadgeStatus() && (
          <StatusBadge
            status={getBadgeStatus()}
            size="sm"
            count={company.unreadCount > 0 ? company.unreadCount : undefined}
            showIcon={company.unreadCount === 0}
            ariaLabel={
              company.liveAgentsCount > 0
                ? `${company.liveAgentsCount} active agents`
                : company.unreadCount > 0
                ? `${company.unreadCount} unread items`
                : undefined
            }
          />
        )}
      </div>
    </div>
  )
}

/**
 * CompanyRail — Left column for multi-tenant company switcher with drag-and-drop.
 *
 * Features:
 * - Draggable company ordering via @dnd-kit
 * - Visual status indicators per company (live agents, unread inbox)
 * - Company-specific branding/icons
 * - Sync across tabs via localStorage
 * - Keyboard navigation (Tab, Enter, Arrow keys)
 * - Collapsible (180px expanded, 60px collapsed)
 *
 * Brain #2 HIGH priority: Drag handle visible at 60% opacity, full on hover
 * Brain #3 CRITICAL: Status badges have BOTH color AND icon coding (WCAG 2.1 AA)
 */
export function CompanyRail() {
  const collapsed = useLayoutStore((state) => state.companyRailCollapsed)
  const toggleCompanyRail = useLayoutStore((state) => state.toggleCompanyRail)
  const companies = useCompanies()
  const activeCompanyId = useActiveCompanyId()
  const setActiveCompany = useCompanyStore((state) => state.setActiveCompany)
  const reorderCompanies = useCompanyStore((state) => state.reorderCompanies)

  // Configure dnd-kit sensors
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // Prevent accidental drags
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event

    if (over && active.id !== over.id) {
      reorderCompanies(active.id as string, over.id as string)
    }
  }

  const handleSelectCompany = (companyId: string) => {
    setActiveCompany(companyId)
  }

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

      {/* Company list with drag-and-drop */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {companies.length === 0 ? (
          <div className="flex items-center justify-center py-4">
            <p className="text-xs text-muted-foreground text-center">
              {collapsed ? 'No companies' : 'No companies yet'}
            </p>
          </div>
        ) : (
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
          >
            <SortableContext
              items={companies.map((c) => c.id)}
              strategy={verticalListSortingStrategy}
            >
              {companies.map((company) => (
                <SortableCompany
                  key={company.id}
                  company={company}
                  isActive={company.id === activeCompanyId}
                  collapsed={collapsed}
                  onSelect={handleSelectCompany}
                />
              ))}
            </SortableContext>
          </DndContext>
        )}
      </div>
    </div>
  )
}
