/**
 * KeyListTable — Display masked API keys with revoke actions.
 *
 * **Columns:** Key (prefix...suffix) | Created | Last Used | Actions (Revoke)
 * **Masking:** Only prefix + "..." + suffix shown — full key never exposed
 * **Revoke:** Confirm dialog → DELETE /api/keys/{id} → invalidate query cache
 *
 * **Phase:** 08-04 — Wave 3 (API Key Management)
 */

'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import type { APIKeyMasked } from './APIKeyManager'

// ─── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Format a date string as relative time (e.g., "2 weeks ago").
 * Falls back to locale date string if Intl.RelativeTimeFormat unavailable.
 */
export function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString)
  const now = Date.now()
  const diffMs = now - date.getTime()
  const diffSec = Math.floor(diffMs / 1000)

  if (diffSec < 60) return 'just now'
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`
  if (diffSec < 2592000) return `${Math.floor(diffSec / 86400)}d ago`
  if (diffSec < 31536000) return `${Math.floor(diffSec / 2592000)}mo ago`
  return `${Math.floor(diffSec / 31536000)}y ago`
}

// ─── Types ────────────────────────────────────────────────────────────────────

export interface KeyListTableProps {
  keys: APIKeyMasked[]
}

// ─── Component ────────────────────────────────────────────────────────────────

/**
 * KeyListTable — table of masked API keys with revoke actions.
 *
 * @example
 * ```tsx
 * <KeyListTable keys={data?.keys ?? []} />
 * ```
 */
export function KeyListTable({ keys }: KeyListTableProps) {
  const [pendingRevokeId, setPendingRevokeId] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { mutate: revokeKey, isPending: isRevoking } = useMutation({
    mutationFn: async (keyId: string) => {
      const res = await fetch(`/api/keys/${keyId}`, { method: 'DELETE' })
      if (!res.ok) throw new Error('Failed to revoke key')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
      setPendingRevokeId(null)
    },
    onError: () => {
      // Keep dialog open on error so user can retry
    },
  })

  const keyToRevoke = keys.find((k) => k.id === pendingRevokeId)

  return (
    <>
      <div className="border rounded-lg overflow-hidden">
        <table className="w-full text-sm" role="table" aria-label="API Keys">
          <thead className="bg-secondary">
            <tr>
              <th className="px-4 py-2 text-left font-medium text-muted-foreground">Key</th>
              <th className="px-4 py-2 text-left font-medium text-muted-foreground">Created</th>
              <th className="px-4 py-2 text-left font-medium text-muted-foreground">Last Used</th>
              <th className="px-4 py-2 text-right font-medium text-muted-foreground">Actions</th>
            </tr>
          </thead>
          <tbody>
            {keys.length === 0 ? (
              <tr>
                <td
                  colSpan={4}
                  className="px-4 py-8 text-center text-muted-foreground"
                  data-testid="empty-state"
                >
                  No API keys yet. Create one to get started.
                </td>
              </tr>
            ) : (
              keys.map((key) => (
                <tr
                  key={key.id}
                  className="border-t hover:bg-secondary/50 transition-colors"
                  data-testid={`key-row-${key.id}`}
                >
                  <td className="px-4 py-3 font-mono text-xs" data-testid="key-masked">
                    {key.prefix}...{key.suffix}
                  </td>
                  <td className="px-4 py-3 text-xs text-muted-foreground">
                    {formatRelativeTime(key.created_at)}
                  </td>
                  <td className="px-4 py-3 text-xs text-muted-foreground">
                    {key.last_used_at ? formatRelativeTime(key.last_used_at) : 'Never'}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => setPendingRevokeId(key.id)}
                      data-testid={`revoke-btn-${key.id}`}
                    >
                      Revoke
                    </Button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Revoke confirmation dialog */}
      <Dialog
        open={!!pendingRevokeId}
        onOpenChange={(isOpen) => !isOpen && setPendingRevokeId(null)}
      >
        <DialogContent showCloseButton={false} data-testid="revoke-confirm-dialog">
          <div className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold">Revoke API Key?</h2>
              <p className="text-sm text-muted-foreground mt-1">
                This action cannot be undone.{' '}
                {keyToRevoke && (
                  <span className="font-mono text-foreground">
                    {keyToRevoke.prefix}...{keyToRevoke.suffix}
                  </span>
                )}{' '}
                will be immediately revoked.
              </p>
            </div>

            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setPendingRevokeId(null)}
                disabled={isRevoking}
                data-testid="cancel-revoke"
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={() => pendingRevokeId && revokeKey(pendingRevokeId)}
                disabled={isRevoking}
                data-testid="confirm-revoke"
              >
                {isRevoking ? 'Revoking...' : 'Revoke'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
