/**
 * BrainYAMLViewer Component
 *
 * **Purpose:** Modal dialog for viewing and copying brain YAML configuration
 * **Context:** Phase 08-03 — Engine Room brain config viewer
 */

'use client'

import { useState, useEffect, useCallback } from 'react'
import SyntaxHighlighter from 'react-syntax-highlighter'
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

// ─── Types ──────────────────────────────────────────────────────────────────

interface BrainYAMLViewerProps {
  brainId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

type CopyStatus = 'idle' | 'success' | 'error'

// ─── Component ──────────────────────────────────────────────────────────────

/**
 * Dialog for viewing brain YAML configuration with syntax highlighting and copy-to-clipboard.
 * Fetches from GET /api/brains/{id}/yaml when opened.
 */
export function BrainYAMLViewer({ brainId, open, onOpenChange }: BrainYAMLViewerProps) {
  const [yamlContent, setYamlContent] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [fetchError, setFetchError] = useState<string | null>(null)
  const [copyStatus, setCopyStatus] = useState<CopyStatus>('idle')

  // ─── Fetch YAML when dialog opens ──────────────────────────────────────

  useEffect(() => {
    if (!open) return

    const fetchYAML = async () => {
      setIsLoading(true)
      setFetchError(null)
      setYamlContent('')

      try {
        const res = await fetch(`/api/brains/${brainId}/yaml`)
        if (!res.ok) {
          throw new Error(`Failed to fetch brain YAML: ${res.status} ${res.statusText}`)
        }
        const yaml = await res.text()
        setYamlContent(yaml)
      } catch (e) {
        setFetchError(e instanceof Error ? e.message : 'Failed to load brain YAML')
      } finally {
        setIsLoading(false)
      }
    }

    fetchYAML()
  }, [open, brainId])

  // ─── Copy to clipboard ──────────────────────────────────────────────────

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(yamlContent)
      setCopyStatus('success')
      setTimeout(() => setCopyStatus('idle'), 2000)
    } catch {
      setCopyStatus('error')
      setTimeout(() => setCopyStatus('idle'), 2000)
    }
  }, [yamlContent])

  // ─── Copy button label ──────────────────────────────────────────────────

  const copyLabel = {
    idle: 'Copy to Clipboard',
    success: 'Copied!',
    error: 'Copy failed',
  }[copyStatus]

  // ─── Render ─────────────────────────────────────────────────────────────

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-auto">
        <DialogHeader>
          <DialogTitle>Brain Configuration: {brainId}</DialogTitle>
        </DialogHeader>

        {/* Loading state */}
        {isLoading && (
          <div className="flex items-center justify-center py-8 text-muted-foreground text-sm">
            Loading configuration...
          </div>
        )}

        {/* Error state */}
        {!isLoading && fetchError && (
          <div
            className="px-4 py-3 rounded bg-destructive/10 text-destructive text-sm"
            role="alert"
          >
            {fetchError}
          </div>
        )}

        {/* YAML content */}
        {!isLoading && !fetchError && yamlContent && (
          <>
            <div className="rounded overflow-hidden" aria-label="YAML configuration content">
              <SyntaxHighlighter
                language="yaml"
                style={atomOneDark}
                customStyle={{ margin: 0, fontSize: '0.75rem' }}
                wrapLongLines
              >
                {yamlContent}
              </SyntaxHighlighter>
            </div>

            <DialogFooter>
              {/* Copy status feedback */}
              {copyStatus !== 'idle' && (
                <span
                  className={`text-xs mr-auto self-center ${
                    copyStatus === 'success' ? 'text-green-500' : 'text-destructive'
                  }`}
                  role="status"
                  aria-live="polite"
                >
                  {copyLabel}
                </span>
              )}
              <Button
                onClick={handleCopy}
                variant="outline"
                disabled={!yamlContent}
                aria-label="Copy YAML to clipboard"
              >
                {copyLabel}
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
