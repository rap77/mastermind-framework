import { Check, AlertTriangle, X } from 'lucide-react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const statusBadgeVariants = cva(
  'flex items-center justify-center rounded-full font-medium',
  {
    variants: {
      status: {
        live: 'bg-green-500 text-white',
        warning: 'bg-yellow-500 text-white',
        error: 'bg-red-500 text-white',
      },
      size: {
        sm: 'w-2 h-2',
        md: 'w-3 h-3',
        lg: 'w-4 h-4',
      },
    },
    defaultVariants: {
      status: 'live',
      size: 'md',
    },
  }
)

export interface StatusBadgeProps
  extends VariantProps<typeof statusBadgeVariants> {
  count?: number
  showIcon?: boolean
  className?: string
  ariaLabel?: string
}

/**
 * StatusBadge — Visual status indicator with color AND icon coding (WCAG 2.1 AA compliant).
 *
 * Brain #3 requirement: Status indicators must have both color and icon coding
 * to ensure accessibility for users with color vision deficiencies.
 *
 * Variants:
 * - live (green): System operational, checkmark icon
 * - warning (yellow): Attention needed, warning icon
 * - error (red): Error state, X icon
 *
 * @example
 * ```tsx
 * <StatusBadge status="live" size="md" showIcon />
 * <StatusBadge status="warning" size="lg" count={5} showIcon />
 * <StatusBadge status="error" size="md" showIcon ariaLabel="Connection error" />
 * ```
 */
export function StatusBadge({
  status,
  size,
  count,
  showIcon = true,
  className,
  ariaLabel,
}: StatusBadgeProps) {
  const iconMap = {
    live: Check,
    warning: AlertTriangle,
    error: X,
  }

  const Icon = iconMap[status || 'live']

  // If count is provided, show a badge instead of a dot
  if (count !== undefined && count > 0) {
    return (
      <div
        className={cn(
          'flex items-center justify-center rounded-full bg-yellow-500 text-white font-bold text-xs min-w-[18px] h-[18px] px-1',
          className
        )}
        aria-label={ariaLabel || `${count} unread items`}
      >
        {count > 99 ? '99+' : count}
      </div>
    )
  }

  return (
    <div
      className={cn(statusBadgeVariants({ status, size }), className)}
      aria-label={ariaLabel || `Status: ${status}`}
    >
      {showIcon && <Icon className="w-full h-full" aria-hidden="true" />}
    </div>
  )
}
