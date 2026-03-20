/**
 * Bento Grid Component (Placeholder for Task 1 tests)
 *
 * **Purpose:** Temporary placeholder to pass Task 1 tests
 * **Full Implementation:** Task 2
 */

import { Brain } from '@/lib/api'

interface BentoGridProps {
  brains: Brain[]
}

/**
 * BentoGrid Component
 *
 * **Temporary Implementation:** Just displays brain count
 * **Full Implementation:** Task 2 with semantic clustering
 */
export function BentoGrid({ brains }: BentoGridProps) {
  return (
    <div data-testid="bento-grid">
      {brains.length} brains
      {/* Full implementation in Task 2 */}
    </div>
  )
}
