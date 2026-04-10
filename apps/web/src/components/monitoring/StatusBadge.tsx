'use client'

import { Check, AlertTriangle, X } from 'lucide-react'
import { cn } from '@/lib/utils'

type StatusVariant = 'idle' | 'running' | 'completed' | 'failed'

interface StatusBadgeProps {
  variant: StatusVariant
  showPing?: boolean
  count?: number
  showCount?: boolean
}

const variantConfig = {
  idle: {
    bgClass: 'bg-gray-100 dark:bg-gray-800',
    textClass: 'text-gray-700 dark:text-gray-300',
    dotColor: 'bg-gray-500',
    label: 'Idle'
  },
  running: {
    bgClass: 'bg-green-100 dark:bg-green-900',
    textClass: 'text-green-700 dark:text-green-300',
    dotColor: 'bg-green-500',
    label: 'Running'
  },
  completed: {
    bgClass: 'bg-blue-100 dark:bg-blue-900',
    textClass: 'text-blue-700 dark:text-blue-300',
    dotColor: 'bg-blue-500',
    label: 'Completed'
  },
  failed: {
    bgClass: 'bg-red-100 dark:bg-red-900',
    textClass: 'text-red-700 dark:text-red-300',
    dotColor: 'bg-red-500',
    label: 'Failed'
  }
}

const iconMap = {
  completed: Check,
  failed: X,
  running: Check,
  idle: AlertTriangle
}

export function StatusBadge({
  variant,
  showPing = false,
  count,
  showCount = false
}: StatusBadgeProps) {
  const config = variantConfig[variant]
  const Icon = iconMap[variant]

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium',
        config.bgClass,
        config.textClass
      )}
      role="status"
      aria-live="polite"
      aria-label={config.label}
    >
      {/* Status dot with ping animation for running */}
      <div className="relative flex items-center">
        {showPing && (
          <span
            className={cn(
              'absolute inline-flex h-full w-full animate-ping rounded-full opacity-75',
              config.dotColor
            )}
            aria-hidden="true"
          />
        )}
        <span
          className={cn(
            'relative inline-flex h-2 w-2 rounded-full',
            config.dotColor
          )}
          aria-hidden="true"
        />
      </div>

      {/* Icon for accessibility */}
      {Icon && (
        <Icon className="w-3.5 h-3" aria-hidden="true" />
      )}

      {/* Label */}
      <span>{showCount && count !== undefined ? `${count}` : config.label}</span>
    </div>
  )
}
