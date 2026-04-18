/**
 * LoadingSpinner — Accessible loading spinner component
 *
 * Reusable loading indicator with size variants and full accessibility support.
 * Includes screen reader announcements and proper ARIA attributes.
 *
 * @example
 * ```tsx
 * <LoadingSpinner size="sm" />
 * <LoadingSpinner size="md" className="text-primary" />
 * ```
 */

interface LoadingSpinnerProps {
  /** Size variant: sm (16px), md (24px), lg (32px) */
  size?: 'sm' | 'md' | 'lg'
  /** Additional CSS classes to apply */
  className?: string
  /** Accessibility label (defaults to "Loading...") */
  ariaLabel?: string
}

export function LoadingSpinner({
  size = 'md',
  className = '',
  ariaLabel = 'Loading...',
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-2',
    lg: 'w-8 h-8 border-4',
  }

  return (
    <div
      className={`animate-spin rounded-full border-current border-t-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite] ${sizeClasses[size]} ${className}`}
      role="status"
      aria-live="polite"
      aria-label={ariaLabel}
    >
      <span className="sr-only">{ariaLabel}</span>
    </div>
  )
}
