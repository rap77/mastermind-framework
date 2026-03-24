/**
 * KeyCreateDialog — Create a new API key with show-once pattern.
 *
 * **Security:** Full key shown ONLY once (in this dialog). Never logged, never cached.
 * User must copy it immediately — closing dialog permanently hides the key.
 *
 * **Flow:**
 * 1. "Create API Key" button → Dialog opens
 * 2. Dialog shows warning + Create button
 * 3. POST /api/keys → success shows full key in code block
 * 4. User copies key → clicks "Done" → dialog closes
 * 5. Key no longer accessible
 *
 * **Phase:** 08-04 — Wave 3 (API Key Management)
 */

'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

// ─── Types ────────────────────────────────────────────────────────────────────

interface CreatedKeyData {
  id: string
  full_key: string
}

// ─── Component ────────────────────────────────────────────────────────────────

/**
 * KeyCreateDialog — modal for API key generation with show-once enforcement.
 *
 * @example
 * ```tsx
 * // In APIKeyManager's "Create Key" tab
 * <KeyCreateDialog />
 * ```
 */
export function KeyCreateDialog() {
  const [open, setOpen] = useState(false)
  const [createdKey, setCreatedKey] = useState<CreatedKeyData | null>(null)
  const [copied, setCopied] = useState(false)
  const [copyError, setCopyError] = useState(false)
  const queryClient = useQueryClient()

  const { mutate: createKey, isPending, isError: createFailed } = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/keys', { method: 'POST' })
      if (!res.ok) throw new Error('Failed to create API key')
      return res.json() as Promise<CreatedKeyData>
    },
    onSuccess: (data) => {
      setCreatedKey(data)
      // Invalidate list — new key will appear when user switches to "My Keys" tab
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
    },
  })

  const handleCopy = async () => {
    if (!createdKey) return
    try {
      await navigator.clipboard.writeText(createdKey.full_key)
      setCopied(true)
      setCopyError(false)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      setCopyError(true)
    }
  }

  const handleClose = () => {
    setOpen(false)
    // Reset state — key is permanently gone after close
    setCreatedKey(null)
    setCopied(false)
    setCopyError(false)
  }

  const handleOpen = () => {
    setOpen(true)
    setCreatedKey(null)
    setCopied(false)
    setCopyError(false)
  }

  return (
    <>
      <div className="space-y-2">
        <p className="text-sm text-muted-foreground">
          Generate a new API key for external integrations. The key will be shown once — save it immediately.
        </p>
        <Button onClick={handleOpen} data-testid="open-create-dialog">
          Create API Key
        </Button>
      </div>

      <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleClose()}>
        <DialogContent
          className="max-w-md"
          showCloseButton={false}
          data-testid="key-create-dialog-content"
        >
          {!createdKey ? (
            /* ─── Step 1: Confirm creation ─── */
            <div className="space-y-4">
              <div>
                <h2 className="text-lg font-semibold">Create API Key</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  A new API key will be generated and shown once.
                  Copy it immediately and store it securely — it cannot be retrieved later.
                </p>
              </div>

              {createFailed && (
                <div
                  className="rounded-md bg-destructive/10 border border-destructive/20 px-3 py-2"
                  role="alert"
                >
                  <p className="text-sm text-destructive">
                    Failed to create API key. Please try again.
                  </p>
                </div>
              )}

              <div className="flex justify-end gap-2">
                <Button
                  variant="outline"
                  onClick={handleClose}
                  disabled={isPending}
                >
                  Cancel
                </Button>
                <Button
                  onClick={() => createKey()}
                  disabled={isPending}
                  data-testid="confirm-create-key"
                >
                  {isPending ? 'Creating...' : 'Create Key'}
                </Button>
              </div>
            </div>
          ) : (
            /* ─── Step 2: Show key once ─── */
            <div className="space-y-4">
              <div>
                <h2 className="text-lg font-semibold">API Key Created</h2>
              </div>

              {/* Security warning */}
              <div
                className="rounded-md bg-amber-500/10 border border-amber-500/30 px-3 py-2"
                role="alert"
              >
                <p className="text-sm text-amber-700 dark:text-amber-400 font-medium">
                  Save this key now. You won't be able to see it again.
                </p>
              </div>

              {/* Key display — monospace, user can click to select all */}
              <div
                className="relative rounded-md bg-slate-900 p-3 cursor-text"
                role="textbox"
                aria-readonly="true"
                aria-label="API key value"
                data-testid="created-key-display"
                onClick={() => {
                  const selection = window.getSelection()
                  const range = document.createRange()
                  const keyEl = document.querySelector('[data-testid="created-key-code"]')
                  if (keyEl && selection) {
                    range.selectNodeContents(keyEl)
                    selection.removeAllRanges()
                    selection.addRange(range)
                  }
                }}
              >
                <code
                  className="text-xs font-mono text-slate-100 break-all"
                  data-testid="created-key-code"
                >
                  {createdKey.full_key}
                </code>
              </div>

              {copyError && (
                <p className="text-xs text-destructive" role="alert">
                  Failed to copy. Please select the key manually and copy it.
                </p>
              )}

              <div className="flex justify-end gap-2">
                <Button
                  variant={copied ? 'default' : 'outline'}
                  onClick={handleCopy}
                  data-testid="copy-key-button"
                  className={copied ? 'bg-green-600 hover:bg-green-700' : ''}
                >
                  {copied ? 'Copied!' : 'Copy to Clipboard'}
                </Button>
                <Button onClick={handleClose} data-testid="done-button">
                  Done
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  )
}
