/**
 * NodeConfigDialog — Stub configuration panel for flow nodes
 *
 * **Phase:** B1 Criterion 11 — Double-click node → configuration panel
 *
 * This is a STUB implementation that shows node information.
 * Full configuration panel will be implemented in future phases.
 *
 * **Features:**
 * - Shows node ID, type, and label
 * - "Configuration panel coming soon" message
 * - Theme-aware (uses var(--color-*) tokens)
 * - Accessible (proper ARIA labels)
 */

'use client'

import { Dialog, DialogContent } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import type { FlowNode } from './types'

// ─── Types ────────────────────────────────────────────────────────────────────

interface NodeConfigDialogProps {
  node: FlowNode | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

// ─── Component ────────────────────────────────────────────────────────────────

/**
 * NodeConfigDialog — stub dialog for node configuration.
 *
 * @example
 * ```tsx
 * const [selectedNode, setSelectedNode] = useState<FlowNode | null>(null)
 * const [dialogOpen, setDialogOpen] = useState(false)
 *
 * <NodeConfigDialog
 *   node={selectedNode}
 *   open={dialogOpen}
 *   onOpenChange={setDialogOpen}
 * />
 * ```
 */
export function NodeConfigDialog({ node, open, onOpenChange }: NodeConfigDialogProps) {
  const handleClose = () => {
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleClose()}>
      <DialogContent
        className="max-w-md"
        data-testid="node-config-dialog"
        aria-describedby="node-config-description"
      >
        <div className="space-y-4">
          {/* Header */}
          <div>
            <h2 className="text-lg font-semibold">Node Configuration</h2>
            <p
              id="node-config-description"
              className="text-sm text-muted-foreground mt-1"
            >
              Configuration panel coming soon
            </p>
          </div>

          {/* Node information */}
          {node && (
            <div className="space-y-2 rounded-md bg-muted/50 border border-border p-3">
              <div className="grid grid-cols-[100px_1fr] gap-2 text-sm">
                <span className="font-medium text-foreground">Node ID:</span>
                <span className="text-muted-foreground font-mono text-xs" data-testid="node-id">
                  {node.id}
                </span>

                <span className="font-medium text-foreground">Type:</span>
                <span className="text-muted-foreground" data-testid="node-type">
                  {node.type}
                </span>

                <span className="font-medium text-foreground">Label:</span>
                <span className="text-muted-foreground" data-testid="node-label">
                  {node.data.label}
                </span>
              </div>
            </div>
          )}

          {/* Close button */}
          <div className="flex justify-end">
            <Button onClick={handleClose} data-testid="close-dialog">
              Close
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
