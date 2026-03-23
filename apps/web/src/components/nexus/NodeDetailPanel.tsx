'use client'

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from '@/components/ui/sheet'
import { NodeStatusIndicator } from './NodeStatusIndicator'
import { useBrainState } from '@/stores/brainStore'
import type { Brain } from '@/lib/api'

interface NodeDetailPanelProps {
  brainId: string | null
  blueprintBrains: Brain[]
  onClose: () => void
}

/**
 * NodeDetailPanel — shadcn Sheet side panel for brain detail
 *
 * Live-bound via useBrainState(brainId) — updates in real-time (NEX-03).
 * Idle mode shows static brain config from blueprint data.
 * Active/complete/error shows status badge and last update timestamp.
 *
 * NOTE: This component is NOT inside React Flow canvas —
 * no nodrag/nopan classes needed here.
 */
export function NodeDetailPanel({
  brainId,
  blueprintBrains,
  onClose,
}: NodeDetailPanelProps) {
  const brain = blueprintBrains.find(b => b.id === brainId) ?? null
  const brainState = useBrainState(brainId ?? '')

  const isOpen = brainId !== null

  return (
    <Sheet open={isOpen} onOpenChange={open => { if (!open) onClose() }}>
      <SheetContent side="right">
        {brain ? (
          <>
            <SheetHeader>
              <SheetTitle>{brain.name}</SheetTitle>
              <SheetDescription>
                Niche: {brain.niche}
              </SheetDescription>
            </SheetHeader>

            <div className="flex flex-col gap-4 p-4">
              {/* Current status — live from brainStore */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Status:</span>
                <NodeStatusIndicator
                  status={brainState?.status ?? 'blueprint'}
                />
              </div>

              {/* Last update timestamp — only when active */}
              {brainState && brainState.lastUpdated > 0 && (
                <div className="text-xs text-muted-foreground">
                  Last updated:{' '}
                  {new Date(brainState.lastUpdated).toLocaleTimeString()}
                </div>
              )}

              {/* Brain config from blueprint */}
              <div className="flex flex-col gap-1">
                <span className="text-sm font-medium">Configuration</span>
                <div className="text-xs text-muted-foreground space-y-1">
                  <div>ID: {brain.id}</div>
                  <div>
                    Uptime: {brain.uptime > 0 ? `${brain.uptime}s` : 'N/A'}
                  </div>
                  {brain.last_called_at && (
                    <div>
                      Last called:{' '}
                      {new Date(brain.last_called_at).toLocaleString()}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="p-4 text-sm text-muted-foreground">
            Select a brain node to view details
          </div>
        )}
      </SheetContent>
    </Sheet>
  )
}
