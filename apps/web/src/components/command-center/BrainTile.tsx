/**
 * BrainTile Component (Placeholder for Task 2 tests)
 *
 * **Purpose:** Temporary placeholder to pass Task 2 tests
 * **Full Implementation:** Task 3 with ICE-validated status animations
 */

'use client'

import { Brain } from '@/lib/api'

interface BrainTileProps {
  brain: Brain
}

/**
 * BrainTile Component
 *
 * **Temporary Implementation:** Just displays brain name
 * **Full Implementation:** Task 3 with ICE-validated animations
 */
export function BrainTile({ brain }: BrainTileProps) {
  return (
    <div data-testid={`brain-${brain.id}`} className="brain-tile">
      {brain.name}
      {/* Full implementation in Task 3 */}
    </div>
  )
}
